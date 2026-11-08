"""Demo day: a depot + deliveries around Chicago (fixed random seed, so repeatable).
Time slots are real clock hours, e.g. (13, 16) = deliver between 1pm and 4pm."""
import random

DEPOT = ("Depot - 1200 W Fulton Market, Chicago", 41.8868, -87.6577)


def make(n=40, seed=7):
    rnd = random.Random(seed)
    stops = []
    for i in range(n):
        start = rnd.choice([9, 9, 10, 11, 12, 13])
        stops.append({"name": f"Customer {i+1}",
                      "lat": 41.88 + rnd.uniform(-0.09, 0.07),
                      "lon": -87.66 + rnd.uniform(-0.08, 0.05),
                      "demand": rnd.choice([1, 1, 2, 3]),
                      "slot": (start, min(start + rnd.choice([2, 3, 8]), 18))})
    return stops
