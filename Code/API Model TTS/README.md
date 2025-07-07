
# 🇨🇲 Whisper Bassa API - Transcription Audio en Langue Bassa

[![Licence: MIT](https://img.shields.io/badge/Licence-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)]()
[![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-green.svg)]()

Ce projet met à disposition une API RESTful performante pour la transcription automatique de fichiers audio en **langue Bassa** (parlée au Cameroun). Il s'appuie sur un modèle **Whisper d'OpenAI fine-tuné** spécifiquement pour cette langue, offrant ainsi une solution spécialisée pour la communauté Bassa et les chercheurs en linguistique.

---

## Fonctionnalités Clés

-   **🎯 Spécialisation Bassa** : Utilise un modèle Whisper fine-tuné pour une meilleure précision sur la langue Bassa.
-   **🎤 Multi-format** : Prend en charge une large gamme de formats audio (`.wav`, `.mp3`, `.flac`, `.ogg`, etc.).
-   **⚙️ Prétraitement Automatique** : Convertit automatiquement les fichiers audio au format requis (`.wav`, mono, 16 kHz) en arrière-plan.
-   **🚀 Accélération GPU** : Détecte et utilise automatiquement un GPU disponible (`CUDA`) pour des transcriptions beaucoup plus rapides.
-   **📚 API Documentée** : Fournit une interface interactive Swagger UI pour tester facilement les points d'accès.

---

## Comment ça marche ?

L'API est construite avec **FastAPI** pour sa rapidité et sa simplicité. Lorsqu'un fichier audio est envoyé :
1.  **Pydub** et **FFmpeg** chargent et convertissent le fichier audio.
2.  **Transformers** et **PyTorch** chargent le modèle Whisper fine-tuné et son processeur.
3.  Le modèle traite le signal audio et retourne la transcription textuelle.

---

## Mise en Route

Suivez ces étapes pour lancer l'API sur votre machine locale.

### 1. Prérequis

Assurez-vous d'avoir les éléments suivants installés :
-   **Python 3.8** ou supérieur.
-   **Git** pour cloner le projet.
-   **FFmpeg** : C'est une dépendance **cruciale** pour le traitement audio.
    -   Pour vérifier s'il est installé, ouvrez un terminal et tapez : `ffmpeg -version`.
    -   Si ce n'est pas le cas, suivez les [instructions d'installation officielles](https://ffmpeg.org/download.html).

### 2. Installation

```bash
# 1. Clonez ce dépôt et naviguez dans le répertoire
git clone https://github.com/TON-UTILISATEUR/whisper-bassa-api.git
cd whisper-bassa-api

# 2. (Recommandé) Créez et activez un environnement virtuel
python -m venv venv
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate

# 3. Installez les dépendances Python
pip install -r requirements.txt
```

### 3. Configuration du Modèle

Le système est configuré pour charger le modèle depuis des dossiers spécifiques :
-   **Modèle fine-tuné** : doit être placé dans `./model/checkpoint-2500/`.
-   **Processeur du modèle** : est chargé depuis `openai/whisper-tiny`.

Si vous possédez un dossier complet contenant à la fois le modèle et le processeur (par exemple, sauvegardé avec `save_pretrained`), vous pouvez :
1.  Placer ce dossier à la racine (ex: `./mon-modele-complet/`).
2.  Modifier le fichier `main.py` pour charger le modèle et le processeur depuis ce dossier unique.

---

## Utilisation

### 1. Lancer l'API

Une fois l'installation terminée, lancez le serveur Uvicorn :

```bash
uvicorn main:app --reload
```

L'option `--reload` permet au serveur de redémarrer automatiquement après chaque modification du code.

### 2. Explorer l'API

Ouvrez votre navigateur et accédez à la documentation interactive générée par Swagger UI :

- **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

Vous pourrez y voir tous les points d'accès disponibles et même envoyer des fichiers audio pour tester l'API directement depuis votre navigateur.

### 3. Exemple avec un Script Python

Voici comment interroger l'API avec un simple script Python.

```python
# test_api.py
import requests

# Remplacez par le chemin de votre fichier audio
audio_file_path = "chemin/vers/votre/audio.mp3"
api_url = "http://127.0.0.1:8000/transcribe/"

try:
    with open(audio_file_path, "rb") as f:
        # L'API attend le fichier dans un champ nommé "file"
        files = {"file": (audio_file_path, f, "audio/mpeg")}
        response = requests.post(api_url, files=files)

        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status() 
        
        data = response.json()
        print("Transcription réussie !")
        print(f"-> {data['transcription']}")

except FileNotFoundError:
    print(f"Erreur : Le fichier '{audio_file_path}' n'a pas été trouvé.")
except requests.exceptions.RequestException as e:
    print(f"Erreur de connexion à l'API : {e}")

```

#### Exemple de Réponse JSON

```json
{
  "transcription": "Ba ñoo bé jón"
}
```

