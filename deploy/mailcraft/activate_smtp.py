#!/usr/bin/env python3
"""Check SMTP locally before changing the persistent, narrow TCP 25 firewall rule."""
import os
from pathlib import Path
from smtplib import SMTP
import socket
import ssl
import subprocess
import sys
from tempfile import NamedTemporaryFile

FIREWALL = Path("/etc/nftables.d/webhost-guard.nft")
BACKUP = Path("/var/backups/webos-mailcraft-c9aeb95f37a1/webhost-guard.before.nft")
BEFORE = b"        tcp dport {80,443} counter accept\n"
RULE = b'        meta nfproto ipv4 tcp dport 25 counter accept comment "WebOS MailCraft MX"\n'
HOST = "mail.ksu.codes"


def check_smtp():
    with SMTP("127.0.0.1", 25, timeout=8) as client:
        client._host = HOST
        assert client.ehlo()[0] == 250
        assert not client.has_extn("auth")
        assert client.starttls(context=ssl.create_default_context())[0] == 220
        assert client.ehlo()[0] == 250
        assert not client.has_extn("auth")
        for recipient, response in (("test@ksu.codes", 250),
                                    ("invalid-recipient-check@ksu.codes", 550),
                                    ("outside@example.net", 550)):
            assert client.mail("mail-probe@example.org")[0] == 250
            actual, _ = client.rcpt(recipient)
            assert actual == response, (recipient, actual, response)
            assert client.rset()[0] == 250


def install(data):
    with NamedTemporaryFile(dir=FIREWALL.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), FIREWALL.stat().st_mode & 0o777)
    try:
        subprocess.run(["nft", "-c", "-f", temporary], check=True)
        os.replace(temporary, FIREWALL)
    finally:
        temporary.unlink(missing_ok=True)


def main(action):
    if os.geteuid() or socket.gethostname().split(".")[0] != "box-webhost":
        raise SystemExit("Run as root on box-webhost")
    current = FIREWALL.read_bytes()
    if action == "enable":
        check_smtp()
        if RULE in current:
            print("TCP 25 firewall rule already installed. Verified local SMTP.")
            return
        assert current.count(BEFORE) == 1
        if not BACKUP.exists():
            with BACKUP.open("xb") as stream:
                stream.write(current)
        assert BACKUP.read_bytes() == current
        candidate = current.replace(BEFORE, RULE + BEFORE, 1)
    elif action == "disable":
        assert current.count(RULE) == 1
        candidate = current.replace(RULE, b"", 1)
    else:
        raise SystemExit("Specify enable or disable")
    install(candidate)
    try:
        subprocess.run(["systemctl", "reload", "webhost-firewall.service"], check=True)
    except BaseException:
        install(current)
        subprocess.run(["systemctl", "reload", "webhost-firewall.service"], check=True)
        raise
    print(f"MailCraft inbound IPv4 TCP 25 firewall rule {action}d")


if __name__ == "__main__":
    main(sys.argv[1])
