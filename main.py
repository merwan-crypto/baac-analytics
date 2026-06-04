import json
import os
import streamlit as st

st.set_page_config(layout="wide", page_title="Projet Fil Rouge")

from src.views import home, dataset, analysis, conclusion, login, logout, profile
from src.router import get_route

st.info("DIAGNOSTIC actif")

base_dir = os.path.dirname(os.path.abspath(__file__))
session_path = os.path.join(base_dir, "data", "session.json")

st.write("session.json existe sur le serveur ?", os.path.exists(session_path))
if os.path.exists(session_path):
    with open(session_path, encoding="utf-8") as f:
        st.write("contenu de session.json :", f.read())

st.write("user_email en session :", st.session_state.get("user_email", "(vide)"))
st.write("route nav :", get_route())

st.markdown("---")
st.write("Appel direct de login.load_view() :")
try:
    login.load_view()
    st.success("login.load_view() s'est execute sans erreur.")
except Exception as e:
    st.exception(e)