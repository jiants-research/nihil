# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import uuid
import os
import tarfile

# Imports Coqui TTS
from TTS.tts.configs.vits_config import VitsConfig
from TTS.tts.models.vits import Vits
from TTS.utils.audio import AudioProcessor
from TTS.tts.utils.text.tokenizer import TTSTokenizer
import torch




# ==== Initialisation unique (chargement du modèle) ====

RUN_FOLDER = "./model"
MODEL_PATH = os.path.join(RUN_FOLDER, "best_model.pth")
CONFIG_PATH = os.path.join(RUN_FOLDER, "config.json")


# Décompression automatique si le .pth n'existe pas

pth_path = os.path.join(RUN_FOLDER, "best_model.pth")
tgz_path = os.path.join(RUN_FOLDER, "best_model.tar.gz")

if not os.path.exists(pth_path) and os.path.exists(tgz_path):
    print("📦 Décompression du best_model...")
    with tarfile.open(tgz_path, "r:gz") as tar:
        tar.extractall(RUN_FOLDER)

device = "cuda" if torch.cuda.is_available() else "cpu"
config = VitsConfig()
config.load_json(CONFIG_PATH)
tokenizer, config = TTSTokenizer.init_from_config(config)
ap = AudioProcessor.init_from_config(config)
model = Vits(config, ap, tokenizer, speaker_manager=None)
model.load_checkpoint(config, MODEL_PATH, eval=True)
model.to(device)

# ==== API FastAPI ====

app = FastAPI()

class SynthesisInput(BaseModel):
    text: str

@app.post("/synthesize")
def synthesize(input: SynthesisInput):
    try:
        # Tokenisation manuelle
        tokens = tokenizer.text_to_ids(input.text, language=config.datasets[0].language)
        x = torch.tensor(tokens, dtype=torch.long).unsqueeze(0).to(device)
        x_lengths = torch.tensor([len(tokens)], dtype=torch.int32).to(device)

        # Synthèse
        with torch.no_grad():
            outputs = model.inference(x, x_lengths)
            wav = outputs["model_outputs"].squeeze().cpu().numpy()

        # Sauvegarde temporaire
        output_path = f"/tmp/output_{uuid.uuid4().hex[:8]}.wav"
        ap.save_wav(wav, output_path, sr=config.audio.sample_rate)

        return FileResponse(output_path, media_type="audio/wav", filename="output.wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
