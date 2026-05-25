import os
import requests
import streamlit as st

DUCKDB_PATH = "/tmp/accidents.duckdb"

GITHUB_RELEASE_URL = (
    "https://github.com/merwan-crypto/baac-analytics/"
    "releases/download/v1.0-data/accidents.duckdb"
)

def ensure_db():
    st.write(f"🔍 DB_PATH = `{DUCKDB_PATH}`")
    st.write(f"📁 Fichier existe : `{os.path.exists(DUCKDB_PATH)}`")
    
    if os.path.exists(DUCKDB_PATH):
        size = os.path.getsize(DUCKDB_PATH)
        st.write(f"📦 Taille fichier : `{size // (1024*1024)} MB`")
        if size < 1024 * 1024:  # moins de 1MB = corrompu
            st.write("⚠️ Fichier trop petit, suppression et re-téléchargement...")
            os.remove(DUCKDB_PATH)
        else:
            st.write("✅ Fichier OK")
            return

    st.write(f"⬇️ Téléchargement depuis : `{GITHUB_RELEASE_URL}`")
    
    try:
        response = requests.get(GITHUB_RELEASE_URL, stream=True, timeout=300)
        st.write(f"📡 Status HTTP : `{response.status_code}`")
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        st.write(f"📏 Taille annoncée : `{total // (1024*1024)} MB`")

        downloaded = 0
        progress = st.progress(0, text="Téléchargement en cours...")

        with open(DUCKDB_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total
                    progress.progress(pct, text=f"{downloaded // (1024*1024)} MB / {total // (1024*1024)} MB")

        progress.empty()
        final_size = os.path.getsize(DUCKDB_PATH)
        st.write(f"✅ Téléchargement terminé : `{final_size // (1024*1024)} MB`")

    except Exception as e:
        st.error(f"❌ Erreur téléchargement : {e}")
        raise