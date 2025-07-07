# Coqui TTS Bassa - API FastAPI

Cette API expose un modèle de synthèse vocale (`Text-to-Speech`) entraîné sur la langue **Bassa** (Cameroon) à l'aide de **Coqui TTS** et **FastAPI**.

Elle permet de transformer du texte en un fichier `.wav` que tu peux écouter ou télécharger.

---

##  Fonctionnalités

-  Chargement d’un modèle VITS entraîné avec Coqui TTS
-  API REST simple avec une seule route `/synthesize`
-  Renvoie un fichier `.wav` synthétisé à partir d’un texte

---

## 📁 Structure du projet

.
├── main.py # Code de l'API FastAPI
├── Dockerfile # Pour créer l'image Docker
├── requirements.txt # Dépendances Python
├── README.md
└── run-July-05-2025_05+29AM-0000000/
├── checkpoint_1.pth # Poids du modèle
└── config.json # Configuration du modèle


---

## ⚙️ Prérequis

- [Docker](https://www.docker.com/) installé

---

##  Installation

### 1. Cloner ce projet

```bash
git clone <lien-vers-ton-repo>
cd coqui-tts-api

```
### 2. Construire l’image Docker

```bash
docker build -t coqui-tts-api
```

### 3. Lancer l’API
```bash
docker run -p 8000:8000 coqui-tts-api
```

## Utilisation de l’API

### Route POST /synthesize
- URL : http://localhost:8000/synthesize
- Méthode : POST

- Corps JSON :
```
{
  "text": "Hôyôs me mbegee!"
}
```
- Réponse : un fichier audio .wav généré par le modèle


## Exemple avec curl
```
curl -X POST http://localhost:8000/synthesize \
     -H "Content-Type: application/json" \
     -d '{"text": "Hôyôs me mbegee!"}' \
     --output bassa_output.wav
```

## Exemple Python
```
import requests

response = requests.post("http://localhost:8000/synthesize", json={"text": "Bibôlôl bi mañ."})
with open("bassa.wav", "wb") as f:
    f.write(response.content)
 Tester localement sans Docker (optionnel)
```

```
pip install -r requirements.txt
uvicorn main:app --reload
```


## 📌 Notes

Le modèle utilisé est un modèle VITS entraîné sur un corpus en langue Bassa.
Le fichier config.json et le checkpoint .pth doivent être présents dans le dossier run-*.
