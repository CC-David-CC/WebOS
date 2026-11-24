#!/usr/bin/env python3
"""Manage the MailCraft pilot's mailbox grants through Stalwart's recovery listener."""
import argparse
import base64
import json
import os
import re
from pathlib import Path
import secrets
import sqlite3
import urllib.error
import urllib.request

DOMAIN = "ksu.codes"
PILOT = ("mail-ops", "dflanag3", "test")
CORE = "urn:ietf:params:jmap:core"
REGISTRY = "urn:stalwart:jmap"
BASE = "http://127.0.0.1:28880"
SCHEMA = """
CREATE TABLE IF NOT EXISTS mailbox (
    account_id TEXT PRIMARY KEY NOT NULL,
    address TEXT UNIQUE COLLATE NOCASE NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS capability (
    name TEXT PRIMARY KEY NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS mailbox_grant (
    account_id TEXT NOT NULL REFERENCES mailbox(account_id) ON DELETE CASCADE,
    capability_name TEXT NOT NULL REFERENCES capability(name),
    PRIMARY KEY (account_id, capability_name)
) WITHOUT ROWID, STRICT;
INSERT OR IGNORE INTO capability(name) VALUES ('access'), ('send'), ('external_send');
"""
ROLE_NAMES = {
    "blocked": "MailCraft blocked",
    "receive": "MailCraft receive only",
    "send": "MailCraft approved sender",
}
NO_FILTER = {permission: True for permission in (
    "jmapVacationResponseUpdate", "jmapSieveScriptCreate",
    "jmapSieveScriptUpdate", "sieveAuthenticate",
)}
NO_SEND = NO_FILTER | {"emailSend": True, "jmapEmailSubmissionCreate": True}

def database(path):
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)
    return db


class Registry:
    def __init__(self, credentials, *, online=False):
        self.base = "http://127.0.0.1:28881" if online else BASE
        key = f"{credentials['username']}:{credentials['secret']}".encode()
        self.authorization = "Basic " + base64.b64encode(key).decode()
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def call(self, kind, action, arguments):
        method = f"x:{kind}/{action}"
        body = json.dumps({"using": [CORE, REGISTRY],
                           "methodCalls": [[method, arguments, "policy"]]}).encode()
        request = urllib.request.Request(self.base + "/jmap", body, {
            "Content-Type": "application/json", "Authorization": self.authorization,
        })
        with self.opener.open(request, timeout=15) as response:
            name, result, _ = json.load(response)["methodResponses"][0]
        if name != method:
            raise ValueError(f"{method} rejected: {result.get('type')}")
        for failure in ("notCreated", "notUpdated", "notDestroyed", "notFound"):
            if result.get(failure):
                errors = result[failure]
                if isinstance(errors, dict):
                    errors = [f"{key}: {item.get('type')} {item.get('properties', [])}"
                              for key, item in errors.items()]
                raise ValueError(f"{method}: {failure} {errors}")
        return result

    def get(self, kind, **arguments):
        return self.call(kind, "get", arguments)["list"]

    def create(self, kind, record):
        return self.call(kind, "set", {"create": {"add": record}})["created"]["add"]["id"]

    def update(self, kind, updates):
        if updates:
            result = self.call(kind, "set", {"update": updates})
            if set(result["updated"]) != set(updates):
                raise ValueError(f"Incomplete {kind} update")


def local_domain(registry):
    domains = registry.get("Domain", properties=["id", "name"])
    domain, = [row for row in domains if row["name"] == DOMAIN]
    return domain["id"]


def accounts(registry):
    return registry.get("Account", properties=["id", "@type", "name", "domainId", "roles"])


def make_roles(registry):
    inventory = {row["description"]: row["id"] for row in registry.get(
        "Role", properties=["id", "description"]
    )}
    current, = registry.get("Authentication", ids=["singleton"],
                            properties=["defaultUserRoleIds"])
    prior = current["defaultUserRoleIds"]
    if ROLE_NAMES["blocked"] in inventory:
        blocked, = registry.get("Role", ids=[inventory[ROLE_NAMES["blocked"]]],
                                properties=["roleIds"])
        prior = blocked["roleIds"]
    if len(prior) != 1:
        raise ValueError("Expected one stock Stalwart User role")

    managed = {}
    for mode, disabled in {
        "blocked": NO_SEND | {"authenticate": True, "emailReceive": True},
        "receive": NO_SEND,
        "send": NO_FILTER,
    }.items():
        label = ROLE_NAMES[mode]
        record = {"description": label, "roleIds": prior, "disabledPermissions": disabled}
        if label in inventory:
            role_id = inventory[label]
            registry.update("Role", {role_id: record})
        else:
            role_id = registry.create("Role", record)
        managed[mode] = role_id
    registry.update("Authentication", {"singleton": {
        "defaultUserRoleIds": {managed["blocked"]: True},
    }})
    return managed


def provision(registry, db, secrets_path):
    domain_id = local_domain(registry)
    existing = {row["name"]: row for row in accounts(registry)
                if row.get("domainId") == domain_id and row.get("@type") == "User"}
    if set(existing) - set(PILOT):
        raise ValueError("Pilot bootstrap requires a store containing only the approved accounts")
    new_logins = {}
    with db:
        for name in PILOT:
            address = f"{name}@{DOMAIN}"
            if name in existing:
                account_id = existing[name]["id"]
            else:
                password = secrets.token_urlsafe(24)
                account_id = registry.create("Account", {
                    "@type": "User", "name": name, "domainId": domain_id,
                    "roles": {"@type": "User"},
                    "credentials": {"0": {"@type": "Password", "secret": password}},
                })
                new_logins[address] = password
            db.execute("INSERT INTO mailbox VALUES (?, ?)", (account_id, address))
            db.executemany("INSERT INTO mailbox_grant VALUES (?, ?)",
                           [(account_id, "access"), (account_id, "send"), (account_id, "external_send")])
        if new_logins:
            with secrets_path.open("x") as stream:
                json.dump(new_logins, stream, indent=2)
                stream.write("\n")


def status(db):
    return db.execute("""
        SELECT m.address, EXISTS(SELECT 1 FROM mailbox_grant g
            WHERE g.account_id = m.account_id AND g.capability_name = 'access'),
            EXISTS(SELECT 1 FROM mailbox_grant g
            WHERE g.account_id = m.account_id AND g.capability_name = 'send'),
            EXISTS(SELECT 1 FROM mailbox_grant g WHERE g.account_id = m.account_id
                   AND g.capability_name = 'external_send')
        FROM mailbox m ORDER BY m.address
    """).fetchall()


def project(registry, db, roles):
    domain_id = local_domain(registry)
    permissions = {}
    for account_id, address in db.execute("SELECT account_id, address FROM mailbox"):
        grants = {name for name, in db.execute(
            "SELECT capability_name FROM mailbox_grant WHERE account_id = ?", (account_id,)
        )}
        if (grants - {"access", "send", "external_send"}
                or ("send" in grants and "access" not in grants)
                or ("external_send" in grants and "send" not in grants)):
            raise ValueError(f"Invalid grants for {address}")
        permissions[account_id] = (address, grants)

    inventory = accounts(registry)
    by_id = {row["id"]: row for row in inventory}
    for account_id, (address, _) in permissions.items():
        row = by_id.get(account_id, {})
        expected = f"{row.get('name')}@{DOMAIN}"
        if row.get("domainId") != domain_id or row.get("@type") != "User" or expected != address:
            raise ValueError(f"Mailbox binding changed for {address}")

    external = sorted(address for address, grants in permissions.values() if "external_send" in grants)
    if any(not re.fullmatch(r"[a-z][a-z0-9-]{1,62}@ksu\.codes", address) for address in external):
        raise ValueError("An external sender address has an unsupported format")
    rule = {"match": {}, "else": " || ".join(
        f"authenticated_as == '{address}'" for address in external
    ) or "false"}
    registry.update("MtaStageRcpt", {"singleton": {"allowRelaying": rule}})
    installed, = registry.get("MtaStageRcpt", ids=["singleton"], properties=["allowRelaying"])
    if installed["allowRelaying"] != rule:
        raise ValueError("Stalwart external-send ACL readback failed")

    updates = {}
    for row in inventory:
        if row.get("@type") != "User":
            continue
        if row.get("roles", {}).get("@type") == "Admin":
            raise ValueError("Remove the bootstrap administrator before starting public mail")
        if row.get("name") == "webos-mail-operator" and row["id"] not in permissions:
            role_ids = {r["id"]: True for r in registry.get("Role", properties=["description"])
                        if r.get("description") == "WebOS mail lifecycle operator"}
            if len(role_ids) != 1 or row["roles"] != {"@type": "Custom", "roleIds": role_ids}:
                raise ValueError("Unexpected lifecycle operator role")
            continue
        _, grants = permissions.get(row["id"], (None, set()))
        mode = "blocked" if "access" not in grants else ("send" if "send" in grants else "receive")
        value = {"@type": "Custom", "roleIds": {roles[mode]: True}}
        if row["roles"] != value:
            updates[row["id"]] = {"roles": value}
    registry.update("Account", updates)
    applied = {row["id"]: row["roles"] for row in accounts(registry)
               if row["id"] in updates}
    if applied != {key: update["roles"] for key, update in updates.items()}:
        raise ValueError("Stalwart role readback failed")


def set_grant(db, args):
    row = db.execute("SELECT account_id FROM mailbox WHERE address = ?", (args.address,)).fetchone()
    if not row:
        raise ValueError("Provision and explicitly bind the mailbox before changing its grants")
    account_id, = row
    if args.action == "grant":
        prerequisite = {"send": "access", "external_send": "send"}.get(args.capability)
        if prerequisite and not db.execute(
            "SELECT 1 FROM mailbox_grant WHERE account_id = ? AND capability_name = ?",
            (account_id, prerequisite),
        ).fetchone():
            raise ValueError(f"Grant {prerequisite} before granting {args.capability}")
        db.execute("INSERT OR IGNORE INTO mailbox_grant VALUES (?, ?)",
                   (account_id, args.capability))
    elif args.capability == "access":
        db.execute("DELETE FROM mailbox_grant WHERE account_id = ?", (account_id,))
    elif args.capability == "send":
        db.execute("DELETE FROM mailbox_grant WHERE account_id = ? AND capability_name IN ('send','external_send')",
                   (account_id,))
    else:
        db.execute("DELETE FROM mailbox_grant WHERE account_id = ? AND capability_name = ?",
                   (account_id, args.capability))


def create_mailbox(registry, db, address, login_file):
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,62}@ksu\.codes", address):
        raise ValueError("Use a canonical ksu.codes mailbox address")
    if login_file.exists():
        raise FileExistsError(login_file)
    name = address.split("@", 1)[0]
    password = secrets.token_urlsafe(24)
    account_id = registry.create("Account", {
        "@type": "User", "name": name, "domainId": local_domain(registry),
        "roles": {"@type": "User"},
        "credentials": {"0": {"@type": "Password", "secret": password}},
    })
    db.execute("INSERT INTO mailbox VALUES (?, ?)", (account_id, address))
    db.executemany("INSERT INTO mailbox_grant VALUES (?, ?)",
                   [(account_id, "access"), (account_id, "send")])
    with login_file.open("x") as stream:
        json.dump({address: password}, stream)
        stream.write("\n")


def upgrade_pilot(registry, db, login_file):
    earlier = f"mail-test@{DOMAIN}"
    approved = f"test@{DOMAIN}"
    row = db.execute("SELECT account_id FROM mailbox WHERE address = ?", (earlier,)).fetchone()
    if row:
        account_id, = row
        current, = registry.get("Account", ids=[account_id], properties=["name"])
        if current["name"] == "mail-test":
            registry.update("Account", {account_id: {"name": "test"}})
        elif current["name"] != "test":
            raise ValueError("Unexpected pilot account identity")
        logins = json.loads(login_file.read_text())
        if earlier in logins:
            logins[approved] = logins.pop(earlier)
            replacement = login_file.with_suffix(".new")
            with replacement.open("x") as stream:
                json.dump(logins, stream)
                stream.write("\n")
            replacement.replace(login_file)
        db.execute("UPDATE mailbox SET address = ? WHERE account_id = ?", (approved, account_id))
    pilot = tuple(f"{name}@{DOMAIN}" for name in PILOT)
    count, = db.execute("SELECT count(*) FROM mailbox WHERE address IN (?, ?, ?)", pilot).fetchone()
    if count != len(pilot):
        raise ValueError("The approved mailbox pilot is incomplete")
    db.execute("DELETE FROM mailbox_grant WHERE capability_name = 'external_send'")
    db.execute("""INSERT INTO mailbox_grant
                  SELECT account_id, 'external_send' FROM mailbox WHERE address IN (?, ?, ?)""", pilot)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    parser.add_argument("--recovery", type=Path)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("list")
    bootstrap = commands.add_parser("bootstrap")
    bootstrap.add_argument("new_logins", type=Path)
    create = commands.add_parser("provision")
    create.add_argument("address")
    create.add_argument("new_login", type=Path)
    upgrade = commands.add_parser("upgrade-pilot")
    upgrade.add_argument("login_file", type=Path)
    bind = commands.add_parser("bind")
    bind.add_argument("address")
    for action in ("grant", "revoke"):
        command = commands.add_parser(action)
        command.add_argument("address")
        command.add_argument("capability", choices=("access", "send", "external_send"))
    commands.add_parser("apply")
    args = parser.parse_args()
    os.umask(0o077)
    with database(args.database) as db:
        if args.action != "list":
            if not args.recovery:
                parser.error("--recovery is required for policy changes")
            registry = Registry(json.loads(args.recovery.read_text()))
            if args.action == "bootstrap":
                if status(db):
                    parser.error("A pilot policy already exists")
                provision(registry, db, args.new_logins)
            elif args.action == "provision":
                create_mailbox(registry, db, args.address, args.new_login)
            elif args.action == "upgrade-pilot":
                upgrade_pilot(registry, db, args.login_file)
            elif args.action == "bind":
                name, separator, domain = args.address.partition("@")
                if not separator or domain != DOMAIN:
                    parser.error("Use the canonical ksu.codes mailbox address")
                domain_id = local_domain(registry)
                row, = [row for row in accounts(registry) if row.get("domainId") == domain_id
                        and row.get("@type") == "User" and row["name"] == name]
                db.execute("INSERT INTO mailbox VALUES (?, ?)", (row["id"], args.address))
            elif args.action in {"grant", "revoke"}:
                set_grant(db, args)
            project(registry, db, make_roles(registry))
        for address, access, internal, external in status(db):
            print(f"{address}\taccess={bool(access)}\tinternal_send={bool(internal)}"
                  f"\texternal_send={bool(external)}")


if __name__ == "__main__":
    main()
