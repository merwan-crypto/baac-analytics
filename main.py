import json
import os
import streamlit as st

st.set_page_config(layout="wide", page_title="Projet Fil Rouge")

from src.config.db_loader import ensure_db
ensure_db()

import streamlit as st
st.cache_resource.clear()

from src.views import home, dataset, analysis, conclusion, login, logout, profile
from src.router import get_route
from src.config.constants import SESSION_PATH
import utils as utl

utl.inject_custom_css()
utl.navbar_component()


def load_session() -> dict:
    """
    Charge la session utilisateur avec une logique de double fallback robuste
    pour garantir la persistance sur mobile.

    Priorité :
      1. st.session_state["user_email"] — déjà en mémoire, survit aux reruns
         normaux sans coupure WebSocket.
      2. session.json (chemin absolu) — survit aux reconnexions WebSocket
         (réseau mobile instable, mise en veille du navigateur).
      3. Retourne {"email": ""} si les deux échouent → redirection login.
    """

    # --- Priorité 1 : session_state déjà initialisé ---
    # Sur mobile le WebSocket peut se couper et vider session_state,
    # mais si la valeur est encore présente on l'utilise directement.
    existing_email = st.session_state.get("user_email", "")
    if existing_email:
        return {"email": existing_email}

    # --- Priorité 2 : lecture du fichier session.json ---
    # On utilise un chemin ABSOLU basé sur l'emplacement de main.py
    # pour éviter les problèmes de répertoire de travail selon l'environnement.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    session_path = os.path.join(base_dir, "data", "session.json")

    if not os.path.exists(session_path):
        return {"email": ""}

    try:
        with open(session_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            email = data.get("email", "")
            # On ignore une entrée vide ou invalide
            if email and isinstance(email, str) and "@" in email:
                return {"email": email}
            return {"email": ""}
    except (json.JSONDecodeError, OSError):
        # Fichier corrompu ou inaccessible → on ne déconnecte pas l'utilisateur
        # brutalement, on retourne vide pour forcer le login proprement.
        return {"email": ""}


def navigation():
    session_data = load_session()
    email = session_data.get("email", "")

    # Synchronisation session_state <-> fichier JSON
    # On ne réécrit le state que si nécessaire pour éviter les reruns inutiles.
    if email and not st.session_state.get("user_email"):
        st.session_state["user_email"] = email
    elif st.session_state.get("user_email") and not email:
        # Le state dit qu'on est connecté mais le fichier est vide :
        # on fait confiance au state (coupure WebSocket temporaire).
        email = st.session_state["user_email"]

    route = get_route()

    # Si non connecté → page login uniquement
    if not email:
        login.load_view()
        return

    # Routing stable
    if route == "/dataset":
        dataset.load_view()
    elif route == "/analysis":
        analysis.load_view()
    elif route == "/conclusion":
        conclusion.load_view()
    elif route == "/profile":
        profile.load_view()
    elif route == "/logout":
        logout.load_view()
    else:
        home.load_view()


navigation()