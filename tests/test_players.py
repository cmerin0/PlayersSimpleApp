import pytest
import json
import uuid
from main import app
from unittest.mock import patch
from src.db import session
from src.models import Player

# Create a test client to use the app
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Fixture to insert a single player in the database as sample
@pytest.fixture
def insert_player():
    _id = (uuid.uuid4().int % 999999) + 1 # generate a random number between 1 and 1e7
    player_name = f"Player_{_id}"
    player = Player(name = player_name, team_id = 1)
    session.add(player)
    session.commit()
    yield player_name

# Testing get players [GET /players endpoint]
def test_get_players(client, insert_player):
    # Inserting a player as a sample 
    player_name = insert_player

    # Getting the list of players
    response = client.get("/api/players")
    data = json.loads(response.data)

    # Assert to verify the request was successful
    assert response.status_code == 200

    # Asserts to verify that there is a proper response 
    assert isinstance(data.get("data"), list)

    # Check if the correct number of players is returned
    assert len(data.get("data")) > 0, "List should not be empty"

# Testing get players [GET /players/<int:id> endpoint]
def test_get_player(client, insert_player):
    # Inserting a player as a sample 
    player_name = insert_player

    # Getting data from player I just inserted
    _id = session.query(Player).filter_by(name=player_name).first().id

    # Getting the player we just inserted
    response = client.get(f"/api/players/{_id}")

    # Asserts to verify the player was found successfully
    assert response.status_code == 200
    data = json.loads(response.data)

    # Veryfing it is the same player we just inserted
    assert data.get("data")[0].get("name") == player_name


# Testing get players [POST /players endpoint]
def test_create_player(client):
    # Creating unique player name
    _id = (uuid.uuid4().int % 999999) + 1 
    player_name = f"Player_{_id}" 
    response = client.post("/api/players", json={ "name": player_name, "team_id": 1 })

    # Verifying it was inserted properly
    assert response.status_code == 200

    # Veryfing it was properly saved
    data = json.loads(response.data)
    assert data.get("message") == "Player created successfully"

# Testing get players [PUT /players/<int:id> endpoint]
def test_update_player(client, insert_player):
    # Inserting a player as a sample
    player_name = insert_player

    # Getting the data of the player I just inserted
    current_player = session.query(Player).filter_by(name=player_name).first()
    _id = current_player.id
    _team_id = current_player.team_id

    # Updating the current field
    updated_data = { "name" : f"updated_{player_name}", "team_id": _team_id}
    response = client.put(f"/api/players/{_id}", json=updated_data)
    data = json.loads(response.data)

    # Asserts to verify it was updated successfully
    assert response.status_code == 200
    assert data.get("message") == "Player updated successfully"

# Testing get players [DELETE /players/<int:id> endpoint]
def test_delete_player(client, insert_player):
    # Inserting a client as a sample 
    player_name = insert_player

    # Getting data from player I just inserted
    current_player_id = session.query(Player).filter_by(name=player_name).first().id

    # Deleting the player we just inserted 
    response = client.delete(f"/api/players/{current_player_id}")
    data = json.loads(response.data)

    # Asserts to verify the player was deleted successfully 
    assert response.status_code == 200
    assert data.get("message") == "Player deleted successfully"

# SECTION: Testing Error Handling in the Requests 

# Testing exception when player is not found [404]
def test_exception_get_player(client):
    # Getting a player that doesnt exists 
    response = client.get(f"/api/players/{uuid.uuid4().int}")

    # Asserts that get the 404 Exception user not found 
    assert response.status_code == 404 

    # Verifying the message of player not found is sent
    data = json.loads(response.data)
    assert "Not Found" in data.get("message")

# Testing exception when player is created [400]
def test_exception_create_player_invalid_body(client):
    # Inserting the new player through the endpoint
    response = client.post("/api/players", json={ "wrong_field": "wrong_name" })
    data = json.loads(response.data)

    # Assert that get the server error 400 bad request
    assert response.status_code == 400
    assert "Bad Request" in data.get("message")

# Testing exception when team id doesn't exist [400]
def test_exception_create_player_invalid_team(client):
    # Inserting the new player through the endpoint
    response = client.post("/api/players", json={ "name": "team_name", "team_id": uuid.uuid4().int })
    data = json.loads(response.data)

    # Assert that get the server error 400 bad request
    assert response.status_code == 400
    assert "Team does not exist" in data.get("message")

# Testing exception in update when player id is correct but body sent is invalid
def test_exception_update_player_invalid_body(client, insert_player):
    # Inserting a player to make sure at least one field exists
    player_name = insert_player

    # Updating an existent player but sending wrong body
    response = client.put("/api/players/1", json={ "wrong_field": "wrong_name" })
    data = json.loads(response.data)

    # Assert that get the server error 400 bad request
    assert response.status_code == 400
    assert "Team does not exist" in data.get("message")

# Testing exception in update when player id is invalid
def test_exception_update_player_invalid_id(client):
    # Updating an non existent player
    response = client.put(f"/api/players/{uuid.uuid4().int}", json={ "name": "test_player_name" })
    data = json.loads(response.data)

    # Assert that get the server error 404 player not found
    assert response.status_code == 404
    assert "Not Found" in data.get("message")

# Testing exception in delete when player id is invalid
def test_exception_delete_player_invalid_id(client):
    # Deleting an existent player but sending wrong id
    response = client.delete(f"/api/players/{uuid.uuid4().int}")
    data = json.loads(response.data)

    # Assert that get the server error 404 player not found
    assert response.status_code == 404
    assert "Not Found" in data.get("message")

# SECTION: Testing Database Errors or Errors coming from Server [500]

# Testing exception error when getting players
def test_database_error_get_players(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    with patch('src.db.session.query') as mock_query:
        # Make the add function raise an exception
        mock_query.side_effect = Exception(_error) 

        response = client.get('/api/players')

        assert response.status_code == 500
        data = json.loads(response.data)
        assert _error in data.get("message")

# Testing exception error in server 500s
def test_database_error_create_player(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    with patch('src.db.session.add') as mock_add:
        # Make the add function raise an exception
        mock_add.side_effect = Exception(_error) 

        # Requesting to create player endpoint sending payload
        payload = {'name': 'Test Player', "team_id": 1}
        response = client.post('/api/players', json=payload)
        data = json.loads(response.data)

        # asserts to verify the error message
        assert response.status_code == 500
        assert _error in data.get("message")

# Testing exception error when getting a single player
def test_database_error_get_player(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    with patch('src.db.session.query') as mock_query:
        # Make the query function raise an exception
        mock_query.side_effect = Exception(_error) 

        response = client.get('/api/players/1')
        data = json.loads(response.data)

        assert response.status_code == 500
        assert _error in data.get("message")

# Testing exception error when updating players
def test_database_error_update_player(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    
    with patch('src.db.session.commit') as mock_commit:
        # Make the query function raise an exception
        mock_commit.side_effect = Exception(_error) 

        # Requesting to update player endpoint sending payload
        payload = {'name': 'Updated Player', "team_id": 1}
        response = client.put('/api/players/1', json=payload)
        data = json.loads(response.data)

        assert response.status_code == 500
        assert _error in data.get("message")

# Testing exception error when deleting players
def test_database_error_delete_player(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    with patch('src.db.session.delete') as mock_delete:
        # Make the query function raise an exception
        mock_delete.side_effect = Exception(_error) 

        # Requesting to delete player endpoint 
        response = client.delete('/api/players/1')
        data = json.loads(response.data)

        assert response.status_code == 500
        assert _error in data.get("message")


