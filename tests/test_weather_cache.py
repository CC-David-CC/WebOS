"""Tests of shared revalidation and freshness independent of provider uptime."""

import asyncio
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from webos_weather.cache import AGENT, Unavailable, WeatherCache


class Response:
    def __init__(self, status, value, headers):
        self.status = status
        self.headers = headers
        self.value = value
        self.content = self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass

    async def iter_chunked(self, _):
        yield json.dumps(self.value).encode()


class WeatherTests(unittest.IsolatedAsyncioTestCase):
    url = "https://api.weather.gov/gridpoints/TOP/50,55/forecast/hourly"

    async def test_same_resource_shared_across_clients_then_revalidated(self):
        session = Mock()
        session.get.side_effect = [
            Response(
                200, {"forecast": 1}, {"Cache-Control": "max-age=600", "ETag": '"abc"'}
            ),
            Response(304, None, {"Cache-Control": "max-age=600"}),
        ]
        cache = WeatherCache(session)
        results = await asyncio.gather(*(cache.get(self.url, 3600) for _ in range(12)))
        self.assertEqual(session.get.call_count, 1)
        self.assertEqual(cache.coalesced, 11)
        self.assertTrue(all(r == results[0] for r in results))
        entry, _ = await cache.get(self.url, 3600)
        self.assertEqual(cache.hits, 1)
        entry.expires = 0
        revalidated, stale = await cache.get(self.url, 3600)
        self.assertFalse(stale)
        self.assertEqual(revalidated.data, entry.data)
        self.assertEqual(
            session.get.call_args.kwargs["headers"]["If-None-Match"], '"abc"'
        )
        self.assertEqual(session.get.call_args.kwargs["headers"]["User-Agent"], AGENT)
        await cache.close()

    async def test_old_alert_is_unavailable_during_throttle(self):
        session = Mock()
        session.get.side_effect = [
            Response(200, {"alert": True}, {"Cache-Control": "max-age=1"}),
            Response(429, {}, {"Retry-After": "120"}),
        ]
        cache = WeatherCache(session)
        entry, _ = await cache.get(self.url, 60)
        entry.expires = 0
        for _ in range(2):
            with self.assertRaises(Unavailable) as raised:
                await cache.get(self.url, 60, 0)
            self.assertEqual(raised.exception.status, 429)
        self.assertEqual(session.get.call_count, 2)
        await cache.close()

    async def test_bounds_and_no_store(self):
        session = Mock()
        session.get.side_effect = [
            Response(200, 1, {"Cache-Control": "max-age=300"}) for _ in range(3)
        ]
        cache = WeatherCache(session, capacity=1)
        await cache.get(self.url, 300)
        await cache.get(self.url + "/other", 300)
        self.assertEqual(list(cache.entries), [self.url + "/other"])
        session.get.side_effect = [Response(200, 1, {"Cache-Control": "no-store"})]
        await cache.get(self.url, 300)
        self.assertNotIn(self.url, cache.entries)
        await cache.close()
