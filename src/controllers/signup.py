from src.models.session import Session

def signup(login, mdp):
    """
    Contrôleur d'inscription.
    Retourne un dictionnaire avec le résultat et le message.
    """
    s = Session(login, mdp)
    
    created = s.signin()
    if not created:
        return {"success": False, "message": "E-mail déjà utilisé. Veuillez vous connecter."}
    
    s.login()
    if s.logged:
        s.persist()
        return {"success": True, "message": "Compte créé et connecté avec succès"}
    else:
        return {"success": False, "message": "Impossible de se connecter après l'inscription"}