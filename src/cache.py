import redis 
import os
from dotenv import load_dotenv

load_dotenv()

# Setting up Redis connection
REDIS_URL = os.getenv('REDIS_URL')
redis_client = redis.Redis.from_url(REDIS_URL)