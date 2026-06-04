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
    DUCKDB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "accidents.duckdb"
    )
    ZIP_PATH = None

GITHUB_RELEASE_URL = (
    "https://github.com/merwan-crypto/baac-analytics/"
    "releases/download/v1.0-data/accidents.duckdb.zip"
)


def ensure_db():
    if not _IS_CLOUD:
        return  # En local le fichier existe déjà

    # Base déjà présente et valide ?
    if os.path.exists(DUCKDB_PATH) and os.path.getsize(DUCKDB_PATH) > 1024 * 1024:
        return
    if os.path.exists(DUCKDB_PATH):
        os.remove(DUCKDB_PATH)

    placeholder = st.empty()
    placeholder.info("⏳ Chargement de la base de données (~145 Mo, première visite uniquement)...")

    try:
        # Téléchargement
        response = requests.get(GITHUB_RELEASE_URL, stream=True, timeout=600)
        response.raise_for_status()
        with open(ZIP_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
                f.write(chunk)

        # Extraction : on récupère le membre .duckdb quel que soit son chemin dans le zip
        with zipfile.ZipFile(ZIP_PATH, "r") as z:
            duckdb_member = next(
                (n for n in z.namelist() if n.endswith("accidents.duckdb")),
                None,
            )
            if duckdb_member is None:
                raise FileNotFoundError(
                    f"Aucun 'accidents.duckdb' dans le zip. Contenu : {z.namelist()}"
                )
            # Extrait puis place le fichier exactement à DUCKDB_PATH
            with z.open(duckdb_member) as src, open(DUCKDB_PATH, "wb") as dst:
                dst.write(src.read())

        os.remove(ZIP_PATH)
        placeholder.empty()

    except Exception as e:
        placeholder.error(f"❌ Échec du chargement de la base : {type(e).__name__} — {e}")
        raise