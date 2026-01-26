import json

import streamlit as st

from src.views import home, dataset, analysis, conclusion, login, logout
from src.router import get_route, redirect
import utils as utl

st.set_page_config(layout="wide", page_title="Projet Fil Rouge")

utl.inject_custom_css()
utl.navbar_component()


def navigation():
    # Loading Cookies
    with open("session.json") as json_file:
        SESSION = json.load(json_file)

    # Non user in cookies
    if SESSION["email"] == "":
        redirect("login")

    route = get_route()

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
    elif route == "/logout":
        logout.load_view()
    elif route == "/login":
        login.load_view()
    else:
        home.load_view()

navigation()