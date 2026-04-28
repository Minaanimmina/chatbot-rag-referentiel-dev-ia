"""
Script to
"""

import chainlit as cl
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from config import (
    CHROMA_PATH,
    EMBEDDING_MODEL,
    LLM_MODEL,
    K_CHUNKS
)


system_message = SystemMessage(
    content="""
    Tu es un expert pédagogique Simplon spécialisé dans le
    référentiel RNCP Développeur en Intelligence Artificielle.
    Ton rôle est d'analyser la description d'un projet et d'identifier
    les compétences RNCP qu'il couvre.

    Pour chaque compétence identifiée :
    - Indique son numéro (C7, C13, etc.)
    - Justifie pourquoi elle est couverte en citant un
    extrait du contexte fourni

    Liste également les compétences mentionnées dans le contexte mais
    NON couvertes par le projet.

    IMPORTANT : Base ton analyse uniquement sur le contexte fourni ci-dessous.
    Ne cite pas de compétences absentes du contexte.
    """)


def build_human_message(context: str, question: str) -> HumanMessage:
    return HumanMessage(
        content=f"""Contexte extrait du référentiel : {context}

        Description du projet à analyser : {question}
        """
        )


@cl.on_chat_start
async def on_chat_start():
    # Recharge la base de données ChromaDB
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )
    # Crée le retriever pour récupérer les K_CHUNKS les plus pertinents
    retriever = vectorstore.as_retriever(search_kwargs={"k": K_CHUNKS})
    # Charge le LLM
    llm = ChatOllama(
        model=LLM_MODEL
    )
    cl.user_session.set("retriever", retriever)
    cl.user_session.set("llm", llm)


@cl.on_message
async def on_message(message: cl.Message):
    retriever = cl.user_session.get("retriever")
    llm = cl.user_session.get("llm")
    # Récupère les K_CHUNKS les plus pertinents
    docs = retriever.invoke(message.content)
    # Construit la réponse en utilisant le LLM
    docs_text = "\n\n".join([doc.page_content for doc in docs])
    human_message = build_human_message(docs_text, message.content)
    response = llm.invoke([system_message, human_message])
    response = llm.invoke([system_message, human_message])
    await cl.Message(content=response.content).send()
