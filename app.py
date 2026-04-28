"""
Chainlit application for RNCP competency analysis.
"""

import chainlit as cl
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, BaseMessage
from prompts import system_message, build_human_message
from config import (
    CHROMA_PATH,
    EMBEDDING_MODEL,
    LLM_MODEL,
    K_CHUNKS,
    OLLAMA_BASE_URL
)


@cl.on_chat_start
async def on_chat_start():
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": K_CHUNKS})
    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    cl.user_session.set("retriever", retriever)
    cl.user_session.set("llm", llm)
    cl.user_session.set("history", [])  # initialiser l'historique ici


@cl.on_message
async def on_message(message: cl.Message):
    retriever = cl.user_session.get("retriever")
    llm = cl.user_session.get("llm")
    if not retriever or not llm:
        await cl.Message(content="Erreur : session non initialisée.").send()
        return

    history: list[BaseMessage] = cl.user_session.get("history") or []

    docs = retriever.invoke(message.content)
    docs_text = "\n\n".join([doc.page_content for doc in docs])
    human_message = build_human_message(docs_text, message.content)

    try:
        response = llm.invoke([system_message] + history + [human_message])
    except Exception as e:
        await cl.Message(content=f"Erreur LLM : {str(e)}").send()
        return

    history.append(human_message)
    history.append(AIMessage(content=response.content))
    cl.user_session.set("history", history)

    await cl.Message(content=response.content).send()
