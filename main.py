from src import create_app
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()

debug = os.getenv('DEBUG') or True
port = os.getenv('APP_PORT') or 5000

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG'), port=os.getenv('APP_PORT'))