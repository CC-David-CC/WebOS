#!/usr/bin/env python3
"""Configure the pilot's inbound listener, certificate, and signing key in recovery mode."""
import json
from pathlib import Path
import sys

from policy import DOMAIN, Registry, database, local_domain, make_roles, project

HOST = f"mail.{DOMAIN}"
ACME = "MailCraft SMTP certificate"
LE_DIRECTORY = "https://acme-v02.api.letsencrypt.org/directory"


def ensure(registry, kind, match, record):
    matches = [row for row in registry.get(kind, properties=["id", *record])
               if row[match] == record[match]]
    if not matches:
        return registry.create(kind, record)
    existing, = matches
    changes = {key: value for key, value in record.items() if existing.get(key) != value}
    if changes:
        registry.update(kind, {existing["id"]: changes})
    return existing["id"]


def configure(root, recovery_path):
    registry = Registry(json.loads(recovery_path.read_text()))
    with database(root / "mailcraft-access.sqlite") as db:
        project(registry, db, make_roles(registry))
    domain_id = local_domain(registry)
    cert_provider_id = ensure(registry, "AcmeProvider", "description", {
        "description": ACME, "challengeType": "Http01", "directory": LE_DIRECTORY,
        "contact": {f"mailto:mail-ops@{DOMAIN}": True},
    })
    registry.update("Domain", {domain_id: {
        "certificateManagement": {"@type": "Automatic", "acmeProviderId": cert_provider_id,
                                  "subjectAlternativeNames": {HOST: True}},
    }})
    for tracer in registry.get("Tracer", properties=["id", "@type"]):
        if tracer["@type"] == "Log":
            registry.update("Tracer", {tracer["id"]: {"path": str(root / "logs")}})
    signer, = registry.get("DkimSignature", properties=["id", "selector", "domainId"])
    assert signer["selector"] == "mail202611" and signer["domainId"] == domain_id
    registry.update("DkimSignature", {signer["id"]: {"privateKey": {
        "@type": "File", "filePath": str(root / "secrets/mail202611.key"),
    }}})
    ensure(registry, "NetworkListener", "name", {
        "name": "mailcraft-mx", "bind": {"0.0.0.0:25": True}, "protocol": "smtp",
        "useTls": True, "implicitTls": False,
    })
    listeners = {row["name"]: row["bind"] for row in registry.get(
        "NetworkListener", properties=["name", "bind"],
    )}
    assert listeners == {"mailcraft-jmap": {"127.0.0.1:28881": True},
                         "mailcraft-mx": {"0.0.0.0:25": True}}
    print(json.dumps({"smtp": "0.0.0.0:25", "jmap": "127.0.0.1:28881",
                      "acmeHostname": HOST, "policyProjected": True}))


if __name__ == "__main__":
    configure(Path(sys.argv[1]).resolve(strict=True), Path(sys.argv[2]).resolve(strict=True))
