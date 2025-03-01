import pytest
import json
import uuid
from main import app
from unittest.mock import patch
from src.db import session
from src.models import User
from werkzeug.security import generate_password_hash, check_password_hash

# Create a test client to use the app
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Test the registering an User [POST /register { username, password }]
def test_register_user(client):
    # Creating unique team name
    _username = f"User_{uuid.uuid4()}"
    _password = "TestingPassword"
    response = client.post("/register", json = { "username" : _username, "password" : _password } )
    data = json.loads(response.data)

    # Verifying it was inserted properly
    assert response.status_code == 201 
    assert data.get("message") == "User registered successfully"

    # Check if User was properly inserted
    assert session.query(User).filter_by(username=_username).first() is not None

# Test loging in an User [POST /login {username, password}]
def test_login_user(client):
    # Inserting a valid unique User and Password
    _username = f"User_{uuid.uuid4()}"
    _password = "TestingPassword"
    hashed_password = generate_password_hash(_password, method="pbkdf2:sha256")
    new_user = User(username=_username, password=hashed_password, is_admin=False)
    session.add(new_user)
    session.commit()

    # Requesting to login endpoint sending payload
    response = client.post("/login", json = { "username": _username, "password": _password})
    data = json.loads(response.data)
    print(data)

    # Asserts to verify the everything was successful
    assert response.status_code == 200
    assert data.get("message") == "Login successful"
    assert data.get("access_token") is not None
    assert data.get("refresh_token") is not None

# Test loging out from a session [POST /logout]
def test_logout_user(client):
    # Requesting the logout 
    response = client.post("/logout")

    # Loading the data 
    data = json.loads(response.data)
    
    # Asserts to verify the everything was successful
    assert response.status_code == 200
    assert data.get("message") == "Logged out successfully"