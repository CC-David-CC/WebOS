#!/usr/bin/env python3
"""Loopback-only actual issuer restart/config test; never touches host state."""
import json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
if len(sys.argv)!=4: raise SystemExit('usage: issuer-config-test.py BASE CANDIDATE PYTHON')
base,candidate,python=map(Path,sys.argv[1:]); port=19981; origin=f'http://127.0.0.1:{port}'
with tempfile.TemporaryDirectory(prefix='codi-issuer-config-') as tmp:
 state=str(Path(tmp)/'runtime'); log=open(Path(tmp)/'issuer.log','w+')
 def start(root,extra=()):
  cmd=[str(python),str(root/'scripts/serve-connected.py'),'--port',str(port),'--runtime-dir',state,'--origin',origin,'--user-files',*extra]
  proc=subprocess.Popen(cmd,stdout=log,stderr=log)
  for _ in range(200):
   if proc.poll() is not None: log.flush();raise RuntimeError(Path(log.name).read_text())
   try:
    with urllib.request.urlopen(origin+'/config.json',timeout=.5) as response:return proc,json.load(response)
   except (OSError,ValueError):time.sleep(.1)
  proc.terminate();proc.wait(timeout=10);raise RuntimeError('Issuer startup timed out')
 def stop(proc):
  proc.terminate();proc.wait(timeout=15)
 old,old_config=start(base);stop(old)
 new,new_config=start(candidate,['--beta-opfs-file-content'])
 guest=subprocess.Popen([str(python),str(base/'guest-relay/server.py'),'--port','19982','--origin',origin,'--identity-config-port',str(port),'--no-guest-network'],stdout=log,stderr=log)
 try:
  for _ in range(100):
   if guest.poll() is not None: log.flush();raise RuntimeError(Path(log.name).read_text())
   try:
    with urllib.request.urlopen('http://127.0.0.1:19982/config.json',timeout=.5) as response: forwarded=json.load(response)
    break
   except OSError: time.sleep(.1)
  else: raise RuntimeError('Guest frontend startup timed out')
  assert forwarded==new_config, 'Actual frontend dropped or altered issuer metadata'
 finally: stop(guest);stop(new)
 assert 'fileStorage' not in old_config
 assert new_config.pop('fileStorage')=={'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2}
 assert old_config==new_config, 'Unexpected config/identity change across issuer restart'
 for args in [[],['--user-files','--origin','https://ksu.codes'],['--user-files','--origin','https://beta.ksu.codes','--base-path','/hidden']]:
  run=subprocess.run([str(python),str(candidate/'scripts/serve-connected.py'),'--beta-opfs-file-content',*args],capture_output=True,text=True,timeout=10)
  assert run.returncode!=0 and 'Beta OPFS requires' in run.stderr
 print('PASS actual sealed issuer restart: unchanged identity and configuration, actual guest forwarding, opt-in beta metadata and invalid-origin/mount guards')
