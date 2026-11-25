"""Reset expiring test accounts and their subject-owned data."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import stat
import sys
import time
import uuid
from contextlib import closing

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

KEEP = ("dflanag3", "test")
TABLES = {
    "account_policy",
    "account_policy_metadata",
    "accounts",
    "registered_sessions",
}
POLICY_TRIGGER = (
    "CREATE TRIGGER account_policy_on_insert AFTER INSERT ON accounts "
    "BEGIN INSERT INTO account_policy VALUES(NEW.subject,0,0); END"
)
FILES_QUEUE_TABLE = "files_cleanup_pending"
FILES_QUEUE_SCHEMA = (
    "CREATE TABLE files_cleanup_pending (subject TEXT PRIMARY KEY NOT NULL) WITHOUT ROWID"
)


def assert_private(path, *, is_dir):
    info = path.lstat()
    mode = 0o700 if is_dir else 0o600
    kind = stat.S_ISDIR if is_dir else stat.S_ISREG
    if not kind(info.st_mode) or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != mode:
        raise ValueError("Issuer state must be private and owned by the service user")
    if not is_dir and info.st_nlink != 1:
        raise ValueError("Account database cannot be hard-linked")


def retained_rows(db):
    return db.execute(
        "SELECT username, subject, password_hash, created, disabled, generation "
        "FROM accounts JOIN account_policy USING(subject) "
        "WHERE username IN (?, ?) ORDER BY username",
        KEEP,
    ).fetchall()


def seed_test(db):
    password = sys.stdin.readline(129).removesuffix("\n")
    if not 4 <= len(password) <= 32 or any(ord(ch) < 32 or ord(ch) == 127 for ch in password):
        raise ValueError("Invalid test password input")

    hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=1, hash_len=32, salt_len=16)
    row = db.execute("SELECT subject, password_hash FROM accounts WHERE username='test'").fetchone()
    if row is None:
        db.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)",
                   ("test", "user:" + str(uuid.uuid4()), hasher.hash(password), int(time.time())))
        return "created"
    subject, encoded = row
    try:
        unchanged = hasher.verify(encoded, password)
    except VerifyMismatchError:
        unchanged = False
    if not unchanged:
        db.execute("UPDATE accounts SET password_hash=? WHERE username='test'", (hasher.hash(password),))
        db.execute("UPDATE account_policy SET generation=generation+1 WHERE subject=?", (subject,))
        db.execute("DELETE FROM registered_sessions WHERE json_extract(record, '$.sub')=?", (subject,))
    db.execute("UPDATE account_policy SET disabled=0 WHERE subject=?", (subject,))
    return "verified" if unchanged else "updated"


def managed_reset(db, operation, homes, retire_mailbox, mail_control):
    from webos_accounts.management import revoke_sessions
    if operation == "seed":
        raise ValueError("Use the subject-based account operator after migration")
    active_admin = db.execute(
        "SELECT 1 FROM am_retained JOIN am_membership USING(subject) JOIN account_policy USING(subject) "
        "WHERE role='administrator' AND disabled=0 LIMIT 1"
    ).fetchone()
    if not active_admin:
        raise ValueError("An active retained administrator is required")
    targets = db.execute(
        "SELECT a.subject, a.username, m.account_id FROM accounts a "
        "LEFT JOIN am_mail_binding m USING(subject) WHERE NOT EXISTS "
        "(SELECT 1 FROM am_retained r WHERE r.subject=a.subject) ORDER BY a.subject"
    ).fetchall()
    retained, = db.execute("SELECT count(*) FROM am_retained").fetchone()
    pending = []
    if db.execute("SELECT 1 FROM sqlite_schema WHERE name='files_cleanup_pending'").fetchone():
        pending = [sub for sub, in db.execute("SELECT subject FROM files_cleanup_pending")]
    if operation == "preview":
        return dict(action="preview", retained=retained, accounts_to_delete=len(targets),
                    mailboxes_to_delete=sum(mail is not None for _,_,mail in targets),
                    files_cleanups_pending=len(pending),
                    files_homes_to_delete=len(homes.existing_homes([s for s,_,_ in targets]+pending))
                    if homes else None)
    if homes is None:
        raise ValueError("Managed account resets require Files cleanup")
    for subject in pending:
        if db.execute("SELECT 1 FROM accounts WHERE subject=?", (subject,)).fetchone():
            raise ValueError("A pending Files cleanup subject is still registered")
        homes.retire_and_remove(subject)
        db.execute("DELETE FROM files_cleanup_pending WHERE subject=?", (subject,))
    # Persist the exact identities before calling either external store. Registration
    # keeps the username occupied until that subject's cleanup has succeeded.
    sessions = 0
    for subject, _, _ in targets:
        if db.execute("INSERT OR IGNORE INTO am_retiring VALUES(?)", (subject,)).rowcount:
            sessions += db.execute("SELECT count(*) FROM registered_sessions WHERE json_extract(record,'$.sub')=?",
                                   (subject,)).fetchone()[0]
            db.execute("UPDATE account_policy SET disabled=1 WHERE subject=?", (subject,))
            revoke_sessions(db, subject)
    db.commit()
    removed = boxes = deleted = 0
    failures = []
    for subject, username, _ in targets:
        try:
            result = finish_retirement(db, homes, subject, username, retire_mailbox, mail_control)
        except (OSError, ValueError, sqlite3.Error) as exc:
            db.rollback()
            failures.append(exc)
            continue
        removed += result[0]
        boxes += result[1]
        deleted += result[2]
    if failures:
        # systemd observes failure and the next run retries the still-disabled subjects.
        raise failures[0]
    return dict(action="reset", retained=retained, accounts_deleted=deleted, sessions_deleted=sessions,
                mailboxes_deleted=boxes, files_homes_removed=removed, files_cleanups_completed=len(pending)+deleted)


def finish_retirement(db, homes, subject, username, retire_mailbox, mail_control):
    db.execute("BEGIN IMMEDIATE")
    row = db.execute("SELECT a.username,m.account_id FROM am_retiring JOIN accounts a USING(subject) "
                     "LEFT JOIN am_mail_binding m USING(subject) WHERE subject=? AND "
                     "NOT EXISTS (SELECT 1 FROM am_retained WHERE subject=?)", (subject,subject)).fetchone()
    if row is None:
        db.rollback()
        return 0, 0, 0
    if row[0] != username:
        raise ValueError("Retiring subject identity changed")
    if row[1] is not None:
        if mail_control:
            mail_control.retire(db, subject, row[1])
        elif retire_mailbox:
            retire_mailbox(subject, username, row[1])
        else:
            raise ValueError("Managed mailbox cleanup service is required")
        db.execute("DELETE FROM am_mail_binding WHERE subject=?", (subject,))
    removed = homes.retire_and_remove(subject)
    db.execute("DELETE FROM account_policy WHERE subject=?", (subject,))
    deleted = db.execute("DELETE FROM accounts WHERE subject=?", (subject,)).rowcount
    if db.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("Account integrity verification failed")
    db.commit()
    return removed, int(row[1] is not None), deleted


def run(database, operation, *, cleanup_files=False, retire_mailbox=None, mail_control=None):
    if database.resolve(strict=True) != database or database.name != "accounts.sqlite3":
        raise ValueError("Expected the direct retained issuer database path")
    assert_private(database.parent, is_dir=True)
    assert_private(database, is_dir=False)
    homes = None
    if cleanup_files:
        if database.parent.name != "identity" or operation == "seed":
            raise ValueError("Expected issuer state for a Files cleanup preview or reset")
        from webos_storage.account_cleanup import AccountHomeCleanup

        state = database.parent.parent
        homes = AccountHomeCleanup(state / "storage-state", state / "account-files")
    mode = "ro" if operation == "preview" else "rw"
    with closing(sqlite3.connect(database.as_uri() + "?mode=" + mode, uri=True, timeout=10)) as db:
        db.execute("PRAGMA foreign_keys=ON")
        if operation != "preview":
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA secure_delete=ON")
        db.execute("BEGIN IMMEDIATE" if operation != "preview" else "BEGIN")
        table_names = {row[0] for row in db.execute("SELECT name FROM sqlite_schema WHERE type='table'")}
        trigger = db.execute(
            "SELECT sql FROM sqlite_schema WHERE type='trigger' AND name='account_policy_on_insert'"
        ).fetchone()
        journal = db.execute(
            "SELECT sql FROM sqlite_schema WHERE type='table' AND name=?", (FILES_QUEUE_TABLE,)
        ).fetchone()
        policy_version = db.execute("SELECT version FROM account_policy_metadata").fetchall()
        managed = "am_version" in table_names
        allowed = TABLES
        if managed:
            from webos_accounts.management import MAIL_PROJECTION_TABLES, TABLES as MANAGEMENT_TABLES
            allowed = TABLES | MANAGEMENT_TABLES
            if table_names & MAIL_PROJECTION_TABLES:
                allowed |= MAIL_PROJECTION_TABLES
                if operation == "reset" and mail_control is None:
                    raise ValueError("Managed mail policy is required by this account database")
            if db.execute("SELECT version FROM am_version").fetchall() != [(1,)]:
                raise ValueError("Unexpected management schema version")
        if (table_names - {FILES_QUEUE_TABLE} != allowed
                or journal not in (None, (FILES_QUEUE_SCHEMA,))
                or trigger != (POLICY_TRIGGER,) or policy_version != [(1,)]):
            raise ValueError("Unexpected retained account schema")
        if managed:
            return managed_reset(db, operation, homes, retire_mailbox, mail_control)
        before = retained_rows(db)
        if not before or before[0][0] != "dflanag3" or before[0][4]:
            raise ValueError("Expected the enabled retained owner account")
        if operation == "seed":
            status = seed_test(db)
            if retained_rows(db)[0] != before[0]:
                raise ValueError("Owner credential or policy changed")
            db.commit()
            return dict(action="seed", test=status)
        if tuple(row[0] for row in before) != KEEP or before[1][4]:
            raise ValueError("Both retained accounts must be present and enabled")
        targets = [
            subject for (subject,) in db.execute("SELECT subject FROM accounts WHERE username NOT IN (?, ?)", KEEP)
        ]
        pending = []
        if homes is not None and journal is not None:
            if db.execute("SELECT 1 FROM files_cleanup_pending JOIN accounts USING(subject) LIMIT 1").fetchone():
                raise ValueError("A pending Files cleanup subject is still registered")
            pending = [subject for (subject,) in db.execute("SELECT subject FROM files_cleanup_pending")]
        existing = homes.existing_homes(targets + pending) if homes is not None else set()
        if operation == "preview":
            result = dict(action="preview", retained=len(before), accounts_to_delete=len(targets))
            if homes is not None:
                result.update(files_homes_to_delete=len(existing), files_cleanups_pending=len(pending))
            return result
        if homes is not None and targets:
            # Selection and login deletion commit together. A failed login
            # transaction cannot leave a cleanup job for a surviving account.
            if journal is None:
                db.execute(FILES_QUEUE_SCHEMA)
            db.executemany("INSERT INTO files_cleanup_pending VALUES (?)", ((subject,) for subject in targets))
        subjects = tuple(row[1] for row in before)
        cleared = db.execute(
            "DELETE FROM registered_sessions WHERE json_extract(record, '$.sub') IS NULL "
            "OR json_extract(record, '$.sub') NOT IN (?, ?)",
            subjects,
        ).rowcount
        db.execute("DELETE FROM account_policy WHERE subject NOT IN (?, ?)", subjects)
        deleted = db.execute("DELETE FROM accounts WHERE username NOT IN (?, ?)", KEEP).rowcount
        if deleted != len(targets) or retained_rows(db) != before or db.execute("PRAGMA foreign_key_check").fetchone():
            raise ValueError("Account integrity verification failed")
        db.commit()
        result = dict(action="reset", retained=len(before), accounts_deleted=deleted, sessions_deleted=cleared)
        if homes is not None:
            removed = 0
            completed = 0
            for subject in pending + targets:
                # Hold the issuer write lock from the absence check through
                # acknowledgement, so a restored login cannot race removal.
                db.execute("BEGIN IMMEDIATE")
                if not db.execute("SELECT 1 FROM files_cleanup_pending WHERE subject=?", (subject,)).fetchone():
                    db.rollback()
                    continue
                if db.execute("SELECT 1 FROM accounts WHERE subject=?", (subject,)).fetchone():
                    raise ValueError("A pending Files cleanup subject is still registered")
                removed += homes.retire_and_remove(subject)
                db.execute("DELETE FROM files_cleanup_pending WHERE subject=?", (subject,))
                db.commit()
                completed += 1
            result.update(files_homes_removed=removed, files_cleanups_completed=completed)
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("preview", "seed", "reset"))
    parser.add_argument("database", type=Path)
    parser.add_argument("--cleanup-files", action="store_true")
    args = parser.parse_args()
    try:
        retire_mailbox = None
        mail_control = None
        credentials = os.environ.get("CREDENTIALS_DIRECTORY")
        if args.operation == "reset" and credentials:
            operator = Path(credentials) / "mail-lifecycle-operator"
            if operator.exists():
                if os.environ.get("WEBOS_MAILCRAFT_MANAGED_POLICY") == "1":
                    from mail_control import MailControl
                    mail_control = MailControl(args.database, operator)
                else:
                    from subject_mailboxes import reset_handler

                    def retire_mailbox(subject, username, account_id):
                        reset_handler(operator)(subject, username, account_id)
        result = run(args.database, args.operation, cleanup_files=args.cleanup_files,
                     retire_mailbox=retire_mailbox, mail_control=mail_control)
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Account maintenance failed ({type(error).__name__})", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
