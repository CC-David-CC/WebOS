"""Exercise the compiled grants against disposable Stalwart over SMTP and JMAP."""

from dataclasses import replace
import json
from pathlib import Path
import secrets
import smtplib
import sys
import time

from access_policy import Access, MAIL_SETTINGS, apply
from check_policy import draft, mailbox, method, request, MAIL, SUBMISSION
from policy import Registry, ROLE_NAMES, local_domain

def verify(registry):
    role_ids = {row["description"]: row["id"] for row in registry.get("Role", properties=["description"])}
    roles = {kind: role_ids[name] for kind, name in ROLE_NAMES.items()}
    domain = local_domain(registry)
    users = {}
    policies = {}
    for name in ("reviewpilot", "reviewlocal", "reviewoutside", "reviewreceive"):
        password = secrets.token_urlsafe(24)
        address = name + "@ksu.codes"
        account_id = registry.create("Account", {
            "@type": "User", "name": name, "domainId": domain,
            "roles": {"@type": "Custom", "roleIds": {roles["send"]: True}},
            "credentials": {"0": {"@type": "Password", "secret": password}},
        })
        users[name] = {"username": address, "secret": password}
        policies[name] = Access(account_id, address, (address,), MAIL_SETTINGS)
    previous = list(policies.values())
    for name, grants in {
        "reviewlocal": {"mailbox", "send_local"},
        "reviewoutside": {"mailbox", "receive_external", "send_external"},
        "reviewreceive": {"mailbox", "receive_external"},
    }.items():
        policies[name] = replace(policies[name], grants=frozenset(grants))
    apply(registry, list(policies.values()), roles, current=previous)

    def smtp(name):
        user = users[name]["username"]
        with smtplib.SMTP("127.0.0.1", 2025, timeout=6) as client:
            client.ehlo()
            client.mail("review@example.net")
            return client.rcpt(user)[0]

    def submit(name, targets):
        user = users[name]
        aid, boxes = mailbox(user)
        job = draft(user, aid, boxes, targets[0], "Mailbox permission fixture")
        job["create"]["message"]["envelope"]["rcptTo"] = [{"email": target} for target in targets]
        _, returned, result = method(user, "EmailSubmission/set", job, [MAIL, SUBMISSION])
        if returned != "EmailSubmission/set" or not result.get("created"):
            assert not result.get("created"), result
            return None
        sid = result["created"]["message"]["id"]
        _, _, answer = method(user, "EmailSubmission/get", {
            "accountId": aid, "ids": [sid], "properties": ["deliveryStatus"],
        }, [MAIL, SUBMISSION])
        return {target: reply["smtpReply"].startswith("2") for target, reply in answer["list"][0]["deliveryStatus"].items()}

    for _ in range(40):
        codes = [smtp(name) for name in ("reviewpilot", "reviewlocal", "reviewoutside", "reviewreceive")]
        if codes[0] == codes[2] == codes[3] == 250 and codes[1] >= 500:
            break
        time.sleep(.25)
    else:
        raise AssertionError(f"Outside receipt policy did not take effect: {codes}")
    local = users["reviewpilot"]["username"]
    outside = "fixture@example.net"
    assert submit("reviewoutside", [local, outside]) == {local: False, outside: True}
    assert submit("reviewlocal", [local, outside]) == {local: True, outside: False}
    assert submit("reviewreceive", [local]) is None

    previous = list(policies.values())
    policies["reviewpilot"] = replace(policies["reviewpilot"], grants=frozenset())
    apply(registry, list(policies.values()), roles, current=previous)
    for _ in range(40):
        if request(users["reviewpilot"], "/jmap/session")[0] in (401, 403) and smtp("reviewpilot") >= 500:
            break
        time.sleep(.25)
    else:
        raise AssertionError("Mailbox suspension did not revoke both JMAP and SMTP")
    assert submit("reviewlocal", [local]) == {local: False}
    print("Verified separate SMTP receipt and JMAP local/external sending, partial delivery, receive-only, and mailbox suspension.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or Path(sys.argv[1]).name != "online-operator.json":
        sys.exit("Requires the operator from the isolated Stalwart fixture.")
    verify(Registry(json.loads(Path(sys.argv[1]).read_bytes()), online=True))
