"""Verify subject-bound mailbox disposal and address reuse on a detached Stalwart fixture."""

import importlib.util
import json
import secrets
import smtplib
import sqlite3
import time
import uuid
from contextlib import closing
from email.message import EmailMessage
from pathlib import Path

from check_policy import MAIL, mailbox, method
from policy import ROLE_NAMES, Registry
from subject_mailboxes import ensure, native_name, reload_routes, reset_handler
from webos_accounts.management import migrate, transaction
from webos_accounts.policy_service import setup_policy
from webos_storage import Principal, UserStore


def stage_check(subject, name, pw, epoch):
    u = {"username": native_name(subject) + "@ksu.codes", "secret": pw}
    aid, _ = mailbox(u)

    def count():
        _, n, data = method(u, "Email/query", {"accountId": aid}, [MAIL])
        assert n == "Email/query"
        return len(data["ids"])

    assert count() == 0
    letter = EmailMessage()
    letter["From"] = "qa@example.net"
    letter["To"] = name + "@ksu.codes"
    letter["Subject"] = "Generation " + str(epoch)
    letter.set_content("Private fixture.")
    for i in range(45):
        try:
            with smtplib.SMTP("127.0.0.1", 2025, timeout=15) as s:
                s.send_message(letter)
            break
        except smtplib.SMTPRecipientsRefused:
            time.sleep(1)
    else:
        raise RuntimeError("online recipient route did not activate")
    for i in range(20):
        if count() == 1:
            return
        time.sleep(0.5)
    raise RuntimeError("missing online delivery")


def main():
    # This destructive acceptance test uses only a disposable namespace and private state.
    import socket

    if {name for _, name in socket.if_nameindex()} != {"lo"}:
        raise SystemExit(
            "Run the detached Stalwart fixture in a loopback-only network namespace"
        )
    p = Path.cwd()

    spec = importlib.util.spec_from_file_location(
        "issuer_reset",
        Path(__file__).resolve().parent.parent
        / "test-maintenance/reset-test-accounts.py",
    )
    reset = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reset)

    def registration(db, name):
        sub = "user:" + str(uuid.uuid4())
        db.execute("INSERT INTO accounts VALUES(?,?,?,?)", (name, sub, "disposable", 0))
        return sub

    def principal(sub):
        return Principal(
            sub, str(uuid.uuid4()), "registered", {}, int(time.time()) + 120
        )

    for d in ("identity", "storage-state", "account-files"):
        (p / d).mkdir(mode=0o700)
    ident = p / "identity/accounts.sqlite3"
    with closing(sqlite3.connect(ident)) as db:
        db.execute(
            "CREATE TABLE accounts (username TEXT PRIMARY KEY, subject TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created INTEGER NOT NULL)"
        )
        db.execute(
            "CREATE TABLE registered_sessions (token_digest TEXT PRIMARY KEY, record TEXT NOT NULL, deadline INTEGER NOT NULL)"
        )
        setup_policy(db)
        owner = registration(db, "retainedqa")
        old = registration(db, "reuseqa")
        db.commit()
    ident.chmod(0o600)
    migrate(ident, owner)
    store = UserStore(p / "storage-state", p / "account-files")
    for subject in (owner, old):
        store.ensure_user(principal(subject))
        store.put(principal(subject), "check.txt", subject.encode())
    reg = Registry(json.loads((p / "online-operator.json").read_text()), online=True)
    (receive,) = [
        r["id"]
        for r in reg.get("Role", properties=["id", "description"])
        if r["description"] == ROLE_NAMES["receive"]
    ]

    def provision(s, username="reuseqa"):
        pw = secrets.token_urlsafe(24)
        with transaction(ident) as db:
            aid = ensure(reg, s, username, pw, receive)
            reload_routes(reg)
            db.execute("INSERT INTO am_mail_binding VALUES(?,?)", (s, aid))
        return pw, aid

    keep_pw, keep_id = provision(owner, "retainedqa")
    stage_check(owner, "retainedqa", keep_pw, 0)
    oldpw, oldid = provision(old)
    stage_check(old, "reuseqa", oldpw, 0)

    def home(sub):
        return store.users_path / uuid.UUID(sub[5:]).hex

    assert home(old).exists()
    import smtplib

    held = smtplib.SMTP("127.0.0.1", 2025, timeout=40)
    held.ehlo()
    assert held.mail("qa@example.net")[0] == 250
    assert held.rcpt("reuseqa@ksu.codes")[0] == 250
    result = reset.run(
        ident,
        "reset",
        cleanup_files=True,
        retire_mailbox=reset_handler(p / "online-operator.json"),
    )
    assert (
        result["files_homes_removed"]
        == result["accounts_deleted"]
        == result["mailboxes_deleted"]
        == 1
    )
    assert (
        not home(old).exists()
        and store.read(principal(owner), "check.txt")["bytes"] == owner.encode()
    )
    with transaction(ident) as db:
        new = registration(db, "reuseqa")
    newpw, newid = provision(new)
    assert oldid != newid and new != old
    code, _ = held.data(
        "From: qa@example.net\r\nTo: reuseqa@ksu.codes\r\nSubject: Held before reset\r\n\r\nPrevious generation.\r\n"
    )
    assert code in (250, 451, 550), code
    held.quit()
    stage_check(new, "reuseqa", newpw, 1)
    from check_policy import MAIL, mailbox, method
    from subject_mailboxes import native_name

    user = {"username": native_name(new) + "@ksu.codes", "secret": newpw}
    aid, _ = mailbox(user)
    time.sleep(2)
    _, method_name, msgs = method(user, "Email/query", {"accountId": aid}, [MAIL])
    assert method_name == "Email/query" and len(msgs["ids"]) == 1
    from check_policy import request

    retain_login = {"username": native_name(owner) + "@ksu.codes", "secret": keep_pw}
    keep_mail, _ = mailbox(retain_login)
    assert keep_mail == keep_id
    _, n, items = method(retain_login, "Email/query", {"accountId": keep_mail}, [MAIL])
    assert n == "Email/query" and len(items["ids"]) == 1
    assert request(
        {"username": native_name(old) + "@ksu.codes", "secret": oldpw}, "/jmap/session"
    )[0] in (401, 403)
    print(
        json.dumps(
            {
                "reset": result,
                "retainedFiles": True,
                "retainedMailboxAndMessage": True,
                "oldLoginDenied": True,
                "newSubject": True,
                "newMailboxId": True,
                "newInboxInitiallyEmpty": True,
                "newMessageReceived": True,
                "preResetRecipientIsolated": True,
            }
        )
    )


if __name__ == "__main__":
    main()
