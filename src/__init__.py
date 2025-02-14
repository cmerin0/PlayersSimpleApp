from flask import Flask
from dotenv import load_dotenv
from .routes.auth import auth
import os


# Loading environment variables
load_dotenv()

# Function to create the app with all the configurations
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Testing route <Delete this route>
    @app.route('/')
    def index():
        return 'Hello World from Flask!'
    
    # Importing routes from routes folder
    app.register_blueprint(auth, url_prefix='/')

    return app
