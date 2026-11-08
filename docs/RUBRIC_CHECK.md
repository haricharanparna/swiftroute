# Rubric & jury cross-check

Problem statement: **Last-Mile Delivery Route Optimization** (Operations Research). *"Optimize last-mile delivery routes under capacity, time-window and traffic constraints to reduce cost and improve service."*

## Required deliverables

| Required | Where | Status |
|---|---|---|
| Routing optimization engine | `solver.py` (OR-Tools VRP), `plan.py` | ✅ |
| Capacity constraint | truck capacity dimension | ✅ |
| Time-window constraint | customer slots, Time dimension | ✅ |
| Traffic constraint | real Chicago 2026 hourly traffic, time-dependent legs + hour-by-hour replay | ✅ |
| Visualization of routes | Live plan map, Replay animation, Driver directions | ✅ |
| KPIs | cost, on-time %, km, driver hours, CO₂, delivered | ✅ |
| Code | GitHub repo | ✅ |
| Documentation | README, How it works tab (EN/ES/FR), this file | ✅ |
| Scenario analysis | What if? tab, `scenarios.py` → `results/scenarios.csv` | ✅ |
| Presentation | `docs/PITCH_SCRIPT.md` (slide-by-slide) | ✅ script; slides to build |
| Working demo link | deploy on share.streamlit.io | ⬜ one click (see README) |

## Judging criteria → evidence

| Criterion | Weight | Our strongest evidence |
|---|---|---|
| Innovation & Originality | 20% | Real-traffic **replay** of every route ("honest check") instead of trusting the plan; animated day replay; chaos mode; voice + location input; 3 languages |
| Technical Implementation | 25% | OR-Tools VRP with capacity + time windows + cost objective; time-dependent drive times; OSRM real roads + turn-by-turn; 2.66 M-reading data pipeline; bundled deck.gl animation |
| Problem Relevance | 15% | Exactly the stated problem; all three constraints (capacity, time windows, traffic) handled |
| Data & Analytical Rigor | 15% | Real public data (City of Chicago, OpenStreetMap); per-segment free-flow normalisation; baseline comparison; 6 scenarios; **10-day robustness test: cheaper 10/10 days, mean −30.4%, +23.5 pts on time** |
| Impact & Feasibility | 15% | Free/open stack, runs on a laptop; Google Maps hand-off for drivers; ~$119/day saved for a 4-truck depot (≈ $30k/year at 250 days) |
| Presentation & Documentation | 10% | Polished UI, accessibility, README, rubric map, script + video plan |

## What each jury member will look for

| Who | Background | Show them |
|---|---|---|
| Somnath Banerjee | MDM/CDP architect | Data sources & lineage: Traffic data tab (2.66 M readings, 1,046 segments, dates), per-segment normalisation, honest replay |
| Naveen Kumar Bonagiri | Engineering project manager | Clean modules, README run steps, limitations section, robustness test |
| Rishabh N Dave | Head of Product, BuildOps (field-service ops) | Dispatcher UX: chaos mode, driver directions, Google Maps hand-off, read-aloud, languages |
| Gaurav Vashisht | Finance/Legal/HR systems | Cost model & assumptions, $ saved, cost per scenario, CSV exports |
| Session chairs: Xiaochao Pu, Mogana Kumaran Sivaraman | Tech strategy; data engineering at Gap | Data pipeline (`traffic.py`), retail delivery relevance, scale-up path |
| Judges: Adarsh Naidu (AWS), Dhamotharan Seenivasan, Sai Shuas Bobba, Eshaan Jain | Architecture, delivery, product | Architecture slide, scaling (self-hosted OSRM, more cities), 10-day validation |

## Honest limitations (say them before they're asked)
- Customers in the demo are generated (fixed seeds), not real orders.
- Traffic is one city-wide factor per hour (arterial streets, bus-GPS estimates), not per street.
- SwiftRoute sometimes drives more km than the simple method: it trades a little distance for fewer driver hours and fewer late deliveries (cost and on-time still win 10/10 days).
- Free public OSRM / Nominatim servers: fine for a demo; production would self-host them.
