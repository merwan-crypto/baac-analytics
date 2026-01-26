import streamlit as st
from src.controllers.auth import logout
from src.router import redirect

def load_view():
    """
    Vue de déconnexion.
    Responsabilités :
    - Appeler le contrôleur de déconnexion
    - Rediriger vers la page de login
    """
    result = logout()  # Appel au contrôleur
    redirect("/login", reload=True)