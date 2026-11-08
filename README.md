# 🚚 SwiftRoute: delivery routes that survive real traffic

**DataNova 2026 · Operations Research track · Last-Mile Delivery Route Optimization**

SwiftRoute plans every delivery truck's route around **truck capacity**, **customer time slots** and
**real hourly traffic**, then **replays the whole day against real traffic** to prove the plan holds.

![Live plan](docs/preview_plan.png)

## Features
- 🗺️ **Live plan:** optimized routes on real Chicago streets, cost / on-time / km / driver-hours / CO₂ vs. the simple method
- ▶️ **Replay the day:** animated map, every truck driving its real route at real traffic speed, stops turning green
- 🧭 **Driver directions:** turn-by-turn steps + one tap to **Google Maps**
- 🔥 **Chaos mode:** traffic jam, truck breakdown, urgent order, re-planned in seconds
- 🔮 **What if?:** 6 scenarios (more trucks, bigger trucks, worse traffic, double orders)
- 🎙️📍 **Voice typing & my location** for addresses
- ♿ **Accessibility:** larger text, high contrast, colour-blind-safe colours, reduce motion, read-aloud, keyboard focus, screen-reader map text
- 🌐 **English · Español · Français**

| Replay the day | Driver directions | Español + high contrast |
|---|---|---|
| ![](docs/preview_replay.png) | ![](docs/preview_driver.png) | ![](docs/preview_spanish_contrast.png) |

## Results (real roads + April 2026 Chicago traffic)

**Robustness, 10 different random days** (40 deliveries, 4 trucks × 15 packages, `validate.py`):
SwiftRoute was **cheaper on 10/10 days** and **more on time on 10/10 days**:
mean **−30.4% cost** (range −7.5% to −49.8%) and **+23.5 points on time** (+12.5 to +32.5).

**Scenario analysis** (sample day, `scenarios.py`):

| Scenario | SwiftRoute on time | Simple on time | SwiftRoute cost | Simple cost |
|---|---|---|---|---|
| Normal day (4 trucks × 15) | **90.0%** | 67.5% | **$270** | $389 |
| +1 truck | **97.5%** | 75.0% | **$299** | $439 |
| Traffic 30% worse | **92.5%** | 65.0% | **$319** | $433 |
| Bigger trucks (25 packages) | **100%** | 70.0% | **$274** | $435 |
| Orders double (80 stops) | 53.8% | 40.0% | $258 | $409 |
| Orders double + 4 trucks | **93.8%** | 62.5% | **$501** | $770 |

"Simple" = go to the nearest unvisited stop next. Insight: the fleet is limited by **truck size**
more than time, so bigger trucks reach 100% on time at almost the same cost.

## How it works
1. **Addresses → map points:** OpenStreetMap Nominatim (typed, spoken, or your location).
2. **Real roads:** distance + empty-road drive time for every pair of stops (OSRM / OpenStreetMap).
3. **Real traffic:** City of Chicago *Traffic Tracker* (`4g9f-3jbs`), **2.66 M speed readings, 1,046 road
   segments, Apr 2–30 2026**. Each segment vs. its own free-flow speed (90th pct.) → slowdown per hour of the week.
4. **Optimizer:** Google OR-Tools VRP with capacity + time windows, minimizing fuel + driver cost;
   each leg slowed by the traffic of the hour it's expected to happen in.
5. **Honest check:** every route (ours and the baseline's) is **replayed hour by hour** with real
   traffic. All numbers come from the replay.

| File | Purpose |
|---|---|
| `app.py` | Streamlit app (6 tabs) |
| `traffic.py` | Downloads Chicago traffic → hourly slowdown profile |
| `geo.py` | Geocoding, road tables, turn-by-turn routes |
| `solver.py` | OR-Tools optimizer, nearest-stop baseline, KPIs |
| `plan.py` | Pipeline + hour-by-hour traffic replay |
| `replay.py` | Animated "Replay the day" map (deck.gl, bundled in `static/`) |
| `i18n.py` | English / Spanish / French text |
| `scenarios.py`, `validate.py` | Scenario analysis and 10-day robustness test → `results/` |
| `docs/` | Rubric check, pitch script, video plan, screenshots |

Assumptions: 5 min per delivery · $0.60/km · $25/h per driver · 0.25 kg CO₂/km · 8-hour shift.

## Run it
```bash
git clone https://github.com/haricharanparna/swiftroute
cd swiftroute
pip install -r requirements.txt
streamlit run app.py
```
Windows: `py -3.13 -m pip install -r requirements.txt` then `py -3.13 -m streamlit run app.py`.
Voice typing works best in Chrome or Edge; allow the microphone / location when asked.

**Free online demo:** share.streamlit.io → sign in with GitHub → *Create app* → this repo, branch `main`, file `app.py` → *Deploy*.

## Limitations
- Demo customers are generated (fixed seeds), not real orders.
- Traffic is one city-wide factor per hour from arterial streets (bus-GPS estimates), not per street.
- SwiftRoute sometimes drives more km: it trades distance for fewer driver hours and late deliveries.
- Uses free public OSRM / Nominatim / Google speech servers, fine for demos; production would self-host.

See [docs/RUBRIC_CHECK.md](docs/RUBRIC_CHECK.md) · [docs/PITCH_SCRIPT.md](docs/PITCH_SCRIPT.md) · [docs/VIDEO_PLAN.md](docs/VIDEO_PLAN.md)
