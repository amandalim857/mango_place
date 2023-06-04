import pytest
from db import *

@pytest.fixture(scope="function")
def username():
    return "hewwo"

@pytest.fixture(scope="function")
def password():
    return "password"

class TestValidUsername:
    def test_valid_username(self, user_table):
        assert(user_table.valid_username('mey') == True)
    
    def test_invalid_username(self, user_table):
        assert(user_table.valid_username('hop') == False)

# def test_add_user(username, user_table):
#     user_table.add_user(username, password)
#     assert(user_table.valid_username(username) == True)

