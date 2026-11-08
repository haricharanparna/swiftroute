"""Glue: stops + settings -> traffic-aware drive times -> smart plan + baseline -> hour-by-hour check -> KPIs.

How traffic is used
  * Planning: the drive time from stop A is the empty-road time / Chicago's speed factor at the hour
    the truck is expected to leave A (middle of A's time slot; shift start for the depot).
  * Checking: every route (SwiftRoute and the simple method alike) is replayed minute by minute,
    each leg slowed by the real speed factor of the hour it actually starts in. All KPIs come from
    this replay, so lateness caused by traffic shows up honestly.
"""
from geo import free_flow_matrices
from solver import solve, baseline, kpis, SERVICE_MIN
from traffic import speed_factor

SHIFT_HOURS = 8


def simulate(route, free, windows, factor_at, start_hour):
    """Replay a route with hour-by-hour traffic. route = [(node, planned_minute), ...]."""
    t = route[0][1]
    out = [(0, t)]
    for (a, _), (b, _) in zip(route, route[1:]):
        t += free[a][b] / factor_at(start_hour + t / 60)
        if b != 0:
            t = max(t, windows[b][0])   # early? wait for the time slot to open
        out.append((b, t))
        if b != 0:
            t += SERVICE_MIN
    return out


def run(depot, stops, n_trucks, capacity, profile, day, start_hour, traffic_worse=0.0, seconds=5, solutions=None, van_cost=0):
    end_hour = start_hour + SHIFT_HOURS
    outside = [s for s in stops if s["slot"][1] <= start_hour or s["slot"][0] >= end_hour]
    stops = [s for s in stops if s not in outside]

    factor_at = lambda clock_hour: speed_factor(profile, day, int(clock_hour)) * (1 - traffic_worse)
    shift_avg = sum(factor_at(start_hour + h) for h in range(SHIFT_HOURS)) / SHIFT_HOURS

    points = [(depot[1], depot[2])] + [(s["lat"], s["lon"]) for s in stops]
    dist, free, dist_source = free_flow_matrices(points)
    demands = [0] + [s["demand"] for s in stops]
    to_min = lambda h: int(min(max(h - start_hour, 0), SHIFT_HOURS) * 60)  # clock hour -> minutes into shift
    windows = [(0, SHIFT_HOURS * 60)] + [(to_min(s["slot"][0]), to_min(s["slot"][1])) for s in stops]

    # time-dependent planning matrix: leave stop A around the middle of its slot
    leave_hour = [start_hour] + [min(max((s["slot"][0] + s["slot"][1]) / 2, start_hour), end_hour - 1) for s in stops]
    mins = [[free[a][b] / factor_at(leave_hour[a]) for b in range(len(points))] for a in range(len(points))]

    smart = solve(dist, mins, demands, windows, n_trucks, capacity, seconds, solutions, van_cost)
    naive = baseline(dist, mins, demands, windows, n_trucks, capacity)
    smart = [simulate(r, free, windows, factor_at, start_hour) for r in smart]
    naive = [simulate(r, free, windows, factor_at, start_hour) for r in naive]

    served = {s for r in smart for s, _ in r[1:-1]}
    skipped = [stops[i - 1] for i in range(1, len(points)) if i not in served]
    total = len(stops) + len(outside)
    return {"factor": shift_avg, "points": points, "dist_source": dist_source, "stops": stops,
            "windows": windows, "smart": smart, "naive": naive, "skipped": skipped, "outside": outside,
            "smart_kpi": kpis(smart, dist, windows, total, van_cost=van_cost),
            "naive_kpi": kpis(naive, dist, windows, total, van_cost=van_cost)}
