#!/usr/bin/env python3
"""Stop the two prototype services, reset their test channels, and validate."""
import base64,fcntl,json,os,pathlib,re,shutil,sqlite3,subprocess,time,urllib.request
P=pathlib.Path;assert os.geteuid()==0
lock=P('/home/dflanag3/webhost-sites/.controller.lock');db=P('/var/lib/codi-official/state/official.sqlite');keys=P('/var/lib/codi-official/state/validator-keys');helper=P('/tmp/reset-prototype-chat-chess.py');package=P('/srv/codi-connected/official-services/chess-rotation-r2');python=P('/srv/codi-connected/venvs/official-chess-r1/bin/python')
services=['codi-official.service','codi-featured-chess.service'];result=None;baseline={p.name for p in keys.glob('*.pem')}
def run(args,timeout=120):return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True,timeout=timeout).stdout
def fetch(path):
 with urllib.request.urlopen('https://ksu.codes'+path,timeout=5) as r:return json.load(r)
with lock.open('r+') as lf:
 fcntl.flock(lf,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert all(run(['systemctl','is-active',s]).strip()=='active' for s in services)
 assert len(fetch('/official-directory?after=&limit=32')['items'])==1
 system=fetch('/official-channel?channel=system')['items'][0]['channel'];receipt=P('/srv/codi-connected/prototype-chat-chess-reset-result.json');assert not receipt.exists()
 try:
  run(['systemctl','stop',services[1]]);run(['systemctl','stop',services[0]])
  result=json.loads(run(['sudo','-n','-u','codi-official',python,'-B',helper,db,keys,package]))
  assert result['status']=='PASS' and result['recoveryDirectory'].startswith(str(keys/'.prototype-reset-'))
  run(['systemctl','start',services[0]]);run(['systemctl','start',services[1]])
  for _ in range(20):
   try:
    directory=fetch('/official-directory?after=&limit=32');featured=fetch('/official-channel?channel=featured-game')['invitation']
    assert any(x['channel']==result['newChat'] and x['label']=='General chess chat' for x in directory['items'])
    assert featured['chat']['config']['channel']==result['newChat'] and featured['game']['config']['channel']==result['newGame']
    assert fetch('/official-channel?channel=system')['items'][0]['channel']==system
    assert all(run(['systemctl','is-active',s]).strip()=='active' for s in services)
    break
   except Exception:
    if _==19:raise
    time.sleep(.5)
  recovery=P(result['recoveryDirectory']);retired=set()
  for p in (recovery/'metadata').iterdir():
   value=json.loads(p.read_text())
   if p.name=='general-chess.json':retired.add(value['channel'])
   else:retired.update((value['game']['channel'],value['black']))
  references='\n'.join(p.read_text() for p in keys.glob('*.json'))
  with sqlite3.connect(db) as current:
   for channel,wire in current.execute('SELECT channel,policy_wire FROM official_channels'):
    payload=wire.split('.')[1];references+='\n'+channel+'\n'+base64.urlsafe_b64decode(payload+'='*(-len(payload)%4)).decode()
  removed=0
  for actor in retired:
   assert re.fullmatch(r'[A-Za-z0-9_-]{43}',actor)
   if actor not in references:
    p=keys/(actor+'.pem');assert not p.is_symlink();p.unlink(missing_ok=True);removed+=1
  report={'status':'PASS','newChat':result['newChat'],'newGame':result['newGame'],'removedTestGames':result['removedTestGames'],'removedRetiredKeys':removed}
  receipt.write_text(json.dumps(report,indent=2)+'\n');receipt.chmod(0o600)
  shutil.rmtree(result['recoveryDirectory']);print(json.dumps(report),flush=True)
 except BaseException:
  if result:
   for s in reversed(services):subprocess.run(['systemctl','stop',s],capture_output=True)
   recovery=P(result['recoveryDirectory']);saved=recovery/'metadata';copy=sqlite3.connect(recovery/'official.sqlite');current=sqlite3.connect(db)
   try:copy.backup(current)
   finally:copy.close();current.close()
   for p in [keys/'general-chess.json',*keys.glob('featured-game.json'),*keys.glob('featured-next-*.json')]:p.unlink(missing_ok=True)
   for p in saved.iterdir():shutil.copy2(p,keys/p.name);os.chown(keys/p.name,keys.stat().st_uid,keys.stat().st_gid)
   for p in keys.glob('*.pem'):
    if p.name not in baseline:p.unlink()
   for p in (recovery/'keys').iterdir():shutil.copy2(p,keys/p.name);os.chown(keys/p.name,keys.stat().st_uid,keys.stat().st_gid)
   shutil.rmtree(recovery)
  for s in services:subprocess.run(['systemctl','start',s],capture_output=True)
  raise
