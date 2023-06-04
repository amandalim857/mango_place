import pytest
from db import *

@pytest.fixture(scope="function")
def username():
    return "hewwo"

@pytest.fixture(scope="function")
def password():
    return "password"

class TestUsers:
    def test_add_user(self, user_table, username):
        user_table.add_user(username, password)

        assert user_table.valid_username(username)

    def test_valid_username(self, user_table, username):
        user_table.add_user(username, password)

        assert user_table.valid_username(username)
        assert user_table.valid_username("hello")
