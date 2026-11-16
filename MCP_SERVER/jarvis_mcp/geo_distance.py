import math
from typing import Any, Dict, List, Optional


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float, unit: str = "km") -> float:
    """คำนวณระยะทางทางภูมิศาสตร์ด้วยสูตร Haversine"""
    r_km = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = r_km * c

    if unit == "m":
        return round(distance_km * 1000.0, 2)
    return round(distance_km, 3)


def geo_distance(
    origin: Dict[str, float],
    destinations: List[Dict[str, Any]],
    max_distance_km: Optional[float] = None,
    limit: int = 5,
    unit: str = "km",
) -> Dict[str, Any]:
    """คำนวณและกรองสถานที่ใกล้เคียงตามพิกัดอ้างอิง"""
    if not origin or "latitude" not in origin or "longitude" not in origin:
        raise ValueError("INVALID_INPUT: origin requires latitude and longitude")

    try:
        lat1 = float(origin["latitude"])
        lon1 = float(origin["longitude"])
    except (ValueError, TypeError):
        raise ValueError("INVALID_INPUT: origin coordinates must be numbers")

    if not (-90.0 <= lat1 <= 90.0 and -180.0 <= lon1 <= 180.0):
        raise ValueError("INVALID_INPUT: origin latitude or longitude out of range")

    if not isinstance(destinations, list):
        raise ValueError("INVALID_INPUT: destinations must be a list")

    calculated = []
    warnings = []

    for item in destinations:
        if not isinstance(item, dict):
            continue

        item_lat = item.get("latitude")
        item_lon = item.get("longitude")
        if item_lat is None or item_lon is None:
            continue

        try:
            lat2 = float(item_lat)
            lon2 = float(item_lon)
        except (ValueError, TypeError):
            continue

        if not (-90.0 <= lat2 <= 90.0 and -180.0 <= lon2 <= 180.0):
            continue

        dist = calculate_haversine_distance(lat1, lon1, lat2, lon2, unit=unit)
        dist_km = dist if unit == "km" else dist / 1000.0

        if max_distance_km is not None and dist_km > max_distance_km:
            continue

        calculated.append({
            "id": str(item.get("id", "")),
            "label": str(item.get("label") or item.get("storeLocation") or "Unknown"),
            "distance": dist,
            "unit": unit,
        })

    # Sort ascending by distance
    calculated.sort(key=lambda x: x["distance"])

    # Limit results
    effective_limit = min(max(1, limit), 20)
    results = calculated[:effective_limit]

    return {
        "source": "geo_calc",
        "origin": {
            "latitude": lat1,
            "longitude": lon1,
        },
        "total_matched": len(calculated),
        "returned": len(results),
        "results": results,
        "warnings": warnings,
    }

