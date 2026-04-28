"""
RAG prompt templates for RNCP competency analysis.

Provides the system message and message builder for analyzing projects
against the RNCP AI Developer referential.
"""

from langchain_core.messages import SystemMessage, HumanMessage


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
    Réponds toujours en français, quelle que soit la langue du contexte fourni.
    """)


def build_human_message(context: str, question: str) -> HumanMessage:
    return HumanMessage(
        content=f"""Contexte extrait du référentiel : {context}

        Description du projet à analyser : {question}
        """
        )
