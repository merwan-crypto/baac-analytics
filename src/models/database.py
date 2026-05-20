import sqlite3
import os

import bcrypt


class Database:
    """
    Gestion de la base SQLite utilisateurs.

    Sécurité — migration SHA-256 → bcrypt
    ----------------------------------------
    Le compte admin par défaut est désormais créé avec un hash bcrypt.
    Le mot de passe par défaut reste "admin" mais est haché avec bcrypt
    (salt aléatoire, 12 rounds) au lieu de SHA-256.

    IMPORTANT : en production, changez immédiatement le mot de passe admin
    après le premier lancement, ou désactivez la création automatique.

    Chemin absolu
    -------------
    Le chemin vers users.db est calculé de manière absolue depuis
    l'emplacement de ce fichier pour éviter les problèmes de répertoire
    de travail selon l'environnement de déploiement.
    """

    BCRYPT_ROUNDS = 12

    def __init__(self) -> None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "..", "..", "data", "users.db")
        db_path = os.path.normpath(db_path)

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.__db = sqlite3.connect(db_path)
        self.setup()

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash un mot de passe avec bcrypt.
        Utilisé uniquement pour la création du compte admin par défaut.
        Pour les utilisateurs, le hachage est géré dans Session.hash().
        """
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=Database.BCRYPT_ROUNDS)
        ).decode("utf-8")

    def setup(self) -> None:
        """
        Crée les tables si elles n'existent pas et initialise le compte admin.

        Structure :
          users  — uid (PK), email (UNIQUE), password (bcrypt hash)
          logs   — id (PK), uid (FK), action, value (timestamp UNIX)
        """
        self.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid      INTEGER PRIMARY KEY AUTOINCREMENT,
                email    TEXT    UNIQUE NOT NULL,
                password TEXT    NOT NULL
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                uid    INTEGER NOT NULL,
                action TEXT    NOT NULL,
                value  TEXT
            )
        """)

        # Compte admin par défaut — hash bcrypt
        # Si le compte existe déjà (IntegrityError), on ne fait rien.
        try:
            admin_hash = self.hash_password("admin")
            self.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                ("admin", admin_hash)
            )
        except sqlite3.IntegrityError:
            pass  # Le compte admin existe déjà

        self.commit()

    def drop(self) -> None:
        """Supprime toutes les tables (usage développement uniquement)."""
        self.execute("DROP TABLE IF EXISTS users")
        self.execute("DROP TABLE IF EXISTS logs")
        self.commit()

    def execute(self, query: str, params: tuple = ()):
        return self.__db.execute(query, params)

    def commit(self) -> None:
        self.__db.commit()

    def close(self) -> None:
        self.__db.close()