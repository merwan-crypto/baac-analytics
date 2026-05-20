from src.models.database import Database
from src.models.session import Session
from src.config.constants import SESSION_PATH

import json
import os

os.makedirs("data", exist_ok=True)

db = Database()
db.setup()

s = Session("admin@datarockstars.ai", "admin")
s.signin()

data = {
    "email": ""
}

with open(SESSION_PATH, "w", encoding="utf-8") as outfile:
    json.dump(data, outfile)