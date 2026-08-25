from db.connection import db, redis_client

class BalanceResource:
    def on_get(self, req, resp, username):
        cache_key = f"player:{username}:balance" 

        cached = redis_client.get(cache_key)# 去 redis 查 key 
        if cached is not None:
            resp.media = {"balance":float(cached)} # 有的話，直接存進去
            return
        
        player = db.players.find_one({"username":username}) # 沒有的話，再去 DB 撈
        if player is  None:
            resp.status = '404 Not Found'
            resp.media = {"type":"error", "code":"PLAYER_MISSING", "message":"玩家不存在"}
            return

        balance = player["balance"]
        redis_client.setex(cache_key, 60, balance)
        resp.media = {"balance": balance} # 寫回前端

