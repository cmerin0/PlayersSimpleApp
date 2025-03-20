from flask import Blueprint, request, jsonify
from ..models import Team
from ..cache import redis_client
from ..db import session
import json

# Adding blueprint to the routes
teams = Blueprint('teams', __name__)

# Route to get all teams
@teams.route('/teams', methods=['GET'])
def get_teams():
    try:
        # Attempting to get data from cache
        cached_data = redis_client.get("get_teams")

        # Retrieving data from cache
        if cached_data:
            teams_data = json.loads(cached_data)
            return jsonify({ "data": teams_data, "source": "cache"})

        # Getting all teams from the database
        teams = session.query(Team).all()
        teams_data = [team.to_dict() for team in teams]

        # Caching the data 
        redis_client.set("get_teams", json.dumps(teams_data), ex=15)

        # Returning all teams in JSON format
        return jsonify({ "data": teams_data, "source": "database"}), 200
    
    except Exception as e:
        return jsonify({"Error": "An Error occurred while fetching teams", "message": str(e) }), 500
    
# Route to create a new team
@teams.route('/teams', methods=['POST'])
def create_team():
    try:
        # Getting data from the request
        data = request.get_json()
        name = data.get('name')

        # Cheching if the field name is in the json sent
        if name is None:
            return jsonify({ "message": "The team name is invalid"}), 400

        # Creating a new team
        team = Team(name=name)
        session.add(team)
        session.commit()

        # Clearing the cache for the get_teams endpoint
        redis_client.delete("get_teams")
        redis_client.delete("get_teams_and_players")

        # Returning the new team in JSON format
        return jsonify({ "message": "Team Created Successfully", "Team": data}), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({"Error": "An Error occurred while creating a new team", "message": str(e) }), 500

# Route to get one team 
@teams.route('/teams/<int:_id>', methods=['GET'])
def get_team(_id):
    try:
        # Getting the selected team
        team = session.query(Team).filter_by(id=_id).first()

        # Checking if team exists
        if not team:
            return jsonify({ "message": "Team Not Found" }), 404
        
        # Clearing the cache for the get_teams endpoint
        redis_client.delete("get_teams")
        redis_client.delete("get_teams_and_players")
        
        # Returning the new team in JSON format
        return jsonify({ "message": "Team Found Successfully", "Team": { 'name': team.name } }), 200
    
    except Exception as e:
        return jsonify({"Error": "An Error occurred while fetching a team", "message": str(e) }), 500

# Route to update a team
@teams.route('/teams/<int:_id>', methods=['PUT'])
def update_team(_id):
    try:
        # Getting data from the request
        data = request.get_json()
        new_name = data.get('name')

        # Validating if body is properly sent
        if not new_name:
            return jsonify({ "message": "Not a valid object" }), 400

        # Getting the selected team
        team = session.query(Team).filter_by(id=_id).first()

        # Checking if team exists
        if not team:
            return jsonify({ "message": "Team Not Found" }), 404

        # Updating the team
        team.name = new_name
        session.commit()

        # Clearing the cache for the get_teams endpoint
        redis_client.delete("get_teams")
        redis_client.delete("get_teams_and_players")

        # Returning the updated team in JSON format
        return jsonify({ "message": "Team Updated Successfully", "Team": { "id": team.id, "name": team.name }}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({"Error": "An Error occurred while updating the team", "message": str(e) }), 500
    
# Route to delete a team
@teams.route('/teams/<int:_id>', methods=['DELETE'])
def delete_team(_id):
    try:
        # Getting the selected team
        team = session.query(Team).filter_by(id=_id).first()

        # Checking if team exists
        if not team:
            return jsonify({ "message": "Team Not Found" }), 404

        # Deleting the team
        session.delete(team)
        session.commit()

        # Clearing the cache for the get_teams endpoint
        redis_client.delete("get_teams")
        redis_client.delete("get_teams_and_players")

        # Returning success message
        return jsonify({ "message": "Team Deleted Successfully" }), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({"Error": "An Error occurred while deleting the team", "message": str(e) }), 500
    
# Route to get all teams and their respective players
@teams.route('/teams/players', methods=['GET'])
def get_teams_and_players():
    try:
        # Attempting to get data from cache
        cached_data = redis_client.get("get_teams_and_players")

        if cached_data:
            teams_data = json.loads(cached_data)
            return jsonify({ "data": teams_data, "source": "cache"})

        # Getting all teams from the database
        teams = session.query(Team).all()
        team_list = []
        for team in teams:
            players = [player.to_dict() for player in team.player]
            team_data = team.to_dict()
            team_data["players"] = players
            team_list.append(team_data)

        # Caching the data 
        redis_client.set("get_teams_and_players", json.dumps(team_list), ex=15)

        # Returning all teams in JSON format
        return jsonify({ "data": team_list, "source": "database"}), 200
    
    except Exception as e:
        return jsonify({"Error": "An Error occurred while fetching teams", "message": str(e) }), 500