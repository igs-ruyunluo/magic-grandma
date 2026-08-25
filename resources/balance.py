from db.connection import db, redis_client

class BalanceResource:
    def on_get(self, req, resp, username):
        cache_key = f"player:{username}:balance"

        # 先查 Redis（如果有的話）
        if redis_client is not None:
            cached = redis_client.get(cache_key)
            if cached is not None:
                resp.media = {"balance": float(cached)}
                return

        # Redis 沒有或不可用，去 MongoDB 撈
        player = db.players.find_one({"username": username})
        if player is None:
            resp.status = '404 Not Found'
            resp.media = {"type": "error", "code": "PLAYER_MISSING", "message": "玩家不存在"}
            return

        balance = player["balance"]

        # 寫回 Redis（如果有的話）
        if redis_client is not None:
            redis_client.setex(cache_key, 60, balance)

        resp.media = {"balance": balance}

