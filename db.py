import sqlite3
import bcrypt
import math
from PIL import Image
import numpy as np
import io
import datetime

class Database():

    def __init__(self, database_path="schema.db"):
        self.conn = sqlite3.connect(database_path)
        self.cur = self.conn.cursor()

class UserTable(Database):

    def create_users_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT UNIQUE NOT NULL PRIMARY KEY,
            password TEXT NOT NULL
        );""")
        self.conn.commit()

    def add_user(self, username, password):
        userbytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(userbytes, salt)
        self.cur.execute("INSERT INTO users(username, password) values (?, ?);", (username, hash))
        self.conn.commit()

    def delete_user(self, username):
        self.cur.execute("DELETE FROM users WHERE username == ?;", (username,))
        self.conn.commit()

    # Login validation functions
    def valid_username(self, username):
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username == ?);",(username,))
        return True if self.cur.fetchone()[0] == 1 else False

    def valid_login(self, username, password):
        userbytes = password.encode("utf-8")
        self.cur.execute("SELECT password FROM users WHERE username == ?;",(username,))
        info = self.cur.fetchone()
        if info is None:
            return False

        result = bcrypt.checkpw(userbytes, info[0].encode())
        return result


class CanvasTable(Database):

    def canvas_exists(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='canvas';")
        canvas_exists = self.cur.fetchone()
        return 1 if canvas_exists else 0

    def create_canvas_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS canvas(
            row_id INTEGER PRIMARY KEY,
            column_list BLOB NOT NULL
        );""")
        for id in range(128):
            col_list = bytes([255]*384)
            blob_data = sqlite3.Binary(col_list)
            self.cur.execute("""
            INSERT INTO canvas(row_id, column_list)
            VALUES(?, ?)
            ON CONFLICT(row_id)
            DO UPDATE SET column_list = ?
            ;""", (id, blob_data, blob_data))
        self.conn.commit()

    def get_canvas_table(self):
        grid = bytearray()
        self.cur.execute("SELECT column_list FROM canvas ORDER BY row_id;")
        rows = self.cur.fetchall()
        for row in rows:
            column = row[0]
            grid.extend(column)

        nparray = np.frombuffer(grid, dtype=np.uint8).reshape((128, 128, 3))
        img = Image.fromarray(nparray)
        # save image and send as png
        file = io.BytesIO()
        img.save(file, format="PNG")
        return file

    def update_canvas_pixel(self, row_id, col_id, color):
        # color is a list of 3 values
        self.cur.execute("SELECT column_list FROM canvas WHERE row_id == ?", (row_id,))
        column_list = list(self.cur.fetchone()[0])
        corr_col_id = col_id * 3
        for i in range(3):
            column_list[corr_col_id + i] = color[i]
        new_blob_data = sqlite3.Binary(bytes(column_list))
        self.cur.execute("UPDATE canvas SET column_list = ? WHERE row_id = ?", (new_blob_data, row_id))
        self.conn.commit()

    def delete_canvas_table(self):
        self.cur.execute("DROP TABLE IF EXISTS canvas;")

class PixelTable(Database):

    def create_pixel_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS pixeltable(
            row_id INTEGER NOT NULL,
            col_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            color BLOB NOT NULL,
            timestamp TEXT NOT NULL,
            PRIMARY KEY(row_id, col_id),
            FOREIGN KEY(username) REFERENCES users(username)
        );""")
        self.conn.commit()

    def upsert_pixel_data(self, row_id, col_id, username, color, timestamp):
        # color is a list of 3 values, timestamp is datetime object
        blob_data = sqlite3.Binary(bytes(color))
        self.cur.execute("""
        INSERT INTO pixeltable(row_id, col_id, username, color, timestamp)
        VALUES(?, ?, ?, ?, ?)
        ON CONFLICT(row_id, col_id) DO UPDATE
        SET username = EXCLUDED.username,
            color = EXCLUDED.color,
            timestamp = EXCLUDED.timestamp
        ;""", (row_id, col_id, username, blob_data, timestamp))

        self.conn.commit()

    def get_pixel_data(self, row_id, col_id):
        self.cur.execute("SELECT * FROM pixeltable WHERE row_id == ? AND col_id == ?", (row_id, col_id))
        data = self.cur.fetchone()
        return data

    def get_all_pixel_data(self):
        self.cur.execute("SELECT * FROM pixeltable")
        data = self.cur.fetchall()
        return data

    def delete_pixel_table(self):
        self.cur.execute("DROP TABLE IF EXISTS pixeltable;")
        self.conn.commit()

class CountdownTable(Database):

    def create_countdown_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS countdowntable(
            username TEXT UNIQUE PRIMARY KEY,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        );""")
        self.conn.commit()

    def upsert_user_timestamp(self, username, timestamp):
        self.cur.execute("""
        INSERT INTO countdowntable(username, timestamp)
        VALUES(?, ?)
        ON CONFLICT(username)
        DO UPDATE SET timestamp = EXCLUDED.timestamp
        ;""", (username, timestamp))
        self.conn.commit()

    def seconds_waited(self, username):
        self.cur.execute("SELECT timestamp FROM countdowntable WHERE username == ?;", (username,))
        timestamp_tuple = self.cur.fetchone()
        if timestamp_tuple is None:
            return math.inf
        last_timestamp = datetime.datetime.strptime(timestamp_tuple[0], '%Y-%m-%d %H:%M:%S.%f')
        now = datetime.datetime.utcnow()
        return (now - last_timestamp).total_seconds()

    def delete_countdown_table(self):
        self.cur.execute("DROP TABLE IF EXISTS countdowntable;")
        self.conn.commit()
