#!/usr/bin/env python3
"""Bind an approved mailbox credential to the registered WebOS account's stable subject."""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import stat
from tempfile import NamedTemporaryFile

ROOT = Path("/srv/data/webos-mailcraft")
BINDINGS = Path("/var/lib/webos-mailcraft-sso/mailcraft-bindings")


def readonly(path, statement, values):
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        return db.execute(statement, values).fetchall()


def bind(username, login_file, test, accounts_db):
    address = username + "@ksu.codes"
    [(subject,)] = readonly(accounts_db, """SELECT a.subject FROM accounts a
        JOIN account_policy p USING(subject) WHERE a.username=? AND p.disabled=0""", (username,))
    if not re.fullmatch(r"user:[0-9a-f-]{36}", subject):
        raise ValueError("Unexpected registered account identifier")
    approved = readonly(ROOT / "mailcraft-access.sqlite", """SELECT m.address FROM mailbox m
        JOIN mailbox_grant g USING(account_id) WHERE m.address=? AND g.capability_name='access'""",
        (address,))
    if approved != [(address,)]:
        raise ValueError("Approve mailbox access before binding WebOS sign-in")
    parent = ROOT / "operator"
    if not login_file.is_absolute() or login_file.parent != parent or login_file.resolve() != login_file:
        raise ValueError("Provide the private login file under the MailCraft operator directory")
    details = login_file.lstat()
    if (details.st_uid != 0 or not stat.S_ISREG(details.st_mode)
            or stat.S_IMODE(details.st_mode) != 0o600 or details.st_nlink != 1):
        raise ValueError("A root-owned private mailbox login file is required")
    password = json.loads(login_file.read_text())[address]
    if not isinstance(password, str) or not 1 <= len(password) <= 256 or not password.isprintable():
        raise ValueError("Invalid mailbox credential")
    bindings = json.loads(BINDINGS.read_text())
    if any(key != subject and row["address"] == address for key, row in bindings.items()):
        raise ValueError("The address is already bound to a different WebOS identity")
    if subject in bindings and bindings[subject]["address"] != address:
        raise ValueError("The WebOS identity already has a different mailbox")
    binding = {"address": address, "password": password}
    changed = bindings.get(subject) != binding
    if changed and not test:
        bindings[subject] = binding
        with NamedTemporaryFile(mode="w", dir=BINDINGS.parent, delete=False) as stream:
            json.dump(bindings, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(stream.name, BINDINGS)
    print(f"{address}: " + ("binding is already current" if not changed else
          ("binding can be updated" if test else "binding updated; restart WebOS to load it")))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("login_file", type=Path)
    parser.add_argument("--accounts-db", type=Path, required=True, help="Absolute path to the WebOS identity database")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if os.geteuid() or socket.gethostname().split(".")[0] != "box-webhost":
        parser.error("Run as root on box-webhost")
    if not re.fullmatch("[a-z][a-z0-9]{2,27}", arguments.username):
        parser.error("Use the canonical WebOS username")
    os.umask(0o077)
    bind(arguments.username, arguments.login_file, arguments.check, arguments.accounts_db.resolve(strict=True))
