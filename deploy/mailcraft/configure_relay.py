#!/usr/bin/env python3
"""Configure and read back SMTP2GO SMTP submission on the private Stalwart registry."""
import base64
import json
import os
from pathlib import Path
import stat
import sys
import urllib.request

BASE = "http://127.0.0.1:28880"
REGISTRY = "urn:stalwart:jmap"
RELAY = "smtp2go"
HOST = "mail.smtp2go.com"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def private_file(path):
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_uid != os.geteuid() or info.st_nlink != 1):
        raise ValueError("Expected a private credential file owned by the caller.")
    value = path.read_text()
    if not value or not value.isprintable():
        raise ValueError("Expected a nonempty SMTP credential.")
    return value


def configure(admin, credentials):
    authorization = base64.b64encode(f"{admin['username']}:{admin['secret']}".encode()).decode()

    def call(method, arguments):
        payload = json.dumps({"using": ["urn:ietf:params:jmap:core", REGISTRY],
                              "methodCalls": [[method, arguments, "smtp2go"]]}).encode()
        request = urllib.request.Request(BASE + "/jmap", payload, {
            "Authorization": "Basic " + authorization, "Content-Type": "application/json",
        })
        with opener.open(request, timeout=10) as response:
            name, result, _ = json.load(response)["methodResponses"][0]
        if name != method or any(result.get(key) for key in ("notCreated", "notUpdated")):
            errors = [ (item.get("type"), item.get("properties"))
                       for key in ("notCreated", "notUpdated")
                       for item in result.get(key, {}).values() ]
            raise ValueError(f"Registry rejected {method}: {result.get('type')} {errors}")
        return result

    password_file = credentials / "password"
    private_file(password_file)
    route = {
        "@type": "Relay", "name": RELAY, "host": HOST, "port": 587,
        "protocol": "smtp", "implicitTls": False, "allowInvalidCerts": False,
        "authUsername": private_file(credentials / "username"),
        "authSecret": {"@type": "File", "filePath": str(password_file)},
    }
    tls = {
        "name": RELAY, "startTls": "require", "allowInvalidCerts": False,
        "mtaSts": "optional", "dane": "optional",
    }
    for collection, record in (("MtaRoute", route), ("MtaTlsStrategy", tls)):
        existing = call(f"x:{collection}/get", {"properties": ["id", *record]})["list"]
        rows = [row for row in existing if row["name"] == RELAY]
        if rows:
            row, = rows
            row_id = row["id"]
            changes = {name: value for name, value in record.items()
                       if name != "@type" and row.get(name) != value}
            if changes:
                result = call(f"x:{collection}/set", {"update": {row_id: changes}})
                assert row_id in result["updated"]
        else:
            row_id = call(f"x:{collection}/set", {"create": {RELAY: record}})["created"][RELAY]["id"]
        actual, = call(f"x:{collection}/get", {"ids": [row_id], "properties": list(record)})["list"]
        assert all(actual[key] == value for key, value in record.items() if key != "authSecret")

    strategy = {
        "route": {
            "match": {"0": {"if": "is_local_domain(rcpt_domain)", "then": "'local'"}},
            "else": "'smtp2go'",
        },
        "tls": {"match": {}, "else": "'smtp2go'"},
    }
    response = call("x:MtaOutboundStrategy/set", {"update": {"singleton": strategy}})
    assert "singleton" in response["updated"]
    actual, = call("x:MtaOutboundStrategy/get", {"ids": ["singleton"], "properties": ["route", "tls"]})["list"]
    assert all(actual[key] == value for key, value in strategy.items())
    listeners = call("x:NetworkListener/get", {"properties": ["protocol", "bind"]})["list"]
    print(json.dumps({
        "relay": HOST, "port": 587, "requireStartTls": True, "verifyCertificate": True,
        "localMailDelivery": "local", "remoteMailDelivery": RELAY,
        "publicSubmissionListeners": sum(row["protocol"] == "smtp" for row in listeners),
    }))


if __name__ == "__main__":
    admin = json.loads(Path(sys.argv[1]).read_text())
    configure(admin, Path(sys.argv[2]).resolve(strict=True))
