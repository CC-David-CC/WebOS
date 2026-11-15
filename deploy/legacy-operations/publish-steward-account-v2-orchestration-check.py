#!/usr/bin/env python3
"""Exercise candidate publisher orchestration with isolated fake platform effects."""
import importlib.util,json,shutil,sys,tempfile,types,hashlib
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True;ROOT=Path(__file__).resolve().parents[1];source=ROOT/'scripts/publish-steward-account-v2.py';spec=importlib.util.spec_from_file_location('candidate',source);p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
checks=[];commit='a'*40
with tempfile.TemporaryDirectory(prefix='steward-publisher-orchestration-') as temp:
 root=Path(temp);host=root/'host';host.mkdir();(host/'.controller.lock').write_text('');repo=root/'repo';packet=repo/'tools/codiserver/steward-account-release-r2';packet.mkdir(parents=True);shutil.copyfile(source,packet/'publish-steward-account-v2.py');shutil.copytree(ROOT/'.build/releases/steward-account-features-r1',packet/'release');before=root/'before';shutil.copytree(ROOT/'.build/releases/connected-browser-files-r1',before);dest=root/'after';control=root/'control'/'managed.json';control.parent.mkdir();guest=root/'guest';guest.mkdir();(guest/'config.json').write_text(json.dumps({'stateRoot':str(guest)}))
 helper_text=b'fixture helper';helper_dir=root/hashlib.sha256(helper_text).hexdigest();helper_dir.mkdir();helper=helper_dir/'helper.py';helper.write_bytes(helper_text);publisher_dir=root/hashlib.sha256(source.read_bytes()).hexdigest();publisher_dir.mkdir();installed=publisher_dir/'publisher.py';shutil.copyfile(source,installed)
 state={'instance':'codi-ksu-hidden','origin':'https://ksu.codes','basePath':'','manifestSHA256':p.OLD,'release':str(before),'stateRoot':str(root/'state'),'guestNetwork':{'policySHA256':'436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049','configFile':str(guest/'config.json')}};control.write_text(json.dumps(state));events=[];fail={'on':False}
 def run(args,*a,**kw):
  args=list(map(str,args));
  if 'runuser' in args:return commit if 'rev-parse' in args else ''
  if args[0]=='systemctl':return 'inactive'
  events.append(args);return ''
 def install(src,dst,manifest,pin):
  if Path(src)!=Path(dst):shutil.copytree(src,dst)
  assert p.sha(Path(dst)/manifest)==pin
 def native(action,*args):
  events.append(['native',action,*map(str,args)])
  if fail['on']:raise OSError('fixture failure')
  c=json.loads(control.read_bytes())
  if action=='upgrade':
   target=Path(args[args.index('--release')+1]);c['release']=str(target);c['manifestSHA256']=p.NEW if target==dest else p.OLD;control.write_text(json.dumps(c))
  return {'status':'ok'}
 fake=types.SimpleNamespace(HOST=host,REPO=repo,CONTROL=control,PYTHON='python',protected=lambda x:None,run=run,install=install,native=native,hosting_pins=lambda:p.PINS,capture=lambda c:{'capture':True},preserved=lambda before,c:{'statePreserved':True})
 class DB:
  def __enter__(self):return self
  def __exit__(self,*a):pass
  def execute(self,sql):return self
  def fetchone(self):return (0,)
  def fetchall(self):return []
 real_module=p.module
 def load(name,path):return fake if Path(path)==helper else real_module(name,path)
 real_sha=p.sha
 def digest(path):
  if str(path)=='/var/lib/codi-rooms/ksu/rooms.sqlite3':return 'fixed'
  return real_sha(Path(path))
 p.BEFORE=before;p.DEST=dest;p.HELPER=helper;p.__file__=str(installed);p.module=load;p.sha=digest;p.ensure_renewal=lambda m,c,w:(events.append(['timer',c['manifestSHA256'],w]) or {'timerActive':True})
 with patch.object(p.os,'geteuid',return_value=0),patch.object(p.socket,'gethostname',return_value='box-webhost'),patch.object(p.sqlite3,'connect',side_effect=lambda *a,**k:DB()),patch.object(p.time,'sleep',return_value=None):
  assert p.main('stage',commit)['afterManifestSHA256']==p.OLD and dest.exists();checks.append('stage validates exact release without switch')
  assert p.main('activate',commit)['afterManifestSHA256']==p.NEW;checks.append('activate selects candidate and announces maintenance')
  assert p.main('rollback',commit)['afterManifestSHA256']==p.OLD;checks.append('rollback selects old code without restoring state')
  fail['on']=True
  try:p.main('activate',commit)
  except OSError:pass
  else:raise AssertionError('failed native update reported success')
  assert any('active' in a and 'needs operator recovery' in ' '.join(a) for a in events);checks.append('failed transition leaves maintenance recovery notice')
  fail['on']=False;assert p.main('recover',commit)['action']=='recover';checks.append('recover delegates to journaled native operation')
assert ['timer',p.NEW,True] in events and ['timer',p.OLD,True] in events;checks.append('activation and rollback reconcile renewal pins')
print(json.dumps({'status':'PASS','checks':checks,'scope':'Actual candidate publisher main with fake helper/system state and temporary exact releases; no root custody, systemd or live state.'},indent=2))
