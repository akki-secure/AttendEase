import math

EARTH_RADIUS_METERS = 6_371_000


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """2点間の直線距離をメートルで返す"""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_METERS * math.asin(math.sqrt(a))


def is_within_any_location(lat: float, lon: float, locations: list) -> bool:
    """アクティブな拠点のいずれかの許容半径内かどうか"""
    return any(
        haversine_distance_meters(lat, lon, loc.latitude, loc.longitude) <= loc.radius_meters
        for loc in locations
    )
