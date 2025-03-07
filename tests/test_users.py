import pytest
import json
import uuid
from main import app
from unittest.mock import patch
from src.db import session
from src.models import User
from werkzeug.security import generate_password_hash

# Create a test client to use the app
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Fixture to insert a single team in the database as sample
@pytest.fixture
def insert_user():
    def inner_insert_user(is_admin=False):
        # Creating unique team name
        _uniqueid = (uuid.uuid4().int % 999999) + 1 # generate a random number between 1 and 1e7
        _username = f"User_{ _uniqueid }"
        _password = "TestingPassword"
        hashed_password = generate_password_hash(_password, method="pbkdf2:sha256")

        # Inserting the user in the database
        new_user = User(username=_username, password=hashed_password, is_admin=is_admin)
        session.add(new_user)
        session.commit()

        # Returning the username and password
        return _username, _password
    return inner_insert_user

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
def test_login_user(client, insert_user):
    # Inserting a valid unique User and Password
    _username, _password = insert_user()

    # Requesting to login endpoint sending payload
    response = client.post("/login", json = { "username": _username, "password": _password})
    data = json.loads(response.data)

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

# Test getting all Users [GET /users]
def test_get_users(client, insert_user):
    # Inserting a valid unique User and Password
    _username, _password = insert_user(is_admin=True)

    # Logging in to get access_token
    login = client.post("/login", json = { "username": _username, "password": _password})
    assert login.status_code == 200

    # Requesting to login endpoint sending payload
    response = client.get("/users")

    # Asserts to verify the everything was successful
    assert response.status_code == 200
    assert len(json.loads(response.data)) > 0

# Testing Access Error [404]

# Testing error 401, Invalid Credentials
def test_login_user_invalid_credentials(client):
    # Inserting a valid unique User and Password
    reponse = client.post("/login", json = { "username": "", "password": ""})
    data = json.loads(reponse.data)

    # Asserts to verify that the error was returned
    assert reponse.status_code == 401
    assert data.get("message") == "Invalid credentials"

# Testing error 400 when trying to register a user with missing user/password required
def test_register_user_missing_fields(client):
    # Requesting to login endpoint sending payload
    response = client.post("/register", json = { "username": "", "password": ""})
    data = json.loads(response.data)

    # Asserts to verify the everything was successful
    assert response.status_code == 400
    assert data.get("message") == "Username and password are required"

# Testing error 400 when trying to register a user with an existing username
def test_register_user_existing_user(client, insert_user):
    # Inserting a valid unique User and Password
    _username, _password = insert_user()

    # Requesting to login endpoint sending payload
    response = client.post("/register", json = { "username": _username, "password": _password})
    data = json.loads(response.data)

    # Asserts to verify the everything was successful
    assert response.status_code == 400
    assert data.get("message") == "Username already exists"

# Testing error 403 Forbidden access while getting all users
def test_get_users_forbidden(client, insert_user):
    # Inserting a valid unique User and Password
    _username, _password = insert_user()

    # Logging in to get access_token
    login = client.post("/login", json = { "username": _username, "password": _password})
    assert login.status_code == 200

    # Requesting to login endpoint sending payload
    response = client.get("/users")
    data = json.loads(response.data)

    # Asserts to verify the everything was successful
    assert response.status_code == 403
    assert data.get("message") == "Forbidden Access"

# Testing exception error when getting all users
def test_database_error_get_users(client, insert_user):
    _error = "Simulated database error"
    # Inserting user to allow access
    _username, _password = insert_user(is_admin=True)

    # Logging in to get access_token
    login = client.post("/login", json = { "username": _username, "password": _password})

    # Mock the database session to raise an exception
    with patch('src.db.session.query') as mock_query:
        # Make the add function raise an exception
        mock_query.side_effect = Exception(_error) 

        # Requesting to login endpoint 
        response = client.get('/users')

        assert response.status_code == 500
        data = json.loads(response.data)
        assert _error in data.get("message")

# Testing exception error when registering a user
def test_database_error_register_user(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    with patch('src.db.session.add') as mock_add:
        # Make the add function raise an exception
        mock_add.side_effect = Exception(_error) 

        # Requesting to login endpoint sending payload
        response = client.post("/register", json = { "username": "test", "password": "test"})

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data.get("Error") == "An Error occurred while Creating User"
        assert _error in data.get("message")

# Testing exception error when logging in
def test_database_error_login_user(client, insert_user):
    _error = "Simulated database error"
    # Inserting a valid unique User and Password
    _username, _password = insert_user()

    # Mock the database session to raise an exception
    with patch('src.db.session.query') as mock_query:
        # Make the add function raise an exception
        mock_query.side_effect = Exception(_error) 

        # Requesting to login endpoint sending payload
        response = client.post("/login", json = { "username": _username, "password": _password})

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data.get("Error") == "An Error occurred while Logging In"
        assert _error in data.get("message")