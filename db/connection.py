import redis
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
redis_client = redis.Redis(host = 'localhost', port = 6379, db = 0, protocol=2)
db = client["game_db"]

db.players.create_index("username", unique=True)

