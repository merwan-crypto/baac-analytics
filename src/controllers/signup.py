import json
import os

from src.models.session import Session
from src.config.constants import SESSION_PATH


def save_session(email: str) -> None:
    """Persiste la session dans session.json via le chemin absolu."""
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump({"email": email}, f)


def signup(email: str, mdp: str) -> dict:
    """
    Contrôleur d'inscription.

    Crée le compte avec un hash bcrypt (via Session.signin()),
    puis connecte automatiquement l'utilisateur.

    Retourne :
      {"success": True,  "message": "..."}  si compte créé et connecté
      {"success": False, "message": "..."}  si e-mail déjà utilisé
    """
    s = Session(email, mdp)

    created = s.signin()
    if not created:
        return {
            "success": False,
            "message": "E-mail déjà utilisé. Veuillez vous connecter."
        }

    # Connexion immédiate après inscription
    s.login()
    if s.logged:
        save_session(email)
        return {
            "success": True,
            "message": "Compte créé et connecté avec succès."
        }
    else:
        return {
            "success": False,
            "message": "Compte créé, mais impossible de se connecter. Veuillez vous connecter manuellement."
        }