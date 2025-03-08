from flask import Blueprint, request, jsonify
from ..models import Player, Team
from ..cache import redis_client
from ..db import session
import json

# Adding blueprint to the routes
players = Blueprint('players', __name__)

# Route to get all players
@players.route('/players', methods=['GET'])
def get_players():
    try:
        # Attempting to get data from cache
        cached_data = redis_client.get("get_players")

        # Retrieving data from cache
        if cached_data:
            players_data = json.loads(cached_data)
            return jsonify({ "data": players_data, "source": "cache"})

        # Getting all players from the database
        players = session.query(Player).all()
        players_data = [player.to_dict() for player in players]

        # Caching the data 
        redis_client.set("get_players", json.dumps(players_data), ex=60)

        # Returning all players in JSON format
        return jsonify({ "data": players_data, "source": "database"}), 200
    
    except Exception as e:
        return jsonify({"Error": "An Error occurred while fetching players", "message": str(e) }), 500

# Route to get one player    
@players.route("/players/<int:_id>", methods=["GET"])
def get_player(_id):
    try:
        # Getting the requested player
        player = session.query(Player).filter_by(id=_id).first()

        # Verifying if user exists 
        if not player:
            return jsonify({ "message": "Player Not Found" }), 404
        
        # Getting team name instead of displaying team id
        team = session.query(Team).filter_by(id=player.team_id).first()

        # Returning user info if this one exists 
        player_data = [{ "id" : player.id, "name": player.name, "team": team.name }]  

        # Clearing the cache for the get_teams endpoint
        redis_client.delete("get_players")

        # Returning the player in JSON format
        return jsonify({ "data": player_data, "source": "database" }), 200

    except Exception as e:
        return jsonify({ "error" : "Error fetching the player", "message" : str(e) }), 500

# Creating a new player
@players.route("/players", methods=["POST"])
def create_player():

    # Getting data form body
    data = request.get_json()
    team_id = data.get("team_id")
    name = data.get("name")

    try:
        # Checking if the name is empty
        if name is None or team_id is None:
            return jsonify({ "message": "Bad Request: Player name and Team are required"}), 400

        # Checking if team exists before inserting 
        team = session.query(Team).filter_by(id=team_id).first()
        if not team: 
            return jsonify({ "message": "Player cannot be inserted since Team does not exist"}), 400 
        
        # Inserting new player if everything is correct
        new_player = Player(name=name, team_id=team_id)
        session.add(new_player)
        session.commit()

        # Clearing the cache for the get_teams endpoint
        redis_client.delete("get_players")

        # Returning successfully added message
        return jsonify({ "message": "Player created successfully" }), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({ "error": "Error inserting a new player", "message": str(e) }), 500
    
# Route to update a Player 
@players.route("/players/<int:_id>", methods=["PUT"])
def update_player(_id):
    # Getting data form body
    data = request.get_json()
    team_id = data.get("team_id")
    
    try:
        # Getting information about the player
        player = session.query(Player).filter_by(id=_id).first()
        if not player:
            return jsonify({ "message": "Player Not Found"}), 404

        # Checking if the new team exists before inserting 
        team = session.query(Team).filter_by(id=team_id).first()
        if not team: 
            return jsonify({ "message": "Player cannot be updated since Team does not exist"}), 400 
        
        # Updating the current player
        player.name = data.get("name")
        player.team_id = team_id
        session.commit()

        # Clearing the cache for the get_teams endpoint
        redis_client.delete("get_players")

        # Returning successfully updated message
        return jsonify({ "message": "Player updated successfully" }), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({ "error": "Error updating the player", "message": str(e) }), 500
    
@players.route("/players/<int:_id>", methods=["DELETE"])
def delete_player(_id):
    try:
        # Getting the player to delete
        player = session.query(Player).filter_by(id=_id).first()
        if not player: 
            return jsonify({ "message": "Player Not Found"}), 404

        # Deleting player
        session.delete(player)
        session.commit()

        # Clearing the cache for the get_teams endpoint
        redis_client.delete("get_players")

        # Returning successfully deleted message
        return jsonify({ "message": "Player deleted successfully"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({ "error": "Error deleting the player", "message": str(e) }), 500