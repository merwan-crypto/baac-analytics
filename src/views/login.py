import streamlit as st
from src.controllers.auth import auth
from src.controllers.signup import signup
from src.router import redirect

def load_view():
    """
    Vue d'authentification.
    Responsabilités :
    - Afficher le formulaire (UI)
    - Appeler les contrôleurs (pas de logique métier ici)
    - Afficher les messages retournés par les contrôleurs
    - Rediriger si succès
    """
    st.title('Connexion / Inscription')

    # Formulaire (partie UI)
    email = st.text_input('E-mail', '')
    password = st.text_input('Mot de passe', '', type='password')
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        log_in_button = st.button('Se connecter')
    with col2:
        sign_up_button = st.button("S'inscrire")

    # Gestion des événements utilisateur
    # La vue appelle le contrôleur et utilise le résultat retourné
    if log_in_button:
        result = auth(email, password)  # Appel au contrôleur
        st.text(result["message"])      # Affichage du message du contrôleur
        if result["success"]:           # Redirection si succès
            redirect("home", reload=True)
    
    elif sign_up_button:
        result = signup(email, password)  # Appel au contrôleur
        st.text(result["message"])        # Affichage du message du contrôleur
        if result["success"]:             # Redirection si succès
            redirect("home", reload=True)