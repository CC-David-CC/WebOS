#!/usr/bin/env python3
"""Own a loopback-only outside ChromeDriver and SSH control forward for root tests."""
import argparse
import json
import os
from pathlib import Path
import shlex
import signal
import socket
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = ROOT/'.build/checks/moonpie-browser-fixture.json'
TARGET = 'maint@100.105.243.29'
PREPARE = r'''
import json,os,pathlib,socket,subprocess,time,urllib.request
P=pathlib.Path;folder=P.home()/'snap/chromium/common'/('codi-root-wan-'+str(time.time_ns()));folder.mkdir(mode=0o700)
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
binary='/snap/chromium/current/usr/lib/chromium-browser/chromedriver'
with (folder/'driver.log').open('wb') as log:
 p=subprocess.Popen([binary,'--port='+str(port),'--allowed-ips=127.0.0.1'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
deadline=time.monotonic()+20
while True:
 if p.poll() is not None:raise ValueError('Owned driver exited before readiness')
 try:
  with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/status',timeout=1) as r:assert json.load(r)['value']['ready']
  break
 except OSError:
  if time.monotonic()>deadline:raise
  time.sleep(.1)
print(json.dumps({'folder':str(folder),'port':port,'driverPID':p.pid,'sshTarget':'maint@100.105.243.29','driverStopped':False,'fixtureFolderRemoved':False}))
'''


def remote(code, value=None):
    r = subprocess.run(['ssh', '-o', 'BatchMode=yes', TARGET, '/usr/bin/python3', '-I', '-B', '-c', shlex.quote(code)], input=None if value is None else json.dumps(value), capture_output=True, text=True, timeout=45)
    if r.returncode:raise ValueError(r.stderr[-4000:] or r.stdout[-2000:])
    return json.loads(r.stdout)


def prepare():
    if CONTEXT.exists():
        previous = json.loads(CONTEXT.read_text())
        if not previous.get('driverStopped') or not previous.get('fixtureFolderRemoved'):
            raise ValueError('Inspect/clean the existing owned fixture before creating another')
        CONTEXT.rename(CONTEXT.with_name('moonpie-browser-before-root-'+str(time.time_ns())+'.json'))
    value = remote(PREPARE)
    with socket.socket() as s:s.bind(('127.0.0.1', 0));port = s.getsockname()[1]
    log = (ROOT/'.build/checks/moonpie-root-forward.log').open('ab')
    p = subprocess.Popen(['ssh', '-o', 'BatchMode=yes', '-o', 'ExitOnForwardFailure=yes', '-N', '-L', '127.0.0.1:'+str(port)+':127.0.0.1:'+str(value['port']), TARGET], stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    log.close();value.update(localForwardPID=p.pid, localDriverURL='http://127.0.0.1:'+str(port), forwardStopped=False)
    CONTEXT.write_text(json.dumps(value, indent=2)+'\n')
    deadline = time.monotonic()+20
    while True:
        if p.poll() is not None:raise ValueError('Owned SSH forward exited')
        try:
            with urllib.request.urlopen(value['localDriverURL']+'/status', timeout=1) as r:assert json.load(r)['value']['ready']
            break
        except OSError:
            if time.monotonic()>deadline:raise
            time.sleep(.1)
    return {'status': 'PASS', **value, 'scope': 'Tailscale SSH controls browser only; application URL/data use public HTTPS/RTC'}


def cleanup():
    v = json.loads(CONTEXT.read_text())
    result = remote(r'''
import json,os,pathlib,shutil,signal,sys,time
v=json.load(sys.stdin);P=pathlib.Path;folder=P(v['folder']);assert folder.parent==P.home()/'snap/chromium/common' and folder.name.startswith('codi-root-wan-') and not folder.is_symlink()
pid=int(v['driverPID']);proc=P('/proc')/str(pid)
if proc.exists():
 args=(proc/'cmdline').read_bytes().split(b'\0');assert b'/snap/chromium/current/usr/lib/chromium-browser/chromedriver'==args[0] and ('--port='+str(v['port'])).encode() in args
 os.kill(pid,signal.SIGTERM)
 deadline=time.monotonic()+10
 while proc.exists():
  if (proc/'stat').read_text().split()[2]=='Z':break
  if time.monotonic()>deadline:raise ValueError('Owned driver has not exited')
  time.sleep(.1)
# Refuse to delete profiles belonging to still-running browser processes.
for p in P('/proc').glob('[0-9]*/cmdline'):
 try:args=p.read_bytes().split(b'\0')
 except OSError:continue
 assert not any(a.startswith(('--user-data-dir='+str(folder)+'/').encode()) for a in args),'Owned browser session still active'
if folder.exists():shutil.rmtree(folder)
print(json.dumps({'driverStopped':True,'fixtureFolderRemoved':True}))
''', v)
    pid = v['localForwardPID'];proc = Path('/proc')/str(pid)
    if proc.exists():
        args = (proc/'cmdline').read_bytes().split(b'\0')
        assert TARGET.encode() in args and b'-N' in args and ('127.0.0.1:'+v['localDriverURL'].rsplit(':',1)[1]+':127.0.0.1:'+str(v['port'])).encode() in args
        os.kill(pid, signal.SIGTERM)
    v.update(result, forwardStopped=True);CONTEXT.write_text(json.dumps(v, indent=2)+'\n')
    return {'status': 'PASS', **v}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('action', choices=['prepare', 'cleanup']);args = p.parse_args()
    print(json.dumps(prepare() if args.action == 'prepare' else cleanup(), indent=2))
