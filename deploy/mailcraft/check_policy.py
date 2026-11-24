#!/usr/bin/env python3
"""Exercise the actual JMAP submission endpoint with detached fixture accounts."""
import base64
from email.message import EmailMessage
from email.policy import SMTP
from email.utils import formatdate, make_msgid
import json
from pathlib import Path
import secrets
import sys
import time
import urllib.error
import urllib.request

from policy import CORE, DOMAIN, Registry, database, local_domain, make_roles, project

BASE = "http://127.0.0.1:28881"
MAIL = "urn:ietf:params:jmap:mail"
SUBMISSION = "urn:ietf:params:jmap:submission"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def request(user, path, data=None, content_type="application/json"):
    authorization = base64.b64encode(f"{user['username']}:{user['secret']}".encode()).decode()
    request = urllib.request.Request(BASE + path, data, {
        "Authorization": "Basic " + authorization, "Content-Type": content_type,
    })
    try:
        with OPENER.open(request, timeout=8) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, {}


def method(user, name, arguments, capabilities):
    payload = json.dumps({"using": [CORE, *capabilities],
                          "methodCalls": [[name, arguments, "test"]]}).encode()
    status, response = request(user, "/jmap/", payload)
    if status != 200:
        return status, None, {}
    returned, result, _ = response["methodResponses"][0]
    return status, returned, result


def configure(root):
    registry = Registry(json.loads((root / "recovery.json").read_text()))
    domain_id = local_domain(registry)
    fixtures = {}
    with database(root / "mailcraft-access.sqlite") as db:
        for mode in ("approved", "internal", "receiver", "blocked"):
            name = f"policy-qa-{mode}"
            user = {"username": f"{name}@{DOMAIN}", "secret": secrets.token_urlsafe(24)}
            account_id = registry.create("Account", {
                "@type": "User", "name": name, "domainId": domain_id,
                "roles": {"@type": "User"},
                "credentials": {"0": {"@type": "Password", "secret": user["secret"]}},
            })
            fixtures[mode] = user
            db.execute("INSERT INTO mailbox VALUES (?, ?)", (account_id, user["username"]))
            if mode != "blocked":
                db.execute("INSERT INTO mailbox_grant VALUES (?, 'access')", (account_id,))
            if mode in ("approved", "internal"):
                db.execute("INSERT INTO mailbox_grant VALUES (?, 'send')", (account_id,))
            if mode == "approved":
                db.execute("INSERT INTO mailbox_grant VALUES (?, 'external_send')", (account_id,))
        project(registry, db, make_roles(registry))
    with (root / "policy-fixtures.json").open("x") as stream:
        json.dump(fixtures, stream)


def mailbox(user):
    status, session = request(user, "/jmap/session")
    assert status == 200, status
    account_id = session["primaryAccounts"][MAIL]
    status, method_name, data = method(user, "Mailbox/get", {"accountId": account_id}, [MAIL])
    assert status == 200 and method_name == "Mailbox/get" and data["list"]
    return account_id, data["list"]


def draft(user, account_id, boxes, recipient, subject, identity=None):
    drafts, = [box["id"] for box in boxes if box.get("role") == "drafts"]
    message = EmailMessage(policy=SMTP)
    message["From"] = user["username"]
    message["To"] = recipient
    message["Subject"] = subject
    message["Date"] = formatdate(usegmt=True)
    message["Message-ID"] = make_msgid(domain=DOMAIN)
    message.set_content("Detached MailCraft access-policy test.")
    status, blob = request(user, f"/jmap/upload/{account_id}/", message.as_bytes(), "message/rfc822")
    assert status in (200, 201), status
    _, name, imported = method(user, "Email/import", {"accountId": account_id, "emails": {
        "test": {"blobId": blob["blobId"], "mailboxIds": {drafts: True}, "keywords": {"$draft": True}}
    }}, [MAIL])
    assert name == "Email/import" and imported["created"]["test"]["id"]
    if identity is None:
        status, name, identities = method(user, "Identity/get", {"accountId": account_id},
                                          [MAIL, SUBMISSION])
        assert name == "Identity/get", (status, name, identities.get("type"))
        identity, = [row["id"] for row in identities["list"] if row["email"] == user["username"]]
    return {"accountId": account_id, "create": {"message": {
        "emailId": imported["created"]["test"]["id"], "identityId": identity,
        "envelope": {"mailFrom": {"email": user["username"]}, "rcptTo": [{"email": recipient}]},
    }}}


def verify(root):
    users = json.loads((root / "policy-fixtures.json").read_text())
    approved, internal, receiver, blocked = [users[key] for key in ("approved", "internal", "receiver", "blocked")]
    status, _ = request(blocked, "/jmap/session")
    assert status in (401, 403), status
    approved_id, approved_boxes = mailbox(approved)
    internal_id, internal_boxes = mailbox(internal)
    receiver_id, receiver_boxes = mailbox(receiver)
    status, name, result = method(receiver, "Mailbox/get", {"accountId": approved_id}, [MAIL])
    assert status in (401, 403) or (name == "error" and result["type"] in {
        "accountNotFound", "forbidden", "accountNotSupportedByMethod"
    }), (status, name, result.get("type"))
    subject = "MailCraft granted sender " + secrets.token_hex(8)
    submission = draft(approved, approved_id, approved_boxes, receiver["username"], subject)
    status, name, result = method(approved, "EmailSubmission/set", submission, [MAIL, SUBMISSION])
    assert status == 200 and name == "EmailSubmission/set" and result["created"]["message"]["id"], (
        status, name, result.get("notCreated")
    )
    for _ in range(30):
        _, name, results = method(receiver, "Email/query", {
            "accountId": receiver_id, "filter": {"subject": subject},
        }, [MAIL])
        assert name == "Email/query"
        if results["ids"]:
            break
        time.sleep(1)
    else:
        raise RuntimeError("Grant test message was not delivered locally")

    submission = draft(receiver, receiver_id, receiver_boxes, "outside@example.net", "Denied send",
                       identity="a")
    for caps in ([MAIL, SUBMISSION], [MAIL]):
        status, name, result = method(receiver, "EmailSubmission/set", submission, caps)
        errors = [entry["type"] for entry in result.get("notCreated", {}).values()]
        assert status in (400, 401, 403) or (name == "error" and result.get("type") in {
            "forbidden", "unknownMethod", "unknownCapability"
        }) or errors == ["forbidden"], (status, name, result.get("type"), errors)
        assert not result.get("created")
    for user, account, boxes, local in (
        (internal, internal_id, internal_boxes, False),
        (internal, internal_id, internal_boxes, True),
        (approved, approved_id, approved_boxes, False),
    ):
        target = approved["username"] if local else "outside@example.net"
        subject = "MailCraft relay ACL " + secrets.token_hex(8)
        submission = draft(user, account, boxes, target, subject)
        status, name, result = method(user, "EmailSubmission/set", submission, [MAIL, SUBMISSION])
        assert status == 200 and name == "EmailSubmission/set" and result.get("created"), (
            status, name, result.get("notCreated"),
        )
        submission_id = result["created"]["message"]["id"]
        status, name, result = method(user, "EmailSubmission/get", {
            "accountId": account, "ids": [submission_id], "properties": ["deliveryStatus"],
        }, [MAIL, SUBMISSION])
        delivery = result["list"][0]["deliveryStatus"][target]
        denied = user is internal and not local
        if denied:
            assert delivery["delivered"] == "no" and "Relay not allowed" in delivery["smtpReply"], delivery
        else:
            assert "Relay not allowed" not in delivery.get("smtpReply", ""), delivery
    print(json.dumps({"unapprovedSignin": "denied", "receiveOnlySignin": "verified",
                      "crossMailboxAccess": "denied", "approvedSend": "delivered locally",
                      "receiveOnlySubmission": "denied", "internalOnlyRelay": "denied",
                      "internalOnlyLocal": "accepted", "approvedExternalRelay": "accepted"}))


if __name__ == "__main__":
    root = Path.cwd()
    {"configure": configure, "verify": verify}[sys.argv[1]](root)
