#!/usr/bin/env python3
"""Guarded operator for the optional Browser relay metadata ledger.

This is source-only until installed as a protected, pinned operator bundle.
Changing audit mode restarts the relay and disconnects existing Browser streams.
Neither disabling nor rolling back deletes the signing key or ledger.
"""
import argparse
import base64
import fcntl
import grp
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import pwd
import re
import socket
import ssl
import stat
import subprocess
import sys
import tempfile
import time

# Imported pinned code must never create unmanifested files in immutable trees.
sys.dont_write_bytecode=True

RUNTIME='edfd7db342c856c66bf8a19fa50593aa3c08a7498be584d8fca34b86421b71ca'
VENV='a5ee6aa9a1c18535aad36a52b7ec57ca9c1e1fca03cbb02d4c423fd7ec317326'
ISSUER='33208c945336d9c910368c70894af89c575383d1e3da9ceb9addd0b86bfcfa74'
POLICY='7faf30b5457fa629acc7ffa695c15a6a8a56098ba4372412260ade478af5a537'
BASE=Path('/srv/codi-browser/releases')/RUNTIME
DEST=Path('/etc/codi-browser/destination-policy.json')
UNIT=Path('/etc/systemd/system/codi-browser-relay.service')
KEY=Path('/etc/codi-browser/private/audit-signing-key')
DB=Path('/var/lib/codi-browser-audit/events.sqlite3')
JOURNAL=Path('/var/lib/codi-ingress/browser-audit-switch-journal.json')
HOST_LOCK=Path('/home/dflanag3/webhost-sites/.controller.lock')
POLICY_LOCK=Path('/etc/codi-browser/.destination-policy.json.lock')

def protected(path,*,directory=False,mode=None):
    info=path.lstat();expected=stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    if not expected or info.st_uid!=0 or info.st_mode&0o022 or (not directory and info.st_nlink!=1) or (mode is not None and stat.S_IMODE(info.st_mode)!=mode):raise ValueError('Unprotected operator input: '+str(path))
    return info

def protected_parents(path):
    for directory in path.parents:protected(directory,directory=True)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def imports():
    # The installed operator bundle is named by its manifest hash, and all its
    # code is verified before it is imported with root privileges.
    root=Path(__file__).resolve().parents[2];protected(root,directory=True);protected_parents(root)
    manifest=root/'browser-audit-operator.json';protected(manifest,mode=0o644);raw=manifest.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=root.name:raise ValueError('Operator manifest pin changed')
    value=json.loads(raw);names={'active-system/scripts/manage-browser-audit.py','active-system/scripts/render-browser-service.py','active-system/browser_service/audit_switch.py'}
    if value.get('version')!='codi-browser-audit-operator/1' or set(value.get('files',{}))!=names:raise ValueError('Unexpected operator manifest')
    for name in names:
        path=root/name
        for directory in path.parents:
            if directory==root:break
            protected(directory,directory=True)
        protected(path,mode=0o644);data=path.read_bytes()
        if value['files'][name]!={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}:raise ValueError('Operator code changed')
    # Verify the candidate runtime before importing its policy validator.
    protected(BASE,directory=True);protected_parents(BASE);m=BASE/'browser-relay-runtime.json';protected(m,mode=0o644);raw=m.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=RUNTIME:raise ValueError('Browser runtime pin changed')
    data=json.loads(raw);found=set()
    for path in BASE.rglob('*'):
        if path.is_symlink():raise ValueError('Linked runtime input')
        if path.is_dir():protected(path,directory=True);continue
        protected(path,mode=0o644);name=path.relative_to(BASE).as_posix()
        if name=='browser-relay-runtime.json':continue
        content=path.read_bytes();found.add(name)
        if data['files'].get(name)!={'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()}:raise ValueError('Runtime content changed')
    if found!=set(data['files']):raise ValueError('Runtime file set changed')
    sys.path[:0]=[str(BASE/'apps/system/browser')]
    from relay.policy import DestinationPolicy
    return load('codi_audit_switch',root/'active-system/browser_service/audit_switch.py'),load('codi_audit_render',root/'active-system/scripts/render-browser-service.py'),DestinationPolicy

def credential(create):
    parent=KEY.parent
    if create and not parent.exists():parent.mkdir(mode=0o700)
    protected(parent,directory=True,mode=0o700)
    if create and not KEY.exists():
        if DB.exists() or DB.is_symlink():raise ValueError('Existing ledger has no signing key; restore the original key')
        fd=os.open(KEY,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as stream:stream.write(os.urandom(32));stream.flush();os.fsync(stream.fileno())
        fd=os.open(parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    protected(KEY,mode=0o600)
    if KEY.stat().st_size!=32:raise ValueError('Invalid protected audit signing key')

def restart():
    subprocess.run(['systemctl','daemon-reload'],check=True,timeout=30)
    subprocess.run(['systemctl','restart','codi-browser-relay.service'],check=True,timeout=60)

def check():
    # Type=exec may be active before the Unix socket is accepting requests.
    # Keep this bounded, including connection timeouts, while waiting for the
    # actual routed challenge rather than trusting systemd's active state.
    deadline=time.monotonic()+20;last=None
    while time.monotonic()<deadline:
        try:
            subprocess.run(['systemctl','is-active','--quiet','codi-browser-relay.service'],check=True,timeout=3)
            conn=http.client.HTTPSConnection('ksu.codes',timeout=3)
            conn.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),timeout=2),server_hostname='ksu.codes')
            try:
                conn.request('POST','/browser-relay/challenge',body=b'{}',headers={'Host':'ksu.codes','Origin':'https://ksu.codes','Content-Type':'application/json'})
                response=conn.getresponse();response.read(65536)
                if response.status!=200:raise ValueError('Browser relay challenge is unavailable')
                return
            finally:conn.close()
        except (ValueError,OSError,subprocess.SubprocessError) as error:last=error;time.sleep(.25)
    raise ValueError('Browser relay did not become ready: '+str(last))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('status','enable','disable','recover','report'));p.add_argument('--subject');p.add_argument('--expected-head');a=p.parse_args()
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    switch,renderer,DestinationPolicy=imports()
    # UID/GID are part of the reviewed deployed ingress configuration.
    if pwd.getpwnam('caddy').pw_uid!=997 or grp.getgrnam('caddy').gr_gid!=984:raise ValueError('Caddy UID or GID changed')
    params=dict(runtime=RUNTIME,venv=VENV,issuer=ISSUER,policy=POLICY,proxy_uid=997,proxy_gid=984,reports=True)
    off=renderer.render(**params,audit=False).encode();on=renderer.render(**params,audit=True).encode()
    for path in (DEST,UNIT,HOST_LOCK,POLICY_LOCK):protected(path)
    for path in (DEST,UNIT,POLICY_LOCK,JOURNAL):protected_parents(path)
    with HOST_LOCK.open('r+') as host, POLICY_LOCK.open('r+') as policy_lock:
        fcntl.flock(host,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(policy_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if subprocess.run(['systemctl','show','codi-browser-relay.service','-p','DropInPaths','--value'],check=True,text=True,capture_output=True).stdout.strip():raise ValueError('Unexpected service drop-ins')
        current=DestinationPolicy.load(DEST);unit=UNIT.read_bytes()
        if a.action=='status':
            print(json.dumps({'enabled':current.server_audit_enabled,'serviceMatchesMode':unit==(on if current.server_audit_enabled else off),'transitionPending':JOURNAL.exists(),'keyPresent':KEY.is_file(),'ledgerPresent':DB.is_file()}));return
        if a.action=='report':
            if a.subject is not None and not re.fullmatch(r'user:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',a.subject):raise ValueError('Canonical account subject required')
            if a.expected_head is not None and not re.fullmatch(r'[0-9a-f]{64}',a.expected_head):raise ValueError('Expected head must be a SHA-256 digest')
            credential(False)
            command=['systemd-run','--unit=codi-browser-audit-report','--wait','--pipe','--collect','-p','User=codi-browser','-p','Group=caddy','-p',f'LoadCredential=audit-signing-key:{KEY}',f'/srv/codi-browser/venvs/{VENV}/bin/python','-I','-B',str(BASE/'active-system/scripts/browser-audit-report.py'),'--database',str(DB),'--key','/run/credentials/codi-browser-audit-report.service/audit-signing-key']
            if a.subject:command+=['--subject',a.subject]
            if a.expected_head:command+=['--expected-head',a.expected_head]
            subprocess.run(command,check=True,timeout=120);return
        if a.action=='recover':
            protected(JOURNAL,mode=0o600);record=json.loads(JOURNAL.read_bytes())
            if {base64.b64decode(record[k],validate=True) for k in ('oldUnit','newUnit')}!={off,on}:raise ValueError('Journal unit differs from pinned units')
            old=json.loads(base64.b64decode(record['oldPolicy'],validate=True));new=json.loads(base64.b64decode(record['newPolicy'],validate=True))
            if type(old.get('serverAuditEnabled')) is not bool or type(new.get('serverAuditEnabled')) is not bool or old['serverAuditEnabled']==new['serverAuditEnabled'] or {k:v for k,v in old.items() if k!='serverAuditEnabled'}!={k:v for k,v in new.items() if k!='serverAuditEnabled'}:raise ValueError('Journal policy differs beyond audit mode')
            if base64.b64decode(record['oldUnit'],validate=True)!=(on if old['serverAuditEnabled'] else off) or base64.b64decode(record['newUnit'],validate=True)!=(on if new['serverAuditEnabled'] else off):raise ValueError('Journal unit does not match its audit policy')
            if old['serverAuditEnabled']:credential(False)
            print(json.dumps(switch.recover(DEST,UNIT,JOURNAL,restart=restart,check=check)));return
        enabled=a.action=='enable'
        if JOURNAL.exists() or JOURNAL.is_symlink():raise ValueError('A prior audit transition requires recovery')
        if current.server_audit_enabled==enabled or unit!=(off if enabled else on):raise ValueError('Policy and service are not in the expected starting mode')
        if enabled:credential(True)
        def validate(policy,unit):
            with tempfile.TemporaryDirectory(prefix='codi-audit-validate-') as directory:
                path=Path(directory)/'policy.json';path.write_bytes(policy);parsed=DestinationPolicy.load(path)
                if parsed.server_audit_enabled!=enabled or unit!=(on if enabled else off):raise ValueError('Unexpected transition candidate')
                candidate=Path(directory)/'codi-browser-relay.service';candidate.write_bytes(unit)
                subprocess.run(['systemd-analyze','verify',str(candidate)],check=True,timeout=30)
        result=switch.switch(DEST,UNIT,JOURNAL,expected_unit=off if enabled else on,candidate_unit=on if enabled else off,enabled=enabled,validate=validate,restart=restart,check=check)
        print(json.dumps(result))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        print('Browser audit operation failed: '+str(error),file=sys.stderr);sys.exit(1)
