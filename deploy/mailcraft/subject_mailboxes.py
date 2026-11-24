"""Operate on resettable Stalwart mailboxes using their immutable WebOS subject."""

import re
from uuid import UUID

try:
    from mailcraft_policy import DOMAIN, ROLE_NAMES, Registry, accounts, local_domain
except ModuleNotFoundError as exc:
    if exc.name != "mailcraft_policy":
        raise
    from policy import DOMAIN, ROLE_NAMES, Registry, accounts, local_domain

PUBLIC_NAME = re.compile("[a-z][a-z0-9]{2,27}")
NATIVE_NAME = re.compile("webos-u-[0-9a-f]{32}")
ROUTE_IF = re.compile(r"rcpt == '([a-z][a-z0-9]{2,27})@ksu\.codes'")
ROUTE_TO = re.compile(r"'(webos-u-[a-f0-9]{32})@ksu\.codes'")


def native_name(subject):
    prefix, sep, value = subject.partition(":")
    if prefix != "user" or not sep or str(UUID(value)) != value:
        raise ValueError("Expected a canonical WebOS subject")
    return "webos-u-" + UUID(value).hex


def recipient_routes(registry):
    (stage,) = registry.get("MtaStageRcpt", ids=["singleton"], properties=["rewrite"])
    rule = stage["rewrite"]
    if rule["else"] not in ("", "false") or not isinstance(rule["match"], dict):
        raise ValueError("The existing recipient rewrite requires an operator merge")
    routes = {}
    for item in rule["match"].values():
        key, dest = ROUTE_IF.fullmatch(item["if"]), ROUTE_TO.fullmatch(item["then"])
        if not key or not dest or key[1] in routes:
            raise ValueError("Unexpected existing recipient rewrite")
        routes[key[1]] = dest[1]
    return routes


def route(registry, username, native, *, enable):
    if not PUBLIC_NAME.fullmatch(username) or not NATIVE_NAME.fullmatch(native):
        raise ValueError("Invalid mailbox identity")
    routes = recipient_routes(registry)
    if username in routes and routes[username] != native:
        raise ValueError("Address is bound to a different subject")
    if enable:
        if routes.get(username) == native:
            return
        routes[username] = native
    else:
        if username not in routes:
            return
        del routes[username]
    clauses = {
        str(index): {
            "if": f"rcpt == '{name}@{DOMAIN}'",
            "then": f"'{destination}@{DOMAIN}'",
        }
        for index, (name, destination) in enumerate(sorted(routes.items()))
    }
    registry.update(
        "MtaStageRcpt", {"singleton": {"rewrite": {"match": clauses, "else": "false"}}}
    )
    if recipient_routes(registry) != routes:
        raise ValueError("Recipient routing readback failed")


def locate(registry, subject, account_id=None):
    native = native_name(subject)
    domain = local_domain(registry)
    rows = [
        row
        for row in accounts(registry)
        if row["id"] == account_id
        or (row.get("domainId") == domain and row.get("name") == native)
    ]
    if not rows:
        return None
    (row,) = rows
    if (
        row["@type"] != "User"
        or row["domainId"] != domain
        or row["name"] != native
        or (account_id is not None and row["id"] != account_id)
    ):
        raise ValueError("Stalwart mailbox identity changed")
    return row


def ensure(registry, subject, username, password, receive_role):
    """Call under the single writer lock with a persisted per-subject password."""
    if not PUBLIC_NAME.fullmatch(username):
        raise ValueError("Invalid WebOS mailbox name")
    native = native_name(subject)
    existing = locate(registry, subject)
    if existing is None:
        domain = local_domain(registry)
        # Avoid shadowing a pre-existing user, alias, group or pilot address.
        for row in registry.get("Account", properties=["name", "domainId", "aliases"]):
            if row.get("domainId") == domain and row.get("name") == username:
                raise ValueError("Public mailbox name is already in use")
            if any(
                alias.get("domainId") == domain and alias.get("name") == username
                for alias in (row.get("aliases") or {}).values()
            ):
                raise ValueError("Public mailbox alias is already in use")
        if username in recipient_routes(registry):
            raise ValueError("Public mailbox route is already in use")
        account_id = registry.create(
            "Account",
            {
                "@type": "User",
                "name": native,
                "domainId": domain,
                "roles": {"@type": "Custom", "roleIds": {receive_role: True}},
                "credentials": {"0": {"@type": "Password", "secret": password}},
            },
        )
        existing = locate(registry, subject, account_id)
    route(registry, username, native, enable=True)
    return existing["id"]


def retire(registry, subject, username, account_id, blocked_role):
    """Revoke delivery and authentication before destroying exactly this account."""
    row = locate(registry, subject, account_id)
    if row:
        role = {"@type": "Custom", "roleIds": {blocked_role: True}}
        registry.update("Account", {account_id: {"roles": role}})
        if locate(registry, subject, account_id)["roles"] != role:
            raise ValueError("Mailbox suspension readback failed")
    route(registry, username, native_name(subject), enable=False)
    if row:
        result = registry.call("Account", "set", {"destroy": [account_id]})
        if result.get("destroyed") != [account_id]:
            raise ValueError("Stalwart did not acknowledge mailbox deletion")
    if locate(registry, subject, account_id):
        raise ValueError("Stalwart mailbox still present after deletion")


def reload_routes(registry):
    registry.create("Action", {"@type": "ReloadSettings"})


def retire_online(registry, subject, username, account_id, blocked_role):
    # Reload even when retrying after a successful write and an interrupted reload.
    retire(registry, subject, username, account_id, blocked_role)
    reload_routes(registry)


def reset_handler(credential_path):
    import json
    from pathlib import Path
    from stat import S_ISREG

    path = Path(credential_path)
    info = path.lstat()
    if not S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_size > 4096:
        raise ValueError("Use a protected, read-only mail operator credential")
    with path.open() as source:
        registry = Registry(json.load(source), online=True)
    roles = registry.get("Role", properties=["id", "description"])
    (blocked,) = [
        row["id"] for row in roles if row["description"] == ROLE_NAMES["blocked"]
    ]
    return lambda sub, name, account_id: retire_online(
        registry, sub, name, account_id, blocked
    )
