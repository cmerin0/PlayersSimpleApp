from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from .routes.auth import auth
from .routes.teams import teams
from .routes.players import players
import os

# Loading environment variables
load_dotenv()

# Function to create the app with all the configurations
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    # Initialize JWT Manager
    jwt = JWTManager(app)

    # health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        try:
            return {'status': 'healthy'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500
        
    @app.route('/populate', methods=['GET'])
    def populate():
        from .populatedb import import_players, import_teams
        import_teams('teams.json')
        import_players('players.json')
        return {'status': 'database populated'}, 200
    
    # Importing routes from routes folder
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(teams, url_prefix='/api')
    app.register_blueprint(players, url_prefix='/api')

    return app
