# main.py

import io
import tempfile
import torch
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, validator
from TTS import TTS
from faster_whisper import WhisperModel

import torch
from transformers import pipeline, AutoTokenizer, MT5ForConditionalGeneration

model_path = "UBC-NLP/toucan-1.2B"  # we use the base model because we can't upload the fine-tuned one for test
tokenizer_mt = AutoTokenizer.from_pretrained(model_path)
model_mt = MT5ForConditionalGeneration.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto")
model_mt.eval()

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

# ---- helper
def translate_with_toucan(text, target_code="bas"):
    """
    Runs inference with the loaded toucan-1.2B model using pipeline.

    Args:
        text (str): The text to translate.
        target_code (str): The language code to translate to (e.g., 'eng', 'fra').

    Returns:
        str: The translated text.
    """

    # Format the input string for translation
    input_text = f"{target_code}: {text}"
    input_ids = tokenizer_mt(input_text, return_tensors="pt", max_length=1024, truncation=True).to("cuda:0")
    with torch.no_grad():
        generated_ids = model_mt.generate(**input_ids, num_beams=2, max_new_tokens=len(text), do_sample=True, temperature=0.6, top_p=0.9)
    # Run inference

    translated_text = tokenizer_mt.batch_decode(generated_ids, skip_special_tokens=True,  skip_prompt=True)[0]
    return translated_text

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
    language: str  # "en" or "fr" or "bas" # Target language

    @validator("language")
    def check_lang(cls, v):
        if v not in ("en", "fr", "bas"):
            raise ValueError("language must be 'en' or 'fr' or 'bas'")
        return v

@app.post("/translate/")
async def translate(request: TranslationRequest):
    """
    Tranlation from language to language
    """
    input_text = f"{request.language}: {request.text}"
    translation = translate_with_toucan(request.text, request.language)

    return {
        "translation": translation
    }

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
