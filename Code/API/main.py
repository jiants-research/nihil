import io
import os
import tempfile
import torch
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from starlette.background import BackgroundTask
from pydantic import BaseModel, validator
from TTS.api import TTS
from faster_whisper import WhisperModel
from transformers import AutoTokenizer, MT5ForConditionalGeneration

##
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import torch
import torchaudio
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from pydub import AudioSegment
import tempfile
import os


import os
import zipfile
import requests

MODEL_URL = "https://github.com/jiants-research/nihil/releases/download/whisper-bassa/model_final.zip"
MODEL_DIR = "./model"
ZIP_PATH = os.path.join(MODEL_DIR, "model_final.zip")
EXTRACT_DIR = os.path.join(MODEL_DIR, "model_final")

# === Téléchargement si nécessaire ===
os.makedirs(MODEL_DIR, exist_ok=True)

if not os.path.exists(EXTRACT_DIR):
    print("Téléchargement du modèle...")
    r = requests.get(MODEL_URL, stream=True)
    with open(ZIP_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Décompression...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(MODEL_DIR)

    print("✅ Modèle extrait dans :", EXTRACT_DIR)


# Chargement du modèle
processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
model = WhisperForConditionalGeneration.from_pretrained("./model/model_final")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Limit CPU threads to avoid contention when serving multiple models
torch.set_num_threads(1)

# Select device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load translation model (Toucan-1.2B)
MODEL_PATH = "UBC-NLP/toucan-1.2B"
tokenizer_mt = AutoTokenizer.from_pretrained(MODEL_PATH)
model_mt = MT5ForConditionalGeneration.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto"
)
model_mt.eval()

# Load multilingual TTS model
tts_model = TTS(
    model_name="tts_models/multilingual/multi-dataset/your_tts",
    progress_bar=False
).to(DEVICE)

# Load Whisper STT model
stt_model = WhisperModel(
    "large-v2",
    device=DEVICE,
    compute_type="int8"
)

app = FastAPI(title="FR/EN TTS & STT Service")

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow cookies and authorization headers
    allow_methods=["*"],     # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allow all headers
)

def translate_with_toucan(text: str, target_code: str = "bas") -> str:
    """
    Runs inference with the loaded toucan-1.2B model.
    """
    input_text = f"{target_code}: {text}"
    inputs = tokenizer_mt(
        input_text,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    )
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        generated = model_mt.generate(
            **inputs,
            num_beams=2,
            max_new_tokens=len(text),
            do_sample=True,
            temperature=0.6,
            top_p=0.9
        )

    return tokenizer_mt.decode(generated[0], skip_special_tokens=True)


class TTSRequest(BaseModel):
    text: str
    language: str  # "en" or "fr"

    @validator("language")
    def check_lang(cls, v):
        if v not in ("en", "fr"):
            raise ValueError("language must be 'en' or 'fr'")
        return v


class TranslationRequest(BaseModel):
    text: str
    target_language: str  # "en", "fr", or "bas"

    @validator("target_language")
    def check_lang(cls, v):
        if v not in ("en", "fr", "bas"):
            raise ValueError("target_language must be 'en', 'fr', or 'bas'")
        return v


@app.post("/translate/")
async def translate(request: TranslationRequest):
    """
    Translate input text into the specified target language.
    """
    translation = translate_with_toucan(request.text, request.target_language)
    return {"translation": translation}


@app.post("/tts/")
async def tts(request: TTSRequest):
    """
    Text-to-speech endpoint. Returns a WAV audio stream.
    """
    lang_tag = "en" if request.language == "en" else "fr-fr"

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    try:
        tts_model.tts_to_file(
            text=request.text,
            speaker_wav="Recording.wav",
            language=lang_tag,
            file_path=tmp.name
        )
    except Exception as e:
        tmp.close()
        os.remove(tmp.name)
        raise HTTPException(status_code=500, detail=str(e))
    tmp.close()

    return StreamingResponse(
        open(tmp.name, "rb"),
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=\"tts_output.wav\""},
        background=BackgroundTask(lambda: os.remove(tmp.name))
    )


@app.post("/stt/")
async def stt(
    audio_file: UploadFile = File(...),
    language: str = Form(...)
):
    """
    Speech-to-text endpoint. Accepts WAV/MP3 and returns a JSON transcript.
    """
    if language not in ("en", "fr"):
        raise HTTPException(status_code=400, detail="language must be 'en' or 'fr'")

    suffix = "." + audio_file.filename.split(".")[-1]
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    content = await audio_file.read()
    tmp.write(content)
    tmp.flush()
    tmp.close()

    try:
        segments, _ = stt_model.transcribe(tmp.name, language=language)
        transcript = "".join(seg.text for seg in segments).strip()
    except Exception as e:
        os.remove(tmp.name)
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(
        {"transcript": transcript},
        background=BackgroundTask(lambda: os.remove(tmp.name))
    )

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        filename = file.filename.lower()

        # Fichier temporaire original
        with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as tmp_in:
            tmp_in.write(await file.read())
            tmp_input_path = tmp_in.name

        # Si déjà .wav = vérifier le sampling rate
        if filename.endswith(".wav"):
            info = torchaudio.info(tmp_input_path)
            if info.sample_rate == 16000:
                tmp_wav_path = tmp_input_path
            else:
                tmp_wav_path = tmp_input_path + "_resampled.wav"
                audio = AudioSegment.from_wav(tmp_input_path)
                audio = audio.set_frame_rate(16000).set_channels(1)
                audio.export(tmp_wav_path, format="wav")
        else:
            # Autres formats = conversion .wav
            tmp_wav_path = tmp_input_path + ".wav"
            audio = AudioSegment.from_file(tmp_input_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(tmp_wav_path, format="wav")

        # Charger audio traité
        speech_array, sr = torchaudio.load(tmp_wav_path)
        inputs = processor(speech_array.squeeze().numpy(), sampling_rate=16000, return_tensors="pt")
        input_tensor = inputs.input_features.to(device)

        with torch.no_grad():
            predicted_ids = model.generate(input_tensor)
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

        # Nettoyage
        os.remove(tmp_input_path)
        if tmp_wav_path != tmp_input_path:
            os.remove(tmp_wav_path)

        return JSONResponse({"transcription": transcription})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
##

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=1
    )
