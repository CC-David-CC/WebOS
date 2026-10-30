#!/usr/bin/env python3
"""Coordinate the pinned Browser issuer and managed Caddy backend routes.

This does not deploy the Browser engine or modify user data. A root-owned
journal permits rollback if the issuer/hosting transition is interrupted.
"""
import argparse
import base64
import fcntl
import hashlib
import http.client
import importlib
import json
import os
from pathlib import Path
import pwd
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import tomllib
import types

ROOT=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(ROOT/'ops'))
import common
import webctl as ctl
STATE=Path('/var/lib/codi-ingress');JOURNAL=STATE/'browser-backend-journal.json';RECEIPT=STATE/'browser-backend-result.json'
SOURCE=ROOT/'ops/common.py';MANIFEST=ROOT/'sites.toml';CADDY=Path('/etc/caddy/Caddyfile')
MANAGED=Path('/etc/codi-connected/ksu/managed.json')
OLD_RELEASE='/srv/codi-connected/releases/native27-chat-open-error-r1'
NEW_RELEASE='/srv/codi-connected/releases/browser-issuer-profile28-r2'
PYTHON='/srv/codi-connected/venvs/517179c/bin/python'
MANAGER=NEW_RELEASE+'/scripts/manage-services.py'
PINS={'oldSource':'09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226',
      'oldManifest':'8dbc923802a0fd3f66eaef45bf8105c6257ecb02a592de2956233ee1f369818b',
      'oldCaddy':'525b9b8e4997c53fb5522659a80bb9f8497c63abf3c6b955d6204c1aef79b551',
      'candidateSource':'25d58c0602e296aabce40c24d64d52408140e0c78e63347f6485aa240f39da64',
      'candidateManifest':'a8ac8177967396495711247402ce6b346865d1d2aab84d7e7310817e0c9d7d1c',
      'candidateCaddy':'ce813404d53fd8d9344eef3a49af868fbce53d70f01612cfd78c0e89e552edcd',
      'candidateRelease':'d09ddbbb04ce0e294a97b44ae1d8a8a555d302385c5d42b7fb7fd867bfab4878',
      'browserPolicy':'7faf30b5457fa629acc7ffa695c15a6a8a56098ba4372412260ade478af5a537'}


class RollbackExercise(Exception):pass


def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args,*,check=True,timeout=120):
    return subprocess.run(list(map(str,args)),check=check,capture_output=True,text=True,timeout=timeout)
def write_state(path,value):
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,'w') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(name,path);fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if os.path.exists(name):os.unlink(name)
def generator(raw):
    module=types.ModuleType('candidate_webhost_common');module.__file__=str(SOURCE)
    exec(compile(raw,str(SOURCE),'exec'),module.__dict__)
    return module
def bind(module):
    for name in ('caddy','load','dump','validate','unit'):setattr(ctl,name,getattr(module,name))
def replace_inputs(source,manifest):
    owner=ctl.owner();ctl.write(SOURCE,source,0o644,owner.pw_uid,owner.pw_gid)
    ctl.write(MANIFEST,manifest,0o644,owner.pw_uid,owner.pw_gid)
    module=generator(source);bind(module)
    data=module.tomllib.loads(manifest.decode());module.validate(data)
    return module,data
def request(host,path,*,method='GET',body=None):
    c=http.client.HTTPSConnection(host,timeout=12)
    c.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),5),server_hostname=host)
    try:
        headers={'Host':host,'Origin':'https://'+host}
        if body is not None:headers['Content-Type']='application/json'
        c.request(method,path,body=body,headers=headers);r=c.getresponse();raw=r.read(1048577)
        if len(raw)>1048576:raise ValueError('Unexpectedly large check response')
        return r.status,raw
    finally:c.close()
def site_statuses(data):
    return {s['domain']:request(s['domain'],'/')[0] for s in data['sites'] if s['enabled']}
def wait_checks(expected):
    deadline=time.monotonic()+25;last=None
    while time.monotonic()<deadline:
        try:
            statuses=site_statuses(ctl.load())
            code,raw=request('ksu.codes','/config.json');config=json.loads(raw)
            auth,_=request('ksu.codes','/api/v1/auth',method='POST',body=b'{}')
            challenge,body=request('ksu.codes','/browser-relay/challenge',method='POST',body=b'{}')
            if (statuses==expected and code==200 and config.get('browserRelay',{}).get('policySHA256')==PINS['browserPolicy']
                    and auth==400 and challenge==200 and json.loads(body).get('connection_id')):
                return
            last={'sites':statuses,'config':code,'auth':auth,'challenge':challenge}
        except (OSError,ValueError,KeyError,http.client.HTTPException) as error:last=str(error)
        time.sleep(.5)
    raise ValueError('Backend checks did not pass: '+str(last))
def manager(action):
    args=[PYTHON,'-B',MANAGER,action,'--config',MANAGED]
    if action=='upgrade':args+=['--release',NEW_RELEASE,'--python',PYTHON]
    output=run(args);return json.loads(output.stdout)
def restore(journal):
    old_source=base64.b64decode(journal['oldSource'],validate=True)
    old_manifest=base64.b64decode(journal['oldManifest'],validate=True)
    if digest(old_source)!=PINS['oldSource'] or digest(old_manifest)!=PINS['oldManifest']:raise ValueError('Invalid saved hosting inputs')
    for path,old,new in ((SOURCE,PINS['oldSource'],PINS['candidateSource']),
                         (MANIFEST,PINS['oldManifest'],PINS['candidateManifest'])):
        if path.is_symlink() or digest(path.read_bytes()) not in (old,new):raise ValueError('Hosting input changed: '+str(path))
    if digest(CADDY.read_bytes()) not in (PINS['oldCaddy'],PINS['candidateCaddy']):
        raise ValueError('Active Caddy configuration changed; manual review required')
    module,data=replace_inputs(old_source,old_manifest)
    if digest(CADDY.read_bytes())!=PINS['oldCaddy']:
        ctl.caddy_apply(data,'production')
    if digest(CADDY.read_bytes())!=PINS['oldCaddy']:raise ValueError('Failed to restore old hosting')
    pending=MANAGED.parent/'maintenance.json'
    if pending.exists():
        result=manager('rollback')
        if result.get('status') not in ('interrupted-code-rolled-back','candidate-failed-rolled-back'):
            raise ValueError('Pending issuer transition requires review: '+str(result))
    current=json.loads(MANAGED.read_text())['release']
    if current==NEW_RELEASE:
        result=manager('rollback')
        if result.get('status') not in ('rolled-back','interrupted-code-rolled-back'):raise ValueError('Issuer rollback failed: '+str(result))
    elif current!=OLD_RELEASE:raise ValueError('Unexpected issuer release; manual review required')
    if site_statuses(data)!=journal['sites']:raise ValueError('Site responses differ after rollback')
    JOURNAL.unlink();return {'status':'rolled-back','sites':journal['sites']}
def apply(inputs,*,exercise=False):
    if JOURNAL.exists() or RECEIPT.exists():raise ValueError('Prior transition record exists')
    for path,pin in ((SOURCE,'oldSource'),(MANIFEST,'oldManifest'),(CADDY,'oldCaddy'),
                     (Path(NEW_RELEASE)/'connected-release.json','candidateRelease')):
        if path.is_symlink() or digest(path.read_bytes())!=PINS[pin]:raise ValueError('Unexpected baseline: '+str(path))
    current=json.loads(MANAGED.read_text())
    if current['release']!=OLD_RELEASE or current['python']!=PYTHON:raise ValueError('Unexpected current issuer runtime')
    for service in ('codi-caddy-proxy-guard.service','codi-issuer-ingress.service','codi-browser-relay.service'):
        if run(['systemctl','is-active',service]).stdout.strip()!='active':raise ValueError('Required guard/relay inactive: '+service)
    cand_source=(inputs/'common.py').read_bytes();cand_manifest=(inputs/'sites.toml').read_bytes()
    if digest(cand_source)!=PINS['candidateSource'] or digest(cand_manifest)!=PINS['candidateManifest']:raise ValueError('Candidate inputs changed')
    module=generator(cand_source);candidate=module.tomllib.loads(cand_manifest.decode());module.validate(candidate)
    rendered=module.caddy(candidate,'production').encode()
    if digest(rendered)!=PINS['candidateCaddy']:raise ValueError('Candidate rendering changed')
    with tempfile.NamedTemporaryFile(prefix='.browser-backend-',suffix='.caddy',dir='/etc/caddy') as temp:
        temp.write(rendered);temp.flush()
        os.chown(temp.name,0,pwd.getpwnam('caddy').pw_gid);os.chmod(temp.name,0o640)
        ctl.caddy_validate(temp.name)
    original=common.load();sites=site_statuses(original)
    journal={'version':'codi-browser-backend-transition/1','phase':'prepared','sites':sites,
             'oldSource':base64.b64encode(SOURCE.read_bytes()).decode(),
             'oldManifest':base64.b64encode(MANIFEST.read_bytes()).decode()}
    write_state(JOURNAL,journal)
    try:
        result=manager('upgrade')
        if result.get('status')!='upgraded':raise ValueError('Issuer upgrade not applied: '+str(result))
        journal['phase']='issuer-upgraded';write_state(JOURNAL,journal)
        _,data=replace_inputs(cand_source,cand_manifest);ctl.caddy_apply(data,'production')
        if digest(CADDY.read_bytes())!=PINS['candidateCaddy']:raise ValueError('Unexpected active Caddy config')
        wait_checks(sites)
        if exercise:raise RollbackExercise('Verify coordinated rollback after live checks')
        result={'status':'applied','issuerRelease':NEW_RELEASE,'hostingSHA256':PINS['candidateCaddy'],'sites':sites}
        write_state(RECEIPT,result);JOURNAL.unlink();return result
    except RollbackExercise:
        return {'status':'rollback-exercised','restored':restore(journal)}
    except BaseException:
        if RECEIPT.exists():raise ValueError('Backend committed; use recover to finish the journal')
        restore(journal)
        raise


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
            if journal.get('version')!='codi-browser-backend-transition/1':raise ValueError('Invalid journal')
            if RECEIPT.exists():
                receipt=json.loads(RECEIPT.read_text())
                if (receipt.get('status')!='applied' or receipt.get('issuerRelease')!=NEW_RELEASE
                        or digest(CADDY.read_bytes())!=PINS['candidateCaddy']
                        or json.loads(MANAGED.read_text())['release']!=NEW_RELEASE):
                    raise ValueError('Committed state changed; manual review required')
                wait_checks(journal['sites']);JOURNAL.unlink();result={'status':'committed-state-recovered'}
            else:result=restore(journal)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    try:main()
    except Exception as error:raise SystemExit(type(error).__name__+': '+str(error))
