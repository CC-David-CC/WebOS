"""Small, process-wide HTTP JSON cache for allowlisted weather resources."""

import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import time
from urllib.parse import urlsplit

import aiohttp

AGENT = "WebOS-Weather/1.0 (+https://github.com/CC-David-CC/WebOS; https://ksu.codes/)"
HOSTS = {"api.weather.gov", "api.met.no", "www.ncei.noaa.gov"}


class Unavailable(Exception):
    def __init__(self, status=503):
        self.status = status


@dataclass
class Entry:
    data: object
    headers: dict
    fetched_at: str
    expires: float
    usable_until: float
    size: int


def header_date(value):
    try:
        return parsedate_to_datetime(value).timestamp()
    except (TypeError, ValueError, OverflowError):
        return 0


def retry_seconds(value):
    try:
        return max(1, int(value))
    except (ValueError, TypeError):
        return max(15, header_date(value) - time.time())


class WeatherCache:
    def __init__(self, session, *, capacity=256, max_bytes=12 << 20):
        self.session = session
        self.capacity = capacity
        self.max_bytes = max_bytes
        self.used = 0
        self.entries = OrderedDict()
        self.pending = {}
        self.failures = OrderedDict()
        self.next_request = {}
        self.host_locks = {host: asyncio.Lock() for host in HOSTS}
        self.slots = asyncio.Semaphore(5)
        self.hits = self.requests = self.coalesced = 0

    def forget(self, key):
        old = self.entries.pop(key, None)
        if old:
            self.used -= old.size

    async def get(self, url, ttl, stale=0):
        host = urlsplit(url).hostname
        if host not in HOSTS or urlsplit(url).scheme != "https":
            raise ValueError("Unsupported weather resource")
        now = time.monotonic()
        old = self.entries.get(url)
        if old:
            self.entries.move_to_end(url)
            if old.expires > now:
                self.hits += 1
                return old, False
        fallback = old and old.usable_until > now and stale > 0
        failure = self.failures.get(url)
        if failure and failure[0] > now:
            if fallback:
                return old, True
            raise Unavailable(failure[1])
        task = self.pending.get(url)
        if task:
            self.coalesced += 1
        else:
            if len(self.pending) >= 32:
                if fallback:
                    return old, True
                raise Unavailable(429)
            task = asyncio.create_task(self.refresh(url, host, old, ttl, stale))
            self.pending[url] = task

            def finished(done):
                self.pending.pop(url, None)
                if not done.cancelled():
                    done.exception()  # background revalidation reports its failure via cooldown

            task.add_done_callback(finished)
        if fallback:
            return old, True
        return await asyncio.shield(task), False

    async def refresh(self, url, host, old, ttl, stale):
        headers = {"User-Agent": AGENT, "Accept": "application/json"}
        if old:
            for field, request_field in (
                ("etag", "If-None-Match"),
                ("last-modified", "If-Modified-Since"),
            ):
                if field in old.headers:
                    headers[request_field] = old.headers[field]
        try:
            async with self.slots:
                async with self.host_locks[host]:
                    wait = self.next_request.get(host, 0) - time.monotonic()
                    if wait > 1:
                        raise Unavailable(429)
                    await asyncio.sleep(max(0, wait))
                    self.next_request[host] = time.monotonic() + 0.2
                self.requests += 1
                async with self.session.get(
                    url, headers=headers, allow_redirects=False
                ) as resp:
                    if resp.status in (429, 503) and (
                        resp.status == 429 or resp.headers.get("Retry-After")
                    ):
                        self.next_request[host] = max(
                            self.next_request[host],
                            time.monotonic()
                            + retry_seconds(resp.headers.get("Retry-After")),
                        )
                    if resp.status == 304 and old:
                        data, size, meta = old.data, old.size, dict(old.headers)
                        meta.pop("age", None)
                        meta.pop("date", None)
                    elif resp.status == 200:
                        buf = bytearray()
                        async for part in resp.content.iter_chunked(65536):
                            buf.extend(part)
                            if len(buf) > 3 << 20:
                                raise Unavailable()
                        data, size, meta = json.loads(buf), len(buf), {}
                    else:
                        raise Unavailable(
                            resp.status if resp.status in (404, 429) else 503
                        )
                    meta.update({k.lower(): v for k, v in resp.headers.items()})
            directives = dict(
                (p.strip().lower().split("=", 1) + [None])[:2]
                for p in meta.get("cache-control", "").split(",")
            )
            max_age = directives.get("s-maxage", directives.get("max-age"))
            if max_age:
                date_header = header_date(meta.get("date"))
                age = max(
                    float(meta.get("age", 0)),
                    time.time() - date_header if date_header else 0,
                )
                lifetime = max(0, int(max_age.strip('"')) - age)
            elif "expires" in meta:
                lifetime = max(0, header_date(meta["expires"]) - time.time())
            else:
                lifetime = ttl
            if "no-cache" in directives:
                lifetime = stale = 0
            if (
                any(
                    d in directives
                    for d in ("must-revalidate", "proxy-revalidate", "s-maxage")
                )
                and "stale-while-revalidate" not in directives
            ):
                stale = 0
            if directives.get("stale-while-revalidate"):
                stale = min(stale, int(directives["stale-while-revalidate"]))
            now = time.monotonic()
            expiry = now + min(ttl, lifetime)
            entry = Entry(
                data,
                meta,
                datetime.now(timezone.utc).isoformat(),
                expiry,
                expiry + stale,
                size,
            )
            self.forget(url)
            self.failures.pop(url, None)
            if (
                "no-store" not in directives
                and "private" not in directives
                and meta.get("vary") != "*"
            ):
                self.entries[url] = entry
                self.used += size
                while self.used > self.max_bytes or len(self.entries) > self.capacity:
                    self.forget(next(iter(self.entries)))
            return entry
        except (aiohttp.ClientError, TimeoutError, ValueError, Unavailable) as exc:
            status = exc.status if isinstance(exc, Unavailable) else 503
            self.failures[url] = (
                time.monotonic() + (300 if status == 404 else 15),
                status,
            )
            self.failures.move_to_end(url)
            if len(self.failures) > self.capacity:
                self.failures.popitem(last=False)
            raise Unavailable(status) from exc

    async def close(self):
        jobs = list(self.pending.values())
        for job in jobs:
            job.cancel()
        await asyncio.gather(*jobs, return_exceptions=True)
