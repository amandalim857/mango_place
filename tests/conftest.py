from db import UserTable
import pytest
import tempfile

@pytest.fixture(scope="session")
def tmp_database_path():
    with tempfile.NamedTemporaryFile() as file:
        yield file.name

@pytest.fixture(scope="session")
def user_table(tmp_database_path):
    result = UserTable(database_path=tmp_database_path)
    result.create_users_table()

    yield result
