"""Correctness tests for the optimizer, the benchmark and the traffic replay.
Run:  python -m pytest tests -q        (offline: uses straight-line distances)"""
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import geo  # noqa: E402
import plan  # noqa: E402
import solver  # noqa: E402
from solver import SERVICE_MIN, baseline, kpis, solve  # noqa: E402


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(geo, "road_table", lambda points: None)   # no network: straight-line roads


def instance(n=25, seed=3, slot_hours=(2, 8)):
    rnd = random.Random(seed)
    pts = [(41.8868, -87.6577)] + [(41.88 + rnd.uniform(-0.08, 0.06), -87.66 + rnd.uniform(-0.07, 0.05)) for _ in range(n)]
    dist = [[geo.km_between(a, b) for b in pts] for a in pts]
    mins = [[d / 40 * 60 for d in row] for row in dist]
    demands = [0] + [rnd.choice([1, 2, 3]) for _ in range(n)]
    windows = [(0, 480)]
    for _ in range(n):
        s = rnd.choice([0, 60, 120, 180])
        windows.append((s, min(480, s + 60 * rnd.choice(slot_hours))))
    return dist, mins, demands, windows


def served(routes):
    return [s for r in routes for s, _ in r[1:-1]]


def test_each_stop_at_most_once_and_routes_start_end_at_depot():
    dist, mins, dem, win = instance()
    routes = solve(dist, mins, dem, win, 4, 15, solutions=300)
    s = served(routes)
    assert len(s) == len(set(s))
    assert all(r[0][0] == 0 and r[-1][0] == 0 for r in routes)


def test_capacity_never_exceeded():
    dist, mins, dem, win = instance()
    for cap in (6, 10, 15):
        for r in solve(dist, mins, dem, win, 3, cap, solutions=300):
            assert sum(dem[s] for s, _ in r[1:-1]) <= cap


def test_planned_arrivals_inside_time_windows():
    dist, mins, dem, win = instance()
    for r in solve(dist, mins, dem, win, 4, 15, solutions=300):
        for s, t in r[1:-1]:
            assert win[s][0] <= t <= win[s][1]


def test_order_bigger_than_any_truck_is_left_unassigned_not_crash():
    dist, mins, dem, win = instance(n=5)
    dem[2] = 99
    routes = solve(dist, mins, dem, win, 2, 15, solutions=200)
    assert 2 not in served(routes)
    assert set(served(routes)) == {1, 3, 4, 5}


def test_no_trucks_enough_means_partial_plan_with_unassigned_counted():
    dist, mins, dem, win = instance(n=30)
    routes = solve(dist, mins, dem, win, 1, 10, solutions=200)
    k = kpis(routes, dist, win, 30)
    assert int(k["Delivered"].split("/")[0]) == len(served(routes)) < 30
    assert k["On time %"] <= 100 * len(served(routes)) / 30      # unassigned count against on-time %


def test_no_solution_returns_empty_plan(monkeypatch):
    monkeypatch.setattr(solver.pywrapcp.RoutingModel, "SolveWithParameters", lambda self, p: None)
    dist, mins, dem, win = instance(n=5)
    assert solve(dist, mins, dem, win, 2, 15, solutions=10) == []
    k = kpis([], dist, win, 5)
    assert k["Delivered"] == "0/5" and k["Cost ($)"] == 0


def test_deterministic_with_fixed_search_budget():
    dist, mins, dem, win = instance()
    a = solve(dist, mins, dem, win, 4, 15, solutions=300)
    b = solve(dist, mins, dem, win, 4, 15, solutions=300)
    assert a == b


def test_baseline_respects_capacity_and_visits_each_stop_once():
    dist, mins, dem, win = instance()
    routes = baseline(dist, mins, dem, win, 4, 15)
    s = served(routes)
    assert len(s) == len(set(s))
    for r in routes:
        assert sum(dem[x] for x, _ in r[1:-1]) <= 15


def test_replay_reveals_lateness_when_traffic_is_slower_than_planned():
    route = [(0, 0), (1, 10), (0, 30)]
    free = [[0, 10], [10, 0]]
    windows = [(0, 480), (0, 12)]
    fast = plan.simulate(route, free, windows, lambda h: 1.0, 9)
    slow = plan.simulate(route, free, windows, lambda h: 0.5, 9)
    assert fast[1][1] == 10 and fast[1][1] <= windows[1][1]
    assert slow[1][1] == 20 and slow[1][1] > windows[1][1]          # late, and the KPIs will say so
    assert slow[2][1] == 20 + SERVICE_MIN + 20


def test_run_reports_stops_outside_the_shift_as_undelivered():
    prof = __import__("pandas").DataFrame([{"day_of_week": 3, "hour": h, "speed_factor": 0.9} for h in range(24)])
    stops = [{"name": "early", "lat": 41.9, "lon": -87.62, "demand": 1, "slot": (5, 7)},
             {"name": "ok", "lat": 41.89, "lon": -87.63, "demand": 1, "slot": (9, 17)}]
    r = plan.run(("Depot", 41.8868, -87.6577), stops, 1, 15, prof, 3, 9, solutions=50)
    assert [s["name"] for s in r["outside"]] == ["early"]
    assert r["smart_kpi"]["Delivered"] == "1/2"


def test_van_cost_never_uses_more_vans_and_is_charged():
    dist, mins, dem, win = instance(n=12, slot_hours=(8,))
    free = solve(dist, mins, dem, win, 4, 30, solutions=300, van_cost=0)
    paid = solve(dist, mins, dem, win, 4, 30, solutions=300, van_cost=200)
    assert len(paid) <= len(free) and len(paid) >= 1
    assert sorted(served(paid)) == sorted(served(free))        # still delivers the same orders
    k0, k1 = kpis(paid, dist, win, 12), kpis(paid, dist, win, 12, van_cost=200)
    assert k1["Cost ($)"] - k0["Cost ($)"] == 200 * len(paid)
