import sqlite3
import bcrypt

class Database():

    def __init__(self):
        self.conn = sqlite3.connect("schema.db")
        self.cur = self.conn.cursor()

class UserTable(Database):

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
    

class CanvasTable(Database):
    def create_canvas_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS canvas(
            row_id INTEGER PRIMARY KEY,
            column_list BLOB NOT NULL
        );""")        
        for id in range(128):
            col_list = bytes([255]*384)
            blob_data = sqlite3.Binary(col_list)
            self.cur.execute("INSERT INTO canvas(row_id, column_list) values (?, ?);", (id, blob_data))
        self.conn.commit()  
    
    def get_canvas_table(self):
        self.cur.execute("SELECT column_list FROM canvas ORDER BY row_id")
        rows = self.cur.fetchall()
        for row in rows:
            print(row[0]) # fix the decoding problem
        return rows
    
    def delete_canvas_table(self):
        self.cur.execute("DROP TABLE IF EXISTS canvas;")        
    
    def update_pixel(self, row_id):
        self.cur.execute(row_id)
        pass

canvas_table = CanvasTable()
canvas_table.delete_canvas_table()
canvas_table.create_canvas_table()
thing = canvas_table.get_canvas_table()