import io
import os
import tempfile
import torch
from fastapi import (
    FastAPI, Request, Body, HTTPException,
    File, Form, UploadFile
)
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from pydantic import BaseModel, validator
from typing import Optional
from TTS.api import TTS
from faster_whisper import WhisperModel
from transformers import AutoTokenizer, MT5ForConditionalGeneration
import zipfile
import requests
import torch
import torchaudio
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from pydub import AudioSegment

# Limit CPU threads to avoid contention when serving multiple models
torch.set_num_threads(1)

# Select device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize FastAPI
app = FastAPI(title="FR/EN/BAS TTS & STT Service")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDING_PATH = os.path.join(BASE_DIR, "Recording.wav")
MODEL_DIR = os.path.join(BASE_DIR, "model")
ZIP_PATH = os.path.join(MODEL_DIR, "model_final.zip")
EXTRACT_DIR = os.path.join(MODEL_DIR, "model_final")

# --- Load translation model (Toucan-1.2B) ---
MODEL_PATH = "UBC-NLP/toucan-1.2B"
tokenizer_mt = AutoTokenizer.from_pretrained(MODEL_PATH)
model_mt = MT5ForConditionalGeneration.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto"
)
model_mt.eval()

# --- Load multilingual TTS model ---
tts_model = TTS(
    model_name="tts_models/multilingual/multi-dataset/your_tts",
    progress_bar=False
).to(device)

# --- Load Whisper STT model ---
stt_model = WhisperModel(
    "large-v2",
    device=device,
    compute_type="int8"
)

# --- Ensure custom transcribe model is downloaded/extracted ---
os.makedirs(MODEL_DIR, exist_ok=True)
if not os.path.exists(EXTRACT_DIR):
    r = requests.get(
        "https://github.com/jiants-research/nihil/releases/download/whisper-bassa/model_final.zip",
        stream=True
    )
    with open(ZIP_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(MODEL_DIR)

processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
model_bassa = WhisperForConditionalGeneration.from_pretrained(EXTRACT_DIR)
model_bassa.to(device)
model_bassa.eval()

# --- Pydantic models ---
class TranslationRequest(BaseModel):
    text: str
    target_language: str

    @validator("target_language")
    def check_target(cls, v):
        if v not in ("en", "fr", "bas"):
            raise ValueError("target_language must be 'en', 'fr', or 'bas'")
        return v

class TTSRequest(BaseModel):
    text: str
    language: str

    @validator("language")
    def check_lang(cls, v):
        if v not in ("en", "fr"):
            raise ValueError("language must be 'en' or 'fr'")
        return v

# --- Helper: translate_with_toucan ---
def translate_with_toucan(text: str, target: str = "bas") -> str:
    input_text = f"{target}: {text}"
    inputs = tokenizer_mt(
        input_text,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        gen = model_mt.generate(
            **inputs,
            num_beams=2,
            max_new_tokens=len(text),
            do_sample=True,
            temperature=0.6,
            top_p=0.9
        )
    return tokenizer_mt.decode(gen[0], skip_special_tokens=True)

# --- Endpoints supporting both GET & POST ---

@app.api_route("/translate/", methods=["GET", "POST"])
async def translate_both(
    request: Request,
    payload: Optional[TranslationRequest] = Body(None),
    text: Optional[str] = None,
    target_language: Optional[str] = None,
):
    if request.method == "POST":
        if not payload:
            raise HTTPException(400, "JSON body required for POST")
        text = payload.text
        target_language = payload.target_language
    else:
        if text is None or target_language is None:
            raise HTTPException(400, "Query params 'text' and 'target_language' required for GET")
    translation = translate_with_toucan(text, target_language)
    return {"translation": translation, "method": request.method}

@app.api_route("/tts/", methods=["GET", "POST"])
async def tts_both(
    request: Request,
    payload: Optional[TTSRequest] = Body(None),
    text: Optional[str] = None,
    language: Optional[str] = None,
):
    if request.method == "POST":
        if not payload:
            raise HTTPException(400, "JSON body required for POST")
        text = payload.text
        language = payload.language
    else:
        if text is None or language is None:
            raise HTTPException(400, "Query params 'text' and 'language' required for GET")
    if not os.path.exists(RECORDING_PATH):
        return JSONResponse({"error": "Recording.wav not found."}, status_code=500)
    # generate on temp
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    try:
        tag = "en" if language == "en" else "fr-fr"
        tts_model.tts_to_file(text=text, speaker_wav=RECORDING_PATH,
                              language=tag, file_path=tmp.name)
    except Exception as e:
        tmp.close(); os.remove(tmp.name)
        raise HTTPException(500, detail=str(e))
    tmp.close()
    return StreamingResponse(
        open(tmp.name, "rb"),
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=tts_output.wav"},
        background=BackgroundTask(lambda: os.remove(tmp.name))
    )

@app.api_route("/stt/", methods=["GET", "POST"])
async def stt_both(
    request: Request,
    audio_file: Optional[UploadFile] = File(None),
    form_lang: Optional[str] = Form(None),
    language: Optional[str] = None,
):
    if request.method == "POST":
        if audio_file is None or form_lang is None:
            raise HTTPException(400, "File+form 'language' required for POST")
        lang = form_lang
        # save temp file
        suffix = os.path.splitext(audio_file.filename)[1]
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp.write(await audio_file.read()); tmp.close()
        segs, _ = stt_model.transcribe(tmp.name, language=lang)
        text = "".join(s.text for s in segs).strip()
        return JSONResponse({"transcript": text}, background=BackgroundTask(lambda: os.remove(tmp.name)))
    else:
        if language is None:
            raise HTTPException(400, "Query param 'language' required for GET")
        return {"transcript": f"[DUMMY] Transcript of audio in '{language}'", "method": "GET"}

@app.api_route("/transcribe/", methods=["GET", "POST"])
async def transcribe_both(
    request: Request,
    file: Optional[UploadFile] = File(None)
):
    if request.method == "POST":
        if not file:
            raise HTTPException(400, "File required for POST")
        # save & convert
        name = file.filename.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=name) as tmp_in:
            tmp_in.write(await file.read())
            inp = tmp_in.name
        if name.endswith(".wav"):
            info = torchaudio.info(inp)
            if info.sample_rate != 16000:
                out = inp + "_res.wav"
                AudioSegment.from_wav(inp).set_frame_rate(16000).set_channels(1).export(out, format="wav")
                os.remove(inp); inp = out
        else:
            out = inp + ".wav"
            AudioSegment.from_file(inp).set_frame_rate(16000).set_channels(1).export(out, format="wav")
            os.remove(inp); inp = out
        speech, sr = torchaudio.load(inp)
        inputs = processor(speech.squeeze().numpy(), sampling_rate=16000, return_tensors="pt").input_features.to(device)
        with torch.no_grad(): ids = model_bassa.generate(inputs)
        text = processor.batch_decode(ids, skip_special_tokens=True)[0]
        os.remove(inp)
        return {"transcription": text}
    else:
        return {"transcription": "[DUMMY] This is a placeholder transcription.", "method": "GET"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)
