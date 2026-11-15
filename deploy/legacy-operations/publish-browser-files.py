#!/usr/bin/env python3
"""CANDIDATE: browser-only persistent files integration; not installed. Both forward and rollback retain chat OFF.

Uses existing native transaction recovery; no hosting, service account, history
backend, authority signer, credential or user-data restore is performed.
"""
import argparse,fcntl,hashlib,importlib.util,json,os,re,socket,sqlite3,time
from pathlib import Path
OLD='9f86587c8590eed2c34bbf3eede2efb109fe0a8401328551a00092f19e3b9fe9'
NEW='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46'
PINS={'common.py':'9f7fef18df198f783b71d13da1950272edc8518f8726700ab01e18ff299acd4a','sites.toml':'35bd536bf8933f70a52efbb5ff4bbafbae737568b0fac16b60aba565187fd776','Caddy':'5e76e178c0a54dd43c7a240781d57ae4fcbc9f2f66c5e288e96b5173c553b3bb'}
HELPER=Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
DEST=Path('/srv/codi-connected/releases/native25-'+NEW[:16]);BEFORE=Path('/srv/codi-connected/releases/native25-'+OLD[:16])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify_release(before,destination):
 assert sha(before/'connected-release.json')==OLD and sha(destination/'connected-release.json')==NEW
 # Bind executable validator bytes before importing any candidate Python.
 a=json.loads((before/'connected-release.json').read_bytes())['files'];b=json.loads((destination/'connected-release.json').read_bytes())['files']
 assert a['origin_service/release.py']==b['origin_service/release.py']
 assert sha(before/'origin_service/release.py')==a['origin_service/release.py']['sha256'] and sha(destination/'origin_service/release.py')==b['origin_service/release.py']['sha256']
 contract=module('browser_files_publish_contract',before/'origin_service/release.py');assert contract.verify(before)['manifestSHA256']==OLD
 v=contract.verify(destination);assert v['manifestSHA256']==NEW and v['files']==301
 assert len(contract.V19_NATIVE)==57 and all(a[n]==b[n] for n in contract.V19_NATIVE)
 old=json.loads((before/'assets/desktop/network-release.json').read_bytes());new=json.loads((destination/'assets/desktop/network-release.json').read_bytes());assert old['directory']==new['directory'] and old['modules']==new['modules'] and len(new['modules'])==40
 assert all(a[old['directory']+'/'+n]==b[new['directory']+'/'+n] for n in old['modules'])
 for name in ['networking.js','reference.js','terminal.js']:assert (before/old['coreDirectory']/name).read_bytes()==(destination/new['coreDirectory']/name).read_bytes()
 assert 'const disabled=true;' in (destination/new['coreDirectory']/'networking.js').read_text()
 for n,r in a.items():
  if '/apps/' in n and not n.startswith(('assets/desktop/apps/files/','assets/desktop/apps/text/')):assert b[n]==r
 services=json.loads((destination/'assets/desktop/shared-services.json').read_bytes());prior=json.loads((before/'assets/desktop/shared-services.json').read_bytes());assert len(prior['services'])==1 and len(services['services'])==2 and prior['services'][0] in services['services']
 browser=[s for s in services['services'] if s['name']=='browser-files'];assert len(browser)==1 and browser[0]['sourceAlias']=='assets/desktop/browser-files.mjs' and browser[0]['files']['index.mjs']['sha256']=='21ddfd494b27db31f6992b5dc9cc8d0df7b3b9347b469031152ff8da225b2da7'
 assert browser[0]['path'] in (destination/new['coreDirectory']/'desktop-apps.js').read_text()
 allowed={'index.html','release.json','assets/desktop/network-release.json','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js','assets/desktop/shared-services.json'}
 changed=[n for n in set(a)|set(b) if a.get(n)!=b.get(n)]
 assert all(n in allowed or n.startswith(('assets/desktop/core-v10/','assets/desktop/apps/files/','assets/desktop/apps/text/','assets/desktop/services/browser-files/')) or re.fullmatch(r'assets/desktop/apps-v2-[a-f0-9]{64}\.(mjs|json)',n) for n in changed)
 cache=json.loads((destination/'assets/desktop/cache-manifest.json').read_bytes())
 for s in services['services']:
  assert s['path'] in cache['files']
  assert all(b[str(Path(s['path']).parent/n)]==r for n,r in s['files'].items())
 return v|{'nativeFilesUnchanged':57,'networkModulesUnchanged':40,'otherApplicationBundlesUnchanged':5,'chatPaused':True}

def main(action,commit):
 assert os.geteuid()==0 and socket.gethostname()=='box-webhost' and re.fullmatch('[a-f0-9]{40}',commit)
 assert sha(HELPER)==HELPER.parent.name
 m=module('device_history_publish_helpers',HELPER);m.protected(HELPER);m.protected(Path(__file__));assert Path(__file__).parent.name==sha(Path(__file__));m.NATIVE_DIR=DEST
 def config():
  c=json.loads(m.CONTROL.read_bytes());assert c['manifestSHA256'] in [OLD,NEW] and c['release']==str(BEFORE if c['manifestSHA256']==OLD else DEST)
  assert c['origin']=='https://ksu.codes' and c['basePath']=='' and c['instance']=='codi-ksu-hidden' and 'hostedRooms' not in c
  assert c['guestNetwork']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
  if action!='recover':assert not any((m.CONTROL.parent/n).exists() for n in ['maintenance.json','native-rollout.json','site-cutover.json'])
  return c
 def paused():
  units=['codi-rooms-ksu.service','codi-rooms-ksu-proxy.socket','codi-rooms-ksu-proxy.service','codi-readers-ksu.service','codi-readers-ksu-proxy.socket','codi-readers-ksu-proxy.service','codi-readers-ksu-refresh.timer']
  for u in units:assert m.run(['systemctl','show',u,'-p','ActiveState','--value'])=='inactive',u
  with sqlite3.connect('file:/var/lib/codi-rooms/ksu/rooms.sqlite3?mode=ro',uri=True) as db:assert not any(db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['events','rooms','streams','leases','members','work'])
  assert m.hosting_pins()==PINS
 def usage(c):
  root=Path(json.loads(Path(c['guestNetwork']['configFile']).read_bytes())['stateRoot']);values={}
  for role in ['anonymous','registered']:
   with sqlite3.connect('file:'+str(root/role/'usage.sqlite3')+'?mode=ro',uri=True) as db:values[role]=db.execute('SELECT subject,window,bytes,packets FROM usage ORDER BY subject,window').fetchall()
  return values
 def checked():return verify_release(BEFORE,DEST)
 with (m.HOST/'.controller.lock').open('rb') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  git=lambda *args:m.run(['runuser','-u','dflanag3','--','git','-C',m.REPO,*args]);assert git('rev-parse','HEAD')==commit and not git('status','--porcelain')
  c=config();paused();packet=m.REPO/'tools/codiserver/browser-files-r1';assert sha(packet/'publish-browser-files.py')==sha(Path(__file__))
  result={'status':'PASS','sourceCommit':commit,'action':action,'beforeManifestSHA256':c['manifestSHA256']}
  if action=='stage':m.install(packet/'release',DEST,'connected-release.json',NEW)
  # Existing-destination install is a closed-manifest/root-custody verifier;
  # no files are copied or changed on these two exact existing paths.
  m.install(BEFORE,BEFORE,'connected-release.json',OLD);m.install(DEST,DEST,'connected-release.json',NEW)
  result['releaseVerification']=checked()
  target=NEW if action=='activate' else OLD if action=='rollback' else None
  args=[m.PYTHON,'-I','-B',Path(c['release'])/'scripts/desktop-maintenance.py','--directory',Path(c['stateRoot'])/'public']
  changing=target and c['manifestSHA256']!=target
  if changing:
   m.run([*args,'scheduled','--in-seconds','10','--duration','240','--message','Browser files update in 10 seconds. Please save your work. Chat remains disabled. Unsaved browser work is not backed up.']);time.sleep(10)
  before=m.capture(c);used=usage(c);database=Path('/var/lib/codi-rooms/ksu/rooms.sqlite3');dbpin=sha(database)
  try:
   if changing:result['native']=m.native('upgrade','--release',DEST if target==NEW else BEFORE,'--python',m.PYTHON)
   elif action=='recover':result['native']=m.native('recover-operation')
   elif action=='verify':result['native']=m.native('status')
   after=config();result['state']=m.preserved(before,after);paused();assert sha(database)==dbpin
   if target:assert after['manifestSHA256']==target
   current=usage(after)
   for role,rows in used.items():
    now={(r[0],r[1]):r[2:] for r in current[role]};assert all((r[0],r[1]) in now and all(a>=b for a,b in zip(now[(r[0],r[1])],r[2:])) for r in rows)
   if changing or action=='recover':m.run([*args,'cancelled','--duration','120','--message','Host update ended. Chat remains disabled. Reload to use the current version. Saved browser files remain on this device; running Linux and unsaved work were not backed up.'])
   result.update(afterManifestSHA256=after['manifestSHA256'],nativeConfigSHA256=sha(m.CONTROL),hostingPins=m.hosting_pins(),chatDisabled=True,chatDatabaseUnchangedAndEmpty=True,guestUsageFloorsPreserved=True,rootMinted=False,dataRestored=False,bootPolicyChanged=False,routerPortsChanged=False)
   return result
  except BaseException:
   # Never announce completion on a failed/ambiguous native transition. The
   # native typed journal, not a retry or old database restore, decides recovery.
   if changing or action=='recover':
    try:m.run([*args,'active','--duration','3600','--message','The update needs operator recovery. Chat remains disabled. Saved browser files remain on this device; running Linux and unsaved work were not backed up.'])
    except Exception:pass
   raise
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['stage','activate','rollback','verify','recover']);p.add_argument('--commit',required=True);a=p.parse_args()
 try:v=main(a.action,a.commit)
 except Exception as e:
  import traceback,subprocess
  v={'status':'FAIL','action':a.action,'error':str(e),'traceback':traceback.format_exc(),'recovery':'Inspect native maintenance journal and use explicit recover; keep chat503/routes and units stopped; never restore old chat data.'}
  if isinstance(e,subprocess.CalledProcessError):v.update(operatorStdout=(e.stdout or '')[-3000:],operatorStderr=(e.stderr or '')[-3000:])
 out=Path('/srv/codi-connected')/('browser-files-'+a.action+'-'+str(time.time_ns())+'-result.json');fd=os.open(out,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as f:json.dump(v,f,indent=2)
 print(json.dumps({'status':v['status'],'action':a.action,'rootReceipt':str(out),'rootReceiptSHA256':sha(out),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
