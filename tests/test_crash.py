import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from game.room import run_game_round

for _ in range(20):
    crash_point, final_multi, count = run_game_round()
    print(f"崩潰點: {crash_point:.2f}x, 實際停在: {final_multi:.2f}x, 跑了幾次: {count}")