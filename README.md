# NIHIL — Le Retour des Langues

[![W&B Training Report](https://api.wandb.ai/links/jiants-research/g799trkt)](https://api.wandb.ai/links/jiants-research/g799trkt)

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
