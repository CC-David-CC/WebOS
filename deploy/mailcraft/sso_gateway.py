"""Same-origin JMAP relay authorized by the live, signed WebOS session."""
import asyncio
import base64
from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path
import re
import secrets
import threading
import time
from urllib.parse import unquote, urlsplit

from aiohttp import ClientSession, ClientTimeout, ClientError, web
from yarl import URL
from webos_storage.policy import Denied

PREFIX = "/api/mailcraft/jmap"
TICKET = re.compile(r"Bearer ([A-Za-z0-9_-]{43})")
SUBJECT = re.compile(r"user:[0-9a-f-]{36}")
ADDRESS = re.compile(r"[a-z][a-z0-9]{2,27}@ksu\.codes")
MAX_UPLOAD = 64 * 1024 * 1024
TTL = 90


@dataclass(frozen=True)
class Binding:
    address: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class Ticket:
    subject: str
    sid: str
    expires: float


def load_bindings(path):
    if Path(path).stat().st_size > 65536:
        raise ValueError("MailCraft account bindings are too large")
    rows = json.loads(Path(path).read_text())
    accounts = {}
    addresses = set()
    for subject, row in rows.items():
        address, password = row["address"], row["password"]
        if (not SUBJECT.fullmatch(subject) or not ADDRESS.fullmatch(address)
                or address in addresses or not 1 <= len(password) <= 256 or not password.isprintable()):
            raise ValueError("Invalid MailCraft account binding")
        accounts[subject] = Binding(address, password)
        addresses.add(address)
    return accounts


class MailGateway:
    def __init__(self, origin, binding_file, live, upstream="http://127.0.0.1:28881"):
        self.origin = origin
        self.host = urlsplit(origin).netloc
        self.bindings = load_bindings(binding_file)
        self.upstream = upstream
        self.live = live
        self.tickets = {}
        self.lock = threading.Lock()
        self.http = None

    def issue(self, principal, request):
        if request != {"resource": "mailcraft", "operation": "ticket"}:
            raise Denied("Unknown MailCraft operation.")
        now = time.time()
        binding = self.bindings.get(principal.sub)
        if (principal.kind != "registered" or not binding or principal.deadline <= now
                or not self.live(principal.sub, principal.sid)):
            raise Denied("This account has no approved mailbox.")
        token = secrets.token_urlsafe(32)
        with self.lock:
            self.tickets = {key: value for key, value in self.tickets.items() if value.expires > now}
            if len(self.tickets) >= 2048 or sum(t.subject == principal.sub for t in self.tickets.values()) >= 24:
                raise Denied("Too many MailCraft requests. Try again shortly.")
            self.tickets[sha256(token.encode()).digest()] = Ticket(
                principal.sub, principal.sid, min(now + TTL, principal.deadline),
            )
        return {"address": binding.address, "session": self.origin + PREFIX + "/session", "ticket": token}

    def binding(self, authorization):
        match = TICKET.fullmatch(authorization)
        if not match:
            raise web.HTTPUnauthorized()
        with self.lock:
            ticket = self.tickets.get(sha256(match[1].encode()).digest())
        if ticket is None or ticket.expires <= time.time() or not self.live(ticket.subject, ticket.sid):
            raise web.HTTPUnauthorized()
        return self.bindings[ticket.subject]

    async def start(self, _app):
        self.http = ClientSession(timeout=ClientTimeout(total=45, connect=5), auto_decompress=False)

    async def stop(self, _app):
        if self.http:
            await self.http.close()

    def register(self, app):
        app.router.add_get(PREFIX + "/session", self.proxy, allow_head=False)
        app.router.add_get(PREFIX + "/download/{tail:.+}", self.proxy, allow_head=False)
        app.router.add_post(PREFIX, self.proxy)
        app.router.add_post(PREFIX + "/", self.proxy)
        app.router.add_post(PREFIX + "/upload/{tail:.+}", self.proxy)
        app.on_startup.append(self.start)
        app.on_cleanup.append(self.stop)

    def rewrite_session(self, result):
        for field in ("apiUrl", "downloadUrl", "uploadUrl", "eventSourceUrl"):
            address = result.get(field)
            if not address:
                continue
            parsed = urlsplit(address)
            if parsed.scheme != urlsplit(self.origin).scheme or parsed.netloc != self.host or (
                parsed.path != "/jmap" and not parsed.path.startswith("/jmap/")
            ):
                raise web.HTTPBadGateway()
            result[field] = self.origin + PREFIX + address.split("/jmap", 1)[1]
        return result

    async def proxy(self, request):
        if request.headers.getall("Host", []) != [self.host] or request.headers.getall("Origin", []) not in (
            [], [self.origin],
        ):
            raise web.HTTPForbidden()
        authorization = request.headers.getall("Authorization", [])
        if len(authorization) != 1:
            raise web.HTTPUnauthorized()
        binding = await asyncio.to_thread(self.binding, authorization[0])
        raw_path, mark, query = request.raw_path.partition("?")
        if len(query) > 4096:
            raise web.HTTPBadRequest()
        if not raw_path.startswith(PREFIX):
            raise web.HTTPNotFound()
        tail = raw_path[len(PREFIX):]
        if any(part in (".", "..") or "\\" in part or "\0" in part
               for part in unquote(tail).split("/")):
            raise web.HTTPBadRequest()
        headers = {"Authorization": "Basic " + base64.b64encode(
            f"{binding.address}:{binding.password}".encode()
        ).decode()}
        body = None
        if request.method == "POST":
            size = request.content_length
            if size is None:
                raise web.HTTPLengthRequired()
            limit = MAX_UPLOAD if tail.startswith("/upload/") else 4 * 1024 * 1024
            if size > limit:
                raise web.HTTPRequestEntityTooLarge(max_size=limit, actual_size=size)
            headers["Content-Length"] = str(size)
            headers["Content-Type"] = request.headers.get("Content-Type", "application/octet-stream")
            body = request.content.iter_chunked(65536)
        target = URL(self.upstream + "/jmap" + tail + mark + query, encoded=True)
        try:
            async with self.http.request(request.method, target, headers=headers,
                                         data=body, allow_redirects=False) as upstream:
                outgoing = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
                if 300 <= upstream.status < 400:
                    raise web.HTTPBadGateway()
                if tail == "/session" and upstream.status == 200:
                    data = bytearray()
                    async for chunk in upstream.content.iter_chunked(65536):
                        data.extend(chunk)
                        if len(data) > 262144:
                            raise web.HTTPBadGateway()
                    parsed = self.rewrite_session(json.loads(data))
                    return web.json_response(parsed, headers=outgoing)
                for field in ("Content-Type", "Content-Length", "Content-Disposition"):
                    if field in upstream.headers:
                        outgoing[field] = upstream.headers[field]
                result = web.StreamResponse(status=upstream.status, headers=outgoing)
                await result.prepare(request)
                async for chunk in upstream.content.iter_chunked(65536):
                    await result.write(chunk)
                return result
        except (ClientError, TimeoutError, json.JSONDecodeError):
            raise web.HTTPBadGateway(text="The mail service is temporarily unavailable.")
