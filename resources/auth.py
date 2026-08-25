import bcrypt
from datetime import datetime
from db.connection import db
from pymongo.errors import DuplicateKeyError # 錯誤型態需要被 import

class RegisterResource:
    def on_post(self, req, resp):
        data = req.get_media() # 解析封包後，得到的 request body
        username = data.get("username")
        password = data.get("password")
        
        if not username or not  password:
            resp.status = '400 Bad Requsets'
            resp.media = {"type": "error", "code":"MISSING_FIELDS","message": "登入格式錯誤"}
            return
            
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        
        try:
            player = db.players.insert_one({
                "username": username, 
                "password": hashed_pw,
                "balance": 2000.0,
                "created_at" :datetime.utcnow()
                })

            resp.status = '201 Created'
            resp.media = {"message": "註冊成功"}
        except DuplicateKeyError:
            resp.status = '409 Conflict'
            resp.media = {"type": "error", "code":"USERNAME_TAKEN","message": "註冊失敗，使用者名稱已被命名"}

class LoginResource:
    def on_post(self, req, resp):
        data = req.get_media()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            resp.status = '400 Bad Requsets'
            resp.media = {"type": "error", "code":"MISSING_FIELDS","message": "登入格式錯誤"}
            return
        player = db.players.find_one({"username": username})
        if player is None:
            resp.status = '404 Not Found'
            resp.media = {"type": "error", "code":"PLAYER_NOT_FOUND", "message": "使用者不存在"}
        else:
            if not bcrypt.checkpw(password.encode(), player["password"]):
                resp.status = '401 Unauthorized'
                resp.media = {"type": "error", "code":"WRONG_PASSWORD","message": "密碼錯誤"}
            else:
                resp.media = {"type": "success", "code":"LOGIN_SUCCESS","message": "登入成功"}
                