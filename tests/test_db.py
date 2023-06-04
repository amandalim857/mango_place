import pytest
import uuid

@pytest.fixture(scope="function")
def username():
    return str(uuid.uuid4())

@pytest.fixture(scope="function")
def password():
    return "password"

class TestUsers:
    def test_add_user(self, user_table, username, password):
        user_table.add_user(username, password)

        assert user_table.valid_username(username)

    def test_valid_username(self, user_table, username, password):
        user_table.add_user(username, password)

        assert user_table.valid_username(username)
        assert not user_table.valid_username("hello")

    def test_delete_user(self, user_table, username, password):
        user_table.add_user(username, password)
        user_table.delete_user(username)

        assert not user_table.valid_username(username)

    def test_valid_login(self, user_table, username, password):
        user_table.add_user(username, password)

        assert user_table.valid_login(username, password)
        assert not user_table.valid_login(username, "sprongle")
        assert not user_table.valid_login("springle", "sprongle")
        assert not user_table.valid_login("springle", password)

        user_table.delete_user(username)
        assert not user_table.valid_login(username, password)
        assert not user_table.valid_login("springle", password)
        assert not user_table.valid_login(username, "sprongle")
