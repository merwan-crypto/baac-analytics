import os
import requests
import streamlit as st
from src.config.constants import DUCKDB_PATH

GITHUB_RELEASE_URL = (
    "https://github.com/merwan-crypto/baac-analytics/"
    "releases/download/v1.0-data/accidents.duckdb"
)

def ensure_db():
    """Télécharge la base DuckDB depuis GitHub Releases si absente (Streamlit Cloud)."""
    if os.path.exists(DUCKDB_PATH):
        return

    os.makedirs(os.path.dirname(DUCKDB_PATH), exist_ok=True)

    with st.spinner("Chargement de la base de données... (première visite, ~30s)"):
        response = requests.get(GITHUB_RELEASE_URL, stream=True)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0
        progress = st.progress(0, text="Téléchargement en cours...")

        with open(DUCKDB_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total
                    progress.progress(pct, text=f"Téléchargement... {downloaded // (1024*1024)} MB / {total // (1024*1024)} MB")

        progress.empty()