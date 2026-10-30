#!/usr/bin/env python3
"""Render (but do not install) the issuer's proxy-only nftables boundary."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from network_policy.kernel import render_issuer_ingress_update


def render(proxy_uid, port):
    rules=render_issuer_ingress_update(proxy_uid, port)
    unit='''[Unit]
Description=Protect Codi issuer login listener from untrusted local processes
After=network-pre.target
Before=codi-ksu-hidden-issuer.service
AssertPathExists=/etc/codi-browser/issuer-ingress.nft

[Service]
Type=oneshot
ExecStart=/usr/sbin/nft -f /etc/codi-browser/issuer-ingress.nft
ExecReload=/usr/sbin/nft -f /etc/codi-browser/issuer-ingress.nft
RemainAfterExit=yes
User=root
Group=root
NoNewPrivileges=yes
CapabilityBoundingSet=CAP_NET_ADMIN
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictSUIDSGID=yes
LockPersonality=yes
RestrictAddressFamilies=AF_UNIX AF_NETLINK
'''
    return rules,unit


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--proxy-uid',type=int,required=True);p.add_argument('--port',type=int,required=True)
    p.add_argument('--rules-output',type=Path,required=True);p.add_argument('--unit-output',type=Path,required=True)
    a=p.parse_args()
    try:
        if a.rules_output.absolute()==a.unit_output.absolute():raise ValueError('Output paths must differ')
        rules,unit=render(a.proxy_uid,a.port)
        for target in (a.rules_output,a.unit_output):
            if target.exists() or target.is_symlink():raise ValueError('Refusing to replace existing output')
        a.rules_output.write_text(rules);a.unit_output.write_text(unit)
    except (ValueError,OSError) as error:p.error(str(error))
