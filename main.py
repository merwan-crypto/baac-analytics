import json
import os
import streamlit as st

from src.views import home, dataset, analysis, conclusion, login, logout, profile
from src.router import get_route, redirect
import utils as utl

st.set_page_config(layout="wide", page_title="Projet Fil Rouge")

# utl.inject_custom_css()
# utl.navbar_component()
import streamlit as _st_diag
_st_diag.info("DIAGNOSTIC : si tu vois ce message, le rendu Streamlit fonctionne.")

def load_session():
    if not os.path.exists("session.json"):
        with open("session.json", "w", encoding="utf-8") as outfile:
            json.dump({"email": ""}, outfile)

    with open("session.json", "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def navigation():
    SESSION = load_session()
    route = get_route()

    if SESSION.get("email", "") == "" and route != "/login":
        redirect("login")
        return

    if route == "/home":
        home.load_view()
    elif route == "/goal":
        dataset.load_view()
    elif route == "/dataset":
        dataset.load_view()
    elif route == "/analysis":
        analysis.load_view()
    elif route == "/conclusion":
        conclusion.load_view()
    elif route == "/profile":
        profile.load_view()
    elif route == "/logout":
        logout.load_view()
    elif route == "/login":
        login.load_view()
    else:
        home.load_view()


navigation()
