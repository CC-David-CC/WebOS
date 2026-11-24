#!/usr/bin/env python3
"""Activate the isolated MailCraft certificate route and the qualified viewer."""
import argparse
import json
import os
from pathlib import Path
import socket
import sys

SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE.parent))
from viewer_static_operator import CADDY, command, continuity, fetch, peers, replace, sha

BACKUP = Path("/var/backups/webos-mailcraft-c9aeb95f37a1")
PREVIOUS = "4f2d9d136f2f3a73df2e3e04155d301be86b1a99dea3b8b78e924fe156878cfe"
CANDIDATE = "c9aeb95f37a1e032d4044052df1daab1850aede235cdfb5950b0bb17b7b723e3"


def candidates(plan):
    original = (BACKUP / "Caddyfile.before").read_bytes()
    viewer = (BACKUP / "Caddyfile.candidate").read_bytes()
    if sha(original) != plan["beforeSHA256"] or sha(viewer) != plan["candidateSHA256"]:
        raise ValueError("Stored Caddy baseline changed")
    acme = (SOURCE / "certificate.caddy").read_bytes()
    jmap = (SOURCE / "jmap.caddy").read_bytes()
    marker = b"\nksu.codes {\n"
    if viewer.count(marker) != 1 or b"mail.ksu.codes {" in original or b"@mailcraftJmap" in viewer:
        raise ValueError("Unexpected Caddy routes")
    return {"previous": original, "certificate": original + acme,
            "app": viewer.replace(marker, marker + jmap, 1) + acme}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("certificate", "app", "previous"))
    args = parser.parse_args()
    if os.geteuid() or socket.gethostname().split(".")[0] != "box-webhost":
        raise SystemExit("Run as root on box-webhost")
    plan = json.loads((BACKUP / "plan.json").read_text())
    assert plan["release"] == CANDIDATE and plan["previousRelease"] == PREVIOUS
    choices = candidates(plan)
    before = CADDY.read_bytes()
    if before not in choices.values():
        raise SystemExit("Unexpected live Caddy configuration")
    after = choices[args.mode]
    if after == before:
        print(f"MailCraft ingress already at {args.mode}")
        return
    plan["peerPIDs"] = peers()
    continuity(plan)
    validation = BACKUP / f"mailcraft-{args.mode}.caddy"
    validation.write_bytes(after)
    command("caddy", "validate", "--config", str(validation), "--adapter", "caddyfile")
    if CADDY.read_bytes() != before:
        raise SystemExit("Caddy changed during validation")
    try:
        replace(after, plan, "mailcraft-approved")
        command("systemctl", "reload", "caddy.service")
        continuity(plan)
        expected = CANDIDATE if args.mode == "app" else PREVIOUS
        assert sha(fetch("/viewer-release.json")[0]) == expected
    except BaseException:
        if CADDY.read_bytes() == after:
            replace(before, plan, "mailcraft-recovery")
            command("systemctl", "reload", "caddy.service")
        raise
    print(json.dumps({"ingress": args.mode, "configSHA256": sha(after), "viewer": expected}))


if __name__ == "__main__":
    main()
