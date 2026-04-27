"""
Script to ingest the markdown file into a ChromaDB vector database. It uses
the TextSplitter from LangChain to split the text into chunks, and the Nomic
embedding model to create embeddings for each chunk. The embeddings are then
stored in a ChromaDB vector database for later retrieval.
"""

from config import (
    DATA_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_PATH,
    EMBEDDING_MODEL,
)
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

loader = TextLoader(DATA_PATH, encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP)
texts = text_splitter.split_documents(documents)

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

vectorstore = Chroma.from_documents(
    documents=texts,
    embedding=embeddings,
    persist_directory=CHROMA_PATH
)

print("✅ Data successfully stored in ChromaDB!")
