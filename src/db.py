from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base
import os

# loading environment variables
load_dotenv()

# Temporary hard coded database URI
DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
print("this is my db link" + DATABASE_URI)

# Creating database engine
engine = create_engine(DATABASE_URI)

# Creating tables from model
Base.metadata.create_all(engine)

# Creating session
Session = sessionmaker(bind=engine)
session = Session()