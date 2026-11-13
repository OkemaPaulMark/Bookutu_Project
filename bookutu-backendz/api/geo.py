"""Coordinates for Ugandan towns/terminals used by the mobile map."""

CITY_COORDS = {
    "kampala": (0.3136, 32.5811),
    "entebbe": (0.0512, 32.4637),
    "jinja": (0.4244, 33.2042),
    "mbale": (1.0820, 34.1750),
    "tororo": (0.6928, 34.1810),
    "soroti": (1.7146, 33.6111),
    "lira": (2.2499, 32.8999),
    "gulu": (2.7746, 32.2990),
    "arua": (3.0201, 30.9111),
    "masaka": (-0.3333, 31.7341),
    "mbarara": (-0.6072, 30.6545),
    "kabale": (-1.2486, 29.9899),
    "fort portal": (0.6710, 30.2750),
    "hoima": (1.4331, 31.3524),
    "kasese": (0.1833, 30.0833),
    "busia": (0.4669, 34.0900),
    "mukono": (0.3533, 32.7553),
    "iganga": (0.6092, 33.4686),
    "kabarole": (0.6710, 30.2750),
    "mityana": (0.4175, 32.0228),
}


def coords_for(city):
    if not city:
        return None
    key = city.strip().lower()
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    for name, c in CITY_COORDS.items():
        if name in key or key in name:
            return c
    return None


def route_path(route):
    """Ordered list of (lat, lng) points: origin, intermediate stops, destination."""
    pts = []
    for city in [route.origin_city, *(s if isinstance(s, str) else (s or {}).get("city", "")
                                      for s in (route.intermediate_stops or [])),
                 route.destination_city]:
        c = coords_for(city)
        if c and (not pts or pts[-1] != c):
            pts.append(c)
    return pts


def interpolate(path, progress):
    """Point at fraction `progress` (0..1) along a polyline, by segment length."""
    if not path:
        return None
    if len(path) == 1:
        return path[0]
    progress = max(0.0, min(1.0, progress))
    segs = [((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in zip(path, path[1:])]
    target = sum(segs) * progress
    for (a, b), length in zip(zip(path, path[1:]), segs):
        if target <= length or length == 0:
            f = target / length if length else 0
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        target -= length
    return path[-1]
