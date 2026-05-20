import os
import json
import streamlit as st
from src.config.constants import SESSION_PATH


def load_view():
    if os.path.exists(SESSION_PATH):
        with open(SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump({"email": ""}, f)

    st.session_state.clear()
    st.query_params["nav"] = "/login"
    st.rerun()