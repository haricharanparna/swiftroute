# Presentation script (≈ 6 minutes, 10 slides)

> Speak slowly. Numbers in **bold** are the ones to land. Demo is live; screenshots in `docs/` are the backup.

**Slide 1: Title** (15 s)
"Hi, we're [team]. This is **SwiftRoute**: delivery routes that keep working when real traffic hits."

**Slide 2: The problem** (40 s)
"Every day, small delivery fleets plan routes by hand, usually by driving to the nearest stop next. That ignores three things: how much each truck can carry, when each customer is home, and traffic that changes every hour. The result is late packages, overtime and wasted fuel. Last-mile delivery is the most expensive part of shipping."

**Slide 3: Our solution in one line** (20 s)
"SwiftRoute plans every truck's route around capacity, time slots and **real hourly traffic**, then **replays the whole day against real traffic** to prove the plan holds."

**Slide 4: Live demo, Live plan** (60 s)
- Show the hero card: "**$119 saved today, 31%**, and **22.5 points more deliveries on time** than the nearest-stop method."
- Point at the map: "These routes follow the real streets of Chicago."
- Chaos mode: turn on *A truck breaks down*, then *Urgent order*. "The plan re-optimizes in seconds."

**Slide 5: Live demo, Replay the day** (40 s), *the wow moment*
"Here's the whole Tuesday in 30 seconds. Every truck drives its real route at the speed April-2026 Chicago traffic allowed at that hour. Stops turn green when delivered."

**Slide 6: Live demo, Driver + accessibility** (40 s)
- Driver directions: turn-by-turn, one tap to Google Maps.
- Switch the language to Español: "Drivers and dispatchers work in English, Spanish or French."
- Toggle High contrast and Read aloud. "Accessible by design: voice input, read-aloud, high contrast, colour-blind-safe colours."

**Slide 7: The data** (40 s)
"**2.66 million speed readings** from **1,046 Chicago road segments**, April 2026, from the City of Chicago. We compare each segment with its own free-flow speed, so a highway and a side street are judged fairly. Roads and drive times come from OpenStreetMap." (Show the heatmap: the red block is the 3–6 pm rush.)

**Slide 8: How it works** (40 s)
Diagram: Addresses → OpenStreetMap → real drive times × hourly traffic → OR-Tools optimizer (capacity, time slots, cost) → hour-by-hour replay → KPIs, map, directions.
"Two uses of traffic. To plan, the optimizer uses the traffic at the hour we *expect* each drive to happen. Then we replay every route minute by minute with the traffic of the hour it *actually* happens. If that makes something late, the replay shows it, and all our numbers come from the replay. The benchmark is deliberately simple, nearest stop that fits, like hand-planning, not a second optimizer."

**Slide 9: Results & validation** (50 s)
- Scenario table: bigger trucks → **100% on time**. "The fleet is limited by truck size more than time: a decision a manager can act on."
- Delivered counts next to cost: "With 4 small trucks, 3 of 40 orders can't make their slot (the simple method misses 5). On-time % is out of all orders, so those count against us."
- Robustness: "We tested **10 different days**. SwiftRoute was cheaper and more on time on **all 10**. Average **33% cheaper, +23.8 points on time**, and it delivered at least as many orders every day, so the savings aren't from skipping work."
- Limitations: generated demo customers; one city-wide traffic factor per hour.

**Slide 10: Impact & next steps** (30 s)
"For one 4-truck depot that's about **$30,000 a year**, plus less CO₂. It's built entirely on free, open tools, so any small business can run it. Next: live traffic feeds, more cities, a driver phone app. Thank you!"

### Likely questions
- *Why not just Google Maps?* Google routes one vehicle. We split work across a fleet with capacity and time slots, then hand each driver's route to Google Maps.
- *How do you know it's better?* Same days, same traffic replay, two methods: 10/10 days cheaper and more on time.
- *Does it scale?* OR-Tools handles hundreds of stops; production would self-host OSRM.
- *Can we reproduce it?* Yes: `python validate.py` gives identical numbers on any computer (fixed solver budget, cached roads, committed traffic data). 10 automated tests check the solver.
- *Is it optimal?* OR-Tools' guided local search is a strong heuristic, not a proof of optimality; more search finds slightly better routes.
- *Isn't the baseline too weak?* It's meant to be: it's how small fleets plan by hand today. It respects capacity; we measure its lateness in the same replay. Beating hand-planning is the real-world bar.
- *Do you skip deliveries to look cheaper?* No: we deliver at least as many as the benchmark on all 10 days, and missed orders count against our on-time %.
- *Why more km sometimes?* Cost = fuel + driver time; a slightly longer route that avoids waiting and lateness is cheaper overall.
