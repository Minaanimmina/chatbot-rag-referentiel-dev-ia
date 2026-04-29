import os
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "nomic-embed-text"
CHROMA_PATH = "chromadb_vector_database"
PDF_PATH = "data/Referentiel.pdf"
DATA_PATH = "data/referentiel.md"
LLM_MODEL = "qwen2.5:14b"
K_CHUNKS = 10
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
