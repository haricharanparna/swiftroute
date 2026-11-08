# SwiftRoute: traffic-aware last-mile delivery planning

| File | What it does |
|---|---|
| `traffic.py` | Downloads real Chicago traffic history and works out how slow roads are at each hour |
| `geo.py` | Turns addresses into map points; measures distance between stops |
| `solver.py` | Plans the routes with OR-Tools (truck capacity + time slots) and runs the "nearest stop next" baseline for comparison |
| `plan.py` | Connects the pieces: traffic → travel times → both plans → numbers |
| `sample.py` | A repeatable demo day: 40 deliveries in Chicago |
| `scenarios.py` | "What if" tests: more trucks, worse traffic, double orders |
| `app.py` | The demo website |

## Run it
    pip install -r requirements.txt
    python traffic.py        # download real traffic data (needs internet, run once)
    python scenarios.py      # what-if table -> results/scenarios.csv
    streamlit run app.py     # opens the demo in your browser

Assumptions: city empty-road speed 40 km/h; real road distances from OSRM when online (straight line x 1.3 if offline);
$0.60/km, $25/hr driver, 0.25 kg CO2/km; 5 min per delivery.
