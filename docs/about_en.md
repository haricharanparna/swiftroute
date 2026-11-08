#### How it works
1. **Addresses → map points** with OpenStreetMap — type them, speak them 🎙️, or use your location 📍.
2. **Real roads:** distance and empty-road drive time between every pair of stops (OSRM on OpenStreetMap).
3. **Real traffic:** 2.66 million speed readings from 1,046 Chicago road segments (City of Chicago Traffic Tracker, April 2026). Each segment is compared with its own free-flow speed, giving a slowdown for every hour of the week.
4. **Optimizer:** Google OR-Tools vehicle routing with truck capacity and customer time slots, minimizing real cost (fuel + driver pay). Each drive is slowed by the traffic of the hour it happens in.
5. **Honest check:** every route — ours and the simple method's — is replayed hour by hour with real traffic. All numbers come from that replay.
6. **Benchmark:** the same day planned with "go to the nearest stop next", how many small fleets work by hand.

#### Assumptions
5 min per delivery · $0.60/km · $25/hour per driver · 0.25 kg CO₂/km · 8-hour shift.

#### Accessibility
Keyboard focus outlines · screen-reader map descriptions · larger text · high contrast · colour-blind-safe (Okabe-Ito) colours · reduce motion · read-aloud summary · English, Spanish, French.
