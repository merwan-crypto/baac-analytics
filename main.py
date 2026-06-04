import json
import os
import streamlit as st

st.set_page_config(layout="wide", page_title="Projet Fil Rouge")

from src.views import home, dataset, analysis, conclusion, login, logout, profile
from src.router import get_route
from PATHS import NAVBAR_PATHS, SETTINGS
import utils as utl

utl.inject_custom_css()


def render_navbar():
    items = "".join(
        f'<li><a class="navitem" href="/?nav=%2F{v}">{k}</a></li>'
        for k, v in NAVBAR_PATHS.items()
    )
    settings = "".join(
        f'<a class="settingsNav" href="/?nav={v}">{k}</a>'
        for k, v in SETTINGS.items()
    )
    navbar_html = f"""
    <style>
      .dropdown:hover .dropdown-content {{
          opacity: 1 !important;
          pointer-events: auto !important;
          transform: none !important;
      }}
    </style>
    <div class="navbar-wrap" id="navbar-wrap-root">
      <nav class="navbar">
        <div class="nav-container">
          <div class="brand">
            <a href="/?nav=%2Fhome" class="brand-link">🚗 Accidents FR</a>
          </div>
          <ul class="navlist">{items}</ul>
          <div class="nav-actions">
            <div class="dropdown">
              <div class="dropbtn">⚙</div>
              <div class="dropdown-content">{settings}</div>
            </div>
          </div>
        </div>
      </nav>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)


render_navbar()


def load_session() -> dict:
    existing_email = st.session_state.get("user_email", "")
    if existing_email:
        return {"email": existing_email}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    session_path = os.path.join(base_dir, "data", "session.json")
    if not os.path.exists(session_path):
        return {"email": ""}
    try:
        with open(session_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            email = data.get("email", "")
            if email and isinstance(email, str) and "@" in email:
                return {"email": email}
            return {"email": ""}
    except (json.JSONDecodeError, OSError):
        return {"email": ""}


def navigation():
    session_data = load_session()
    email = session_data.get("email", "")

    if email and not st.session_state.get("user_email"):
        st.session_state["user_email"] = email
    elif st.session_state.get("user_email") and not email:
        email = st.session_state["user_email"]

    route = get_route()

    if not email:
        login.load_view()
        return

    if route == "/dataset":
        dataset.load_view()
    elif route == "/analysis":
        analysis.load_view()
    elif route == "/conclusion":
        conclusion.load_view()
    elif route == "/profile":
        profile.load_view()
    elif route == "/logout":
        logout.load_view()
    else:
        home.load_view()


navigation()