# main.py

import io
import tempfile
import torch
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, validator
from TTS import TTS
from faster_whisper import WhisperModel

# choose device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# load TTS (multilingual your_tts covers both fr and en)
tts_model = TTS(
    model_name="tts_models/multilingual/multi-dataset/your_tts",
    progress_bar=False
).to(DEVICE)

# load STT
stt_model = WhisperModel("large-v2", compute_type="int8")

app = FastAPI(title="FR/EN TTS & STT Service")


class TTSRequest(BaseModel):
    text: str
    language: str  # "en" or "fr"

    @validator("language")
    def check_lang(cls, v):
        if v not in ("en", "fr"):
            raise ValueError("language must be 'en' or 'fr'")
        return v


@app.post("/tts/")
async def tts(request: TTSRequest):
    """
    Text-to-speech.
    Request JSON: { "text": "...", "language": "en" | "fr" }
    Returns: WAV audio stream.
    """
    # map to Coqui TTS language tags
    lang_tag = "en" if request.language == "en" else "fr-fr"
    # generate into an in-memory buffer
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        try:
            tts_model.tts_to_file(
                text=request.text,
                speaker_wav=None,
                language=lang_tag,
                file_path=tmp.name
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        tmp.seek(0)
        data = tmp.read()

    return StreamingResponse(
        io.BytesIO(data),
        media_type="audio/wav",
        headers={"Content-Disposition": 'attachment; filename="tts_output.wav"'}
    )


@app.post("/stt/")
async def stt(
    audio_file: UploadFile = File(...),
    language: str = Form(...)
):
    """
    Speech-to-text.
    Form-data:
      - audio_file: WAV/MP3 file
      - language: "en" or "fr"
    Returns: { "transcript": "..." }
    """
    if language not in ("en", "fr"):
        raise HTTPException(status_code=400, detail="language must be 'en' or 'fr'")

    # write upload to temp file
    suffix = "." + audio_file.filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await audio_file.read()
        tmp.write(content)
        tmp.flush()
        tmp_path = tmp.name

    # run Whisper
    try:
        segments, _ = stt_model.transcribe(tmp_path, language=language)
        text = "".join([seg.text for seg in segments]).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"transcript": text})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
