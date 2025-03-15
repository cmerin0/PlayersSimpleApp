import pytest
import json
import uuid
from main import app
from unittest.mock import patch
from src.db import session
from src.models import Team

# Create a test client to use the app
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Fixture to insert a single team in the database as sample
@pytest.fixture
def insert_team():
    team_name = f"Team_{uuid.uuid4()}"
    team = Team(name = team_name)
    session.add(team)
    session.commit()
    yield team_name

# Testing get teams [GET /teams endpoint]
def test_get_teams(client, insert_team):
    # Inserting a team as a sample 
    team_name = insert_team

    # Getting the list of teams
    response = client.get("/api/teams")

    # Assert to verify the request was successful
    assert response.status_code == 200
    data = json.loads(response.data)

    # Asserts to verify that there is a proper response 
    assert isinstance(data.get("data"), list)

# Testing get teams [GET /teams/<int:id> endpoint]
def test_get_team(client, insert_team):
    # Inserting a team as a sample 
    team_name = insert_team

    # Getting data from team I just inserted
    _id = session.query(Team).filter_by(name=team_name).first().id

    # Getting the team we just inserted
    response = client.get(f"/api/teams/{_id}")

    # Asserts to verify the team was found successfully
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get("message") == "Team Found Successfully"

    # Veryfing it is the same team we just inserted
    assert data.get("Team", {}).get("name") == team_name


# Testing get teams [POST /teams endpoint]
def test_create_team(client):
    # Creating unique team name
    team_name = f"Team_{uuid.uuid4()}" 
    response = client.post("/api/teams", json={ "name": team_name })

    # Verifying it was inserted properly
    assert response.status_code == 201 

    # Veryfing it was properly saved
    data = json.loads(response.data)
    assert data["Team"]["name"] == team_name

# Testing get teams [PUT /teams/<int:id> endpoint]
def test_update_team(client, insert_team):
    # Inserting a team as a sample
    team_name = insert_team

    # Getting the data of the team I just inserted
    current_team = session.query(Team).filter_by(name=team_name).first()
    _id = current_team.id

    # Updating the current field
    updated_data = { "name" : f"updated_{team_name}"}
    response = client.put(f"/api/teams/{_id}", json=updated_data)

    # Asserts to verify it was updated successfully
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get("message") == "Team Updated Successfully"
    assert data.get("Team", {}).get("id") == _id
    assert data.get("Team", {}).get("name") == f"updated_{team_name}"

# Testing get teams [DELETE /teams/<int:id> endpoint]
def test_delete_team(client, insert_team):
    # Inserting a client as a sample 
    team_name = insert_team

    # Getting data from team I just inserted
    current_team_id = session.query(Team).filter_by(name=team_name).first().id

    # Deleting the team we just inserted 
    response = client.delete(f"/api/teams/{current_team_id}")

    # Asserts to verify the team was deleted successfully 
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get("message") == "Team Deleted Successfully"

# SECTION: Testing Error Handling in the Requests 

# Testing exception when team is not found [404]
def test_exception_get_team(client):
    # Getting a team that doesnt exists 
    response = client.get(f"/api/teams/{uuid.uuid4().int}")

    # Asserts that get the 404 Exception user not found 
    assert response.status_code == 404 

    # Verifying the message of team not found is sent
    data = json.loads(response.data)
    assert "Not Found" in data.get("message")

# Testing exception when team is created [400]
def test_exception_create_team(client):
    # Inserting the new team through the endpoint
    response = client.post("/api/teams", json={ "wrong_field": "wrong_name" })

    # Assert that get the server error 400 bad request
    assert response.status_code == 400

# Testing exception in update when team id is correct but body sent is invalid
def test_exception_update_team_invalid_body(client, insert_team):
    # Inserting a team to make sure at least one field exists
    team_name = insert_team

    # Updating an existent team but sending wrong body
    response = client.put("/api/teams/1", json={ "wrong_field": "wrong_name" })

    # Assert that get the server error 400 bad request
    assert response.status_code == 400

# Testing exception in update when team id is invalid
def test_exception_update_team_invalid_id(client):
    # Updating an non existent team
    response = client.put(f"/api/teams/{uuid.uuid4().int}", json={ "name": "test_team_name" })

    # Assert that get the server error 404 team not found
    assert response.status_code == 404

# Testing exception in delete when team id is invalid
def test_exception_delete_team_invalid_id(client):
    # Deleting an existent team but sending wrong id
    response = client.delete(f"/api/teams/{uuid.uuid4().int}")

    # Assert that get the server error 404 team not found
    assert response.status_code == 404

# SECTION: Testing Database Errors or Errors coming from Server [500]

# Testing exception error when getting teams
def test_database_error_get_teams(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    with patch('src.db.session.query') as mock_query:
        # Make the add function raise an exception
        mock_query.side_effect = Exception(_error) 

        response = client.get('/api/teams')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert _error in response_data.get("message")

# Testing exception error in server 500s
def test_database_error_create_team(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    with patch('src.db.session.add') as mock_add:
        # Make the add function raise an exception
        mock_add.side_effect = Exception(_error) 

        data = {'name': 'Test Team'}
        response = client.post('/api/teams', json=data)

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert _error in response_data.get("message")

# Testing exception error when getting a single team
def test_database_error_get_team(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    with patch('src.db.session.query') as mock_query:
        # Make the query function raise an exception
        mock_query.side_effect = Exception(_error) 

        response = client.get('/api/teams/1')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert _error in response_data.get("message")

# Testing exception error when updating teams
def test_database_error_update_team(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    
    with patch('src.db.session.commit') as mock_commit:
        # Make the query function raise an exception
        mock_commit.side_effect = Exception(_error) 

        data = {'name': 'Updated Team'}
        response = client.put('/api/teams/1', json=data)

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert _error in response_data.get("message")

# Testing exception error when deleting teams
def test_database_error_delete_team(client):
    _error = "Simulated database error"
    # Mock the database session to raise an exception
    with patch('src.db.session.delete') as mock_delete:
        # Make the query function raise an exception
        mock_delete.side_effect = Exception(_error) 

        response = client.delete('/api/teams/1')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert _error in response_data.get("message")