from src.models.session import Session
import json 

def auth(login: str, mdp: str) -> dict:
    """
    Contrôleur d'authentification.
    Retourne un dictionnaire avec le résultat et le message.
    """
    s = Session(login, mdp)
    s.login()
    if s.logged:
        s.persist()
        return {"success": True, "message": "Connexion réussie"}
    else:
        return {"success": False, "message": "Identifiants incorrects"}

def logout():
    """
    Contrôleur de déconnexion.
    Efface la session et retourne un message.
    """
    data = {"email": ""}
    with open("session.json", 'w') as outfile:
        json.dump(data, outfile)
    return {"success": True, "message": "Déconnexion réussie"}