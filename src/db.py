from sqlalchemy import create_engine, event 
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

# Temporary hard coded database URI
DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI") or "mysql+pymysql://playuser:playpass@127.0.0.1:3306/soccer_db"

# Creating database engine
engine = create_engine(DATABASE_URI)

# Creating tables from model
Base.metadata.create_all(engine)

# Creating session
Session = sessionmaker(bind=engine)
session = Session()