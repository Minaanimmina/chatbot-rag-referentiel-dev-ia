"""
Chainlit application for RNCP competency analysis.

Loads ChromaDB vector store and Ollama LLM to process
user project descriptions.
Retrieves relevant referential documents and generates competency analysis.
"""

import chainlit as cl
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from rag import system_message, build_human_message
from config import (
    CHROMA_PATH,
    EMBEDDING_MODEL,
    LLM_MODEL,
    K_CHUNKS,
    OLLAMA_BASE_URL
)


@cl.on_chat_start
async def on_chat_start():
    # Recharge la base de données ChromaDB
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
        )
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )
    # Crée le retriever pour récupérer les K_CHUNKS les plus pertinents
    retriever = vectorstore.as_retriever(search_kwargs={"k": K_CHUNKS})
    # Charge le LLM
    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    cl.user_session.set("retriever", retriever)
    cl.user_session.set("llm", llm)


@cl.on_message
async def on_message(message: cl.Message):
    retriever = cl.user_session.get("retriever")
    llm = cl.user_session.get("llm")
    if not retriever or not llm:
        await cl.Message(content="Erreur : session non initialisée.").send()
        return
    # Récupère les K_CHUNKS les plus pertinents
    docs = retriever.invoke(message.content)
    # Construit la réponse en utilisant le LLM
    docs_text = "\n\n".join([doc.page_content for doc in docs])
    human_message = build_human_message(docs_text, message.content)
    try: 
        response = llm.invoke([system_message, human_message])
    except Exception as e:
        await cl.Message(content=f"Erreur lors de l'appel au LLM : {str(e)}").send()
        return
    await cl.Message(content=response.content).send()
