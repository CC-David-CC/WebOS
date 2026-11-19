"""Weather routes mounted in the existing aiohttp process. No account data or separate daemon."""

from datetime import date
from urllib.parse import urlencode

import aiohttp
from aiohttp import web

from .cache import WeatherCache, Unavailable
from .forecast import forecast
from .places import coordinates, nearest_station, point, search

CACHE = web.AppKey("weather-cache", WeatherCache)


async def history(cache, lat, lon, day):
    station = nearest_station(lat, lon)
    if not station:
        return {
            "years": [],
            "source": "NOAA NCEI",
            "reason": "No nearby reference station in coverage",
        }
    # Complete past calendar years are shared by every query at this station.
    year = day.year
    args = dict(
        dataset="daily-summaries",
        stations=station["id"],
        startDate=f"{year - 10}-01-01",
        endDate=f"{year - 1}-12-31",
        format="json",
        units="metric",
        dataTypes="TMAX,TMIN,PRCP,WSF2,WDF2",
    )
    entry, stale = await cache.get(
        "https://www.ncei.noaa.gov/access/services/data/v1?" + urlencode(args),
        86400,
        604800,
    )
    years = []
    for row in reversed(entry.data):
        recorded = date.fromisoformat(row["DATE"])
        if (
            (recorded.month, recorded.day) != (day.month, day.day)
            or not row.get("TMAX")
            or not row.get("TMIN")
        ):
            continue

        def value(key, factor=1):
            return round(float(row[key]) * factor, 2) if row.get(key) else None

        years.append(
            dict(
                yearsAgo=year - recorded.year,
                date=row["DATE"],
                max=value("TMAX"),
                min=value("TMIN"),
                precipitation=value("PRCP"),
                windMax=value("WSF2", 3.6),
                windDirection=value("WDF2"),
                kind="unknown",
            )
        )
    return dict(
        years=years,
        source="NOAA NCEI Daily Summaries",
        station=station,
        fetchedAt=entry.fetched_at,
        stale=stale,
    )


def install(app):
    async def session_lifetime(app):
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=12), cookie_jar=aiohttp.DummyCookieJar()
        ) as session:
            cache = WeatherCache(session)
            app[CACHE] = cache
            try:
                yield
            finally:
                await cache.close()

    app.cleanup_ctx.append(session_lifetime)

    async def handle(request):
        route = request.match_info["route"]
        query = request.query
        try:
            if route == "places":
                count = min(15, max(1, int(query.get("count", "8"))))
            else:
                lat, lon = coordinates(query["lat"], query["lon"])
            if route == "history":
                day = date.fromisoformat(query["date"])
                if abs(day.year - date.today().year) > 1:
                    raise ValueError("Date outside current display window")
        except (KeyError, ValueError, OverflowError):
            return web.json_response({"error": "invalid_request"}, status=400)

        try:
            if route == "places":
                result = dict(
                    results=search(query.get("q", ""), count),
                    source="GeoNames · CC BY 4.0",
                )
            elif route == "places/reverse":
                result = dict(place=point(lat, lon), source="GeoNames · CC BY 4.0")
            elif route == "history":
                result = await history(request.app[CACHE], lat, lon, day)
            else:
                place = point(lat, lon)
                # User-supplied labels never enter the upstream cache.
                for key in ("name", "id"):
                    if query.get(key):
                        place[key] = query[key][:120]
                result = await forecast(request.app[CACHE], place)
        except Unavailable as exc:
            if exc.status == 429:
                return web.json_response(
                    {"error": "rate_limit"},
                    status=429,
                    headers={"Cache-Control": "no-store"},
                )
            return web.json_response(
                {"error": "provider_error"},
                status=503,
                headers={"Cache-Control": "no-store"},
            )
        except (KeyError, TypeError, ValueError, OverflowError):
            # An unexpected upstream schema must not break the desktop.
            return web.json_response(
                {"error": "provider_error"},
                status=503,
                headers={"Cache-Control": "no-store"},
            )
        return web.json_response(result, headers={"Cache-Control": "no-store"})

    app.router.add_get(
        "/services/weather/{route:weather|places|places/reverse|history}", handle
    )
