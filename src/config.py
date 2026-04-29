"""
Configuration constants for the RNCP RAG chatbot application.
Loads environment variables and defines paths and model settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory for path resolution
BASE_DIR: Path = Path(__file__).parent.parent

EMBEDDING_MODEL: str = "nomic-embed-text"
CHROMA_PATH: str = str(BASE_DIR / "chromadb_vector_database")
DATA_PATH: str = str(BASE_DIR / "data" / "referentiel.md")
LLM_MODEL: str = "qwen2.5:14b"
K_CHUNKS: int = 10
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MAX_HISTORY: int = 20