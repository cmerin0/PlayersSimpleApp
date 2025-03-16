from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base
import os

# loading environment variables
load_dotenv()

# Creating database engine URI
_username = os.getenv("MYSQL_USER")
_password = os.getenv("MYSQL_PASSWORD")
_db = os.getenv("MYSQL_DATABASE")
_host = os.getenv("MYSQL_HOST")
_port = os.getenv("MYSQL_PORT")

DB_URI = f"mysql+pymysql://{_username}:{_password}@{_host}:{_port}/{_db}"

# Creating database engine
engine = create_engine(DB_URI)

# Creating tables from model
Base.metadata.create_all(engine)

# Creating session
Session = sessionmaker(bind=engine)
session = Session()