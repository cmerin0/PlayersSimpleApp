import json
from .models import Player, Team
from .db import session

def import_teams(json_file_path):
    with open(json_file_path, 'r') as f:
        teams_data = json.load(f)

    for team_data in teams_data:
        new_team = Team(name=team_data['name'])
        session.add(new_team)

    try:
        session.commit()
        print("Teams imported successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error importing teams: {e}")

def import_players(json_file_path):
    with open(json_file_path, 'r') as f:
        players_data = json.load(f)

    for player_data in players_data:
        new_player = Player(name=player_data['name'], team_id=player_data['team_id'])
        session.add(new_player)
    try:
        session.commit()
        print("Players imported successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error importing players: {e}")

import_teams("/data/teams.json")
import_players("/data/players.json")