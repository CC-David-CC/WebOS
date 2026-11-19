"""Normalize documented provider measurements to Pohoda's metric display schema."""

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from math import isfinite
import re
import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .cache import Unavailable

NWS = "https://api.weather.gov"
MET = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
DIRECTIONS = "N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW".split()
COVERAGE = [
    (24, 50, -125, -66),
    (51, 72, -180, -129),
    (51, 55, 169, 180),
    (18, 23, -161, -154),
    (17, 19, -68, -64),
    (13, 21, 144, 147),
    (-15, -10, -172, -168),
]


def now():
    return datetime.now(timezone.utc)


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def number(value):
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
    ):
        return value
    return None


def scaled(value, factor):
    return round(value * factor, 3) if number(value) is not None else None


def quantity(props, key):
    return number((props.get(key) or {}).get("value"))


def kind(label):
    text = (label or "").lower()
    for key, pattern in [
        ("thunder", "thunder"),
        ("hail", "hail"),
        ("sleet", "sleet|freezing rain|ice pellet"),
        ("snow", "snow|blizzard|flurr"),
        ("heavy-rain", "heavy.?rain"),
        ("drizzle", "drizzle|light.?rain"),
        ("rain", "rain|shower"),
        ("fog", "fog|mist|haze"),
        ("partly", "partly|few clouds|mostly sunny|mostly clear|fair"),
        ("overcast", "overcast|mostly cloudy"),
        ("cloudy", "cloud"),
        ("clear", "clear|sunny"),
    ]:
        if re.search(pattern, text):
            return key
    return "unknown"


def base_hour(t, temp, label, daylight, **values):
    row = dict(
        time=t,
        temperature=temp,
        kind=kind(label),
        summary=label,
        isDay=daylight,
        precipitation=None,
        precipitationProbability=None,
        windSpeed=None,
        windDirection=None,
        humidity=None,
        uvIndex=None,
        visibility=None,
    )
    row.update(values)
    return row


def nws_hours(periods):
    hours = []
    for p in periods:
        temp = number(p.get("temperature"))
        if temp is None:
            continue
        if p["temperatureUnit"] == "F":
            temp = round((temp - 32) * 5 / 9, 2)
        elif p["temperatureUnit"] != "C":
            continue
        text = p.get("windSpeed") or ""
        speeds = re.findall(r"\d+(?:\.\d+)?", text)
        factor = 1.609344 if "mph" in text else 1 if "km/h" in text else None
        direction = p.get("windDirection")
        hours.append(
            base_hour(
                p["startTime"],
                temp,
                p.get("shortForecast"),
                p.get("isDaytime"),
                windSpeed=scaled(float(speeds[-1]), factor)
                if speeds and factor
                else None,
                windDirection=DIRECTIONS.index(direction) * 22.5
                if direction in DIRECTIONS
                else None,
                precipitationProbability=quantity(p, "probabilityOfPrecipitation"),
                humidity=quantity(p, "relativeHumidity"),
                dewPoint=quantity(p, "dewpoint"),
            )
        )
    return hours


def met_hours(series):
    hours = []
    for step in series:
        data = step["data"]
        inst = data["instant"]["details"]
        temp = number(inst.get("air_temperature"))
        if temp is None:
            continue
        period = (
            data.get("next_1_hours")
            or data.get("next_6_hours")
            or data.get("next_12_hours")
            or {}
        )
        symbol = period.get("summary", {}).get("symbol_code", "")
        hours.append(
            base_hour(
                step["time"],
                temp,
                symbol.split("_")[0],
                True
                if symbol.endswith("_day")
                else False
                if symbol.endswith("_night")
                else None,
                pressure=number(inst.get("air_pressure_at_sea_level")),
                humidity=number(inst.get("relative_humidity")),
                cloudCover=number(inst.get("cloud_area_fraction")),
                windSpeed=scaled(inst.get("wind_speed"), 3.6),
                windDirection=number(inst.get("wind_from_direction")),
                precipitation=number(
                    data.get("next_1_hours", {})
                    .get("details", {})
                    .get("precipitation_amount")
                ),
            )
        )
    return hours


def summary(hours, zone):
    groups = defaultdict(list)
    for row in hours:
        groups[stamp(row["time"]).astimezone(zone).date().isoformat()].append(row)
    daily = []
    for date, rows in groups.items():
        temps = [r["temperature"] for r in rows]
        mid = rows[len(rows) // 2]
        winds = [r["windSpeed"] for r in rows if r["windSpeed"] is not None]
        probs = [
            r["precipitationProbability"]
            for r in rows
            if r["precipitationProbability"] is not None
        ]
        daily.append(
            dict(
                date=date,
                kind=mid["kind"],
                min=min(temps),
                max=max(temps),
                feelsMin=None,
                feelsMax=None,
                precipitation=None,
                precipitationProbability=max(probs, default=None),
                windMax=max(winds, default=None),
                windGustMax=None,
                windDirection=None,
                uvMax=None,
                humidityMean=None,
                sunrise=None,
                sunset=None,
                source="forecast",
            )
        )
    return daily


def snapshot(place, provider, entry, stale, hours, issued):
    if not hours:
        raise Unavailable()
    try:
        zone = ZoneInfo(place["timezone"])
    except ZoneInfoNotFoundError:
        zone = timezone.utc
    clock = now()
    if stamp(hours[-1]["time"]) < clock - timedelta(hours=6):
        raise Unavailable()
    current_hour = next(
        (r for r in reversed(hours) if stamp(r["time"]) <= clock), hours[0]
    )
    hours = [r for r in hours if stamp(r["time"]) >= stamp(current_hour["time"])]
    current = dict.fromkeys(
        ("feelsLike", "pressure", "windGust", "cloudCover", "dewPoint")
    )
    current.update(current_hour, source="forecast")
    daily = summary(hours, zone)
    expiry = clock + timedelta(seconds=entry.expires - time.monotonic())
    return dict(
        place=place,
        provider=provider,
        fetchedAt=entry.fetched_at,
        forecastIssuedAt=issued,
        freshness=dict(stale=stale, expiresAt=expiry.isoformat()),
        timezone=place["timezone"],
        utcOffsetSeconds=int(clock.astimezone(zone).utcoffset().total_seconds()),
        current=current,
        hourly=hours,
        daily=daily,
        forecastDays=len(daily),
        climateDays=0,
        notes=[],
        alerts=[],
        alertStatus="outside-coverage",
        alertsValidUntil=None,
    )


async def observation(cache, grid):
    stations, _ = await cache.get(
        NWS + "/gridpoints/" + grid + "/stations", 86400, 3600
    )
    for f in stations.data.get("features", [])[:2]:
        station = f.get("properties", {}).get("stationIdentifier", "")
        if not re.fullmatch("[A-Z0-9]{3,8}", station):
            continue
        try:
            e, stale = await cache.get(
                NWS + "/stations/" + station + "/observations/latest", 600, 0
            )
        except Unavailable:
            continue
        p = e.data["properties"]
        temp = quantity(p, "temperature")
        t = p.get("timestamp")
        if (
            temp is None
            or not t
            or not now() - timedelta(hours=2)
            <= stamp(t)
            <= now() + timedelta(minutes=5)
        ):
            continue

        # NWS observation JSON uses WMO units. Keep unknown units missing.
        def measured(key, units):
            item = p.get(key) or {}
            unit = (item.get("unitCode") or "").split(":")[-1]
            return scaled(item.get("value"), units[unit]) if unit in units else None

        temp = measured("temperature", {"degC": 1})
        if temp is None:
            continue
        current = base_hour(
            t,
            temp,
            p.get("textDescription"),
            None,
            source="observation",
            station=station,
            windSpeed=measured("windSpeed", {"km_h-1": 1, "m_s-1": 3.6}),
            windGust=measured("windGust", {"km_h-1": 1, "m_s-1": 3.6}),
            windDirection=quantity(p, "windDirection"),
            pressure=measured("barometricPressure", {"Pa": 0.01, "hPa": 1}),
            humidity=quantity(p, "relativeHumidity"),
            dewPoint=measured("dewpoint", {"degC": 1}),
            visibility=measured("visibility", {"m": 1}),
            precipitation=measured("precipitationLastHour", {"m": 1000, "mm": 1}),
            feelsLike=None,
            cloudCover=None,
        )
        return current


async def forecast(cache, place):
    lat, lon = place["lat"], place["lon"]
    pt = f"{lat:.2f},{lon:.2f}"
    point = None
    if any(s <= lat <= n and w <= lon <= e for s, n, w, e in COVERAGE):
        try:
            point, _ = await cache.get(NWS + "/points/" + pt, 86400, 86400)
        except Unavailable as exc:
            if exc.status != 404:
                raise
    if point is None:
        entry, stale = await cache.get(f"{MET}?lat={lat:.2f}&lon={lon:.2f}", 3600, 7200)
        props = entry.data["properties"]
        out = snapshot(
            place,
            "met-no",
            entry,
            stale,
            met_hours(props["timeseries"]),
            props["meta"].get("updated_at"),
        )
        out["source"] = "MET Norway · Locationforecast (CC BY 4.0)"
        return out
    p = point.data["properties"]
    office = p.get("gridId", "")
    if not re.fullmatch("[A-Z0-9]{3,4}", office):
        raise Unavailable()
    grid = f"{office}/{int(p['gridX'])},{int(p['gridY'])}"
    place = dict(place, timezone=p.get("timeZone") or place["timezone"])
    fc, obs, alerts = await asyncio.gather(
        cache.get(NWS + "/gridpoints/" + grid + "/forecast/hourly", 3600, 7200),
        observation(cache, grid),
        cache.get(NWS + "/alerts/active?point=" + pt, 60, 0),
        return_exceptions=True,
    )
    if isinstance(fc, BaseException):
        raise fc
    entry, stale = fc
    props = entry.data["properties"]
    out = snapshot(
        place,
        "nws",
        entry,
        stale,
        nws_hours(props["periods"]),
        props.get("updateTime") or props.get("generatedAt"),
    )
    out.update(
        source="NOAA / National Weather Service", grid=grid, alertStatus="unavailable"
    )
    if isinstance(obs, dict):
        out["current"] = obs
    if isinstance(alerts, tuple):
        a, _ = alerts
        out["alertsValidUntil"] = (
            now() + timedelta(seconds=max(0, a.expires - time.monotonic()))
        ).isoformat()
        if a.expires > time.monotonic():
            out["alertStatus"] = "current"
            for feature in a.data.get("features", []):
                warning = feature["properties"]
                end = (
                    min(
                        stamp(t)
                        for t in (warning.get("expires"), warning.get("ends"))
                        if t
                    )
                    if warning.get("expires")
                    else None
                )
                if (
                    end
                    and end > now()
                    and warning.get("status") == "Actual"
                    and warning.get("messageType") != "Cancel"
                    and (
                        not warning.get("effective")
                        or stamp(warning["effective"]) <= now()
                    )
                ):
                    out["alerts"].append(
                        dict(
                            headline=warning.get("headline") or warning.get("event"),
                            severity=warning.get("severity"),
                            expires=end.isoformat(),
                        )
                    )
    return out
