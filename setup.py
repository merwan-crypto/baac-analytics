from src.models.database import Database
from src.models.session import Session

import json 

db = Database()
db.setup()

# Initialiser une session administrateur par défaut
s = Session("admin@datarockstars.ai", "admin")
s.signin()

# Réinitialiser la session fichier
data = {
    "email": ""
}

with open("session.json", 'w') as outfile:
    json.dump(data, outfile)