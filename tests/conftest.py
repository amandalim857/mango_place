from db import UserTable, CanvasTable, PixelTable, CountdownTable
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

@pytest.fixture(scope="session")
def canvas(tmp_database_path):
    canvas = CanvasTable(database_path=tmp_database_path)
    canvas.create_canvas_table()
    yield canvas

@pytest.fixture(scope="session")
def pixel_table(tmp_database_path):
    pixel_table = PixelTable(database_path=tmp_database_path)
    pixel_table.create_pixel_table()
    yield pixel_table

@pytest.fixture(scope="session")
def countdown_table(tmp_database_path):
    countdown_table = CountdownTable(database_path=tmp_database_path)
    countdown_table.create_countdown_table()
    yield countdown_table
    
