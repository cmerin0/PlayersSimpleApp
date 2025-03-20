import json
from .models import Player, Team
from .db import session

def import_teams(json_file):
    # Verifying if the data already exists in the database
    teamsData = session.query(Team).first()

    # If data exists, return
    if teamsData is not None:
        return
    
    try:
        with open(f"./src/data/{json_file}", 'r') as f:
            teams_data = json.load(f)

        for team_data in teams_data:
            new_team = Team(name=team_data['name'])
            session.add(new_team)
        session.commit()

    except FileNotFoundError as e:
        session.rollback()
        print(f"Error importing teams: {e}")

def import_players(json_file):
    # Verifying if the data already exists in the database
    playersData = session.query(Player).first()

    # If data exists, return
    if playersData is not None:
        return
    
    try:
        with open(f"./src/data/{json_file}", 'r') as f:
            players_data = json.load(f)

        for player_data in players_data:
            new_player = Player(name=player_data['name'], team_id=player_data['team_id'])
            session.add(new_player)
        session.commit()
        
    except FileNotFoundError as e:
        session.rollback()
        print(f"Error importing players: {e}")