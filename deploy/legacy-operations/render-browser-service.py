#!/usr/bin/env python3
"""Render a KSU Browser relay service; no install or activation is performed."""
import argparse
from pathlib import Path
import re

def digest(value):
    if not re.fullmatch('[0-9a-f]{64}',value):raise ValueError('A 64-character lowercase SHA-256 is required')
    return value

def caddy_dependency():
    # The static relay is pulled in whenever the boot-enabled web server starts.
    # A relay failure must not prevent the rest of the website from starting.
    return '[Unit]\nWants=codi-browser-relay.service\nAfter=codi-browser-relay.service\n'

def render(*,runtime,venv,issuer,policy,proxy_uid,proxy_gid,reports=False):
    for value in (runtime,venv,issuer,policy):digest(value)
    if any(type(value) is not int or not 1<=value<=2**31-1 for value in (proxy_uid,proxy_gid)):
        raise ValueError('Non-root numeric proxy UID and GID required')
    executable='/srv/codi-browser/venvs/'+venv+'/bin/python'
    script='/srv/codi-browser/releases/'+runtime+'/active-system/scripts/serve-browser-relay.py'
    args=[executable,'-I','-B',script,'--origin','https://ksu.codes','--runtime-manifest-sha256',runtime,'--require-root-runtime',
          '--issuer-policy','/etc/codi-browser/issuer-policy.json','--issuer-policy-sha256',issuer,
          '--policy-sha256',policy,'--destination-policy','/etc/codi-browser/destination-policy.json',
          '--access-policy','/etc/codi-browser/access-policy.json','--geoip','/etc/codi-browser/country.mmdb',
          '--socket','/run/codi-browser/relay.sock','--proxy-uid',str(proxy_uid),'--proxy-gid',str(proxy_gid)]
    if type(reports) is not bool:raise ValueError('Reports setting must be boolean')
    if reports:args+=['--report-database','/var/lib/codi-browser-reports/reports.sqlite3','--report-admins','/etc/codi-browser/report-admins.json']
    state='StateDirectory=codi-browser-reports\nStateDirectoryMode=0700\n' if reports else ''
    return '''[Unit]
Description=Codi registered Browser relay
After=network-online.target
Wants=network-online.target

[Service]
Type=exec
User=codi-browser
Group=caddy
RuntimeDirectory=codi-browser
RuntimeDirectoryMode=0750
'''+state+'''UMask=0077
ExecStart='''+' '.join(args)+'''
Restart=on-failure
RestartSec=2s
TimeoutStopSec=15s
KillMode=control-group
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictNamespaces=yes
RestrictSUIDSGID=yes
LockPersonality=yes
SystemCallArchitectures=native
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
CapabilityBoundingSet=
AmbientCapabilities=
InaccessiblePaths=-/etc/caddy -/var/lib/caddy -/run/caddy -/etc/codi-connected -/var/lib/codi-connected -/etc/codi-user-files -/var/lib/codi-user-files
ReadOnlyPaths=/etc/codi-browser
Environment=PYTHONDONTWRITEBYTECODE=1
MemoryMax=512M
TasksMax=64
LimitNOFILE=4096
'''

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('runtime','venv','issuer','policy'):p.add_argument('--'+name,required=True)
    p.add_argument('--proxy-uid',type=int,required=True);p.add_argument('--proxy-gid',type=int,required=True)
    p.add_argument('--reports',action='store_true')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:a.output.write_text(render(runtime=a.runtime,venv=a.venv,issuer=a.issuer,policy=a.policy,proxy_uid=a.proxy_uid,proxy_gid=a.proxy_gid,reports=a.reports))
    except (ValueError,OSError) as error:p.error(str(error))
