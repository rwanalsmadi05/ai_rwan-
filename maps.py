"""
maps.py
-------
Finds nearby farmers for a buyer location.
- Distance is computed with the haversine formula (no key needed, always works).
- If an Azure Maps key is present, we also return real road travel time.
"""
import json
import math
import requests
import config

_FARMERS = json.loads((config.DATA_DIR / "farmers.json").read_text(encoding="utf-8"))["farmers"]


def _haversine_km(lat1, lng1, lat2, lng2) -> float:
    """Great-circle distance between two points in kilometers."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 2)


def _azure_travel_minutes(lat1, lng1, lat2, lng2):
    """Optional: real driving time from Azure Maps Route API."""
    if not config.HAS_AZURE_MAPS:
        return None
    url = "https://atlas.microsoft.com/route/directions/json"
    params = {
        "api-version": "1.0",
        "subscription-key": config.AZURE_MAPS_KEY,
        "query": f"{lat1},{lng1}:{lat2},{lng2}",
        "travelMode": "car",
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        sec = r.json()["routes"][0]["summary"]["travelTimeInSeconds"]
        return round(sec / 60)
    except Exception:
        return None


def nearby_farmers(lat: float, lng: float, radius_km: float = 50, crop: str | None = None) -> dict:
    """
    Return farmers within radius_km of (lat, lng), nearest first.
    Optionally filter by a crop name (e.g. 'بندورة').
    """
    results = []
    for f in _FARMERS:
        dist = _haversine_km(lat, lng, f["lat"], f["lng"])
        if dist > radius_km:
            continue
        if crop and not any(crop in p["name"] for p in f["products"]):
            continue
        results.append({
            "id": f["id"],
            "name": f["name"],
            "city": f["city"],
            "region": f["region"],
            "rating": f["rating"],
            "verified": f["verified"],
            "lat": f["lat"],
            "lng": f["lng"],
            "distance_km": dist,
            "travel_minutes": _azure_travel_minutes(lat, lng, f["lat"], f["lng"]),
            "products": f["products"],
        })

    results.sort(key=lambda x: x["distance_km"])
    return {
        "count": len(results),
        "source": "azure" if config.HAS_AZURE_MAPS else "haversine",
        "farmers": results,
    }
