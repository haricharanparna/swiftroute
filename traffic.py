"""Traffic: how slow roads are at each hour of the week.

Source: Chicago Traffic Tracker - Historical Congestion Estimates by Segment, 2024-2026
(City of Chicago open data, dataset 4g9f-3jbs). ~1,000 arterial road segments, a speed
reading roughly every 10 minutes, estimated from GPS on CTA buses.

Method (per road segment, so busy and quiet roads are compared fairly):
  1. average speed for every (segment, weekday, hour)
  2. that segment's "free-flow" speed = its 90th-percentile hourly speed over the period
  3. speed factor = hourly speed / free-flow speed   (1.0 = flowing freely, 0.8 = 20% slower)
  4. average the factor over all segments  ->  one number per weekday + hour (168 rows)

Run once to download:  python traffic.py
"""
import io
import json
import os

import pandas as pd
import requests

DATASET = "https://data.cityofchicago.org/resource/4g9f-3jbs"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "data", "traffic_profile.csv")
META = os.path.join(HERE, "data", "traffic_meta.json")
WEEKS = 4

# Placeholder used only if the real data can't be downloaded (rough typical US city weekday).
FALLBACK = [1.0, 1.0, 1.0, 1.0, 0.98, 0.93, 0.82, 0.70, 0.66, 0.76, 0.82, 0.80,
            0.78, 0.79, 0.77, 0.72, 0.65, 0.62, 0.70, 0.80, 0.87, 0.92, 0.96, 0.99]


def _week(start, end):
    """Raw speed readings for one week, only the columns we need (CSV keeps it small and fast)."""
    params = {"$select": "segment_id, day_of_week, hour, speed",
              "$where": f"speed > 0 AND time between '{start:%Y-%m-%dT%H:%M:%S}' and '{end:%Y-%m-%dT%H:%M:%S}'",
              "$limit": 3_000_000}
    r = requests.get(f"{DATASET}.csv", params=params, timeout=240)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))


def build_profile(raw):
    hourly = raw.groupby(["segment_id", "day_of_week", "hour"], as_index=False)["speed"].mean()
    free_flow = hourly.groupby("segment_id")["speed"].quantile(0.9).rename("free_flow")
    hourly = hourly.join(free_flow, on="segment_id")
    hourly["factor"] = (hourly["speed"] / hourly["free_flow"]).clip(upper=1.0)
    prof = (hourly.groupby(["day_of_week", "hour"])
            .agg(speed_factor=("factor", "mean"), segments=("segment_id", "nunique"), avg_mph=("speed", "mean"))
            .reset_index())
    return prof


def download_chicago(weeks=WEEKS):
    last = requests.get(f"{DATASET}.json", params={"$select": "max(time) as last"}, timeout=120).json()[0]["last"]
    end = pd.Timestamp(last).floor("D")
    parts = []
    for w in range(weeks):
        s, e = end - pd.Timedelta(days=7 * (w + 1)), end - pd.Timedelta(days=7 * w)
        print(f"  downloading {s:%Y-%m-%d} to {e:%Y-%m-%d} ...", flush=True)
        parts.append(_week(s, e))
    raw = pd.concat(parts, ignore_index=True)
    prof = build_profile(raw)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    prof.to_csv(CACHE, index=False)
    meta = {"source": "Chicago Traffic Tracker (City of Chicago), dataset 4g9f-3jbs",
            "from": f"{end - pd.Timedelta(days=7 * weeks):%Y-%m-%d}", "to": f"{end:%Y-%m-%d}",
            "readings": int(len(raw)), "segments": int(raw.segment_id.nunique())}
    json.dump(meta, open(META, "w"), indent=2)
    return prof, meta


def load_profile():
    """Returns (DataFrame[day_of_week, hour, speed_factor], label, meta dict)."""
    if not os.path.exists(CACHE):
        try:
            download_chicago()
        except Exception:
            rows = [{"day_of_week": d, "hour": h, "speed_factor": FALLBACK[h]}
                    for d in range(1, 8) for h in range(24)]
            return pd.DataFrame(rows), "PLACEHOLDER traffic (run `python traffic.py`)", {}
    meta = json.load(open(META)) if os.path.exists(META) else {}
    label = "Chicago Traffic Tracker (real data)"
    if meta:
        label += f", {meta['from']} to {meta['to']}"
    return pd.read_csv(CACHE), label, meta


def speed_factor(profile, day_of_week, hour):
    row = profile[(profile.day_of_week == day_of_week) & (profile.hour == int(hour) % 24)]
    return float(row.speed_factor.iloc[0]) if len(row) else 1.0


if __name__ == "__main__":
    prof, meta = download_chicago()
    print(json.dumps(meta, indent=2))
    print(prof.pivot(index="hour", columns="day_of_week", values="speed_factor").round(2))
    print("saved to", CACHE)
