import io
import os
import tempfile
import torch
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.background import BackgroundTask
from starlette.background import BackgroundTask
from pydantic import BaseModel, validator
from TTS.api import TTS
from faster_whisper import WhisperModel
from transformers import AutoTokenizer, MT5ForConditionalGeneration

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
            speaker_wav=None,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=1
    )
