import os
import redis
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

client = MongoClient(MONGO_URI)

try:
    redis_client = redis.from_url(REDIS_URL, protocol=2)
    redis_client.ping()
except:
    redis_client = None  # Redis 不可用時設為 None
db = client["game_db"]

db.players.create_index("username", unique=True)

