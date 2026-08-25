import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from game.room import run_game_round

round = 100000
target = 2
total_return = 0

for _ in range(round):
    crash_point, current_multi, count = run_game_round()
    if crash_point >= target:
        total_return += target

    rtp = total_return / round
    
    print(f"RTP = {rtp:.4f} ({rtp*100:.2f}%)")