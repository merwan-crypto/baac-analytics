import streamlit as st
from urllib.parse import unquote


def get_route():
    url = st.query_params.get("nav")
    url = url[0] if isinstance(url, list) else url
    return unquote(url) if url else None


def redirect(new_route, reload=False):
    if not new_route.startswith("/"):
        new_route = "/" + new_route

    st.query_params["nav"] = new_route

    if reload:
        st.rerun()