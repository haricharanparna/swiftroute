"""Addresses -> map points, and distance/time between points."""
import math
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


def road_km(points):
    """Real road distances from the free OSRM server (OpenStreetMap roads). None if offline."""
    coords = ";".join(f"{lon},{lat}" for lat, lon in points)
    try:
        r = requests.get(f"https://router.project-osrm.org/table/v1/driving/{coords}",
                         params={"annotations": "distance"}, timeout=30).json()
        return [[d / 1000 for d in row] for row in r["distances"]]
    except Exception:
        return None


def matrices(points, free_flow_kmh, factor):
    """Distance (km) and drive time (minutes) between every pair of points.
    Uses real road distances when online, otherwise straight line x 1.3."""
    dist = road_km(points)
    source = "real road distances (OpenStreetMap)"
    if dist is None:
        dist = [[km_between(a, b) for b in points] for a in points]
        source = "estimated distances (straight line x 1.3, offline)"
    mins = [[d / (free_flow_kmh * factor) * 60 for d in row] for row in dist]
    return dist, mins, source


def road_path(points):
    """The actual street-by-street line through these stops (OSRM). [[lon, lat], ...] or None if offline."""
    coords = ";".join(f"{lon},{lat}" for lat, lon in points)
    try:
        r = requests.get(f"https://router.project-osrm.org/route/v1/driving/{coords}",
                         params={"overview": "full", "geometries": "geojson"}, timeout=30).json()
        return r["routes"][0]["geometry"]["coordinates"]
    except Exception:
        return None
