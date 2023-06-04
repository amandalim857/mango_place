import pytest
from db import *

@pytest.fixture(scope="session")
def user_db():
    conn = sqlite3.connect(":memory")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE users(
        username TEXT UNIQUE NOT NULL PRIMARY KEY,
        password TEXT NOT NULL
    );""")

@pytest.fixture(scope="session")
def user_table():
    users = UserTable()
    users.cur.execute("INSERT INTO users(username, password) VALUES('mey', 'pp');")
    users.conn.commit()

    yield users
