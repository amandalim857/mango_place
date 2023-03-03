import sqlite3
import bcrypt

def create_connection():
    conn = sqlite3.connect("schema.db")
    return conn


def create_users_table(conn):
    cur = conn.cursor()
    cur.execute("""
    DROP TABLE IF EXISTS users;
    CREATE TABLE users(
        id INTEGER PRIMARY KEY autoincrement,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );""")
    conn.commit()


def add_user(conn, username, password):
    cur = conn.cursor()
    userbytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(userbytes, salt)
    cur.execute("INSERT INTO users(username, password) values (?, ?)", (username, hash))
    conn.commit()


def delete_user(conn, username):
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username == ?)", (username))
    conn.commit()

# Login validation functions
def valid_username(username):
    conn = create_connection()
    cur = conn.cursor()
    username_exists = cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username == ?)",(username))
    conn.commit()
    return username_exists

def valid_login(username, password):
    conn = create_connection()
    cur = conn.cursor()
    userbytes = password.encode("utf        -8")
    info = cur.execute("SELECT password FROM users WHERE username == ?)",(username))
    conn.commit()
    result = bcrypt.checkpw(userbytes, info[0])
    return result

def login_user(username):
    # create jwt token thing
    pass

def logout_user():
    pass
    
