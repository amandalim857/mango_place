import pytest
from app import create_app
from urllib.parse import urlparse


@pytest.fixture
def app(tmp_database_path):
    app = create_app(database_path=tmp_database_path)
    app.config['TESTING'] = True

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

# Login/Logout
def test_signup(client):
    rv = client.post('/signup', data={'username':'jimbob', 'password':'password'})
    assert rv.status_code == 302
    assert urlparse(rv.location).path == '/'
    assert urlparse(rv.location).query == ''

    rv = client.post('/signup', data={'username':'jimbob', 'password':'password'})
    assert rv.status_code == 302
    assert urlparse(rv.location).path == '/'
    assert urlparse(rv.location).query == 'error=account_exists'

def test_login(client):
    client.post('/signup', data={'username':'hobo', 'password':'password'})
    rv = client.post('/login', data={'username':'hobo', 'password':'password'})
    assert rv.status_code == 302
    assert urlparse(rv.location).path == '/'
    assert urlparse(rv.location).query == ''

    rv = client.put('/canvas/3/4', query_string={'hexcolor':'#3399FF'})
    assert rv.status_code == 200

    rv = client.post('/login', data={'username':'mangoes', 'password':'password'})
    assert rv.status_code == 302
    assert urlparse(rv.location).path == '/'
    assert urlparse(rv.location).query == 'error=nonexistent_username'

    rv = client.post('/login', data={'username':'hobo', 'password':'banana'})
    assert rv.status_code == 302
    assert urlparse(rv.location).path == '/'
    assert urlparse(rv.location).query == 'error=incorrect_password'


def test_get_canvas(client):
    rv = client.get('/canvas')
    assert rv.status_code == 200
    assert rv.mimetype == 'image/png'

# to do: post and make sure canvas updates and it persists,
# change same pixel and make sure that it changes and persists
# put another bunch of pixels to make a :| face
# and then test the time function and the 409 error i shld be getting
# else get status 200
# def test_place_pixel(client):
#         client.post('/signup', data={'username':'jimbob', 'password':'password'})
#         client.post('/login', data={'username':'jimbob', 'password':'password'})
#         rv = client.put('/canvas/4/3', query_string={'hexcolor':'3399FF'})
#         print(rv.status_code)
#         assert rv.status_code == 200
#         assert list(db.get_pixel_data(4, 3)) == [30, 144, 255]
