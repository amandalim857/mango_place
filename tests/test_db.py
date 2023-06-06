import pytest
import uuid
import datetime
import math
from PIL import Image

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


class TestCanvas():
    def test_canvas_exists(self, canvas):
        canvas.create_canvas_table()
        assert canvas.canvas_exists()
        canvas.delete_canvas_table()
        assert not canvas.canvas_exists()

    def test_create_canvas_table(self, canvas):
        canvas.create_canvas_table()
        assert canvas.canvas_exists()
    
    def test_get_canvas_table(self, canvas):
        canvas.create_canvas_table()
        canvas_table = canvas.get_canvas_table()
        with Image.open(canvas_table) as img:
            assert img.size == (128, 128)

    def test_update_canvas_pixel(self, canvas):
        canvas.create_canvas_table()
        canvas.update_canvas_pixel(3, 4, [30, 144, 255])
        canvas.update_canvas_pixel(1, 1, [255, 165, 0])
        canvas_table = canvas.get_canvas_table()
        img = Image.open(canvas_table)
        assert img.size == (128, 128)
        r, g, b = img.getpixel((4, 3))
        assert [r, g, b] == [30, 144, 255]
        
        r, g, b = img.getpixel((1, 1))
        assert [r, g, b] == [255, 165, 0]

        canvas.update_canvas_pixel(1, 1, [75, 156, 211])
        img = Image.open(canvas.get_canvas_table())
        r, g, b = img.getpixel((1, 1))
        assert [r, g, b] == [75, 156, 211]
        img.close()

    def test_delete_canvas_table(self, canvas):
        canvas.create_canvas_table()
        canvas.delete_canvas_table()
        assert not canvas.canvas_exists()


class TestPixelTable():
    def test_create_pixel_table(self, pixel_table):
        pixel_table.create_pixel_table()
        pixel_table.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pixeltable';")
        data = pixel_table.cur.fetchone()
        assert data is not None

    def test_upsert_pixel_data(self, pixel_table, username):
        pixel_table.create_pixel_table()
        row_id, col_id = 3, 4
        user = username
        timestamp = datetime.datetime.utcnow()
        pixel_table.upsert_pixel_data(row_id, col_id, user, [1, 2, 3], timestamp)
        data = pixel_table.get_pixel_data(row_id, col_id)
    
        assert data[2] == user
        assert list(data[3]) == [1, 2, 3]
        assert datetime.datetime.strptime(data[4], '%Y-%m-%d %H:%M:%S.%f') == timestamp

        pixel_table.upsert_pixel_data(row_id, col_id, user, [8, 5, 7], timestamp)
        data = pixel_table.get_pixel_data(row_id, col_id)

        assert data[2] == user
        assert list(data[3]) == [8, 5, 7]
        assert datetime.datetime.strptime(data[4], '%Y-%m-%d %H:%M:%S.%f') == timestamp

        user2 = username
        timestamp2 = datetime.datetime.now()

        pixel_table.upsert_pixel_data(8, 7, user2, [8, 8, 8], timestamp2)
        data = pixel_table.get_pixel_data(8, 7)

        assert data[2] == user2
        assert list(data[3]) == [8, 8, 8]
        assert datetime.datetime.strptime(data[4], '%Y-%m-%d %H:%M:%S.%f') == timestamp2

    def test_get_pixel_data(self, pixel_table, username):
        pixel_table.create_pixel_table()
        user = username
        timestamp = datetime.datetime.utcnow()
        pixel_table.upsert_pixel_data(8, 7, user, [225, 225, 225], timestamp)
        data = pixel_table.get_pixel_data(8, 7)

        assert data[2] == user
        assert list(data[3]) == [225, 225, 225]
        assert datetime.datetime.strptime(data[4], '%Y-%m-%d %H:%M:%S.%f') == timestamp

    
    def test_get_all_pixel_data(self, pixel_table, username):
        pixel_table.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pixeltable';")
        if pixel_table.cur.fetchall() is not None:
            pixel_table.delete_pixel_table()
        pixel_table.create_pixel_table()
        pixel_table.upsert_pixel_data(8, 7, username, [255, 255, 255], datetime.datetime.utcnow())
        pixel_table.upsert_pixel_data(8, 7, username, [255, 255, 255], datetime.datetime.utcnow())
        data = pixel_table.get_all_pixel_data()
        assert len(data) == 1

        pixel_table.upsert_pixel_data(10, 11, username, [255, 255, 255], datetime.datetime.utcnow())
        data = pixel_table.get_all_pixel_data()
        assert len(data) == 2
    
    def test_delete_pixel_table(self, pixel_table):
        pixel_table.create_pixel_table()
        pixel_table.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pixeltable';")
        exists = pixel_table.cur.fetchone()
        assert exists is not None

        pixel_table.delete_pixel_table()
        pixel_table.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pixeltable';")
        exists = pixel_table.cur.fetchone()
        assert exists is None
    
class TestCountdownTable():
    def test_create_countdown_table(self, countdown_table):
        countdown_table.create_countdown_table()
        countdown_table.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='countdowntable';")
        data = countdown_table.cur.fetchone()
        assert data is not None
    
    def test_upsert_user_timestamp(self, countdown_table,username):
        user = username
        now = datetime.datetime.now()
        countdown_table.create_countdown_table()
        countdown_table.upsert_user_timestamp(user, datetime.datetime.utcnow())
        countdown_table.upsert_user_timestamp(user, now)
        countdown_table.cur.execute("SELECT timestamp FROM countdowntable WHERE username == ?;", (user,))
        data = countdown_table.cur.fetchone()

        assert datetime.datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S.%f') == now

        utcnow = datetime.datetime.utcnow()
        countdown_table.upsert_user_timestamp(user, utcnow)
        countdown_table.cur.execute("SELECT timestamp FROM countdowntable WHERE username == ?;", (user,))
        data = countdown_table.cur.fetchone()

        assert datetime.datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S.%f') == utcnow

    def test_seconds_waited(self, countdown_table, username):
        # user does not exist in cd table yet
        assert countdown_table.seconds_waited(username) == math.inf
        # user exists
        user = username
        countdown_table.create_countdown_table()
        two_seconds_ago = datetime.datetime.utcnow() - datetime.timedelta(seconds=2)
        countdown_table.upsert_user_timestamp(user, two_seconds_ago)
        assert countdown_table.seconds_waited(user) <= (2 + 15)

        five_min_ago = datetime.datetime.utcnow() - datetime.timedelta(seconds=300)
        countdown_table.upsert_user_timestamp(user, five_min_ago)
        assert countdown_table.seconds_waited(user) <= (300 + 15)

        user2 = username
        five_years_ago = datetime.datetime.utcnow() - datetime.timedelta(days=3*365)
        countdown_table.upsert_user_timestamp(user2, five_years_ago)
        assert datetime.timedelta(seconds=countdown_table.seconds_waited(user2)) <= datetime.timedelta(days=3*365, seconds=15)

    def test_delete_countdown_table(self, countdown_table):
        countdown_table.create_countdown_table()
        countdown_table.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='countdowntable';")
        exists = countdown_table.cur.fetchone()
        assert exists is not None

        countdown_table.delete_countdown_table()
        countdown_table.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pixeltable';")
        exists = countdown_table.cur.fetchone()
        assert exists is None
        