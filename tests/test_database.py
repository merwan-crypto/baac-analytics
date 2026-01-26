from src.models.database import Database
from src.models.session import Session

import unittest

class UnitTest (unittest.TestCase):
    def test_execute(self):
        db = Database()
        res = db.execute("SELECT * FROM users")
        self.assertIsNotNone(res, "execute function doesn't works !!!")

    def test_commit(self):
        db = Database()
        s = Session("test@gmail.com", "123456789")
        db.execute(f"INSERT INTO users (email,password) VALUES ('{s.email}', '{s.hash()}')", )
        print(f"SELECT uid FROM users WHERE password='{s.hash()}' and email='{s.email}'")
        res = db.execute(f"SELECT uid FROM users WHERE password='{s.hash()}' and email='{s.email}'")
        self.assertEqual(len(res.fetchone()), 1, "commit function doesn't works !!!" )


if __name__ == '__main__':
    unittest.main()