"""
Script to ingest the RNCP referential markdown into ChromaDB.
Chunks by competency block (## Cx) instead of by character size,
preserving semantic coherence of each competency.
"""

import re
import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from config import (
    CHROMA_PATH,
    DATA_PATH,
    EMBEDDING_MODEL,
)


def load_and_chunk_by_competency(filepath: str) -> list[Document]:
    """
    Split the markdown file into chunks, one per competency block (## Cx / ## Bloc).
    Adds metadata: competency code, block title.
    Raises FileNotFoundError if the file does not exist.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Referential file not found: {filepath}")

    with open(path, encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"\n(?=## )", content)

    documents = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        header_match = re.match(r"## (.+)", section)
        title = header_match.group(1).strip() if header_match else "Unknown"

        code_match = re.match(r"## (C\d+|A\d+|E\d+|BLOC \d+)", section)
        code = code_match.group(1) if code_match else "misc"

        doc = Document(
            page_content=section,
            metadata={
                "source": filepath,
                "competency_code": code,
                "title": title,
            },
        )
        documents.append(doc)

    return documents


def ingest(data_path: str, chroma_path: str) -> None:
    """
    Load, chunk and embed the referential into ChromaDB.
    Raises RuntimeError if Ollama is unreachable.
    """
    documents = load_and_chunk_by_competency(data_path)
    print(f"{len(documents)} chunks créés (un par compétence)")
    for doc in documents:
        print(f"  - [{doc.metadata['competency_code']}] {doc.metadata['title'][:60]}")

    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        Chroma.from_documents(
            documents=documents, embedding=embeddings, persist_directory=chroma_path
        )
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'ingestion dans ChromaDB : {e}") from e

    print("Référentiel ingéré dans ChromaDB par compétence")


if __name__ == "__main__":
    try:
        ingest(DATA_PATH, CHROMA_PATH)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)
