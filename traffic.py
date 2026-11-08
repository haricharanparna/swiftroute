"""Traffic: how slow roads are at each hour of the day.

Real data: Chicago Traffic Tracker (City of Chicago open data), ~1,000 road
segments. We take the latest 8 weeks available and ask the city's server to average speed by
weekday + hour, so the download is tiny (168 rows).

speed_factor = speed at that hour / fastest hour  (1.0 = free-flowing, 0.6 = slow)
"""
import os
import pandas as pd
import requests

URL = "https://data.cityofchicago.org/resource/sxs8-h27x.json"
CACHE = os.path.join(os.path.dirname(__file__), "data", "traffic_profile.csv")

# Placeholder used only until real data is downloaded (rough typical US city weekday).
FALLBACK = [1.0, 1.0, 1.0, 1.0, 0.98, 0.93, 0.82, 0.70, 0.66, 0.76, 0.82, 0.80,
            0.78, 0.79, 0.77, 0.72, 0.65, 0.62, 0.70, 0.80, 0.87, 0.92, 0.96, 0.99]


def download_chicago(weeks=8):
    # Latest weeks only: keeps the city's server fast (the full history can time out).
    last = requests.get(URL, params={"$select": "max(time) as last"}, timeout=120).json()[0]["last"]
    since = (pd.Timestamp(last) - pd.Timedelta(days=7 * weeks)).strftime("%Y-%m-%dT00:00:00")
    print(f"Using Chicago traffic from {since[:10]} to {last[:10]}")
    params = {
        "$select": "day_of_week, hour, avg(speed) as avg_speed, count(*) as n",
        "$where": f"speed > 0 AND time > '{since}'",
        "$group": "day_of_week, hour",
        "$limit": 500,
    }
    rows = requests.get(URL, params=params, timeout=240).json()
    df = pd.DataFrame(rows).astype({"day_of_week": int, "hour": int, "avg_speed": float, "n": int})
    df["speed_factor"] = df["avg_speed"] / df["avg_speed"].max()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    df.sort_values(["day_of_week", "hour"]).to_csv(CACHE, index=False)
    return df


def load_profile():
    """Returns (DataFrame with day_of_week, hour, speed_factor), source label."""
    if os.path.exists(CACHE):
        return pd.read_csv(CACHE), "Chicago Traffic Tracker (real data)"
    try:
        return download_chicago(), "Chicago Traffic Tracker (real data)"
    except Exception:
        rows = [{"day_of_week": d, "hour": h, "speed_factor": FALLBACK[h]}
                for d in range(1, 8) for h in range(24)]
        return pd.DataFrame(rows), "PLACEHOLDER curve (no internet - run `python traffic.py`)"


def speed_factor(profile, day_of_week, hour):
    row = profile[(profile.day_of_week == day_of_week) & (profile.hour == int(hour) % 24)]
    return float(row.speed_factor.iloc[0]) if len(row) else 1.0


if __name__ == "__main__":
    df = download_chicago()
    print(df.pivot(index="hour", columns="day_of_week", values="speed_factor").round(2))
    print("saved to", CACHE)
