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

    # Testing route <Delete this route>
    @app.route('/health-check', methods=['GET'])
    def healthcheck():
        return 'Success', 200
    
    # Importing routes from routes folder
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(teams, url_prefix='/api')
    app.register_blueprint(players, url_prefix='/api')

    return app
