from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel
import os

app = FastAPI(title="Dummy FR/EN TTS & STT Service")

# Path to the dummy audio file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDING_PATH = os.path.join(BASE_DIR, "Recording.wav")

# --- Pydantic request models ---
class TranslationRequest(BaseModel):
    text: str
    target_language: str  # "en", "fr", or "bas"

class TTSRequest(BaseModel):
    text: str
    language: str  # "en" or "fr"

# --- Endpoints ---
@app.post("/translate/")
async def translate(request: TranslationRequest):
    """
    Dummy translation endpoint.
    """
    # Return a placeholder translation
    return {"translation": f"[DUMMY] '{request.text}' -> '{request.target_language}'"}

@app.post("/tts/")
async def tts(request: TTSRequest):
    """
    Dummy TTS endpoint: streams a static WAV file regardless of input.
    """
    if not os.path.exists(RECORDING_PATH):
        return JSONResponse({"error": "Recording.wav not found."}, status_code=500)

    # Stream the dummy recording
    file_stream = open(RECORDING_PATH, "rb")
    return StreamingResponse(
        file_stream,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=tts_output.wav"}
    )

@app.post("/stt/")
async def stt(
    audio_file: UploadFile = File(...),
    language: str = Form(...)
):
    """
    Dummy STT endpoint: ignores the uploaded file and returns a fixed transcript.
    """
    return {"transcript": f"[DUMMY] Transcript of audio in '{language}'"}

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Dummy transcription endpoint: returns a static transcription.
    """
    return {"transcription": "[DUMMY] This is a placeholder transcription."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "dummy_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
