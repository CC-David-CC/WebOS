#!/usr/bin/env python3
"""Reconcile the reviewed Browser issuer upgrade with its renewal unit.

Run only on box-webhost after the renewal operator's read-only inspect passes.
The controller lock, exact configuration/release pins, unit backup, atomic
replacement and systemd validation prevent silently accepting another change.
"""
import fcntl,hashlib,json,os,pathlib,subprocess,tempfile
P=pathlib.Path
config=P('/etc/codi-connected/ksu/managed.json')
unit=P('/etc/systemd/system/codi-ksu-live-root-renew.service')
lock=P('/home/dflanag3/webhost-sites/.controller.lock')
backup=P('/var/backups/codi-renew-before-browser-issuer-r3.service')
oldconfig='b88ef5dd47031104824f52fa0fafa777b392df845ac2a62987a65b17938f259e'
oldrelease='14c3655633cbe74388c1e7382f20768ce75e7cbb99eb22903c8686f3a270d1d0'
newconfig='0651b5e6bc49657795c6d77e768d35a3ee351561ab6baad994fc2b013f524e18'
newrelease='0aaf61849fa03e41376d63a36496c83e83adbc97c14aeafe366100ff9e530af2'
release=P('/srv/codi-connected/releases/browser-issuer-profile28-large-r3')
digest=lambda value:hashlib.sha256(value).hexdigest()

if os.geteuid()!=0 or os.uname().nodename!='box-webhost':raise ValueError('Root on box-webhost required')
with lock.open('r+') as lf:
    fcntl.flock(lf,fcntl.LOCK_EX|fcntl.LOCK_NB)
    raw=config.read_bytes();data=json.loads(raw);original=unit.read_bytes()
    if (digest(raw)!=newconfig or data['manifestSHA256']!=newrelease or
        data['release']!=str(release) or digest((release/'connected-release.json').read_bytes())!=newrelease):
        raise ValueError('Reviewed issuer configuration changed')
    if unit.is_symlink() or unit.stat().st_uid!=0 or unit.stat().st_mode&0o022:raise ValueError('Unsafe renewal unit')
    if original.count(oldconfig.encode())!=1 or original.count(oldrelease.encode())!=1:raise ValueError('Renewal baseline changed')
    if subprocess.run(['systemctl','is-active','--quiet','codi-ksu-live-root-renew.service']).returncode==0:raise ValueError('Renewal already running')
    if subprocess.run(['systemctl','is-active','--quiet','codi-ksu-live-root-renew.timer']).returncode!=0:raise ValueError('Renewal timer not active')
    replacement=original.replace(oldconfig.encode(),newconfig.encode()).replace(oldrelease.encode(),newrelease.encode())
    fd=os.open(backup,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(original);f.flush();os.fsync(f.fileno())
    with tempfile.TemporaryDirectory(prefix='.codi-renew-browser-',dir=unit.parent) as directory:
        candidate=P(directory)/unit.name; rollback=P(directory)/'rollback.service'
        for path,contents in ((candidate,replacement),(rollback,original)):
            with path.open('wb') as f:f.write(contents);f.flush();os.fsync(f.fileno())
            path.chmod(0o644)
        subprocess.run(['systemd-analyze','verify',str(candidate)],check=True)
        try:
            os.replace(candidate,unit)
            subprocess.run(['systemctl','daemon-reload'],check=True)
        except BaseException:
            os.replace(rollback,unit)
            subprocess.run(['systemctl','daemon-reload'],check=True)
            raise
print(json.dumps({'status':'updated','configSHA256':newconfig,'releaseSHA256':newrelease,'backup':str(backup)}))
