import os
import requests

DUCKDB_PATH = "/tmp/accidents.duckdb"

GITHUB_RELEASE_URL = (
    "https://github.com/merwan-crypto/baac-analytics/"
    "releases/download/v1.0-data/accidents.duckdb"
)

def ensure_db():
    if os.path.exists(DUCKDB_PATH):
        if os.path.getsize(DUCKDB_PATH) > 1024 * 1024:
            return
        os.remove(DUCKDB_PATH)

    response = requests.get(GITHUB_RELEASE_URL, stream=True, timeout=300)
    response.raise_for_status()

    with open(DUCKDB_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
            f.write(chunk)