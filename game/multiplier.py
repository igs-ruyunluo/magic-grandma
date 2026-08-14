from config import GROWTH_RATE

def grow_multiplier(current_multi, growth_rate=GROWTH_RATE):
    new_multi = current_multi * growth_rate
    return new_multi

