import time
import json
import os

import bcrypt

from src.models.database import Database
from src.config.constants import SESSION_PATH


class Session:
    """
    Modèle de session utilisateur.

    Sécurité — migration SHA-256 → bcrypt
    ----------------------------------------
    SHA-256 est un algorithme de hachage généraliste conçu pour la
    PERFORMANCE (milliards d'opérations/seconde).  C'est précisément
    ce qu'il ne faut PAS pour les mots de passe : un attaquant peut
    tester des dictionnaires entiers en quelques secondes.

    bcrypt est conçu pour être intentionnellement LENT (coût ajustable
    via le paramètre `rounds`).  Il génère aussi un salt aléatoire
    par mot de passe, ce qui rend les attaques par table arc-en-ciel
    impossible même si la base est compromise.

    Compatibilité ascendante
    -------------------------
    Les comptes existants (hachés en SHA-256) ne peuvent pas être
    migrés automatiquement sans connaître les mots de passe en clair.
    La méthode `_verify_password()` gère la transition en détectant
    l'ancien format SHA-256 (64 caractères hex) et en forçant un
    re-hash bcrypt à la prochaine connexion réussie.
    """

    # Coût bcrypt — 12 est le standard actuel (2^12 itérations).
    # Augmenter si les serveurs de production le permettent.
    BCRYPT_ROUNDS = 12

    def __init__(self, email: str, password: str) -> None:
        self.logged: bool = False
        self.email: str = email
        self._password: str = password

    # ── Hachage ──────────────────────────────────────────────────────────────

    def hash(self) -> str:
        """
        Génère un hash bcrypt du mot de passe.
        Chaque appel produit un hash DIFFÉRENT (salt aléatoire intégré)
        — c'est le comportement attendu, la vérification se fait via
        bcrypt.checkpw(), pas par comparaison directe.
        """
        return bcrypt.hashpw(
            self._password.encode("utf-8"),
            bcrypt.gensalt(rounds=self.BCRYPT_ROUNDS)
        ).decode("utf-8")

    @staticmethod
    def _is_sha256(stored: str) -> bool:
        """Détecte un ancien hash SHA-256 (64 caractères hexadécimaux)."""
        return len(stored) == 64 and all(c in "0123456789abcdef" for c in stored)

    def _verify_password(self, stored_hash: str) -> bool:
        """
        Vérifie le mot de passe contre le hash stocké.
        Gère la transition SHA-256 → bcrypt :
          - Si le hash stocké est un SHA-256 (ancien format), on compare
            avec l'ancien algorithme pour ne pas bloquer les utilisateurs
            existants.
          - Si c'est un hash bcrypt (nouveau format), on utilise
            bcrypt.checkpw().
        """
        if self._is_sha256(stored_hash):
            # Ancien format : vérification SHA-256 temporaire
            import hashlib
            salt = os.getenv("APP_SALT", "mon_super_salt_fil_rouge")
            old_hash = hashlib.sha256(
                (self._password + salt).encode("utf-8")
            ).hexdigest()
            return old_hash == stored_hash
        else:
            # Nouveau format : vérification bcrypt
            try:
                return bcrypt.checkpw(
                    self._password.encode("utf-8"),
                    stored_hash.encode("utf-8")
                )
            except Exception:
                return False

    def _rehash_if_needed(self, uid: int, stored_hash: str) -> None:
        """
        Si l'utilisateur s'est connecté avec un ancien hash SHA-256,
        on profite de cette connexion réussie (seul moment où on a le
        mot de passe en clair) pour mettre à jour vers bcrypt.
        """
        if self._is_sha256(stored_hash):
            new_hash = self.hash()
            db = Database()
            db.execute(
                "UPDATE users SET password = ? WHERE uid = ?",
                (new_hash, uid)
            )
            db.commit()
            db.close()

    # ── Base de données ───────────────────────────────────────────────────────

    def email_exists(self) -> bool:
        db = Database()
        res = db.execute(
            "SELECT uid FROM users WHERE email = ?",
            (self.email,)
        )
        user = res.fetchone()
        db.close()
        return user is not None

    def _get_user_row(self):
        """Retourne (uid, password_hash) ou None si l'utilisateur n'existe pas."""
        db = Database()
        res = db.execute(
            "SELECT uid, password FROM users WHERE email = ?",
            (self.email,)
        )
        row = res.fetchone()
        db.close()
        return row

    def getUID(self) -> int | None:
        row = self._get_user_row()
        if row and self._verify_password(row[1]):
            return row[0]
        return None

    def login(self) -> None:
        """
        Authentifie l'utilisateur et logue l'action.
        Migre automatiquement les anciens hashs SHA-256 vers bcrypt.
        """
        row = self._get_user_row()
        if row is None:
            return

        uid, stored_hash = row
        if not self._verify_password(stored_hash):
            return

        # Mise à jour vers bcrypt si l'ancien format est détecté
        self._rehash_if_needed(uid, stored_hash)

        # Enregistrement de la connexion dans les logs
        db = Database()
        db.execute(
            "INSERT INTO logs (uid, action, value) VALUES (?, ?, ?)",
            (uid, "logged", str(int(time.time())))
        )
        db.commit()
        db.close()
        self.logged = True

    def signin(self) -> bool:
        """
        Crée un nouveau compte avec hash bcrypt.
        Retourne True si le compte a été créé, False si l'e-mail existe déjà.
        """
        if self.email_exists():
            return False

        password_hash = self.hash()  # bcrypt avec salt aléatoire

        db = Database()
        db.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (self.email, password_hash)
        )
        db.commit()

        res = db.execute(
            "SELECT uid FROM users WHERE email = ?",
            (self.email,)
        )
        user = res.fetchone()

        if user:
            db.execute(
                "INSERT INTO logs (uid, action, value) VALUES (?, ?, ?)",
                (user[0], "signup", str(int(time.time())))
            )
            db.commit()

        db.close()
        return True

    # ── Session persistante ───────────────────────────────────────────────────

    def persist(self) -> None:
        """Sauvegarde la session dans session.json (chemin absolu)."""
        os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
        with open(SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump({"email": self.email}, f)

    @staticmethod
    def get_current_user_email() -> str:
        if not os.path.exists(SESSION_PATH):
            return ""
        try:
            with open(SESSION_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("email", "")
        except Exception:
            return ""

    @staticmethod
    def get_user_logs(email: str):
        db = Database()
        res = db.execute(
            """
            SELECT logs.action, logs.value
            FROM logs
            JOIN users ON users.uid = logs.uid
            WHERE users.email = ?
            ORDER BY logs.id DESC
            """,
            (email,)
        )
        logs = res.fetchall()
        db.close()
        return logs