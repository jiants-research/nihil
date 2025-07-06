# NIHIL — Le Retour des Langues

[![Watch the video](./Communication/video-thumbnail.png)](./Communication/prom.mp4)



---

## 🎤 Mot de l’équipe

> **Bonsoir à l’équipe du concours CONIA,  
> JIANTS vous présente Nihil : l’IA pour donner une voix aux langues camerounaises et pas seulement traduire.**  
>
> “Nihil, a IA inyu ti we lipém inyu ngandak langues camerounaises.”  
> *Traduit en basaa par Nihil, notre Intelligence Artificielle.*

---

## 📌 À propos du projet

**Titre du projet :** BACK TO TONGUES  
**Nom de l’application :** NIHIL  
**Nom de l’équipe :** The Young JIANTS  
**Responsable :** André Kévin NYEMB, Ingénieur de recherche en IA  

Nihil est une plateforme éducative et culturelle conçue pour promouvoir, valoriser et préserver les langues maternelles camerounaises. L’application propose des services de traduction multiforme et d’apprentissage interactif pour le **basaa**, le **français** et l’**anglais**, avec pour ambition de se déployer progressivement vers d’autres idiomes.

---

## 🎯 Objectifs

### Objectifs généraux  
- **Valoriser la culture locale** et les langues maternelles.  
- **Intégrer l’IA** dans l’apprentissage linguistique.  
- **Réduire la fracture numérique** en offrant des outils accessibles à tous.

### Objectifs spécifiques  
- Développer un **module de traduction** (text-to-text, text-to-speech, speech-to-text, speech-to-speech).  
- Concevoir des **jeux éducatifs** et cours structurés pour une pratique quotidienne.  
- Mettre en place un **correcteur vocal** pour améliorer prononciation et orthographe.  
- Constituer et raffiner un **corpus multilingue** (basaa ←→ français ←→ anglais, 112 000 lignes alignées).

---


### Presentation App

### 🗣️ 1. Traduction vocale en temps réel *(Speech-to-Speech)*  
Parlez dans une langue locale, obtenez la voix traduite dans une autre.

![Traduction vocale](assets/screens/01_traduction_vocale.png)

---

### 💬 2. Traduction texte à texte  
Saisissez un texte dans n’importe quelle langue prise en charge et obtenez sa traduction instantanée.

![Texte à texte](assets/screens/02_text_to_text.png)

---

### 📂 3. Upload de fichiers audio  
Importez un fichier (journal radio, message vocal, podcast...) → obtenez **transcription + traduction**.

![Upload audio](assets/screens/03_upload_audio.png)

---

### 🧠 4. Détection automatique de la langue  
Plus besoin de choisir manuellement la langue d’entrée. L’application la détecte intelligemment.

![Langue automatique](assets/screens/04_lang_detect.png)

---

### 👥 5. Mode conversation  
Parfait pour les discussions bilingues : chacun parle dans sa langue, l'app traduit pour l’autre.

![Mode conversation](assets/screens/05_mode_conversation.png)

---

### 🌍 Cas d’usage réels

- 🎙️ Traduction de journaux radios communautaires  
- 🏥 Communication patient-soignant en milieu rural  
- 🎓 Enseignement bilingue et alphabétisation  
- 📱 Traduction de messages vocaux WhatsApp  
- 🎭 Sauvegarde du patrimoine oral

---

## 🚀 Fonctionnalités clés

1. **Traduction tridirectionnelle**  
   - Basaa ↔ Français  
   - Basaa ↔ Anglais  
   - Français ↔ Anglais  
2. **Speech-to-Text & Text-to-Speech**  
   - Transcription en direct des conversations WhatsApp en basaa.  
   - Synthèse vocale expérimentale en basaa.  
3. **Jeux & Cours interactifs**  
   - Quiz, flashcards, puzzles de mots.  
   - Leçons modulaires (grammaire, vocabulaire, expressions).  
4. **Suivi de progression**  
   - Historique, scores, badges et encouragements.  
5. **Interface adaptée**  
   - Conçue pour enfants et adultes, sans création de compte ni abonnement.

---

## 📈 Rapport d’entraînement

- **Modèle de base** (220 M paramètres) finement ajusté — batch_size=64.  
- **Toucan-1.2B + PEFT (LoRA)** — entraînement d’adaptateurs légers, batch_size=128.  
- Visualisation des courbes de perte, BLEU scores et consommation GPU sur Weights & Biases.  
  👉 [Voir le rapport complet](https://api.wandb.ai/links/jiants-research/g799trkt)

---

## 🛠️ Installation & Usage

1. **Cloner le dépôt**  
   ```bash
   git clone https://github.com/jiants-research/nihil.git
   cd nihil
