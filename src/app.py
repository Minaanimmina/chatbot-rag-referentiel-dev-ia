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
    # await cl.Message(
    #     content=(
    #         "## Assistant RNCP Développeur IA\n\n"
    #         "Je suis là pour analyser la couverture de votre projet par rapport au référentiel RNCP Dev IA.\n\n"
    #         "Décrivez votre projet (technologies, tâches, outils) et je vous indique quelles compétences sont couvertes, partielles ou manquantes.\n\n"
    #         "💡 *Utilisez les suggestions ci-dessous pour démarrer rapidement.*"
    #     )
    # ).send()
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


@cl.set_starters
async def set_starters(users):
    return [
        cl.Starter(
            label="🔍 Analyse rapide",
            message="Mon projet utilise FastAPI et Docker.",
        ),

        cl.Starter(
            label="⚙️ Projet MLOps",
            message="Mon projet déploie une API FastAPI exposant un modèle LightGBM via Docker, avec un pipeline CI/CD GitHub Actions qui exécute des tests pytest automatiquement.",
        ),
        cl.Starter(
            label="🏆 Projet complet",
            message="Mon projet entraîne un modèle LightGBM sur des données d'accidents de la route, l'expose via une API FastAPI Dockerisée avec authentification. J'ai mis en place un monitoring avec Prometheus et Grafana, des tests automatisés pytest, un pipeline CI/CD GitHub Actions avec semantic release, et un dashboard Streamlit pour visualiser les prédictions.",
        ),
        cl.Starter(
            label="👩‍🏫 Vue formateur",
            message="Un apprenant m'a rendu un projet avec une API FastAPI Dockerisée et des tests pytest, mais sans CI/CD ni monitoring. Quelles compétences RNCP sont couvertes, lesquelles sont partielles, et que lui conseiller pour compléter son dossier avant la soutenance ?",
        )
    ]


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

    # Créer les éléments sources
    source_elements = []
    for i, doc in enumerate(docs):
        source_elements.append(
            cl.Text(
                name=f"Source {i+1}",
                content=doc.page_content,
                display="side"
            )
        )

    # Envoyer la réponse avec les sources
    await cl.Message(
        content=response.content,
        elements=source_elements
    ).send()
