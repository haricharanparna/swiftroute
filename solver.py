"""Route planning.

solve()    -> smart plan with Google OR-Tools (respects truck capacity + time slots)
baseline() -> "go to the nearest stop next", what many small businesses do
Times are minutes after the shift starts. Stop 0 is the depot.
"""
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

SERVICE_MIN = 5  # minutes to hand over a package
CENTS_PER_KM = 60          # $0.60 per km (fuel + wear)
CENTS_PER_DRIVER_MIN = 42  # $25 per hour


def solve(dist, mins, demands, windows, n_trucks, capacity, seconds=5):
    n = len(dist)
    mgr = pywrapcp.RoutingIndexManager(n, n_trucks, 0)
    model = pywrapcp.RoutingModel(mgr)

    # Goal = lowest real cost (in cents): fuel per km + driver pay per minute on the road.
    def km_cost(i, j):
        return int(dist[mgr.IndexToNode(i)][mgr.IndexToNode(j)] * CENTS_PER_KM)
    model.SetArcCostEvaluatorOfAllVehicles(model.RegisterTransitCallback(km_cost))

    def minutes(i, j):
        a, b = mgr.IndexToNode(i), mgr.IndexToNode(j)
        return int(round(mins[a][b])) + (SERVICE_MIN if a else 0)
    t = model.RegisterTransitCallback(minutes)
    horizon = max(w[1] for w in windows)
    model.AddDimension(t, 60, horizon, False, "Time")  # up to 60 min waiting allowed
    time_dim = model.GetDimensionOrDie("Time")
    time_dim.SetSpanCostCoefficientForAllVehicles(CENTS_PER_DRIVER_MIN)  # pay drivers from leaving to returning
    for v in range(n_trucks):  # trucks may leave the depot later instead of waiting at a customer
        model.AddVariableMinimizedByFinalizer(time_dim.CumulVar(model.End(v)))
        model.AddVariableMaximizedByFinalizer(time_dim.CumulVar(model.Start(v)))
    for node in range(1, n):
        time_dim.CumulVar(mgr.NodeToIndex(node)).SetRange(*windows[node])

    load = model.RegisterUnaryTransitCallback(lambda i: demands[mgr.IndexToNode(i)])
    model.AddDimensionWithVehicleCapacity(load, 0, [capacity] * n_trucks, True, "Load")

    for node in range(1, n):  # a stop may be skipped, but at a big penalty
        model.AddDisjunction([mgr.NodeToIndex(node)], 1_000_000)

    p = pywrapcp.DefaultRoutingSearchParameters()
    p.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    p.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    p.time_limit.seconds = seconds
    sol = model.SolveWithParameters(p)

    routes = []
    for v in range(n_trucks):
        i, stops = model.Start(v), []
        while not model.IsEnd(i):
            stops.append((mgr.IndexToNode(i), sol.Value(time_dim.CumulVar(i))))
            i = sol.Value(model.NextVar(i))
        stops.append((0, sol.Value(time_dim.CumulVar(i))))
        if len(stops) > 2:
            routes.append(stops)
    return routes


def baseline(dist, mins, demands, windows, n_trucks, capacity):
    left, routes = set(range(1, len(dist))), []
    for _ in range(n_trucks):
        here, clock, room, stops = 0, 0, capacity, [(0, 0)]
        while True:
            fits = [s for s in left if demands[s] <= room]
            if not fits:
                break
            nxt = min(fits, key=lambda s: dist[here][s])
            clock = max(clock + mins[here][nxt], windows[nxt][0])  # wait if early
            stops.append((nxt, clock))
            room -= demands[nxt]; left.discard(nxt); here = nxt
            clock += SERVICE_MIN
        stops.append((0, clock + mins[here][0]))
        if len(stops) > 2:  # leave the depot late enough to not wait at the first stop
            first, arrive = stops[1]
            stops[0] = (0, max(0, arrive - mins[0][first]))
            routes.append(stops)
    return routes


def kpis(routes, dist, windows, n_stops, cost_per_km=0.6, driver_per_hr=25, co2_per_km=0.25):
    """Assumptions: $0.60/km fuel+wear, $25/hr driver, 0.25 kg CO2/km (delivery van)."""
    km = sum(dist[a][b] for r in routes for (a, _), (b, _) in zip(r, r[1:]))
    hours = sum(r[-1][1] - r[0][1] for r in routes) / 60
    served = [(s, t) for r in routes for s, t in r[1:-1]]
    on_time = sum(1 for s, t in served if t <= windows[s][1])
    return {
        "Trucks used": len(routes),
        "Total km": round(km, 1),
        "Driver hours": round(hours, 1),
        "Cost ($)": round(km * cost_per_km + hours * driver_per_hr),
        "CO2 (kg)": round(km * co2_per_km, 1),
        "Delivered": f"{len(served)}/{n_stops}",
        "On time %": round(100 * on_time / n_stops, 1),
    }
