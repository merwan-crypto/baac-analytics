import os
import zipfile
import requests
import streamlit as st

# En local on utilise le vrai fichier, sur le cloud on télécharge
_IS_CLOUD = os.path.exists("/mount/src")

if _IS_CLOUD:
    DUCKDB_PATH = "/tmp/accidents.duckdb"
    ZIP_PATH = "/tmp/accidents.duckdb.zip"
else:
    DUCKDB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "accidents.duckdb")
    ZIP_PATH = None

GITHUB_RELEASE_URL = (
    "https://github.com/merwan-crypto/baac-analytics/"
    "releases/download/v1.0-data/accidents.duckdb.zip"
)

def ensure_db():
    if not _IS_CLOUD:
        return  # En local le fichier existe déjà
    
    if os.path.exists(DUCKDB_PATH):
        if os.path.getsize(DUCKDB_PATH) > 1024 * 1024:
            return
        os.remove(DUCKDB_PATH)

    placeholder = st.empty()
    placeholder.info("⏳ Chargement de la base de données...")

    response = requests.get(GITHUB_RELEASE_URL, stream=True, timeout=300)
    response.raise_for_status()

    with open(ZIP_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
            f.write(chunk)

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extract("accidents.duckdb", "/tmp")

    os.remove(ZIP_PATH)
    placeholder.empty()