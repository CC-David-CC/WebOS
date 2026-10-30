#!/usr/bin/env python3
"""Guard Caddy's PROXY listeners and pin HAProxy's service UID on box-webhost.

The existing HAProxy unit remains unchanged. systemd uses the pre-existing
static account in preference to allocating a new DynamicUser. A root-only
journal permits recovery if the controlled service transition is interrupted.
Run only on box-webhost, with the reviewed three rendered files in --inputs.
"""
import argparse
import fcntl
import grp
import hashlib
import http.client
import json
import os
from pathlib import Path
import pwd
import socket
import ssl
import stat
import subprocess
import tempfile
import time
import tomllib

UID=966
NAME='codi-shared-ingress'
STATE=Path('/var/lib/codi-ingress')
JOURNAL=STATE/'caddy-proxy-guard-journal.json'
RECEIPT=STATE/'caddy-proxy-guard-result.json'
ROOT=Path('/home/dflanag3/webhost-sites')
RULES=Path('/etc/codi-browser/caddy-proxy-guard.nft')
UNIT=Path('/etc/systemd/system/codi-caddy-proxy-guard.service')
DROPIN=Path('/etc/systemd/system/caddy.service.d/40-codi-caddy-proxy-guard.conf')
FILES={
    'caddy-proxy-guard.nft':(RULES,'31b66c371f59b872e68c92703748e0f151644b247e5ad1dd387e9d03edb2ca23'),
    'codi-caddy-proxy-guard.service':(UNIT,'3a2c604be9f1fdb0c979839de77053c0a598d54f0690c80de77e1750a1db3222'),
    '40-codi-caddy-proxy-guard.conf':(DROPIN,'1edbc6f79011119d37be7b3c1867ef700f582a77232c8a24459b231e4a14be76'),
}
INGRESS_UNIT_SHA='a4a2140c8e6e0329f16cd5acd8a5b7c8bd38ccdb1e03eedddf5caec53cd67fcf'
CADDY_SHA='525b9b8e4997c53fb5522659a80bb9f8497c63abf3c6b955d6204c1aef79b551'
MANIFEST_SHA='8dbc923802a0fd3f66eaef45bf8105c6257ecb02a592de2956233ee1f369818b'


class RollbackExercise(Exception):pass


def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args,*,check=True,input=None,timeout=30):
    return subprocess.run(list(map(str,args)),input=input,text=True,capture_output=True,check=check,timeout=timeout)
def atomic(path,raw,mode=0o600):
    path=Path(path)
    if path.is_symlink():raise ValueError('Refusing linked destination: '+str(path))
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
        os.replace(name,path)
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.exists(name):os.unlink(name)
def write_state(path,value):atomic(path,(json.dumps(value,sort_keys=True,indent=2)+'\n').encode())
def static_user():
    return next((line.split(':') for line in Path('/etc/passwd').read_text().splitlines() if line.split(':',1)[0]==NAME),None)
def static_group():
    return next((line.split(':') for line in Path('/etc/group').read_text().splitlines() if line.split(':',1)[0]==NAME),None)
def smoke():
    sites=tomllib.loads((ROOT/'sites.toml').read_text())['sites'];results={}
    for site in sites:
        if not site['enabled']:continue
        host=site['domain'];connection=http.client.HTTPSConnection(host,timeout=10)
        connection.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),5),server_hostname=host)
        try:
            connection.request('GET','/',headers={'Host':host});response=connection.getresponse();response.read();results[host]=response.status
        finally:connection.close()
    return results
def wait_smoke(expected):
    deadline=time.monotonic()+15;last=None
    while time.monotonic()<deadline:
        try:
            last=smoke()
            if last==expected:return
        except (OSError,ssl.SSLError,http.client.HTTPException) as error:last=str(error)
        time.sleep(.25)
    raise ValueError('Site responses did not recover: '+str(last))
def untrusted_connects():
    code='import socket;socket.create_connection(("127.0.0.1",8443),timeout=3)'
    return run(['/usr/bin/setpriv','--reuid','65534','--regid','65534','--clear-groups',
                '/usr/bin/python3','-c',code],check=False,timeout=5).returncode==0
def remove_known(path,expected):
    if path.exists() or path.is_symlink():
        if path.is_symlink() or digest(path.read_bytes())!=expected:raise ValueError('Changed guard file: '+str(path))
        path.unlink()
def delete_table():
    result=run(['/usr/sbin/nft','list','table','inet','codi_caddy_proxy_guard'],check=False)
    if result.returncode==0:
        if 'meta skuid != 966' not in result.stdout or '8080' not in result.stdout or '8443' not in result.stdout:
            raise ValueError('Guard table changed; manual review required')
        run(['/usr/sbin/nft','delete','table','inet','codi_caddy_proxy_guard'])


def recover(journal):
    if RECEIPT.exists():
        result=json.loads(RECEIPT.read_text())
        user=static_user()
        table=run(['/usr/sbin/nft','list','table','inet','codi_caddy_proxy_guard'],check=False)
        if (result.get('status')!='applied' or result.get('uid')!=UID or not user or int(user[2])!=UID
                or table.returncode or 'meta skuid != 966' not in table.stdout
                or run(['systemctl','is-active',UNIT.name],check=False).stdout.strip()!='active'
                or untrusted_connects() or smoke()!=journal['beforeSites']):
            raise ValueError('Committed guard state differs; manual review required')
        JOURNAL.unlink()
        return {'status':'committed-state-recovered','uid':UID}
    # The old issuer must still be active: once sign-in depends on this
    # boundary, removing it first would make its client-IP policy forgeable.
    managed=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_text())
    if managed['release']!='/srv/codi-connected/releases/native27-chat-open-error-r1':
        raise ValueError('Restore the prior issuer before removing this boundary')
    run(['systemctl','stop',NAME+'.service'],check=False)
    run(['systemctl','stop',UNIT.name],check=False)
    delete_table()
    for _,(path,sha) in FILES.items():remove_known(path,sha)
    run(['systemctl','daemon-reload'])
    user=static_user();group=static_group()
    if user:
        if int(user[2])!=UID or int(user[3])!=UID or user[5]!='/nonexistent' or user[6]!='/usr/sbin/nologin':
            raise ValueError('Static ingress account changed; manual review required')
        run(['userdel',NAME])
    group=static_group()
    if group:
        if int(group[2])!=UID or group[3]:raise ValueError('Ingress group changed; manual review required')
        run(['groupdel',NAME])
    run(['systemctl','reset-failed',NAME+'.service'],check=False)
    run(['systemctl','start',NAME+'.service'])
    wait_smoke(journal['beforeSites'])
    JOURNAL.unlink()
    return {'status':'rolled-back','sites':journal['beforeSites']}


def apply(inputs,*,exercise=False):
    if JOURNAL.exists() or RECEIPT.exists():raise ValueError('Prior transition record exists; inspect it first')
    for path,sha in [(Path('/etc/systemd/system/codi-shared-ingress.service'),INGRESS_UNIT_SHA),
                     (Path('/etc/caddy/Caddyfile'),CADDY_SHA),(ROOT/'sites.toml',MANIFEST_SHA)]:
        if path.is_symlink() or digest(path.read_bytes())!=sha:raise ValueError('Hosting baseline changed: '+str(path))
    managed=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_text())
    if managed['release']!='/srv/codi-connected/releases/native27-chat-open-error-r1':raise ValueError('Unexpected issuer release')
    if static_user() or static_group():raise ValueError('Ingress static identity already exists')
    try:pwd.getpwuid(UID);raise ValueError('Target UID already allocated')
    except KeyError:pass
    try:grp.getgrgid(UID);raise ValueError('Target GID already allocated')
    except KeyError:pass
    rendered={}
    for name,(target,sha) in FILES.items():
        source=inputs/name
        if source.is_symlink() or not source.is_file() or digest(source.read_bytes())!=sha:raise ValueError('Invalid input: '+name)
        if target.exists() or target.is_symlink():raise ValueError('Guard destination exists: '+str(target))
        rendered[name]=source.read_bytes()
        if digest(rendered[name])!=sha:raise ValueError('Input changed during reading: '+name)
    if run(['/usr/sbin/nft','list','table','inet','codi_caddy_proxy_guard'],check=False).returncode==0:raise ValueError('Guard table exists')
    if run(['systemctl','is-active',NAME+'.service']).stdout.strip()!='active':raise ValueError('Shared ingress is not active')
    run(['/usr/sbin/nft','--check','-f','-'],input=rendered['caddy-proxy-guard.nft'].decode())
    run(['systemd-analyze','verify',inputs/'codi-caddy-proxy-guard.service'])
    before=smoke()
    if not untrusted_connects():raise ValueError('Expected prior loopback path differs')
    journal={'version':'codi-caddy-guard-transition/1','uid':UID,'beforeSites':before,'phase':'prepared'}
    write_state(JOURNAL,journal)
    try:
        run(['systemctl','stop',NAME+'.service']);journal['phase']='stopped';write_state(JOURNAL,journal)
        for _ in range(50):
            try:pwd.getpwnam(NAME)
            except KeyError:break
            time.sleep(.1)
        else:raise ValueError('Dynamic ingress identity did not release')
        run(['groupadd','--system','--gid',str(UID),NAME])
        run(['useradd','--system','--no-create-home','--home-dir','/nonexistent','--shell','/usr/sbin/nologin','--uid',str(UID),'--gid',str(UID),NAME])
        account=pwd.getpwnam(NAME)
        shadow=next((line.split(':') for line in Path('/etc/shadow').read_text().splitlines() if line.split(':',1)[0]==NAME),None)
        if (account.pw_uid!=UID or account.pw_gid!=UID or account.pw_dir!='/nonexistent'
                or account.pw_shell!='/usr/sbin/nologin' or set(os.getgrouplist(NAME,UID))!={UID}
                or not shadow or not shadow[1].startswith(('!','*'))):
            raise ValueError('Ingress service account is not locked and isolated')
        run(['systemctl','start',NAME+'.service'])
        pid=int(run(['systemctl','show',NAME+'.service','-p','MainPID','--value']).stdout)
        status=Path('/proc',str(pid),'status').read_text();actual=int(next(x for x in status.splitlines() if x.startswith('Uid:')).split()[1])
        if actual!=UID:raise ValueError('Static ingress identity does not match')
        wait_smoke(before)
        journal['phase']='static-identity';write_state(JOURNAL,journal)
        for name,(target,_) in FILES.items():atomic(target,rendered[name],0o644)
        run(['systemctl','daemon-reload']);run(['systemctl','start',UNIT.name])
        if untrusted_connects():raise ValueError('Caddy still accepts untrusted loopback connections')
        wait_smoke(before)
        if exercise:raise RollbackExercise('Verify rollback after applying the real guard')
        state={'status':'applied','uid':UID,'beforeSites':before,'unitSHA256':INGRESS_UNIT_SHA,'caddySHA256':CADDY_SHA}
        write_state(RECEIPT,state);JOURNAL.unlink();return state
    except RollbackExercise:
        restored=recover(journal)
        return {'status':'rollback-exercised','restored':restored}
    except BaseException:
        recover(journal)
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('apply','exercise','recover'));p.add_argument('--inputs',type=Path);a=p.parse_args()
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    if not STATE.is_dir() or STATE.is_symlink() or STATE.stat().st_uid!=0 or stat.S_IMODE(STATE.stat().st_mode)!=0o700:raise ValueError('Invalid private ingress state directory')
    with (ROOT/'.controller.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if a.action in ('apply','exercise'):
            if a.inputs is None:raise ValueError('Reviewed input directory required')
            result=apply(a.inputs,exercise=a.action=='exercise')
        else:
            if not JOURNAL.is_file() or JOURNAL.is_symlink() or JOURNAL.stat().st_uid!=0:raise ValueError('No valid pending journal')
            journal=json.loads(JOURNAL.read_text())
            if journal.get('version')!='codi-caddy-guard-transition/1' or journal.get('uid')!=UID:raise ValueError('Invalid pending journal')
            result=recover(journal)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    try:main()
    except Exception as error:raise SystemExit(type(error).__name__+': '+str(error))
