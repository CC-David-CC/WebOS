"""Coordinate normalized WebOS mailbox grants with the local Stalwart registry."""

import asyncio
import json
import logging
from pathlib import Path
import sqlite3

from webos_accounts.management import migrate_mail_projection, transaction
from access_policy import Access, DENIED_RECIPIENT, MAIL_SETTINGS, apply

try:
    from mailcraft_policy import DOMAIN, ROLE_NAMES, Registry, local_domain
except ModuleNotFoundError as exc:
    if exc.name != "mailcraft_policy":
        raise
    from policy import DOMAIN, ROLE_NAMES, Registry, local_domain


from subject_mailboxes import native_name


class MailControl:
    def __init__(self, database, credentials):
        self.database = database
        self.registry = Registry(json.loads(Path(credentials).read_bytes()), online=True)

    def view(self, db, subject):
        requested = self.requested(db, subject)
        confirmed = self.applied(db, subject)
        if confirmed is None:
            return {"mailState": "unprovisioned", "effectiveMail": None}
        effective = requested if "mailbox" in requested else frozenset()
        return {"mailState": "applied" if confirmed == effective else "pending",
                "effectiveMail": sorted(confirmed)}

    @staticmethod
    def requested(db, subject):
        return frozenset(row[0] for row in db.execute(
            "SELECT setting FROM am_requested_mail WHERE subject=?", (subject,)))

    @staticmethod
    def applied(db, subject):
        if not db.execute("SELECT 1 FROM am_mail_projected WHERE subject=?", (subject,)).fetchone():
            return None
        return frozenset(row[0] for row in db.execute(
            "SELECT setting FROM am_applied_mail WHERE subject=?", (subject,)))

    def inventory(self, db, *, excluding=None):
        domain = local_domain(self.registry)
        roles_by_label = {row["description"]: row["id"]
                          for row in self.registry.get("Role", properties=["description"])}
        roles = {key: roles_by_label[label] for key, label in ROLE_NAMES.items()}
        records = {}
        for row in self.registry.get("Account", properties=["name", "@type", "domainId", "roles", "aliases"]):
            if row["domainId"] != domain:
                continue
            name = f"{row['name']}@{DOMAIN}"
            aliases = tuple(sorted(
                f"{a['name']}@{DOMAIN}" for a in (row.get("aliases") or {}).values()
                if a.get("enable") and a["domainId"] == domain))
            if DENIED_RECIPIENT in (name, *aliases):
                raise ValueError("Mail denial address already exists")
            records[row["id"]] = name, aliases, row
        ops_login = f"mail-ops@{DOMAIN}"
        [(ops_id, (name, aliases, ops))] = [
            (aid, record) for aid, record in records.items() if record[0] == ops_login
        ]
        if ops["@type"] != "User" or set(aliases) != {
            f"{alias}@{DOMAIN}" for alias in ("abuse", "dmarc", "postmaster")
        }:
            raise ValueError("Unexpected operations mailbox addresses")
        ops_access = Access(ops_id, ops_login, (ops_login, *aliases), MAIL_SETTINGS)
        previous, desired, claims = [ops_access], [ops_access], {}
        for sub, username, aid in db.execute(
            "SELECT subject,username,account_id FROM am_mail_binding JOIN accounts USING(subject)"
        ):
            if sub == excluding and aid not in records:
                continue
            login, aliases, row = records[aid]
            public = f"{username}@{DOMAIN}"
            if row["@type"] != "User" or ((login, aliases) not in (
                (public, ()), (f"{native_name(sub)}@{DOMAIN}", (public,)),
            )):
                raise ValueError("Stalwart mailbox binding changed")
            if sub == excluding:
                continue
            grants = self.requested(db, sub)
            if db.execute("SELECT 1 FROM am_retiring WHERE subject=?", (sub,)).fetchone():
                grants = frozenset()
            effective = grants if "mailbox" in grants else frozenset()
            before = self.applied(db, sub)
            previous.append(Access(aid, login, (public,), before or frozenset()))
            desired.append(Access(aid, login, (public,), effective))
            claims[sub] = effective
        return roles, previous, desired, claims

    def read_policy(self):
        row, = self.registry.get("MtaStageRcpt", ids=["singleton"], properties=["rewrite", "allowRelaying"])
        return {key: row[key] for key in ("rewrite", "allowRelaying")}

    def install(self, db, *, excluding=None, force=False):
        roles, previous, desired, claims = self.inventory(db, excluding=excluding)
        if not force and all(self.applied(db, sub) == grants for sub, grants in claims.items()):
            return
        apply(self.registry, desired, roles, current=previous)
        for sub, grants in claims.items():
            db.execute("INSERT OR IGNORE INTO am_mail_projected VALUES(?)", (sub,))
            db.execute("DELETE FROM am_applied_mail WHERE subject=?", (sub,))
            db.executemany("INSERT INTO am_applied_mail VALUES(?,?)",
                           ((sub, setting) for setting in sorted(grants)))

    def reconcile(self, *, force=False):
        with transaction(self.database) as db:
            if force or self.pending(db):
                self.install(db, force=force)

    def pending(self, db):
        grants = db.execute("""
            SELECT setting.subject, setting.setting FROM am_requested_mail setting
            JOIN am_mail_binding binding USING(subject)
            WHERE EXISTS (SELECT 1 FROM am_requested_mail
                          WHERE subject=binding.subject AND setting='mailbox')
              AND NOT EXISTS (SELECT 1 FROM am_retiring WHERE subject=binding.subject)
            EXCEPT SELECT subject,setting FROM am_applied_mail
        """).fetchone()
        if grants:
            return True
        removals = db.execute("""
            SELECT applied.subject, applied.setting FROM am_applied_mail applied
            WHERE NOT EXISTS (SELECT 1 FROM am_requested_mail
                              WHERE subject=applied.subject AND setting=applied.setting)
               OR NOT EXISTS (SELECT 1 FROM am_requested_mail
                              WHERE subject=applied.subject AND setting='mailbox')
        """).fetchone()
        return removals is not None

    def try_reconcile(self, *, force=False):
        try:
            self.reconcile(force=force)
        except (KeyError, OSError, sqlite3.Error, ValueError) as error:
            logging.getLogger(__name__).warning("Mail policy will retry (%s)", type(error).__name__)
            return False
        return True

    async def retry_pending(self, _app):
        async def worker():
            while True:
                await asyncio.sleep(20)
                await asyncio.to_thread(self.try_reconcile)

        task = asyncio.create_task(worker())
        try:
            yield
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    def retire(self, db, subject, account_id):
        # The reset already holds the same SQLite write lock as reconciliation.
        # Withdraw routing before destroying the account, even when retrying.
        self.install(db, excluding=subject, force=True)
        rows = self.registry.get("Account", properties=["id"])
        if any(row["id"] == account_id for row in rows):
            result = self.registry.call("Account", "set", {"destroy": [account_id]})
            if result.get("destroyed") != [account_id]:
                raise ValueError("Stalwart did not acknowledge mailbox destruction")

    def adopt_legacy(self, db):
        roles, _, mailboxes, _ = self.inventory(db)
        singleton = self.read_policy()
        if singleton["rewrite"] != {"match": {}, "else": "false"}:
            raise ValueError("Expected the legacy pilot recipient router")
        profile = [box for box in mailboxes if box.login != f"mail-ops@{DOMAIN}"]
        if {box.login for box in profile} != {f"{name}@{DOMAIN}" for name in ("dflanag3", "test")}:
            raise ValueError("Expected the two canonical pilot mailboxes")
        relay = {"match": {}, "else": " || ".join(
            f"authenticated_as == '{box.login}'" for box in sorted(mailboxes, key=lambda item: item.login))}
        if singleton["allowRelaying"] != relay:
            raise ValueError("Review existing pilot grants before adopting managed mail policy")
        ids = [box.account_id for box in mailboxes]
        rows = self.registry.get("Account", ids=ids, properties=["roles"])
        expected = {"@type": "Custom", "roleIds": {roles["send"]: True}}
        if len(rows) != len(ids) or any(row["roles"] != expected for row in rows):
            raise ValueError("Pilot role does not match the adopted permissions")
        db.execute("INSERT INTO am_mail_projected SELECT subject FROM am_mail_binding")
        db.execute("INSERT INTO am_applied_mail SELECT subject,name FROM am_mail_projected CROSS JOIN am_mail_setting")

    def initialize(self):
        with transaction(self.database) as db:
            existing = db.execute("SELECT 1 FROM sqlite_schema WHERE name='am_mail_projected'").fetchone()
            migrate_mail_projection(db)
            if not existing:
                self.adopt_legacy(db)
        self.reconcile(force=True)
