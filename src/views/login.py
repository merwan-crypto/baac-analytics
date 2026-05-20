import json
import os
import streamlit as st

from src.controllers.auth import auth
from src.controllers.signup import signup
from src.models.nosql_db import get_last_page
from src.config.constants import SESSION_PATH

# Politique de mot de passe — 8 caractères minimum (standard ANSSI / OWASP)
PASSWORD_MIN_LENGTH = 8


def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email and len(email) >= 5


def save_session(email: str) -> None:
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump({"email": email}, f)


def _set_session(email: str) -> None:
    save_session(email)
    st.session_state["user_email"] = email
    st.session_state["_session_just_set"] = True


def load_view() -> None:
    st.title("Connexion / Inscription")

    email    = st.text_input("E-mail", "")
    password = st.text_input("Mot de passe", "", type="password")

    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        log_in_button = st.button("Se connecter")
    with col2:
        sign_up_button = st.button("S'inscrire")

    if log_in_button:
        if not email or not password:
            st.error("Veuillez remplir l'e-mail et le mot de passe.")
        elif not is_valid_email(email):
            st.error("Veuillez saisir un e-mail valide.")
        else:
            result = auth(email, password)
            if result["success"]:
                _set_session(email)
                last_page = get_last_page(email)
                if not last_page or last_page in ("login", "/login"):
                    last_page = "home"
                st.success(result["message"])
                st.query_params["nav"] = "/" + last_page.lstrip("/")
                st.rerun()
            else:
                st.error(result["message"])

    elif sign_up_button:
        if not email or not password:
            st.error("Veuillez remplir l'e-mail et le mot de passe.")
        elif not is_valid_email(email):
            st.error("Veuillez saisir un e-mail valide.")
        elif len(password) < PASSWORD_MIN_LENGTH:
            st.error(
                f"Le mot de passe doit contenir au moins {PASSWORD_MIN_LENGTH} caractères. "
                f"(Standard de sécurité ANSSI / OWASP)"
            )
        else:
            result = signup(email, password)
            if result["success"]:
                _set_session(email)
                st.success(result["message"])
                st.query_params["nav"] = "/home"
                st.rerun()
            else:
                st.error(result["message"])