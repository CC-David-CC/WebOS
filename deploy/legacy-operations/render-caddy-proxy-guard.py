#!/usr/bin/env python3
"""Render a Caddy PROXY-protocol guard; this does not install it."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from network_policy.kernel import render_caddy_proxy_guard


def render(uid):
    rules=render_caddy_proxy_guard(uid)
    unit='''[Unit]
Description=Protect Caddy PROXY listeners from local address spoofing
After=network-pre.target
Before=caddy.service
AssertPathExists=/etc/codi-browser/caddy-proxy-guard.nft

[Service]
Type=oneshot
ExecStart=/usr/sbin/nft -f /etc/codi-browser/caddy-proxy-guard.nft
ExecReload=/usr/sbin/nft -f /etc/codi-browser/caddy-proxy-guard.nft
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
    dropin='''[Unit]
Requires=codi-caddy-proxy-guard.service
After=codi-caddy-proxy-guard.service
'''
    return rules,unit,dropin


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--proxy-uid',type=int,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    try:
        if a.output.exists() or a.output.is_symlink():raise ValueError('New output directory required')
        rules,unit,dropin=render(a.proxy_uid);a.output.mkdir()
        for name,content in [('caddy-proxy-guard.nft',rules),('codi-caddy-proxy-guard.service',unit),('40-codi-caddy-proxy-guard.conf',dropin)]:
            (a.output/name).write_text(content)
    except (OSError,ValueError) as error:p.error(str(error))
