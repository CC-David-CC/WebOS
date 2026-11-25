"""Translate WebOS mailbox grants into the Stalwart policies used by SMTP and JMAP."""

from dataclasses import dataclass
import re

try:
    from mailcraft_policy import DOMAIN
except ModuleNotFoundError as exc:
    if exc.name != "mailcraft_policy":
        raise
    from policy import DOMAIN


LOCAL_ADDRESS = re.compile(rf"[a-z][a-z0-9-]{{1,62}}@{re.escape(DOMAIN)}")
DENIED_RECIPIENT = f"webos-no-delivery@{DOMAIN}"
OPERATOR_LOGIN = f"webos-mail-operator@{DOMAIN}"
MAIL_SETTINGS = frozenset({"mailbox", "receive_external", "send_local", "send_external"})


@dataclass(frozen=True)
class Access:
    account_id: str
    login: str
    addresses: tuple[str, ...]
    grants: frozenset[str]

    def __post_init__(self):
        if (not self.addresses or self.grants - MAIL_SETTINGS
                or not all(LOCAL_ADDRESS.fullmatch(a) and a not in (DENIED_RECIPIENT, OPERATOR_LOGIN)
                           for a in (self.login, *self.addresses))):
            raise ValueError("Invalid installed mailbox access")

    def allows(self, setting):
        return "mailbox" in self.grants and setting in self.grants

    @property
    def role(self):
        if not self.allows("mailbox"):
            return "blocked"
        return "send" if self.allows("send_local") or self.allows("send_external") else "receive"


def expression(matches, fallback):
    return {
        "match": {str(index): {"if": condition, "then": value}
                  for index, (condition, value) in enumerate(matches)},
        "else": fallback,
    }


def recipient_policy(mailboxes):
    """Return an exact router and relay allowlist for one complete mailbox snapshot.

    Stalwart runs this RCPT stage for public SMTP and authenticated JMAP submission.
    Local messages are always routed to the immutable mailbox login before queuing.
    """
    mailboxes = sorted(mailboxes, key=lambda box: box.login)
    logins = [box.login for box in mailboxes]
    addresses = [address for box in mailboxes for address in box.addresses]
    if len(set(logins)) != len(logins) or len(set(addresses)) != len(addresses):
        raise ValueError("Duplicate mailbox policy binding")
    # Do not let another user's alias point at a canonical account login.
    owner_by_login = {box.login: box.account_id for box in mailboxes}
    if any(owner_by_login.get(a, box.account_id) != box.account_id
           for box in mailboxes for a in box.addresses):
        raise ValueError("Mailbox address is already assigned")

    local = f"rcpt_domain == '{DOMAIN}'"
    deny = f"'{DENIED_RECIPIENT}'"
    authenticated = "!is_empty(authenticated_as)"
    local_rewrites = [
        (f"{local} && authenticated_as == '{OPERATOR_LOGIN}'", deny),
        *((f"{local} && authenticated_as == '{box.login}'", deny)
          for box in mailboxes if not box.allows("send_local")),
    ]
    for box in mailboxes:
        if not box.allows("mailbox"):
            continue
        for address in sorted(box.addresses):
            rule = f"rcpt == '{address}'"
            if not box.allows("receive_external"):
                rule += f" && {authenticated}"
            local_rewrites.append((rule, f"'{box.login}'"))
    # Refuse unconfigured local addresses, disabled inboxes, and raw internal login names.
    local_rewrites.append((local, deny))
    external_senders = [
        (f"authenticated_as == '{box.login}'", "true")
        for box in mailboxes if box.allows("send_external")
    ]
    return {"rewrite": expression(local_rewrites, "false"),
            "allowRelaying": expression(external_senders, "false")}


def apply(registry, mailboxes, roles, *, current):
    """Withdraw removed rights first, then apply the requested roles and routes."""
    before = {box.account_id: box for box in current}
    after = {box.account_id: box for box in mailboxes}
    restrictive = [
        Access(box.account_id, box.login, box.addresses,
               before[box.account_id].grants & box.grants if box.account_id in before else frozenset())
        for box in mailboxes
    ]
    stage = "MtaStageRcpt"
    keys = ["rewrite", "allowRelaying"]

    def activate(value):
        registry.update(stage, {"singleton": value})
        actual, = registry.get(stage, ids=["singleton"], properties=keys)
        if any(actual[key] != value[key] for key in keys):
            raise ValueError("Mail recipient policy readback failed")
        registry.create("Action", {"@type": "ReloadSettings"})

    activate(recipient_policy(restrictive))
    actual_roles = {row["id"]: row["roles"] for row in
                    registry.get("Account", ids=list(after), properties=["roles"])}
    desired_roles = {aid: {"@type": "Custom", "roleIds": {roles[box.role]: True}}
                     for aid, box in after.items()}
    registry.update("Account", {aid: {"roles": wanted}
                                for aid, wanted in desired_roles.items()
                                if actual_roles.get(aid) != wanted})
    roles_after = {row["id"]: row["roles"] for row in
                   registry.get("Account", ids=list(after), properties=["roles"])}
    if roles_after != desired_roles:
        raise ValueError("Mailbox role readback failed")
    activate(recipient_policy(mailboxes))
