# ✅ 1. Image de base Python avec CUDA support si besoin
FROM python:3.10-slim

# ✅ 2. Variables d’environnement pour éviter les prompts
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ✅ 3. Dépendances système
RUN apt-get update && apt-get install -y \
    libsndfile1-dev \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# ✅ 4. Création du dossier de travail
WORKDIR /app

# ✅ 5. Copie du code
COPY . /app

# ✅ 6. Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    TTS

# ✅ 7. Port exposé
EXPOSE 8000

# ✅ 8. Commande de lancement
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
