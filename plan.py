"""Glue: stops + settings -> traffic-aware matrices -> smart plan + baseline + KPIs."""
from geo import matrices
from solver import solve, baseline, kpis
from traffic import speed_factor

FREE_FLOW_KMH = 40  # city driving speed when roads are empty
SHIFT_HOURS = 8


def run(depot, stops, n_trucks, capacity, profile, day, start_hour, traffic_worse=0.0, seconds=5):
    # Stops whose time slot doesn't overlap the shift can't be delivered at all.
    end_hour = start_hour + SHIFT_HOURS
    outside = [s for s in stops if s["slot"][1] <= start_hour or s["slot"][0] >= end_hour]
    stops = [s for s in stops if s not in outside]

    # Average traffic over the hours the trucks are on the road.
    hours = [start_hour + h for h in range(SHIFT_HOURS)]
    factor = sum(speed_factor(profile, day, h) for h in hours) / len(hours) * (1 - traffic_worse)

    points = [(depot[1], depot[2])] + [(s["lat"], s["lon"]) for s in stops]
    dist, mins, dist_source = matrices(points, FREE_FLOW_KMH, factor)
    demands = [0] + [s["demand"] for s in stops]
    to_min = lambda h: int(min(max(h - start_hour, 0), SHIFT_HOURS) * 60)  # clock hour -> minutes into shift
    windows = [(0, SHIFT_HOURS * 60)] + [(to_min(s["slot"][0]), to_min(s["slot"][1])) for s in stops]

    smart = solve(dist, mins, demands, windows, n_trucks, capacity, seconds)
    naive = baseline(dist, mins, demands, windows, n_trucks, capacity)
    served = {s for r in smart for s, _ in r[1:-1]}
    skipped = [stops[i - 1] for i in range(1, len(points)) if i not in served]
    total = len(stops) + len(outside)
    return {"factor": factor, "points": points, "dist_source": dist_source, "stops": stops,
            "smart": smart, "naive": naive, "skipped": skipped, "outside": outside,
            "smart_kpi": kpis(smart, dist, windows, total),
            "naive_kpi": kpis(naive, dist, windows, total)}
