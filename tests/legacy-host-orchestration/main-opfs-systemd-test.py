#!/usr/bin/env python3
"""Isolated real-systemd issuer and actual transaction; fixture substitutions below."""
import hashlib,importlib.util,json,os,pathlib,select,signal,subprocess,sys,tempfile,time,urllib.error,urllib.request
P=pathlib.Path;root=P(sys.argv[1]).resolve();assert os.geteuid()==0
assert hashlib.sha256((root/'connected-release.json').read_bytes()).hexdigest()=='01080b868f2d040fe1053dfcc09d4dfe25652d77c11be4e4142ad37ba4eea563'
manifest=json.loads((root/'connected-release.json').read_bytes());found={}
for item in root.rglob('*'):
 if item.is_symlink() or not(item.is_file() or item.is_dir()):raise ValueError('Unsafe release input')
 if item.is_file() and item.name!='connected-release.json':
  raw=item.read_bytes();found[item.relative_to(root).as_posix()]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
assert found==manifest['files'],'release inventory changed'
sys.path[:0]=[str(root),str(root/'codiserver-server-v0.3.0')];spec=importlib.util.spec_from_file_location('fixture_op',root/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
from origin_service import opfs_management as tx,maintenance,deployment
port=int(os.environ.get('CODI_TEST_PORT','19927'));name='codi-main-opfs-fixture-'+str(os.getpid());unit=P('/run/systemd/system')/(name+'-issuer.service');py='/tmp/codi-audio-upload-19584-venv/bin/python';origin='https://ksu.codes'
assert not unit.exists()
def run(*a):return subprocess.run(a,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30).stdout
def systemctl(*a):return run('/usr/bin/systemctl',*a)
def get():
 request=urllib.request.Request(f'http://127.0.0.1:{port}/config.json',headers={'Host':'ksu.codes'})
 with urllib.request.urlopen(request,timeout=2) as r:return json.load(r)
def ready(*args):
 for _ in range(120):
  try:
   if systemctl('is-active',name+'-issuer.service').strip()=='active':return get()
  except (OSError,ValueError,subprocess.SubprocessError):time.sleep(.1)
 raise RuntimeError('fixture issuer failed readiness')
with tempfile.TemporaryDirectory(prefix='codi-main-opfs-systemd-',dir='/var/lib') as d:
 state=P(d);(state/'public').mkdir();cfg=state/'config.json';config={'release':str(root),'stateRoot':str(state),'basePath':'','origin':origin,'ports':{'issuer':port,'steward':port+1,'guest':port+2},'python':py,'instance':name,'unitDir':'/run/systemd/system','maintenance':1,'userFiles':{'fixture':True}}
 def render(c,role):
  assert role=='issuer';command=f'{py} -B {root}/scripts/serve-connected.py --port {port} --runtime-dir {state}/issuer --origin {origin} --user-files'
  if c.get('opfsFileContentOrigin'):command+=' --opfs-file-content-origin '+c['opfsFileContentOrigin']
  return ('[Unit]\nDescription=Disposable issuer fixture\n[Service]\nType=exec\nExecStart='+command+'\nRestart=no\n').encode()
 # This fixture uses the actual issuer and systemd, but substitutes a minimal
 # renderer (no production discovery/profile-28 flags), custody, lock and
 # installed checks. It never reads production state or units.
 op.render=render;op.installed=lambda *a:None;op.ready=ready;op.issuer_config=lambda c:get();maintenance.guard=lambda *a:None;maintenance.guard_epoch=lambda *a:None;deployment.syntax=lambda *a:None;deployment.active=lambda *a:['issuer'];op.systemctl=systemctl
 def stop(c,roles):
  assert roles==['issuer'];systemctl('stop',name+'-issuer.service')
 op.stop=stop
 def current():return json.loads(cfg.read_text())
 def reset():
  if unit.exists():systemctl('stop',name+'-issuer.service')
  op.atomic(unit,render(config,'issuer'),0o644);op.atomic(cfg,(json.dumps(config)+'\n').encode());systemctl('daemon-reload');systemctl('start',name+'-issuer.service');actual=ready();op.atomic(state/'public/origin-discovery.json',json.dumps({'identity':actual['identity']}).encode(),0o444)
 def snapshot():return get()
 def interrupt(where):
  r,w=os.pipe();pid=os.fork()
  if pid==0:
   os.close(r);original=op.atomic
   def atomic(path,raw,*args):
    original(path,raw,*args)
    hit=(where=='unit' and P(path)==unit) or (where=='commit' and P(path).name=='maintenance.json' and json.loads(raw).get('phase')=='committed')
    if hit:os.write(w,b'X');signal.pause()
   op.atomic=atomic
   try:tx.configure(op,current(),cfg,origin)
   except BaseException as e:os.write(w,('E'+repr(e)).encode()[:200])
   os._exit(1)
  os.close(w)
  try:
   if not select.select([r],[],[],30)[0]:raise RuntimeError('fixture boundary timed out')
   assert os.read(r,1)==b'X','child failed before target boundary'
   os.kill(pid,signal.SIGKILL);os.waitpid(pid,0);pid=None
  finally:
   os.close(r)
   if pid is not None:
    try:os.kill(pid,signal.SIGKILL);os.waitpid(pid,0)
    except ProcessLookupError:pass
 try:
  reset();result=tx.configure(op,current(),cfg,origin);assert result['status']=='opfs-switch-configured' and snapshot()['fileStorage']==tx.EXPECTED;print('PASS actual issuer/systemd normal transition',flush=True)
  reset();interrupt('unit');assert b'--opfs-file-content-origin' in unit.read_bytes() and 'opfsFileContentOrigin' not in current();r=tx.recover(op,current(),cfg);assert r['status']=='opfs-switch-rolled-back' and 'fileStorage' not in snapshot();print('PASS actual SIGKILL after unit before config: rollback and issuer restart',flush=True)
  reset();interrupt('commit');assert json.loads((state/'maintenance.json').read_text())['phase']=='committed';r=tx.recover(op,current(),cfg);assert r['status']=='opfs-switch-committed-recovered' and snapshot()['fileStorage']==tx.EXPECTED;print('PASS actual SIGKILL after committed journal: forward recovery and issuer restart',flush=True)
 finally:
  subprocess.run(['/usr/bin/systemctl','stop',name+'-issuer.service'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);unit.unlink(missing_ok=True);subprocess.run(['/usr/bin/systemctl','daemon-reload'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
