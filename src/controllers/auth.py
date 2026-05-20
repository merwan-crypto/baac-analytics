import json
import os
import time

import streamlit as st

from src.models.session import Session
from src.config.constants import SESSION_PATH


# ---------------------------------------------------------------------------
# Protection anti-brute force — Rate limiting en mémoire
# ---------------------------------------------------------------------------
# On stocke dans st.session_state un compteur de tentatives échouées et
# un timestamp de dernier échec par e-mail.
#
# Seuils choisis :
#   MAX_ATTEMPTS  = 5  tentatives échouées avant blocage
#   LOCKOUT_TIME  = 60 secondes de blocage
#
# Limites de cette approche (à mentionner en soutenance) :
#   - Le compteur est en mémoire → réinitialisé si Streamlit redémarre.
#   - Pour la production, un rate limiting côté serveur (Redis, Nginx)
#     ou une solution comme streamlit-authenticator serait préférable.
# ---------------------------------------------------------------------------

MAX_ATTEMPTS = 5
LOCKOUT_TIME = 60  # secondes


def _get_attempts_key(email: str) -> str:
    return f"_login_attempts_{email}"


def _get_lockout_key(email: str) -> str:
    return f"_login_lockout_{email}"


def _is_locked_out(email: str) -> tuple[bool, int]:
    """
    Vérifie si l'e-mail est actuellement bloqué.
    Retourne (is_blocked, secondes_restantes).
    """
    lockout_key = _get_lockout_key(email)
    lockout_time = st.session_state.get(lockout_key, 0)

    if lockout_time == 0:
        return False, 0

    elapsed = int(time.time()) - lockout_time
    remaining = LOCKOUT_TIME - elapsed

    if remaining > 0:
        return True, remaining

    # Blocage expiré → réinitialisation
    st.session_state[lockout_key] = 0
    st.session_state[_get_attempts_key(email)] = 0
    return False, 0


def _record_failed_attempt(email: str) -> int:
    """
    Incrémente le compteur d'échecs.
    Déclenche le blocage si MAX_ATTEMPTS est atteint.
    Retourne le nombre de tentatives restantes.
    """
    attempts_key = _get_attempts_key(email)
    st.session_state[attempts_key] = st.session_state.get(attempts_key, 0) + 1
    attempts = st.session_state[attempts_key]

    if attempts >= MAX_ATTEMPTS:
        st.session_state[_get_lockout_key(email)] = int(time.time())

    return MAX_ATTEMPTS - attempts


def _reset_attempts(email: str) -> None:
    """Réinitialise le compteur après une connexion réussie."""
    st.session_state[_get_attempts_key(email)] = 0
    st.session_state[_get_lockout_key(email)] = 0


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

def save_session(email: str) -> None:
    """Persiste la session dans session.json via le chemin absolu."""
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump({"email": email}, f)


# ---------------------------------------------------------------------------
# Contrôleurs publics
# ---------------------------------------------------------------------------

def auth(email: str, mdp: str) -> dict:
    """
    Contrôleur d'authentification avec protection anti-brute force.

    Retourne :
      {"success": True,  "message": "..."}  si connexion réussie
      {"success": False, "message": "..."}  si échec ou blocage
    """
    # Vérification du blocage avant toute tentative
    locked, remaining = _is_locked_out(email)
    if locked:
        return {
            "success": False,
            "message": (
                f"Trop de tentatives échouées. "
                f"Réessayez dans {remaining} seconde(s)."
            )
        }

    s = Session(email, mdp)
    s.login()

    if s.logged:
        _reset_attempts(email)
        save_session(email)
        return {"success": True, "message": "Connexion réussie"}
    else:
        remaining_attempts = _record_failed_attempt(email)
        locked_now, _ = _is_locked_out(email)

        if locked_now:
            return {
                "success": False,
                "message": (
                    f"Identifiants incorrects. Compte temporairement bloqué "
                    f"après {MAX_ATTEMPTS} tentatives. "
                    f"Réessayez dans {LOCKOUT_TIME} secondes."
                )
            }

        attempts_done = st.session_state.get(_get_attempts_key(email), 0)
        return {
            "success": False,
            "message": (
                f"Identifiants incorrects "
                f"({attempts_done}/{MAX_ATTEMPTS} tentatives)."
            )
        }


def logout() -> dict:
    """Déconnecte l'utilisateur en vidant session.json."""
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump({"email": ""}, f)

    return {"success": True, "message": "Déconnexion réussie"}