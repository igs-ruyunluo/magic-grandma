import random
from config import HOUSE_EDGE

def generate_crash_point(house_edge=HOUSE_EDGE):
    r = random.random()
    if r == 0:
        r = 0.0000001
    crash_point = (1.00 - house_edge) / r

    return max(crash_point, 1.00)


# for _ in range(100):
#     a = generate_crash_point()
#     print(a)