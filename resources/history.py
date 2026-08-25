from db.connection import db

class LeaderboardResources:
    def on_get(self, req, resp):
        results = list(db.bet_records.aggregate([
            {"$group":{
                "_id":"$username",
                "total_bet":{"$sum":"$bet_amount"},
                "total_profit":{"$sum":"$profit"},
                "total_win":{"$sum":{"$cond": [{"$gt": ["$profit", 0]}, {"$add": ["$profit", "$bet_amount"]}, 0]}}
            }}, # 按 userna"me 分組，把每一個人的 profit 作加總
            {"$addFields": {"rtp": {"$cond": [{"$gt": ["$total_bet", 0]}, {"$divide": ["$total_win", "$total_bet"]}, 0]}}},
            {"$sort":{"total_profit":-1}}, # 從大排到小
            {"$limit":10} # 取前十個
        ]))

        resp.media = {"leaderboard":results}