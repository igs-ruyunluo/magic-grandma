import gevent
import json
from game.crash import generate_crash_point
from game.multiplier import grow_multiplier
from config import TICK_INTERVAL
from game.room import player_bet, settle_win
from db.connection import db

def handle_game_round(ws):

    while True:        
        bet_msg = ws.receive()
        if bet_msg is None:
            return
        
        bet_data = json.loads(bet_msg)
        player_id = bet_data["player_id"]
        amount = bet_data["amount"]

       
        # 扣款
        if not player_bet(player_id, amount):
            ws.send(json.dumps({"type":"error", "message":"餘額不足"}))
            break
        
        player = db.players.find_one({"username":player_id})
        ws.send(json.dumps({"type": "game_start", "balance": player["balance"]}))
        
        crash_point = generate_crash_point()
        current_multi = 1.00
        cashed_out = [False]

        def listen_for_cashout():
            """另一條 greenlet，專門等玩家傳訊息"""
            while True:
                msg = ws.receive()  # 這裡會阻塞等玩家
                if msg == "cash_out":
                    cashed_out[0] = True
                    break
                if msg is None:  # 連線斷了
                    break

        # 啟動一條 greenlet 去監聽
        listener = gevent.spawn(listen_for_cashout) 
        
        while True:
            ws.send(json.dumps({"type":"tick", "multiplier":round(current_multi, 2)}))
            gevent.sleep(TICK_INTERVAL)
            
            if cashed_out[0]:
                settle_win(player_id, amount, current_multi)
                player = db.players.find_one({"username":player_id}) # 重新查餘額
                ws.send(json.dumps({
                    "type":"cash_out", 
                    "multiplier":round(current_multi, 2),
                    "balance":player["balance"]
                    }))
                break
            else:
                current_multi = grow_multiplier(current_multi)
                if current_multi >= crash_point:
                    ws.send(json.dumps({"type":"crash", "multiplier":round(current_multi, 2)}))
                    listener.kill()
                    break

