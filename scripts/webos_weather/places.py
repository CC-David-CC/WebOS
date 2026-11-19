"""Offline GeoNames lookup avoids sending users' typed searches to a geocoder."""

from collections import defaultdict
from functools import lru_cache
import gzip
from math import cos, floor, radians
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parent


def fold(text):
    return "".join(
        c
        for c in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(c)
    )


@lru_cache(maxsize=1)
def cities():
    rows = []
    bins = defaultdict(list)
    with gzip.open(ROOT / "cities.tsv.gz", "rt", encoding="utf8") as stream:
        for line in stream:
            ident, name, ascii_name, country, region, lat, lon, zone = line.rstrip(
                "\n"
            ).split("\t")
            place = dict(
                id="geonames:" + ident,
                name=name,
                countryCode=country,
                admin1=region,
                lat=float(lat),
                lon=float(lon),
                timezone=zone or "UTC",
            )
            rows.append((fold(name), fold(ascii_name), place))
            bins[floor(place["lat"]), floor(place["lon"])].append(place)
    return rows, bins


def coordinates(lat, lon):
    lat, lon = float(lat), float(lon)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid coordinates")
    return round(lat, 2), round(lon, 2)


def distance_sq(lat, lon, place):
    dx = ((place["lon"] - lon + 180) % 360 - 180) * cos(radians(lat))
    return dx * dx + (place["lat"] - lat) ** 2


def point(lat, lon):
    lat, lon = coordinates(lat, lon)
    bins = cities()[1]
    span = min(180, int(1 / max(0.005, cos(radians(lat)))) + 1)
    nearby = (
        p
        for y in range(floor(lat) - 1, floor(lat) + 2)
        for x in range(floor(lon) - span, floor(lon) + span + 1)
        for p in bins.get((y, (x + 180) % 360 - 180), ())
    )
    city = min(nearby, key=lambda p: distance_sq(lat, lon, p), default=None)
    coords = f"{lat:.2f}, {lon:.2f}"
    place = dict(id="geo:" + coords, name=coords, lat=lat, lon=lon, timezone="UTC")
    if city and distance_sq(lat, lon, city) < 0.25:
        place.update(
            name=city["name"]
            if distance_sq(lat, lon, city) < 0.0025
            else "Near " + city["name"],
            countryCode=city["countryCode"],
            timezone=city["timezone"],
        )
    return place


def search(term, count):
    term = fold(term.strip())
    if not 2 <= len(term) <= 120:
        return []
    if "," in term:
        try:
            return [point(*term.split(","))]
        except (TypeError, ValueError):
            pass
    exact, prefixes = [], []
    for name, ascii_name, place in cities()[0]:
        if term in (name, ascii_name):
            exact.append(place)
        elif len(prefixes) < count and (
            name.startswith(term) or ascii_name.startswith(term)
        ):
            prefixes.append(place)
    return (exact + prefixes)[:count]


@lru_cache(maxsize=1)
def stations():
    with gzip.open(ROOT / "stations.tsv.gz", "rt", encoding="utf8") as stream:
        return [
            dict(id=i, lat=float(y), lon=float(x), name=n)
            for i, y, x, n in (line.rstrip("\n").split("\t") for line in stream)
        ]


def nearest_station(lat, lon):
    station = min(stations(), key=lambda p: distance_sq(lat, lon, p))
    return station if distance_sq(lat, lon, station) <= 0.2 else None
