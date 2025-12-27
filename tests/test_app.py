import pytest
from app.app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_welcome(client):
    response = client.get("/")
    assert response.status_code == 200

def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_signup_page(client):
    response = client.get("/signup")
    assert response.status_code == 200
