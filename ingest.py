"""
Script to ingest the RNCP referential markdown into ChromaDB.
Chunks by competency block (## Cx) instead of by character size,
preserving semantic coherence of each competency.
"""

from config import (
    DATA_PATH,
    CHROMA_PATH,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
)
import re
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


def load_and_chunk_by_competency(filepath: str) -> list[Document]:
    """
    Split the markdown file into chunks, one per competency block (## Cx / ## Bloc).
    Adds metadata: competency code, block title.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split on ## headers (competency blocks)
    sections = re.split(r"\n(?=## )", content)

    documents = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract competency code from header (e.g. "C9", "C18", "BLOC 1")
        header_match = re.match(r"## (.+)", section)
        title = header_match.group(1).strip() if header_match else "Unknown"

        # Extract Cx/Ax/Ex code if present
        code_match = re.match(r"## (C\d+|A\d+|E\d+|BLOC \d+)", section)
        code = code_match.group(1) if code_match else "misc"

        doc = Document(
            page_content=section,
            metadata={
                "source": filepath,
                "competency_code": code,
                "title": title,
            }
        )
        documents.append(doc)

    return documents


documents = load_and_chunk_by_competency(DATA_PATH)

print(f"{len(documents)} chunks créés (un par compétence)")
for doc in documents:
    print(f"  - [{doc.metadata['competency_code']}] {doc.metadata['title'][:60]}")

embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=OLLAMA_BASE_URL
)

vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory=CHROMA_PATH
)

print("Référentiel ingéré dans ChromaDB par compétence")