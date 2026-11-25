"""Coordinate normalized WebOS mailbox grants with the local Stalwart registry."""

import asyncio
from base64 import urlsafe_b64encode
from hmac import digest
import json
import logging
from pathlib import Path
import sqlite3

from webos_accounts.management import MAIL_CREATION_SCHEMA, migrate_mail_projection, transaction
from access_policy import Access, DENIED_RECIPIENT, MAIL_SETTINGS, apply

try:
    from mailcraft_policy import DOMAIN, ROLE_NAMES, Registry, local_domain
except ModuleNotFoundError as exc:
    if exc.name != "mailcraft_policy":
        raise
    from policy import DOMAIN, ROLE_NAMES, Registry, local_domain


from subject_mailboxes import native_name


CANONICAL_PILOTS = frozenset(("dflanag3", "test"))
SEND_GRANTS = frozenset(("send_local", "send_external"))


class MailControl:
    def __init__(self, database, credentials, provision_key=None, *,
                 auto_provision=None, legacy_queue=None):
        self.database = database
        if legacy_queue not in (None, "prepare", "confirmed"):
            raise ValueError("Unknown WebOS legacy queue state")
        self.legacy_queue = legacy_queue
        self.registry = Registry(json.loads(Path(credentials).read_bytes()), online=True)
        self.provision_key = Path(provision_key).read_bytes() if provision_key else None
        if self.provision_key is not None and len(self.provision_key) != 32:
            raise ValueError("Expected a 32-byte MailCraft credential key")
        self.auto_provision = self.provision_key is not None if auto_provision is None else auto_provision
        if self.auto_provision and self.provision_key is None:
            raise ValueError("Mailbox provisioning requires its credential key")

    def view(self, db, subject):
        requested = self.requested(db, subject)
        confirmed = self.applied(db, subject)
        if confirmed is None:
            return {"mailState": "unprovisioned" if "mailbox" in requested else "applied",
                    "effectiveMail": None if "mailbox" in requested else []}
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

    def legacy_sender_clear(self, public):
        if self.legacy_queue != "confirmed":
            return False
        try:
            result = self.registry.call("QueuedMessage", "query", {
                "filter": {"text": public}, "limit": 1,
            })
        except (OSError, ValueError):
            logging.getLogger(__name__).warning("Legacy mail queue check will retry")
            return False
        # Stalwart's text filter searches both envelope recipients and
        # return paths. A broader match delays the grant safely.
        return result.get("ids") == []

    def inventory(self, db, *, excluding=None):
        domain = local_domain(self.registry)
        roles_by_label = {row["description"]: row["id"]
                          for row in self.registry.get("Role", properties=["description"])}
        roles = {key: roles_by_label[label] for key, label in ROLE_NAMES.items()}
        records = {}
        for row in self.registry.get("Account", properties=["name", "@type", "domainId", "roles", "aliases", "description"]):
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
        [(ops_id, (_, aliases, ops))] = [
            (aid, record) for aid, record in records.items() if record[0] == ops_login
        ]
        if ops["@type"] != "User" or set(aliases) != {
            f"{alias}@{DOMAIN}" for alias in ("abuse", "dmarc", "postmaster")
        }:
            raise ValueError("Unexpected operations mailbox addresses")
        ops_access = Access(ops_id, ops_login, (ops_login, *aliases), MAIL_SETTINGS)
        previous, desired, claims = [ops_access], [ops_access], {}
        identity_updates = {}
        for sub, username, aid in db.execute(
            "SELECT subject,username,account_id FROM am_mail_binding JOIN accounts USING(subject)"
        ):
            retiring = db.execute("SELECT 1 FROM am_retiring WHERE subject=?", (sub,)).fetchone()
            # Mail destruction can succeed before Files cleanup. A retry must
            # tolerate the missing retired mailbox while preserving its journal.
            if (sub == excluding or retiring) and aid not in records:
                continue
            login, aliases, row = records[aid]
            public = f"{username}@{DOMAIN}"
            subject_name = native_name(sub)
            subject_address = f"{subject_name}@{DOMAIN}"
            is_native = login == subject_address
            is_canonical = login == public and username in CANONICAL_PILOTS
            if row["@type"] != "User" or not (
                (is_canonical and aliases in ((), (subject_address,)))
                or (is_native and aliases in ((), (public,)))
            ):
                raise ValueError("Stalwart mailbox binding changed")
            if sub == excluding:
                continue

            delivery = None
            if is_canonical and self.legacy_queue:
                if row["description"] != "WebOS account " + sub:
                    raise ValueError("Expected the verified pilot mailbox")
                delivery = subject_address
                if not aliases:
                    identity_updates[aid] = subject_name, domain

            grants = self.requested(db, sub) if not retiring else frozenset()
            effective = grants if "mailbox" in grants else frozenset()
            if is_native and not aliases and effective & SEND_GRANTS:
                if username in CANONICAL_PILOTS and not self.legacy_sender_clear(public):
                    # Keep this subject's sending grant pending without
                    # blocking its receipt or changes to other mailboxes.
                    effective -= SEND_GRANTS
                else:
                    identity_updates[aid] = username, domain
            before = self.applied(db, sub)
            previous.append(Access(aid, login, (public,), before or frozenset(), delivery))
            desired.append(Access(aid, login, (public,), effective, delivery))
            claims[sub] = effective
        return roles, previous, desired, claims, identity_updates

    def read_policy(self):
        row, = self.registry.get("MtaStageRcpt", ids=["singleton"], properties=["rewrite", "allowRelaying"])
        return {key: row[key] for key in ("rewrite", "allowRelaying")}

    def install(self, db, *, excluding=None, force=False):
        roles, previous, desired, claims, identity_updates = self.inventory(db, excluding=excluding)
        if not force and not identity_updates and all(
            self.applied(db, sub) == grants for sub, grants in claims.items()
        ):
            return
        for account, (username, domain) in identity_updates.items():
            alias = {"name": username, "domainId": domain, "enable": True}
            self.registry.update("Account", {account: {"aliases": {"0": alias}}})
            row, = self.registry.get("Account", ids=[account], properties=["aliases"])
            if any(row["aliases"].get("0", {}).get(k) != v for k, v in alias.items()):
                raise ValueError("Mail sending address readback failed")
        apply(self.registry, desired, roles, current=previous,
              isolate_return_path=self.legacy_queue is not None)
        for sub, grants in claims.items():
            db.execute("INSERT OR IGNORE INTO am_mail_projected VALUES(?)", (sub,))
            db.execute("DELETE FROM am_applied_mail WHERE subject=?", (sub,))
            db.executemany("INSERT INTO am_applied_mail VALUES(?,?)",
                           ((sub, setting) for setting in sorted(grants)))

    def reconcile(self, *, force=False):
        with transaction(self.database) as db:
            if force or self.pending(db):
                self.install(db, force=force)

    def credential(self, subject):
        name = native_name(subject)
        if self.provision_key is None:
            raise ValueError("MailCraft provisioning is disabled")
        secret = digest(self.provision_key, f"webos-mailcraft/v1:{subject}".encode(), "sha256")
        return f"{name}@{DOMAIN}", urlsafe_b64encode(secret).decode().rstrip("=")

    def binding_details(self, subject):
        with transaction(self.database, write=False) as db:
            username, = db.execute("SELECT username FROM accounts WHERE subject=?", (subject,)).fetchone()
        login, password = self.credential(subject)
        return f"{username}@{DOMAIN}", password, login

    def native_record(self, subject):
        name = native_name(subject)
        domain = local_domain(self.registry)
        matches = [
            row for row in self.registry.get("Account", properties=["name", "domainId", "@type", "description", "aliases"])
            if row["name"] == name and row["domainId"] == domain
        ]
        if matches:
            row, = matches
            if row["@type"] != "User" or row["description"] != "WebOS account " + subject or row.get("aliases"):
                raise ValueError("Native mailbox binding changed")
            return row["id"]
        return None

    def provision(self, subject):
        _, secret = self.credential(subject)
        with transaction(self.database) as db:
            if not self.eligible(db, subject):
                return
            db.execute("INSERT OR IGNORE INTO am_mail_creating VALUES(?)", (subject,))
        with transaction(self.database) as db:
            # The reset may have acquired the write lock between these transactions.
            if not self.eligible(db, subject):
                return
            native = native_name(subject)
            domain = local_domain(self.registry)
            public_name, = db.execute("SELECT username FROM accounts WHERE subject=?", (subject,)).fetchone()
            for row in self.registry.get("Account", properties=["name", "domainId", "aliases"]):
                if (row["domainId"] == domain and row["name"] == public_name) or any(
                    item["domainId"] == domain and item["name"] == public_name
                    for item in (row.get("aliases") or {}).values()
                ):
                    raise ValueError("Public mailbox name is already assigned")
            aid = self.native_record(subject)
            if aid is None:
                blocked, = [
                    row["id"] for row in self.registry.get("Role", properties=["description"])
                    if row["description"] == ROLE_NAMES["blocked"]
                ]
                aid = self.registry.create("Account", {
                    "@type": "User", "name": native, "domainId": domain,
                    "description": "WebOS account " + subject,
                    "roles": {"@type": "Custom", "roleIds": {blocked: True}},
                    "credentials": {"0": {"@type": "Password", "secret": secret}},
                    "quotas": {"maxDiskQuota": 128 * 1024 * 1024},
                })
                if aid != self.native_record(subject):
                    raise ValueError("New Stalwart mailbox readback failed")
            db.execute("INSERT INTO am_mail_binding VALUES(?,?)", (subject, aid))
            db.execute("DELETE FROM am_mail_creating WHERE subject=?", (subject,))
        self.reconcile()

    @staticmethod
    def eligible(db, subject):
        return db.execute("""
            SELECT 1 FROM am_requested_mail JOIN account_policy USING(subject)
            WHERE subject=? AND setting='mailbox' AND disabled=0
              AND NOT EXISTS (SELECT 1 FROM am_mail_binding WHERE subject=?)
              AND NOT EXISTS (SELECT 1 FROM am_retiring WHERE subject=?)
        """, (subject, subject, subject)).fetchone() is not None

    def provision_one_pending(self):
        if not self.auto_provision:
            return
        with transaction(self.database, write=False) as db:
            subjects = [row[0] for row in db.execute("""
                SELECT a.subject FROM accounts a JOIN am_requested_mail m USING(subject)
                JOIN account_policy USING(subject)
                WHERE m.setting='mailbox' AND disabled=0
                  AND NOT EXISTS (SELECT 1 FROM am_mail_binding WHERE subject=a.subject)
                  AND NOT EXISTS (SELECT 1 FROM am_retiring WHERE subject=a.subject)
                ORDER BY a.created DESC, a.subject LIMIT 8
            """)]
        for subject in subjects:
            try:
                self.provision(subject)
            except (KeyError, OSError, sqlite3.Error, ValueError) as error:
                logging.getLogger(__name__).warning("Mailbox provisioning will retry (%s)", type(error).__name__)

    def authorized_mailbox(self, subject, *, create=False):
        with transaction(self.database, write=False) as db:
            available = self.applied(db, subject)
            requested = "mailbox" in self.requested(db, subject)
            can_provision = self.auto_provision and self.eligible(db, subject)
        if create and can_provision:
            self.provision(subject)
            return self.authorized_mailbox(subject)
        if not available or not requested or "mailbox" not in available:
            return None
        return True

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
                await asyncio.sleep(5 if self.auto_provision else 20)
                await asyncio.to_thread(self.try_reconcile)
                await asyncio.to_thread(self.provision_one_pending)

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
        aid = account_id or self.native_record(subject)
        rows = self.registry.get("Account", properties=["id"])
        if aid and any(row["id"] == aid for row in rows):
            blocked, = [
                row["id"] for row in self.registry.get("Role", properties=["description"])
                if row["description"] == ROLE_NAMES["blocked"]
            ]
            expected = {"@type": "Custom", "roleIds": {blocked: True}}
            self.registry.update("Account", {aid: {"roles": expected}})
            row, = self.registry.get("Account", ids=[aid], properties=["roles"])
            if row["roles"] != expected:
                raise ValueError("Mailbox suspension readback failed")
            result = self.registry.call("Account", "set", {"destroy": [aid]})
            if result.get("destroyed") != [aid]:
                raise ValueError("Stalwart did not acknowledge mailbox destruction")
            return True
        return False

    def adopt_legacy(self, db):
        roles, _, mailboxes, _, _ = self.inventory(db)
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
            if self.provision_key is not None:
                db.execute(MAIL_CREATION_SCHEMA)
            if not existing:
                self.adopt_legacy(db)
        self.reconcile(force=True)
