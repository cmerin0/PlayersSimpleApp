from flask import Blueprint, request, jsonify
from ..models import Player, Team
from ..db import session

# Adding blueprint to the routes
players = Blueprint('players', __name__)

# Route to get all players
@players.route('/players', methods=['GET'])
def get_players():
    try:
        # Getting all players from the database
        players = session.query(Player).all()

        players_data = [player.to_dict() for player in players]

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
            return jsonify({ "message": "Player not Found" }), 404
        
        # Getting team name instead of displaying team id
        team = session.query(Team).filter_by(id=player.team_id).first()

        # Returning user info if this one exists 
        player_data = [{ "id" : player.id, "name": player.name, "team": team.name }]  
        return jsonify({ "data": player_data, "source": "database" }), 200

    except Exception as e:
        return jsonify({ "Message" : "Error fetching the player", "Error" : str(e) }), 500

# Creating a new player
@players.route("/players", methods=["POST"])
def create_player():

    # Getting data form body
    data = request.get_json()
    team_id = data.get("team_id")
    name = data.get("name")

    try:
        # Checking if team exists before inserting 
        team = session.query(Team).filter_by(id=team_id).first()
        if not team: 
            return jsonify({ "Message": "Player cannot be inserted since Team does not Exist"}), 400 
        
        # Inserting new player if everything is correct
        new_player = Player(name=name, team_id=team_id)
        session.add(new_player)
        session.commit()
        return jsonify({ "Message": "Player created successfully" }), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({ "Message": "Error inserting a new player", "Error": str(e) }), 500
    
# Route to update a Player 
@players.route("/players/<int:_id>", methods=["PUT"])
def update_player(_id):
    # Getting data form body
    data = request.get_json()
    team_id = data.get("team_id")
    
    try:
        # Getting information about the player
        player = session.query(Player).filter_by(id=_id).first()

        # Checking if the new team exists before inserting 
        team = session.query(Team).filter_by(id=team_id).first()
        if not team: 
            return jsonify({ "Message": "Player cannot be updated since Team does not Exist"}), 400 
        
        # Updating the current player
        player.name = data.get("name")
        player.team_id = team_id
        session.commit()

        return jsonify({ "Message": "Player updated successfully" }), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({ "Message": "Error updating the player", "Error": str(e) }), 500
    
@players.route("/players/<int:_id>", methods=["DELETE"])
def delete_player(_id):
    try:
        # Getting the player to delete
        player = session.query(Player).filter_by(id=_id).first()
        if not player: 
            return jsonify({ "Message": "Player does not exists"}), 400 

        # Deleting player
        session.delete(player)
        session.commit()
        return jsonify({ "Message": "Player deleted successfully"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({ "Message": "Error deleting the player", "Error": str(e) }), 500