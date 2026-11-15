#!/usr/bin/env python3
"""Temporarily grant one disposable test account report administration.

Root on box-webhost only. `restore` recovers an interrupted test. The journal
preserves exact prior bytes; unexpected independent changes stop restoration.
"""
import base64, fcntl, hashlib, json, os, re, socket, sqlite3, subprocess, sys, tempfile, time
from pathlib import Path

CONFIG=Path('/etc/codi-browser/report-admins.json')
JOURNAL=Path('/run/codi-browser-report-admin-test.json')
LOCK=Path('/run/codi-browser-report-admin-test.lock')
DB=Path('/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3')
def sha(x): return hashlib.sha256(x).hexdigest()
def replace(path,data,mode):
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,'wb') as out:out.write(data);out.flush();os.fsync(out.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def restart():
    subprocess.run(['systemctl','restart','codi-browser-relay.service'],check=True,timeout=40)
    subprocess.run(['systemctl','is-active','--quiet','codi-browser-relay.service'],check=True,timeout=10)
    deadline=time.monotonic()+20
    while True:
        try:
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as probe:probe.connect('/run/codi-browser/relay.sock')
            break
        except OSError:
            if time.monotonic()>=deadline:raise RuntimeError('Browser relay did not become ready')
            time.sleep(.1)
def main():
    if os.geteuid()!=0 or os.uname().nodename!='box-webhost':raise ValueError('Root on box-webhost required')
    if len(sys.argv)!=3 or sys.argv[1] not in ('apply','restore') or not re.fullmatch(r'browserprobe[0-9a-f]{10}',sys.argv[2]):raise ValueError('Expected apply/restore and disposable username')
    action,name=sys.argv[1:]
    with LOCK.open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if action=='apply':
            if JOURNAL.exists():raise ValueError('Test journal already exists; restore it first')
            if CONFIG.is_symlink() or not CONFIG.is_file() or CONFIG.stat().st_uid!=0 or CONFIG.stat().st_mode&0o022:raise ValueError('Unsafe administrator configuration')
            original=CONFIG.read_bytes();admins=json.loads(original)
            with sqlite3.connect(f'file:{DB}?mode=ro',uri=True) as db: row=db.execute('SELECT subject FROM accounts WHERE username=?',(name,)).fetchone()
            if not row or not re.fullmatch(r'user:[0-9a-f-]{36}',row[0]) or row[0] in admins:raise ValueError('Disposable account not found or already an administrator')
            updated=(json.dumps(admins+[row[0]],indent=2)+'\n').encode()
            journal={'username':name,'subject':row[0],'original':base64.b64encode(original).decode(),'originalHash':sha(original),'updatedHash':sha(updated)}
            replace(JOURNAL,(json.dumps(journal)+'\n').encode(),0o600)
            replace(CONFIG,updated,0o644);restart();print('Temporary report administrator enabled')
        else:
            if not JOURNAL.is_file() or JOURNAL.is_symlink() or JOURNAL.stat().st_uid!=0:raise ValueError('No safe journal')
            j=json.loads(JOURNAL.read_text());original=base64.b64decode(j['original'],validate=True)
            if j['username']!=name or sha(original)!=j['originalHash'] or sha(CONFIG.read_bytes()) not in (j['originalHash'],j['updatedHash']):raise ValueError('Configuration changed independently')
            # Delete only report requests created by this test subject. Run as
            # the service user so SQLite journal files retain correct ownership.
            code='import sqlite3,sys; d=sqlite3.connect("/var/lib/codi-browser-reports/reports.sqlite3"); s=sys.argv[1]; d.execute("BEGIN IMMEDIATE"); d.execute("DELETE FROM reports WHERE request_id IN (SELECT id FROM requests WHERE owner=?)",(s,)); d.execute("DELETE FROM requests WHERE owner=?",(s,)); d.commit()'
            subprocess.run(['sudo','-n','-u','codi-browser','/usr/bin/python3','-c',code,j['subject']],check=True,timeout=20)
            replace(CONFIG,original,0o644);restart();JOURNAL.unlink();print('Prior report administrators restored; test requests removed')
if __name__=='__main__':main()
