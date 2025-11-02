import os
from dotenv import load_dotenv
import redis

load_dotenv()

try:
    redis_client = redis.StrictRedis(
        host = os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        username=os.getenv("REDIS_USERNAME"),
        password=os.getenv("REDIS_PASSWORD"),
        decode_responses=True
    )
    redis_client.ping()
    print("Connected to Redis Client")
    
except Exception as e:
    redis_client=None
    print(f"Redis connection failed: {str(e)}")