#!/usr/bin/env python3
"""Guarded Git-first native16 staging and managed code-only upgrade/rollback.

Reuses the tested native checkpoint/rollout controller. It does not edit hosting,
policies, service accounts, ports, boot state, private files or authority data.
"""
import argparse,hashlib,json,re,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import fcntl,hashlib,json,os,re,shutil,stat,subprocess,sys,tempfile,time
from pathlib import Path
v=json.load(sys.stdin);assert os.geteuid()==0 and v['action'] in ['plan','install','upgrade','rollback','recover']
base=Path('/home/dflanag3/webhost-sites');repo=base/'sites/ksu.codes';key=v['manifestSHA256'];cfg=Path('/etc/codi-connected/ksu/managed.json')
source=repo/'tools/codiserver/native-candidates'/key;destination=Path('/srv/codi-connected/releases')/('native16-'+key[:16])
baseline=Path('/srv/codi-connected/releases/native15-6789b29e7ed65ff2');basekey='6789b29e7ed65ff2087e791448306ba68ab0b8bcc45ed70cdaa60a23fa404f35'
prior=Path('/srv/codi-connected/releases/native16-b109768a09f12760');priorkey='b109768a09f1276047d74616d722f212bb12e261ff437fd1d1a6cccd4963b8cc'
controller=Path('/srv/codi-connected/rollout-controllers')/v['rolloutSHA256']
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run(args,timeout=60):return subprocess.check_output(list(map(str,args)),text=True,timeout=timeout).strip()
def protected(path,mode=None):
 for p in [path,*path.parents]:
  s=p.lstat();assert not p.is_symlink() and s.st_uid==s.st_gid==0 and not s.st_mode&0o022
 if mode is not None:assert stat.S_IMODE(path.stat().st_mode)==mode
def read(path):
 for p in [path,*path.parents]:assert not p.is_symlink()
 with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
  s=os.fstat(f.fileno());assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and 0<=s.st_size<=134217728;raw=f.read(s.st_size+1);assert len(raw)==s.st_size;return raw
def install(folder,values):
 protected(folder.parent,0o755)
 def verify(p):
  protected(p,0o755);assert {str(f.relative_to(p)) for f in p.rglob('*') if not f.is_dir()}==set(values)
  for n,data in values.items():protected(p/n,0o644);assert read(p/n)==data
 if folder.exists():verify(folder);return
 stage=Path(tempfile.mkdtemp(prefix='.routed-release-',dir=folder.parent))
 try:
  for n,data in values.items():
   p=stage/n;p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('wb') as f:os.fchmod(f.fileno(),0o644);f.write(data);f.flush();os.fsync(f.fileno())
  for p in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:p.chmod(0o755)
  verify(stage);stage.rename(folder);fd=os.open(folder.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if stage.exists():shutil.rmtree(stage)
 verify(folder)
with (base/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 def git(*args):return run(['runuser','-u','dflanag3','--','git','-C',repo,*args])
 assert git('rev-parse','HEAD')==v['commit'] and not git('status','--porcelain')
 before=read(cfg);assert sha(before)==v['configSHA256'];c=json.loads(before)
 assert c['instance']=='codi-ksu-hidden' and c['origin']=='https://ksu.codes' and c['basePath']=='/hidden' and c['version']=='codi-managed-instance/5' and c['maintenance']==1
 assert c['python']=='/srv/codi-connected/venvs/517179c/bin/python' and c['ports']=={'issuer':8118,'steward':8119,'guest':8132}
 assert c['stateRoot']=='/var/lib/codi-connected/ksu' and c['unitDir']=='/etc/systemd/system'
 assert (c['release'],c['manifestSHA256']) in [(str(baseline),basekey),(str(prior),priorkey),(str(destination),key)]
 assert c['guestNetwork']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
 assert sha(read(baseline/'connected-release.json'))==basekey
 old=json.loads(read(baseline/'connected-release.json'));old_public=json.loads(read(baseline/'release.json'))['files']
 raw=read(source/'connected-release.json');assert sha(raw)==key;m=json.loads(raw);public=json.loads(read(source/'release.json'))['files']
 assert m['version']=='codi-connected-development/16' and {k:w for k,w in m.items() if k not in ['version','files']}=={k:w for k,w in old.items() if k not in ['version','files']}
 native=set(old['files'])-set(old_public)-{'release.json'};assert set(m['files'])==set(public)|native|{'release.json'}
 changed={n for n in native if m['files'][n]!=old['files'][n]}
 assert changed=={'origin_service/release.py','origin_service/deployment.py','origin_service/turn_management.py','scripts/manage-services.py','scripts/serve-connected.py','guest_service/client.mjs'}
 for n,r in old_public.items():
  if n not in ['index.html','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js']:assert public[n]==r
 app_assets=set()
 if key!=priorkey:
  assert sha(read(prior/'connected-release.json'))==priorkey
  previous_public=json.loads(read(prior/'release.json'))['files']
  for n,r in previous_public.items():
   if n not in ['index.html','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js','assets/desktop/network-release.json']:assert public[n]==r
  graph=json.loads(read(source/'assets/desktop/network-release.json'));previous_graph=json.loads(read(prior/'assets/desktop/network-release.json'))
  assert graph['modules']==previous_graph['modules'] and graph['directory']==previous_graph['directory']
  desktop=read(source/graph['coreDirectory']/'desktop-apps.js').decode();loader_name=re.search(r'assets/desktop/apps-v2-[a-f0-9]{64}\.mjs',desktop)[0]
  loader=read(source/loader_name);assert loader_name=='assets/desktop/apps-v2-'+sha(loader)+'.mjs'
  catalog_name='assets/desktop/'+re.search(r'apps-v2-[a-f0-9]{64}\.json',loader.decode())[0];catalog_raw=read(source/catalog_name);assert catalog_name=='assets/desktop/apps-v2-'+sha(catalog_raw)+'.json'
  catalog=json.loads(catalog_raw);assert catalog['version']=='codi-public-apps/2' and catalog['hostAPI']==2 and len(catalog['apps'])==7
  previous_desktop=read(prior/previous_graph['coreDirectory']/'desktop-apps.js').decode();previous_loader=re.search(r'assets/desktop/apps-v2-[a-f0-9]{64}\.mjs',previous_desktop)[0];previous_catalog='assets/desktop/'+re.search(r'apps-v2-[a-f0-9]{64}\.json',read(prior/previous_loader).decode())[0]
  previous_apps={a['id']:a for a in json.loads(read(prior/previous_catalog))['apps']};assert {a['id'] for a in catalog['apps']}==set(previous_apps)
  app_assets={loader_name,catalog_name}
  for a in catalog['apps']:
   if a['id']!='terminal':assert a==previous_apps[a['id']]
   else:
    folder=Path(a['path']).parent;assert str(folder)=='assets/desktop/apps/terminal/'+a['bundleSHA256']
    assert sha(json.dumps(a['files'],separators=(',',':'),ensure_ascii=False).encode())==a['bundleSHA256']
    for n,r in a['files'].items():
     assert not Path(n).is_absolute() and '..' not in Path(n).parts;name=str(folder/n);assert public[name]==r;app_assets.add(name)
 for n in set(public)-set(old_public):assert n.startswith(('assets/desktop/network-v2/','assets/desktop/core-v2/')) or n=='assets/desktop/network-release.json' or n in app_assets or (key!=priorkey and n in previous_public and public[n]==previous_public[n])
 assert {str(p.relative_to(source)) for p in source.rglob('*') if not p.is_dir()}==set(m['files'])|{'connected-release.json'}
 assert len(git('ls-files','--','tools/codiserver/native-candidates/'+key).splitlines())==len(m['files'])+1
 values={'connected-release.json':raw}
 for n,r in m['files'].items():
  assert not Path(n).is_absolute() and all(p not in ('','.','..') for p in n.split('/'));data=read(source/n);assert r=={'bytes':len(data),'sha256':sha(data)};values[n]=data
 tool_source=repo/'tools/codiserver/routed-native-r8/scripts/native-rollout.py';tool=read(tool_source);assert sha(tool)==v['rolloutSHA256'] and len(tool)==v['rolloutBytes']
 hosting={str(p):sha(read(p)) for p in [base/'ops/common.py',base/'sites.toml',Path('/etc/caddy/Caddyfile')]}
 assert hosting=={str(base/'ops/common.py'):'718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4',str(base/'sites.toml'):'c946c1e71461a49692332f4287633f64ab6e4bebb97283a4263d53bf98f10715','/etc/caddy/Caddyfile':'694518124e11bd918471cfc4b10ad3164d557bba0d003cc1de01fe7ce214dbad'}
 website=Path('/srv/webapps/ksu.codes/current').resolve();home=sha(read(website/'public/index.html'));prototype=website/'public/desktop'
 assert sha(read(prototype/'release.json'))=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9'
 pm=json.loads(read(prototype/'release.json'));assert len(pm['files'])==133
 for n,r in pm['files'].items():
  data=read(prototype/n);assert r=={'bytes':len(data),'sha256':sha(data)}
 def pids():return {r:int(run(['systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value'])) for r in ['issuer','steward','guest']}
 before_pids=pids()
 if v['action']!='recover':assert all(before_pids.values()) and not any((cfg.parent/n).exists() for n in ['native-rollout.json','maintenance.json','guest-signin-migration.json'])
 assert run(['systemctl','show',c['instance']+'-issuer-bootstrap.service','-p','MainPID','--value'])=='0'
 result={'status':'PASS','action':v['action'],'sourceCommit':v['commit'],'manifestSHA256':key,'destination':str(destination),'controllerSHA256':v['rolloutSHA256'],'prototypeFilesVerified':133,'beforePIDs':before_pids}
 if v['action']!='plan':
  install(destination,values);install(controller,{'native-rollout.py':tool})
  if v['action'] in ['upgrade','rollback','recover']:
   command=[c['python'],'-I','-B',controller/'native-rollout.py','recover' if v['action']=='recover' else 'upgrade','--operator',destination/'scripts/manage-services.py','--operator-manifest-sha256',key,'--config',cfg]
   if v['action']!='recover':command+=['--release',prior if v['action']=='rollback' else destination,'--python',c['python'],'--backup-parent','/var/backups/codi-connected/ksu']
   result['rollout']=json.loads(run(command,300))
  else:assert read(cfg)==before and pids()==before_pids
 assert hosting=={p:sha(read(Path(p))) for p in hosting} and Path('/srv/webapps/ksu.codes/current').resolve()==website and sha(read(website/'public/index.html'))==home
 after=json.loads(read(cfg));assert {k:w for k,w in after.items() if k not in ['release','manifestSHA256']}=={k:w for k,w in c.items() if k not in ['release','manifestSHA256']}
 assert Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0' and Path('/proc/sys/net/ipv4/ping_group_range').read_text().split()==['1000','1001']
 for role in ['issuer','steward','guest']:
  r=subprocess.run(['systemctl','is-enabled',c['instance']+'-'+role+'.service'],capture_output=True,text=True);assert r.returncode==1 and r.stdout.strip()=='disabled'
 result.update(afterPIDs=pids(),activeManifestSHA256=after['manifestSHA256'],hostingAndHomepageUnchanged=True,dataRestored=False)
 if v['action']!='plan':
  receipt=Path('/srv/codi-connected')/('routed-native-'+v['action']+'-'+str(time.time_ns())+'-result.json')
  with os.fdopen(os.open(receipt,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),'w') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  result['rootReceipt']=str(receipt)
 print(json.dumps(result))
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action',choices=['plan','install','upgrade','rollback','recover'],default='plan');p.add_argument('--commit',required=True);p.add_argument('--manifest-sha256',required=True);p.add_argument('--config-sha256',required=True);a=p.parse_args()
 assert re.fullmatch('[0-9a-f]{40}',a.commit) and all(re.fullmatch('[0-9a-f]{64}',k) for k in [a.manifest_sha256,a.config_sha256])
 raw=(ROOT/'scripts/native-rollout.py').read_bytes();v={'action':a.action,'commit':a.commit,'manifestSHA256':a.manifest_sha256,'configSHA256':a.config_sha256,'rolloutSHA256':hashlib.sha256(raw).hexdigest(),'rolloutBytes':len(raw)}
 r=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(v),text=True,capture_output=True,timeout=400)
 if r.returncode:raise RuntimeError(r.stderr[-5000:] or r.stdout[-5000:])
 result=json.loads(r.stdout);result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('routed-native-'+a.action+'-result.json')
 if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
