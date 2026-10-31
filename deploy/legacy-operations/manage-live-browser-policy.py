#!/usr/bin/env python3
"""Inspect and atomically edit the live Browser and login access lists."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import sys
import tempfile

RUNTIME=Path('/srv/codi-browser/releases/c54118ec1a534860f8293d74cd92dbe0744d31c72fa602f52fef986437ae4b37')
RUNTIME_PIN=RUNTIME.name
ACCESS=Path('/etc/codi-browser/access-policy.json')
DESTINATION=Path('/etc/codi-browser/destination-policy.json')

def protect(path):
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or info.st_mode&0o022 or info.st_nlink!=1:
        raise ValueError('Expected a root-owned, protected regular file: '+str(path))

def runtime_imports():
    for directory in (RUNTIME,RUNTIME/'active-system',RUNTIME/'active-system/network_policy',
                      RUNTIME/'apps',RUNTIME/'apps/system',RUNTIME/'apps/system/browser',RUNTIME/'apps/system/browser/relay'):
        info=directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=0 or info.st_mode&0o022:raise ValueError('Unprotected relay runtime directory')
    manifest=RUNTIME/'browser-relay-runtime.json';protect(manifest)
    raw=manifest.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=RUNTIME_PIN:raise ValueError('Relay runtime manifest changed')
    data=json.loads(raw)
    names=('active-system/network_policy/__init__.py','active-system/network_policy/policy.py',
           'apps/system/browser/relay/__init__.py','apps/system/browser/relay/policy.py')
    for name in names:
        path=RUNTIME/name;protect(path);record=data['files'][name]
        content=path.read_bytes()
        if len(content)!=record['bytes'] or hashlib.sha256(content).hexdigest()!=record['sha256']:
            raise ValueError('Relay policy code changed')
    sys.path[:0]=[str(RUNTIME/'active-system'),str(RUNTIME/'apps/system/browser')]
    from network_policy.policy import AccessPolicy, countries, networks
    from relay.policy import DestinationPolicy, hostname
    return AccessPolicy,countries,networks,DestinationPolicy,hostname

class ValidationGeo:
    def country(self,_ip):raise RuntimeError('Validation must not look up IP addresses')

def edit(path,validator,change):
    """Lock, validate, atomically replace and fsync a single policy file."""
    path=Path(path)
    if not path.is_absolute():raise ValueError('Absolute policy path required')
    lockpath=path.parent/('.'+path.name+'.lock')
    fd=os.open(lockpath,os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'r+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        protect(path);validator(path);before=path.read_bytes();data=json.loads(before)
        if not change(data):return False
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,prefix='.'+path.name+'.',delete=False) as f:
                temporary=Path(f.name);os.fchmod(f.fileno(),stat.S_IMODE(path.stat().st_mode))
                json.dump(data,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
            validator(temporary)
            if path.read_bytes()!=before:raise ValueError('Policy changed outside the operator lock')
            os.replace(temporary,path);temporary=None
            directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(directory)
            finally:os.close(directory)
        finally:
            if temporary is not None:temporary.unlink(missing_ok=True)
    return True

def update_access(path,action,direction,kind,value,imports):
    AccessPolicy,countries,networks,_,_=imports
    if action not in ('add','remove') or direction not in ('incomingLogin','outgoing') or kind not in ('blockedCidrs','blockedCountries'):raise ValueError('Unknown access rule')
    (networks if kind=='blockedCidrs' else countries)([value])
    def change(data):
        items=data[direction][kind]
        if action=='add':
            if value in items:return False
            items.append(value)
        else:
            if value not in items:raise ValueError('Rule is not present')
            items.remove(value)
        return True
    return edit(path,lambda p:AccessPolicy.load(p,ValidationGeo()),change)

def update_domains(path,action,kind,value,imports):
    _,_,_,DestinationPolicy,hostname=imports
    if action=='set':
        if kind!='whitelistEnabled' or value not in ('on','off'):raise ValueError('Use whitelistEnabled on or off')
        def change(data):
            enabled=value=='on'
            if data[kind]==enabled:return False
            data[kind]=enabled;return True
    else:
        if action not in ('add','remove') or kind not in ('blacklist','whitelist'):raise ValueError('Unknown domain list')
        value=hostname(value)
        def change(data):
            items=data[kind]
            if action=='add':
                if value in items:return False
                items.append(value)
            else:
                if value not in items:raise ValueError('Domain is not present')
                items.remove(value)
            return True
    return edit(path,DestinationPolicy.load,change)

def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Run as root on box-webhost')
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='policy',required=True)
    a=sub.add_parser('access');a.add_argument('action',choices=('show','add','remove'));a.add_argument('direction',nargs='?');a.add_argument('kind',nargs='?');a.add_argument('value',nargs='?')
    d=sub.add_parser('domains');d.add_argument('action',choices=('show','add','remove','set'));d.add_argument('kind',nargs='?');d.add_argument('value',nargs='?')
    args=p.parse_args();imports=runtime_imports();path=ACCESS if args.policy=='access' else DESTINATION
    if args.action=='show':
        protect(path)
        if args.policy=='access':imports[0].load(path,ValidationGeo())
        else:imports[3].load(path)
        print(path.read_text(),end='');return
    changed=update_access(path,args.action,args.direction,args.kind,args.value,imports) if args.policy=='access' else update_domains(path,args.action,args.kind,args.value,imports)
    print('Updated.' if changed else 'Already set.')

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as error:raise SystemExit('Policy unchanged: '+str(error))
