"""Addresses -> map points, and distance/time between points."""
import hashlib
import json
import math
import os
import time
import requests

def geocode(address):
    """Free OpenStreetMap lookup. Returns (lat, lon) or None."""
    r = requests.get("https://nominatim.openstreetmap.org/search",
                     params={"q": address, "format": "json", "limit": 1, "countrycodes": "us"},
                     headers={"User-Agent": "SwiftRoute-hackathon-demo"}, timeout=20)
    time.sleep(1)  # Nominatim rule: max 1 request per second
    hits = r.json()
    return (float(hits[0]["lat"]), float(hits[0]["lon"])) if hits else None


def km_between(a, b):
    """Straight-line km x 1.3 (roads are ~30% longer than a straight line in cities)."""
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h)) * 1.3


CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "road_cache")


def road_table(points):
    """Real road distance (km) and empty-road drive time (min) between every pair of stops,
    from the free OSRM server on OpenStreetMap roads (knows highways are faster than side streets).
    Saved in data/road_cache/ so experiments re-run on exactly the same road data.
    Returns (km, minutes) or None if offline."""
    coords = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)
    path = os.path.join(CACHE_DIR, hashlib.sha1(coords.encode()).hexdigest()[:16] + ".json")
    if os.path.exists(path):
        with open(path) as f:
            d = json.load(f)
        return d["km"], d["min"]
    try:
        r = requests.get(f"https://router.project-osrm.org/table/v1/driving/{coords}",
                         params={"annotations": "distance,duration"}, timeout=60).json()
        km = [[d / 1000 for d in row] for row in r["distances"]]
        mins = [[s / 60 for s in row] for row in r["durations"]]
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(path, "w") as f:
                json.dump({"coords": coords, "km": km, "min": mins}, f)
        except OSError:
            pass
        return km, mins
    except Exception:
        return None


def free_flow_matrices(points, fallback_kmh=40):
    """Distance (km) and empty-road drive time (minutes) between every pair of points.
    Real roads when online; otherwise straight line x 1.3 at a flat city speed."""
    table = road_table(points)
    if table:
        return table[0], table[1], "real roads + drive times (OpenStreetMap)"
    km = [[km_between(a, b) for b in points] for a in points]
    mins = [[d / fallback_kmh * 60 for d in row] for row in km]
    return km, mins, "estimated distances (straight line x 1.3, offline)"


def road_path(points):
    """The actual street-by-street line through these stops (OSRM). [[lon, lat], ...] or None if offline."""
    coords = ";".join(f"{lon},{lat}" for lat, lon in points)
    try:
        r = requests.get(f"https://router.project-osrm.org/route/v1/driving/{coords}",
                         params={"overview": "full", "geometries": "geojson"}, timeout=30).json()
        return r["routes"][0]["geometry"]["coordinates"]
    except Exception:
        return None


def route_detail(points):
    """Street-level route through the stops, with turn-by-turn steps (OSRM).
    Returns {"legs": [{"coords": [[lon, lat], ...], "steps": [...]}, ...]} or None if offline.
    Leg i goes from points[i] to points[i+1]."""
    coords = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)
    try:
        r = requests.get(f"https://router.project-osrm.org/route/v1/driving/{coords}",
                         params={"overview": "false", "steps": "true", "geometries": "geojson"},
                         timeout=60).json()
        legs = []
        for leg in r["routes"][0]["legs"]:
            line, steps = [], []
            for s in leg["steps"]:
                g = s["geometry"]["coordinates"]
                line += g if not line else g[1:]
                m = s["maneuver"]
                steps.append({"type": m["type"], "modifier": m.get("modifier", ""), "name": s.get("name", ""),
                              "km": s["distance"] / 1000, "exit": m.get("exit")})
            legs.append({"coords": line, "steps": steps})
        return {"legs": legs}
    except Exception:
        return None


def reverse(lat, lon):
    """Map point -> street address (OpenStreetMap). Returns a string or None."""
    try:
        r = requests.get("https://nominatim.openstreetmap.org/reverse",
                         params={"lat": lat, "lon": lon, "format": "json", "zoom": 18},
                         headers={"User-Agent": "SwiftRoute-hackathon-demo"}, timeout=20).json()
        return r.get("display_name")
    except Exception:
        return None
