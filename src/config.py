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

EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_PATH: str = str(BASE_DIR / "chromadb_vector_database")
DATA_PATH: str = str(BASE_DIR / "data" / "referentiel.md")
LLM_MODEL: str = "llama-3.1-8b-instant"
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
K_CHUNKS: int = 10
MAX_HISTORY: int = 20
