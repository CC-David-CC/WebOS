import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from webos_storage.policy import Denied

from sso_gateway import MailGateway

SUBJECT = "user:93d064f3-2cbb-4706-ab26-ff4938afb917"
OTHER = "user:89cee208-cd47-4988-b307-4934745323f2"
ORIGIN = "https://ksu.codes"
PREFIX = "/api/mailcraft/jmap"


class MailGatewayTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        bindings = Path(tmp.name) / "bindings.json"
        bindings.write_text(json.dumps({
            SUBJECT: {"address": "test@ksu.codes", "password": "fixture-only-one"},
            OTHER: {"address": "another@ksu.codes", "password": "fixture-only-two"},
        }))
        self.active = {(SUBJECT, "active"), (OTHER, "other")}
        self.forwarded = []

        async def upstream(request):
            self.forwarded.append((request.method, request.path,
                                   request.headers.get("Authorization"),
                                   await request.read()))
            if request.path == "/jmap/session":
                return web.json_response({"apiUrl": ORIGIN + "/jmap/",
                    "downloadUrl": ORIGIN + "/jmap/download/{accountId}/{blobId}/{name}?type={type}",
                    "uploadUrl": ORIGIN + "/jmap/upload/{accountId}/"})
            return web.json_response({"accepted": True})

        mailbox = web.Application()
        mailbox.router.add_route("*", "/jmap/{tail:.*}", upstream)
        server = TestServer(mailbox)
        await server.start_server()
        self.addAsyncCleanup(server.close)
        self.gateway = MailGateway(ORIGIN, bindings, lambda sub, sid: (sub, sid) in self.active,
                                   str(server.make_url("/")).removesuffix("/"))
        app = web.Application()
        self.gateway.register(app)
        self.client = TestClient(TestServer(app))
        await self.client.start_server()
        self.addAsyncCleanup(self.client.close)
        self.operator = SimpleNamespace(sub=SUBJECT, sid="active", deadline=10**10, kind="registered")

    def token(self, principal=None):
        payload = {"resource": "mailcraft", "operation": "ticket"}
        return self.gateway.issue(principal or self.operator, payload)["ticket"]

    def headers(self, token):
        return {"Host": "ksu.codes", "Origin": ORIGIN, "Authorization": "Bearer " + token}

    async def test_signin_routes_to_its_bound_mailbox_and_rewrites_session(self):
        token = self.token()
        async with self.client.get(PREFIX + "/session", headers=self.headers(token)) as resp:
            data = await resp.json()
            self.assertEqual(resp.status, 200)
        self.assertEqual(data["apiUrl"], ORIGIN + PREFIX + "/")
        self.assertIn(PREFIX + "/download/", data["downloadUrl"])
        self.assertEqual(self.forwarded[0][2],
                         "Basic " + base64.b64encode(b"test@ksu.codes:fixture-only-one").decode())
        other = SimpleNamespace(sub=OTHER, sid="other", deadline=10**10, kind="registered")
        async with self.client.post(PREFIX + "/", headers=self.headers(self.token(other)),
                                    json={"using": ["fixture"]}) as resp:
            self.assertEqual(resp.status, 200)
            self.assertTrue((await resp.json())["accepted"])
        self.assertEqual(self.forwarded[1][2],
                         "Basic " + base64.b64encode(b"another@ksu.codes:fixture-only-two").decode())
        self.assertEqual(json.loads(self.forwarded[1][3]), {"using": ["fixture"]})

    async def test_logout_revokes_existing_ticket(self):
        token = self.token()
        self.active.remove((SUBJECT, "active"))
        async with self.client.get(PREFIX + "/session", headers=self.headers(token)) as resp:
            self.assertEqual(resp.status, 401)
        self.assertEqual(self.forwarded, [])

    async def test_unknown_account_and_cross_origin_are_denied(self):
        with self.assertRaises(Denied):
            self.token(SimpleNamespace(sub="user:unknown", sid="active", deadline=10**10,
                                       kind="registered"))
        headers = self.headers(self.token()) | {"Origin": "https://other.example"}
        async with self.client.get(PREFIX + "/session", headers=headers) as resp:
            self.assertEqual(resp.status, 403)
        self.assertEqual(self.forwarded, [])
