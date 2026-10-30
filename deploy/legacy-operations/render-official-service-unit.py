#!/usr/bin/env python3
"""Render a candidate systemd unit for a separately provisioned official store.

This does not install a user, state directory, package, unit, or route.
"""
import argparse,re
from pathlib import PurePosixPath

def path(value):
    if not isinstance(value,str) or not re.fullmatch(r'/[A-Za-z0-9_./-]+',value):raise ValueError('Use an absolute systemd-safe path')
    p=PurePosixPath(value)
    if '..' in p.parts or str(p)!=value or value=='/':raise ValueError('Canonical non-root path required')
    return value

def render(*,python,package,state,policy,port,discovery=False):
    python,package,state,policy=map(path,(python,package,state,policy))
    if not isinstance(port,int) or isinstance(port,bool) or not 1024<=port<=65535:raise ValueError('Unprivileged fixed port required')
    if type(discovery) is not bool:raise ValueError('Discovery selection must be boolean')
    policy_flag='--issuer-discovery' if discovery else '--issuer-policy'
    paths=[PurePosixPath(package),PurePosixPath(state)]
    if any(a==b or a in b.parents or b in a.parents for a,b in [tuple(paths)]):raise ValueError('Package and mutable state must be disjoint')
    return f'''[Unit]
Description=Codi official channel storage
After=network.target

[Service]
Type=simple
User=codi-official
Group=codi-official
UMask=0077
WorkingDirectory={package}
ExecStart={python} -I -B {package}/scripts/run-official-runtime.py --database {state}/official.sqlite --ledger {state}/access.sqlite {policy_flag} {policy} --port {port}
Restart=on-failure
RestartSec=3s
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths={state}
CapabilityBoundingSet=
AmbientCapabilities=
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
IPAddressDeny=any
IPAddressAllow=localhost
LockPersonality=yes
MemoryDenyWriteExecute=yes
RestrictSUIDSGID=yes
LimitNOFILE=1024
TasksMax=64

[Install]
WantedBy=multi-user.target
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('python','package','state','policy'):p.add_argument('--'+name,required=True)
 p.add_argument('--port',type=int,required=True);p.add_argument('--discovery',action='store_true');a=p.parse_args();print(render(python=a.python,package=a.package,state=a.state,policy=a.policy,port=a.port,discovery=a.discovery),end='')
