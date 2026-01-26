import sqlite3

class Database:
    def __init__(self) -> None:
        self.__db = sqlite3.connect("data/users.db")

    def setup(self):
        self.execute("CREATE TABLE IF NOT EXISTS users(uid INTEGER PRIMARY KEY UNIQUE ,email VARCHAR UNIQUE, password VARCHAR)")
        self.execute("CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY UNIQUE ,uid INTERGER ,action VARCHAR ,value VARCHAR)")
        try:
            self.execute(f"INSERT INTO users (email,password) VALUES ('admin', 'admin')")
        except:
            print("Admin already exists.")
        self.commit()

    def drop(self):
        self.execute("DROP TABLE users")
        self.execute("DROP TABLE logs")

    def execute(self, query:str):
        return self.__db.execute(query)

    def commit(self):
        return self.__db.commit()

    def close(self):
        self.__db.close()
