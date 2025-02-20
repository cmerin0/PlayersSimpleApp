import pytest
import json
import uuid
from main import app
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

    # Check if the correct number of teams is returned
    assert len(data.get("data")) > 0, "List should not be empty"

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

# Testing Error Handling in the Requests 
