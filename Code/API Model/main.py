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
processor = WhisperProcessor.from_pretrained("./local_whisper_tiny")
model = WhisperForConditionalGeneration.from_pretrained("./model/model_final")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()


app = FastAPI(title="Whisper Bassa API")

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

@app.get("/")
async def root():
    return {"message": "Welcome to the Whisper Bassa API! Use /transcribe/ to transcribe audio files."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Pour lancer le serveur, exécutez la commande suivante dans le terminal :
# uvicorn main:app --reload

# Assurez-vous d'avoir installé les dépendances nécessaires :
# pip install fastapi uvicorn torch torchaudio transformers