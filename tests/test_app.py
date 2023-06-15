import pytest
import datetime
import helper
from app import create_app
from urllib.parse import urlparse
from pytest_mock import mocker

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

    rv = client.post('/signup', data={'username':'jimbob'})
    assert rv.status_code == 400

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

    rv = client.post('/login', data={'password':'banana'})
    assert rv.status_code == 400

def test_logout(client):
    client.post('/signup', data={'username':'hobo', 'password':'password'})
    rv = client.get('/logout')
    assert rv.status_code == 401
    client.post('/login', data={'username':'hobo', 'password':'password'})
    rv = client.get('/logout')
    assert rv.status_code == 302
    rv = client.put('/canvas/7/7', query_string={'hexcolor':'#3399FF'})
    assert rv.status_code == 401

# Test Canvas
def test_get_canvas(client):
    rv = client.get('/canvas')
    assert rv.status_code == 200
    assert rv.mimetype == 'image/png'

def test_place_pixel(client):
    # user not logged in
    rv = client.put('/canvas/4/3', query_string={'hexcolor':'#3399FF'})
    assert rv.status_code == 401
    
    client.post('/signup', data={'username':'jimbob', 'password':'password'})
    client.post('/login', data={'username':'jimbob', 'password':'password'})
    rv = client.put('/canvas/7/7', query_string={'hexcolor':'#3399FF'})
    assert rv.status_code == 200

    rv = client.put('/canvas/4/3', query_string={'hexcolor':'#daa520'})
    assert rv.status_code == 429

    rv = client.put('/canvas/7/7', query_string={'hexcolor':'3399FF'})
    assert rv.status_code == 400

    rv = client.put('/canvas/7/7', query_string={'hexcolor':'#3399'})
    assert rv.status_code == 400

def test_place_pixel_time_limit(client, mocker):
    client.post('/signup', data={'username':'jades', 'password':'password'})
    client.post('/login', data={'username':'jades', 'password':'password'})
    rv = client.put('/canvas/7/7', query_string={'hexcolor':'#ffaa00'})
    assert rv.status_code == 200

    mocker.patch('helper.helper_datetime_utcnow', return_value = datetime.datetime.utcnow() + datetime.timedelta(minutes=3))
    rv = client.put('/canvas/7/7', query_string={'hexcolor':'#3399FF'})
    assert rv.status_code == 429

    helper.helper_datetime_utcnow.return_value = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    rv = client.put('/canvas/7/7', query_string={'hexcolor':'#3399FF'})
    assert rv.status_code == 200