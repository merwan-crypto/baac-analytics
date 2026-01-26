import streamlit as st

def load_view():
    """Vue de la page d'accueil du projet

    Objectifs :
    - Présenter rapidement le projet et sa structure.
    - Donner des actions claires (explorer les données, analyses, objectifs).
    - Indiquer les bonnes pratiques et commandes pour démarrer.
    """

    st.set_page_config(page_title="Accueil", layout="wide")

    st.title("Accueil — Projet d'analyse de données")

    st.markdown(
        """
        Bienvenue sur votre projet d'analyse de données / Data Science. Cette page d'accueil est conçue pour :

        - Accueillir le visiteur de votre projet.
        - Expliquer l'objectif, les ambitions du projet et la raison pour laquelle vous le menez.
        - Eventuellement vous présenter brièvement.
        - Ce que vous jugerez bon de documenter pour introduire le projet.
        """
    )