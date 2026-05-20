import os
import streamlit as st
from src.models.nosql_db import set_last_page

_VIEW_DIR    = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR     = os.path.dirname(_VIEW_DIR)
_PROJECT_DIR = os.path.dirname(_SRC_DIR)
_DOCS_PDF    = os.path.join(_PROJECT_DIR, "docs", "Description des bases de données annuelles.pdf")


def load_view():
    email = st.session_state.get("user_email", "guest")
    set_last_page(email, "home")

    st.title("Accueil — Projet d'analyse de données")

    st.markdown("""
        Bienvenue sur votre projet d'analyse de données / Data Science.

        Cette application a pour objectif d'explorer et analyser les accidents corporels de la circulation en France,
        à partir des données officielles issues du fichier BAAC (Bulletin d'Analyse des Accidents Corporels).
    """)

    st.markdown("---")
    st.subheader("🎯 Objectifs du projet")
    st.markdown("""
        - Comprendre les facteurs influençant les accidents routiers  
        - Identifier des tendances (temps, lieu, type d'usagers, etc.)  
        - Proposer des visualisations claires et exploitables  
        - Faciliter l'interprétation des données pour la prise de décision  
    """)

    st.markdown("---")
    st.subheader("📊 Source des données")
    st.markdown("""
        Les données utilisées proviennent du fichier national des accidents corporels (BAAC),
        administré par l'Observatoire national interministériel de la sécurité routière (ONISR).

        Chaque accident recensé :
        - implique au moins un véhicule
        - a lieu sur une voie ouverte à la circulation
        - comporte au moins une victime nécessitant des soins

        Les données sont structurées en 4 tables principales :
        - **Caractéristiques** (conditions de l'accident)
        - **Lieux** (environnement et infrastructure)
        - **Véhicules** (types et comportements)
        - **Usagers** (profil des personnes impliquées)
    """)

    st.markdown("---")
    st.subheader("🧭 Navigation dans l'application")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📁 Jeu de données\n\nExploration brute des données")
    with col2:
        st.info("📈 Analyse\n\nVisualisations et insights")
    with col3:
        st.info("🧠 Conclusion\n\nRésumé et interprétation")

    st.markdown("---")
    st.subheader("📄 Documentation")

    if os.path.exists(_DOCS_PDF):
        with open(_DOCS_PDF, "rb") as file:
            st.download_button(
                label="📥 Télécharger la documentation officielle",
                data=file,
                file_name="description_baac.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Documentation PDF introuvable. Vérifiez que le dossier docs/ est présent à la racine du projet.")

    st.markdown("---")
    st.subheader("🚀 À propos de ce projet")
    st.markdown("""
        Ce projet s'inscrit dans une démarche de Data Analysis visant à :
        - manipuler des données réelles
        - appliquer des techniques d'analyse exploratoire (EDA)
        - produire des visualisations pertinentes
        - construire une application interactive avec Streamlit
    """)