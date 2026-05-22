"""
setup.py — Initialisation de la base utilisateurs et de la session.

⚠️  Sécurité : ce script ne crée plus de compte admin par défaut.
    Le compte admin est créé automatiquement par Database.setup()
    avec le mot de passe "admin" haché en bcrypt.
    Changez ce mot de passe immédiatement après le premier lancement
    en production.
"""

import json
import os

from src.models.database import Database
from src.config.constants import SESSION_PATH

os.makedirs("data", exist_ok=True)

# Initialise la structure de la base SQLite (tables + compte admin bcrypt)
db = Database()
db.setup()
db.close()

# Réinitialise le fichier de session (aucun utilisateur connecté au démarrage)
os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
with open(SESSION_PATH, "w", encoding="utf-8") as outfile:
    json.dump({"email": ""}, outfile)

print("✅ Base utilisateurs initialisée.")
print("⚠️  Pensez à changer le mot de passe admin en production.")