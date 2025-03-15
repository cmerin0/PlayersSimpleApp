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
DB_URI = f"mysql+pymysql://${_username}:${_password}@soccer_db:3306/${_db}"

# Temporary hard coded database URI
DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

# Creating database engine
engine = create_engine(DATABASE_URI)

# Creating tables from model
Base.metadata.create_all(engine)

# Creating session
Session = sessionmaker(bind=engine)
session = Session()