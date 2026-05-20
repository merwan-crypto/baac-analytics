import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models.database import Database
from src.models.session import Session


class TestDatabase(unittest.TestCase):
    """Tests unitaires pour Database et Session (auth bcrypt)."""

    def setUp(self):
        """Crée une instance DB propre avant chaque test."""
        self.db = Database()

    # ------------------------------------------------------------------
    # Database.execute
    # ------------------------------------------------------------------
    def test_execute_returns_cursor(self):
        """execute() doit retourner un curseur non-nul sur une requête valide."""
        res = self.db.execute("SELECT * FROM users")
        self.assertIsNotNone(res, "execute() ne retourne pas de curseur")

    # ------------------------------------------------------------------
    # Session.signin + Session.login (bcrypt)
    # ------------------------------------------------------------------
    def test_signin_creates_user(self):
        """signin() doit insérer un nouvel utilisateur et retourner True."""
        email = "testcreate_unit@example.com"
        # Nettoyage préalable pour idempotence
        self.db.execute("DELETE FROM users WHERE email = ?", (email,))
        self.db.commit()

        s = Session(email, "MotDePasse123!")
        result = s.signin()
        self.assertTrue(result, "signin() doit retourner True pour un nouvel email")

        # Vérification en base — requête paramétrée
        row = self.db.execute(
            "SELECT uid FROM users WHERE email = ?", (email,)
        ).fetchone()
        self.assertIsNotNone(row, "L'utilisateur doit exister en base après signin()")

        # Nettoyage
        self.db.execute("DELETE FROM users WHERE email = ?", (email,))
        self.db.commit()

    def test_signin_duplicate_returns_false(self):
        """signin() doit retourner False si l'email existe déjà."""
        email = "duplicate_unit@example.com"
        self.db.execute("DELETE FROM users WHERE email = ?", (email,))
        self.db.commit()

        s = Session(email, "MotDePasse123!")
        s.signin()
        result_duplicate = s.signin()
        self.assertFalse(result_duplicate, "signin() doit retourner False pour un email déjà enregistré")

        # Nettoyage
        self.db.execute("DELETE FROM users WHERE email = ?", (email,))
        self.db.commit()

    def test_login_success_with_bcrypt(self):
        """login() doit authentifier un utilisateur dont le hash est bcrypt."""
        email = "logintest_unit@example.com"
        password = "SecretPassword42!"

        self.db.execute("DELETE FROM users WHERE email = ?", (email,))
        self.db.commit()

        # Création du compte
        s_create = Session(email, password)
        s_create.signin()

        # Authentification
        s_login = Session(email, password)
        s_login.login()
        self.assertTrue(s_login.logged, "login() doit passer logged à True avec les bons identifiants")

        # Nettoyage
        self.db.execute("DELETE FROM users WHERE email = ?", (email,))
        self.db.commit()

    def test_login_wrong_password_fails(self):
        """login() doit refuser un mauvais mot de passe."""
        email = "wrongpass_unit@example.com"

        self.db.execute("DELETE FROM users WHERE email = ?", (email,))
        self.db.commit()

        Session(email, "BonMotDePasse!").signin()

        s_fail = Session(email, "MauvaisMotDePasse!")
        s_fail.login()
        self.assertFalse(s_fail.logged, "login() ne doit pas authentifier avec un mauvais mot de passe")

        # Nettoyage
        self.db.execute("DELETE FROM users WHERE email = ?", (email,))
        self.db.commit()

    def test_hash_is_bcrypt_format(self):
        """hash() doit produire un hash bcrypt (commence par $2b$)."""
        s = Session("any@example.com", "password")
        h = s.hash()
        self.assertTrue(
            h.startswith("$2b$") or h.startswith("$2a$"),
            f"Le hash doit être au format bcrypt, obtenu : {h[:10]}..."
        )

    def test_hash_produces_different_values(self):
        """Deux appels à hash() doivent produire des valeurs différentes (salt aléatoire)."""
        s = Session("any@example.com", "password")
        self.assertNotEqual(
            s.hash(), s.hash(),
            "bcrypt doit produire un hash différent à chaque appel (salt aléatoire)"
        )


if __name__ == "__main__":
    unittest.main()