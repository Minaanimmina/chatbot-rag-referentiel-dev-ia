---
title: Chatbot RAG RNCP Dev IA
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
short_description: RAG chatbot on RNCP Dev IA referential - Simplon
---

# Chatbot RAG — Référentiel RNCP Développeur en IA

![Python](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![Chainlit](https://img.shields.io/badge/Chainlit-2.x-green)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector%20db-purple)
![Docker](https://img.shields.io/badge/Docker-enabled-blue?logo=docker)
![Ollama](https://img.shields.io/badge/Ollama-local%20LLM-red)

## À propos

Chatbot RAG alimenté par le **référentiel RNCP certification 37827** *(Développeur en Intelligence Artificielle, niveau 6)*, permettant aux apprenants et formateurs **Simplon** d'analyser la couverture d'un projet par rapport aux compétences requises.

Cet outil exploite une architecture **Retrieval-Augmented Generation (RAG)** pour fournir des réponses précises et sourcées directement du référentiel officiel.

---

## Contexte et problème résolu

### Problématique

Les apprenants Simplon suivent une certification RNCP avec des dizaines de compétences à acquérir. Répondre à la question *"Mon projet couvre-t-il bien les compétences du référentiel ?"* demande aujourd'hui de relire manuellement un document de 40+ pages, de retrouver les critères d'évaluation par compétence, et de les comparer avec ce que le projet implémente réellement. C'est long, subjectif, et souvent fait à la dernière minute avant la soutenance.

### Solution

Ce chatbot RAG permet de :
- **Interroger le référentiel en langage naturel** : posez une question, obtenez une réponse précise et sourcée
- **Analyser la couverture d'un projet** : mappez vos réalisations aux compétences RNCP
- **Explorer les critères d'évaluation** : comprenez les attentes de chaque compétence
- **Identifier les compétences manquantes** : avant la soutenance

---

## Architecture RAG

### Pipeline (4 étapes)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE RAG (4 ÉTAPES)                      │
└─────────────────────────────────────────────────────────────────┘

1  LOAD (Chargement)
    │
    ├─ Fichier source : data/referentiel.md
    │  (référentiel RNCP structuré en Markdown)
    │
    └─→ Contenu brut

2  CHUNK (Fragmentation)
    │
    ├─ Découpage par compétence
    │  (une compétence = un chunk sémantique)
    │
    └─→ Chunks structurés avec métadonnées (code, titre)

3  EMBED (Vectorisation)
    │
    ├─ Modèle : nomic-embed-text (via Ollama)
    │
    └─→ Embeddings stockés dans ChromaDB

4  STORE/RETRIEVE (Stockage & Récupération)
    │
    ├─ Base vectorielle : ChromaDB (persistante)
    │
    ├─ Recherche : similarité cosinus
    │  (récupère les K chunks les plus similaires)
    │
    └─→ Chunks pertinents enrichissent le prompt LLM

    ⬇ ENRICHISSEMENT DU PROMPT

    ┌─────────────────────────────────┐
    │ LLM Ollama (qwen2.5:14b)        │
    │ + contexte du référentiel       │
    │ + historique de conversation    │
    └─────────────────────────────────┘

    ⬇ RÉPONSE STREAMÉE + SOURCES EN PANNEAU LATÉRAL
```

### Flux de conversation

```
Utilisateur
    ↓
Chainlit UI
    ↓
Vectorisation de la requête (nomic-embed-text)
    ↓
Recherche dans ChromaDB (top-K chunks)
    ↓
Construction du contexte RAG
    ↓
LLM Ollama + System Prompt
    ↓
Réponse streamée + Sources affichées
    ↓
Historique conservé par session (max 20 messages)
```

---

## Technologies utilisées

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **LLM** | Ollama + Qwen2.5 | 14B | Génération de réponses |
| **Embeddings** | Ollama + Nomic-Embed-Text | latest | Vectorisation texte |
| **Orchestration RAG** | LangChain | latest | Chaîne RAG complète |
| **Interface conversationnelle** | Chainlit | 2.x | UI interactive avec streaming |
| **Base vectorielle** | ChromaDB | latest | Stockage persistant des embeddings |
| **Runtime Python** | Python | 3.12 | Exécution |
| **Gestionnaire dépendances** | uv | latest | Installation rapide |
| **Conteneurisation** | Docker + Compose | latest | Déploiement isolé |

---

## Prérequis

### Pour les deux modes

- **Ollama** installé et en cours d'exécution ([ollama.ai](https://ollama.ai))
- Modèles téléchargés :
  ```bash
  ollama pull qwen2.5:14b
  ollama pull nomic-embed-text
  ```

### Mode local uniquement

- **Python** ≥ 3.12
- **uv** installé ([astral-sh/uv](https://github.com/astral-sh/uv))

### Mode Docker uniquement

- **Docker** ≥ 20.10 + **Docker Compose** ≥ 2.0
- Ollama doit tourner sur la machine hôte (le container communique via `host.docker.internal`)

---

## Installation et lancement

### Mode 1 : Local (développement)

```bash
# 1. Cloner le dépôt
git clone https://github.com/Minaanimmina/chatbot-rag-referentiel-dev-ia.git
cd chatbot-rag-referentiel-dev-ia

# 2. Installer les dépendances
uv sync

# 3. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env si nécessaire

# 4. Ingérer le référentiel dans ChromaDB (première exécution uniquement)
uv run python src/ingest.py

# 5. Lancer l'application
uv run chainlit run src/app.py --watch
```

L'application est accessible à `http://localhost:8000`

---

### Mode 2 : Docker

```bash
# 1. Cloner le dépôt
git clone https://github.com/Minaanimmina/chatbot-rag-referentiel-dev-ia.git
cd chatbot-rag-referentiel-dev-ia

# 2. Configurer les variables d'environnement
cp .env.example .env

# 3. Lancer le container
docker compose up --build
```

L'application est accessible à `http://localhost:8001`

> ⚠️ Ollama doit tourner sur la machine hôte. Le container communique avec lui via `host.docker.internal:11434`.

```bash
# Arrêter
docker compose down
```

---

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine (ou consultez `.env.example`) :

```env
OLLAMA_BASE_URL=http://localhost:11434
```

Toutes les autres constantes (modèles, chemins, paramètres RAG) sont configurées dans `src/config.py`.

---

## Exemples de questions

Le chatbot propose quatre scénarios de démarrage :

**🔍 Analyse rapide** — description minimale pour observer les limites :
> "Mon projet utilise FastAPI et Docker."

**⚙️ Projet MLOps** — description intermédiaire :
> "Mon projet déploie une API FastAPI exposant un modèle LightGBM via Docker, avec un pipeline CI/CD GitHub Actions qui exécute des tests pytest automatiquement."

**🏆 Projet complet** — description riche et détaillée :
> "Mon projet entraîne un modèle LightGBM sur des données d'accidents de la route, l'expose via une API FastAPI Dockerisée avec authentification. J'ai mis en place un monitoring avec Prometheus et Grafana, des tests automatisés pytest, un pipeline CI/CD GitHub Actions avec semantic release, et un dashboard Streamlit pour visualiser les prédictions."

**👩‍🏫 Vue formateur** :
> "Un apprenant m'a rendu un projet avec une API FastAPI Dockerisée et des tests pytest, mais sans CI/CD ni monitoring. Quelles compétences RNCP sont couvertes, lesquelles sont partielles, et que lui conseiller pour compléter son dossier avant la soutenance ?"

---

## Structure du projet

```
chatbot-rag-referentiel-dev-ia/
│
├── src/
│   ├── app.py                  # Application Chainlit principale
│   ├── config.py               # Configuration + chargement .env
│   ├── prompts.py              # Prompts système + construction messages
│   └── ingest.py               # Ingestion du référentiel dans ChromaDB
│
├── data/
│   └── referentiel.md          # Référentiel RNCP source (structuré par compétence)
│
├── public/
│   ├── custom.css              # Charte graphique Simplon
│   ├── theme.json              # Variables de thème Chainlit
│   └── img/                    # Assets (logos)
│
├── chromadb_vector_database/   # Base vectorielle persistante (ignorée par git)
│
├── docker-compose.yml          # Orchestration conteneurs
├── Dockerfile                  # Image application
├── entrypoint.sh               # Script de démarrage (ingestion + lancement)
├── pyproject.toml              # Dépendances Python (uv)
├── .env.example                # Template variables d'environnement
├── chainlit.md                 # Documentation accessible via "Lisez-moi"
└── .gitignore
```

---

## Limites connues

- Qualité des réponses dépend de la qualité du référentiel Markdown source
- Modèle Qwen2.5 14B : temps de réponse variable selon le matériel (16 GB RAM recommandés)
- Pas de persistance multi-session (par conception)
- Ollama doit être en cours d'exécution avant de lancer l'application

---

## Auteur

Réalisé par **Mina Guinchard**, en formation à Simplon Lyon (2025-2026)

- **Contexte** : Certification RNCP 37827 — Développeur en Intelligence Artificielle
- **GitHub** : [Minaanimmina](https://github.com/Minaanimmina)

---

## Ressources

- [Documentation Chainlit](https://docs.chainlit.io)
- [Documentation LangChain](https://python.langchain.com)
- [Documentation ChromaDB](https://docs.trychroma.com)
- [Documentation Ollama](https://ollama.ai)

---

**Dernière mise à jour** : Avril 2026