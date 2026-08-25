from game.crash import generate_crash_point
from game.multiplier import grow_multiplier
from db.connection import db

# fake_players = {
#     "player1": {"balance": 2000.0}
# }


def run_game_round():
    crash_point = generate_crash_point()
    current_multi = 1.00
    count = 0

    while current_multi < crash_point:
        current_multi = grow_multiplier(current_multi)
        count +=1

    return crash_point, current_multi, count


def player_bet(player_id, amount):
    player = db.players.find_one({"username":player_id})
    if player is None:
        return False
    if player["balance"] < amount:
        return False
    
    db.players.update_one({"username":player_id},
                     {"$inc":{"balance":-amount}})
    return True

def settle_win(player_id, amount, multiplier):
    player = db.players.find_one({"username":player_id})
    if player is None:
        return False
    db.players.update_one({"username":player_id},
                     {"$inc":{"balance":+amount * multiplier}})
   