import pytest
from . import db

@pytest.fixture(scope="session")
def user_table():
    result = UserTable(testing=True)
    result.create_users_table()

    yield result
