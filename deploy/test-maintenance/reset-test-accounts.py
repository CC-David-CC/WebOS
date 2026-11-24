"""Keep the two named logins in the retained ksu.codes account registry."""
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


def run(database, operation, *, cleanup_files=False):
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
        if (table_names - {FILES_QUEUE_TABLE} != TABLES
                or journal not in (None, (FILES_QUEUE_SCHEMA,))
                or trigger != (POLICY_TRIGGER,) or policy_version != [(1,)]):
            raise ValueError("Unexpected retained account schema")
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
        result = run(args.database, args.operation, cleanup_files=args.cleanup_files)
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Account maintenance failed ({type(error).__name__})", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
