import sqlite3
import bcrypt

class Database():

    def __init__(self):
        self.conn = sqlite3.connect("schema.db")
        self.cur = self.conn.cursor()


    def create_users_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY autoincrement,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );""")
        self.conn.commit()


    def add_user(self, username, password):
        userbytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(userbytes, salt)
        self.cur.execute("INSERT INTO users(username, password) values (?, ?)", (username, hash))
        self.conn.commit()


    def delete_user(self, username):
        self.cur.execute("DELETE FROM users WHERE username == ?)", (username))
        self.conn.commit()

    # Login validation functions
    def valid_username(self, username):
        username_exists = self.cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username == ?)",(username))
        self.conn.commit()
        return username_exists

    def valid_login(self, username, password):
        userbytes = password.encode("utf-8")
        info = self.cur.execute("SELECT password FROM users WHERE username == ?)",(username))
        self.conn.commit()
        result = bcrypt.checkpw(userbytes, info[0])
        return result