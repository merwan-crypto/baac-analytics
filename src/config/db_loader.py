import os
import shutil
import zipfile
import requests
import streamlit as st

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

_MIN_DB_SIZE = 50 * 1024 * 1024


def ensure_db():
    if not _IS_CLOUD:
        return

    if os.path.exists(DUCKDB_PATH) and os.path.getsize(DUCKDB_PATH) > _MIN_DB_SIZE:
        return
    if os.path.exists(DUCKDB_PATH):
        os.remove(DUCKDB_PATH)

    placeholder = st.empty()
    placeholder.info("Chargement de la base de donnees (~145 Mo, premiere requete uniquement)...")

    tmp_extract = DUCKDB_PATH + ".part"
    try:
        with requests.get(GITHUB_RELEASE_URL, stream=True, timeout=600) as response:
            response.raise_for_status()
            with open(ZIP_PATH, "wb") as f:
                for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
                    if chunk:
                        f.write(chunk)

        with zipfile.ZipFile(ZIP_PATH, "r") as z:
            member = next((n for n in z.namelist() if n.endswith("accidents.duckdb")), None)
            if member is None:
                raise FileNotFoundError("Pas de accidents.duckdb dans le zip")
            with z.open(member) as src, open(tmp_extract, "wb") as dst:
                shutil.copyfileobj(src, dst, length=8 * 1024 * 1024)

        os.replace(tmp_extract, DUCKDB_PATH)
        os.remove(ZIP_PATH)
        placeholder.empty()

    except Exception as e:
        for p in (tmp_extract, ZIP_PATH):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
        placeholder.error(f"Echec du chargement de la base : {type(e).__name__} - {e}")
        raise