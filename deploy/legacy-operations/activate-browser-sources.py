#!/usr/bin/env python3
"""Activate a pinned, exact-file Browser license/source route on box-webhost."""
import argparse
import base64
import fcntl
import hashlib
import http.client
import json
import os
from pathlib import Path
import socket
import ssl
import sys
import tempfile
import types

ROOT=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(ROOT/'ops'))
import common
import webctl as ctl
SOURCE=ROOT/'ops/common.py';MANIFEST=ROOT/'sites.toml';CADDY=Path('/etc/caddy/Caddyfile')
FILES=Path('/srv/codi-browser/source-staging/engine-6736dce5')
STATE=Path('/var/lib/codi-ingress');JOURNAL=STATE/'browser-sources-journal.json';RECEIPT=STATE/'browser-sources-result.json'
PINS={'oldSource':'25d58c0602e296aabce40c24d64d52408140e0c78e63347f6485aa240f39da64',
      'oldManifest':'a8ac8177967396495711247402ce6b346865d1d2aab84d7e7310817e0c9d7d1c',
      'oldCaddy':'ce813404d53fd8d9344eef3a49af868fbce53d70f01612cfd78c0e89e552edcd',
      'newSource':'9bb5e958f27985891b8c927215e4927ddd514870309e271ec0f29790e2de8c68',
      'newManifest':'3ff13521fdca82c339d39fff09be45258e41f132d893a9e7c9fc51796636d93f',
      'newCaddy':'a4d05c0e404188ddf2192dd5f9efb53076aa499f76d5dc2b36e87c6ee7e3df63',
      'notices':'f6f82f92168d3d23277656a7951822ec394e981604e804ab8d2d0e350ef49799'}


class RollbackExercise(Exception):pass
def digest(raw):return hashlib.sha256(raw).hexdigest()
def filehash(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def save(path,value):
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,'w') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(name,path);fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if os.path.exists(name):os.unlink(name)
def module(raw):
    result=types.ModuleType('browser_sources_hosting');result.__file__=str(SOURCE)
    exec(compile(raw,str(SOURCE),'exec'),result.__dict__);return result
def bind(m):
    for name in ('caddy','load','dump','validate','unit'):setattr(ctl,name,getattr(m,name))
def replace(source,manifest):
    owner=ctl.owner();ctl.write(SOURCE,source,0o644,owner.pw_uid,owner.pw_gid)
    ctl.write(MANIFEST,manifest,0o644,owner.pw_uid,owner.pw_gid)
    m=module(source);bind(m);data=m.tomllib.loads(manifest.decode());m.validate(data);return m,data
def request(host,path,method='GET',headers=None):
    c=http.client.HTTPSConnection(host,timeout=15);c.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),5),server_hostname=host)
    try:
        c.request(method,path,headers={'Host':host,**(headers or {})});r=c.getresponse();body=r.read(1048577)
        if len(body)>1048576:raise ValueError('Unexpectedly large check response')
        return r.status,body
    finally:c.close()
def sites(data):return {s['domain']:request(s['domain'],'/')[0] for s in data['sites'] if s['enabled']}
def verify_notices():
    manifest=FILES/'notice-manifest.json'
    if FILES.is_symlink() or FILES.stat().st_uid!=0 or FILES.stat().st_mode&0o022 or filehash(manifest)!=PINS['notices']:raise ValueError('Unsafe or changed notice manifest')
    data=json.loads(manifest.read_text())
    if data.get('version')!='codi-browser-notices/1':raise ValueError('Invalid notice manifest')
    expected={**{name:rec['sha256'] for name,rec in data['files'].items()},**data['sourceArchives']}
    for name,sha in expected.items():
        p=FILES/name
        if '/' in name or p.is_symlink() or not p.is_file() or p.stat().st_uid!=0 or p.stat().st_mode&0o022 or filehash(p)!=sha:
            raise ValueError('Source or notice changed: '+name)
def check(data,expected):
    if sites(data)!=expected:raise ValueError('Site status changed')
    code,body=request('ksu.codes','/browser-sources/')
    if code!=200 or b'Browser licenses and source' not in body:raise ValueError('Notice index unavailable')
    if request('ksu.codes','/browser-sources/unknown-file')[0]!=404:raise ValueError('Unlisted source path exposed')
    code,body=request('ksu.codes','/browser-sources/firefox-2e1e835a.tar.zst',headers={'Range':'bytes=0-31'})
    if code!=206 or len(body)!=32:raise ValueError('Large source range request failed')
    if request('ksu.codes','/api/v1/auth',method='POST',headers={'Origin':'https://ksu.codes','Content-Type':'application/json','Content-Length':'0'})[0] in (404,502,503):raise ValueError('Sign-in route unavailable')
def restore(journal):
    old_source=base64.b64decode(journal['source'],validate=True);old_manifest=base64.b64decode(journal['manifest'],validate=True)
    if digest(old_source)!=PINS['oldSource'] or digest(old_manifest)!=PINS['oldManifest']:raise ValueError('Saved baseline changed')
    for path,old,new in ((SOURCE,PINS['oldSource'],PINS['newSource']),(MANIFEST,PINS['oldManifest'],PINS['newManifest']),(CADDY,PINS['oldCaddy'],PINS['newCaddy'])):
        if path.is_symlink() or digest(path.read_bytes()) not in (old,new):raise ValueError('Hosting state changed: '+str(path))
    _,data=replace(old_source,old_manifest)
    if digest(CADDY.read_bytes())!=PINS['oldCaddy']:ctl.caddy_apply(data,'production')
    if digest(CADDY.read_bytes())!=PINS['oldCaddy'] or sites(data)!=journal['sites']:raise ValueError('Hosting rollback did not validate')
    JOURNAL.unlink();return {'status':'rolled-back','sites':journal['sites']}
def apply(inputs,*,exercise=False):
    if JOURNAL.exists() or RECEIPT.exists():raise ValueError('Prior source transition record exists')
    for path,key in ((SOURCE,'oldSource'),(MANIFEST,'oldManifest'),(CADDY,'oldCaddy')):
        if path.is_symlink() or digest(path.read_bytes())!=PINS[key]:raise ValueError('Hosting baseline changed: '+str(path))
    raw=(inputs/'common.py').read_bytes();manifest=(inputs/'sites.toml').read_bytes()
    if digest(raw)!=PINS['newSource'] or digest(manifest)!=PINS['newManifest']:raise ValueError('Candidate hosting inputs changed')
    m=module(raw);data=m.tomllib.loads(manifest.decode());m.validate(data);rendered=m.caddy(data,'production').encode()
    if digest(rendered)!=PINS['newCaddy']:raise ValueError('Candidate rendering changed')
    verify_notices()
    with tempfile.NamedTemporaryFile(prefix='.browser-sources-',suffix='.caddy',dir='/etc/caddy') as temp:
        import pwd
        temp.write(rendered);temp.flush();os.chown(temp.name,0,pwd.getpwnam('caddy').pw_gid);os.chmod(temp.name,0o640);ctl.caddy_validate(temp.name)
    original=common.load();before=sites(original)
    journal={'version':'codi-browser-sources-transition/1','sites':before,'source':base64.b64encode(SOURCE.read_bytes()).decode(),'manifest':base64.b64encode(MANIFEST.read_bytes()).decode()}
    save(JOURNAL,journal)
    try:
        _,data=replace(raw,manifest);ctl.caddy_apply(data,'production')
        if digest(CADDY.read_bytes())!=PINS['newCaddy']:raise ValueError('Unexpected active Caddy config')
        check(data,before)
        if exercise:raise RollbackExercise()
        result={'status':'applied','caddySHA256':PINS['newCaddy'],'sites':before};save(RECEIPT,result);JOURNAL.unlink();return result
    except RollbackExercise:return {'status':'rollback-exercised','restored':restore(journal)}
    except BaseException:
        if RECEIPT.exists():raise ValueError('Sources route committed; use recover to finish journal')
        restore(journal);raise
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('apply','exercise','recover'));p.add_argument('--inputs',type=Path);a=p.parse_args()
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    with (ROOT/'.controller.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if a.action in ('apply','exercise'):
            if a.inputs is None:raise ValueError('Pinned hosting inputs required')
            result=apply(a.inputs,exercise=a.action=='exercise')
        else:
            if not JOURNAL.is_file() or JOURNAL.is_symlink() or JOURNAL.stat().st_uid!=0:raise ValueError('No valid pending journal')
            journal=json.loads(JOURNAL.read_text())
            if journal.get('version')!='codi-browser-sources-transition/1':raise ValueError('Invalid journal')
            if RECEIPT.exists():
                receipt=json.loads(RECEIPT.read_text());data=ctl.load()
                if receipt.get('caddySHA256')!=PINS['newCaddy'] or digest(CADDY.read_bytes())!=PINS['newCaddy']:raise ValueError('Committed state changed')
                check(data,journal['sites']);JOURNAL.unlink();result={'status':'committed-state-recovered'}
            else:result=restore(journal)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    try:main()
    except Exception as error:raise SystemExit(type(error).__name__+': '+str(error))
