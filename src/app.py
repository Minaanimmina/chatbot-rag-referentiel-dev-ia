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
    OLLAMA_BASE_URL,
    MAX_HISTORY,
)


@cl.on_chat_start
async def on_chat_start() -> None:
    """
    Initialise la session utilisateur : embeddings, vectorstore, LLM et historique.
    En cas d'échec (Ollama indisponible, ChromaDB corrompue), informe l'utilisateur
    avec un message générique et interrompt l'initialisation.
    """
    try:
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
    except Exception:
        await cl.Message(
            content="Le service IA n'est pas disponible. Veuillez réessayer dans quelques instants."
        ).send()
        return

    cl.user_session.set("retriever", retriever)
    cl.user_session.set("llm", llm)
    cl.user_session.set("history", [])


@cl.set_starters
async def set_starters(user: cl.User | None) -> list[cl.Starter]:
    """
    Définit les suggestions de démarrage affichées sur l'écran d'accueil.
    Couvre trois niveaux de description de projet (vague, moyen, complet)
    et un cas d'usage formateur.
    """
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
async def on_message(message: cl.Message) -> None:
    """
    Traite chaque message entrant : récupère les chunks pertinents via le retriever,
    construit le contexte avec l'historique, streame la réponse du LLM et affiche
    les sources en fin de réponse.
    """
    retriever = cl.user_session.get("retriever")
    llm = cl.user_session.get("llm")
    if not retriever or not llm:
        await cl.Message(
            content="La session n'est pas initialisée. Veuillez rafraîchir la page."
        ).send()
        return

    history: list[BaseMessage] = cl.user_session.get("history") or []

    try:
        docs = await retriever.ainvoke(message.content)
    except Exception:
        await cl.Message(
            content="Impossible d'accéder à la base de connaissances. Veuillez réessayer."
        ).send()
        return

    docs_text = "\n\n".join([doc.page_content for doc in docs])
    human_message = build_human_message(docs_text, message.content)

    # Créer le message vide immédiatement
    msg = cl.Message(content="")
    await msg.send()

    # Streamer les tokens au fur et à mesure
    full_response = ""
    try:
        async for chunk in llm.astream([system_message] + history + [human_message]):
            await msg.stream_token(chunk.content)
            full_response += chunk.content
    except Exception:
        msg.content = "Le service IA est temporairement indisponible. Veuillez réessayer."
        await msg.update()
        return

    # Ajouter les sources au message une fois le stream terminé
    msg.elements = [ # type: ignore[assignment]
    cl.Text(
        name=f"Source {i+1}",
        content=doc.page_content,
        display="side"
    )
    for i, doc in enumerate(docs)
    ]
    await msg.update()

    # Mettre à jour l'historique
    history.append(human_message)
    history.append(AIMessage(content=full_response))
    cl.user_session.set("history", history[-MAX_HISTORY:])
