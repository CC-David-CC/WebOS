#!/usr/bin/env python3
"""Inspect exact live code, authority, paused chat, all prototype bytes and sites."""
import argparse,hashlib,json,shlex,subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REMOTE=r'''
import datetime,fcntl,hashlib,importlib.util,json,pathlib,sqlite3,subprocess,sys,time
P=pathlib.Path;sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();host=P('/home/dflanag3/webhost-sites');path=P('/etc/codi-connected/ksu/managed.json')
with (host/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);c=json.loads(path.read_bytes());assert c['origin']=='https://ksu.codes' and c['basePath']=='' and c['manifestSHA256']==EXPECTED and 'hostedRooms' not in c
 release=P(c['release']);assert sha(release/'connected-release.json')==EXPECTED;sys.path[:0]=[str(release),str(host/'ops')]
 s=importlib.util.spec_from_file_location('browser_file_health_native',release/'scripts/manage-services.py');op=importlib.util.module_from_spec(s);sys.modules[s.name]=op;s.loader.exec_module(op)
 with op.locked(path):
  op.load(path);op.ready(c,op.ROLES);assert not any((path.parent/n).exists() for n in ['maintenance.json','native-rollout.json','site-cutover.json'])
  from origin_service import maintenance,network_management
  binding=maintenance.binding(P(c['stateRoot']));assert binding['rootRevision']==4
  from steward.protocol import jose
  provision=json.loads((P(c['stateRoot'])/'steward/provision.json').read_bytes());seed=jose.inspect(provision['seed'],'codi-seed/1',32768)[1];assert seed['revision']==4 and seed['exp']>time.time()+3600
  worker=network_management.Binding(op,c,c['guestNetwork']).run('status');assert worker['active'] and worker['kernelMatches'] and not worker['guardFault'] and not worker['bootEnabled']
  assert c['guestNetwork']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
  roles={}
  for role in op.ROLES:
   unit=op.unit(c,role);pid=int(op.systemctl('show',unit,'-p','MainPID','--value'));assert pid>0 and op.systemctl('show',unit,'-p','UnitFileState','--value').strip()=='disabled'
   status=dict(line.split(':',1) for line in P('/proc',str(pid),'status').read_text().splitlines());assert int(status['Uid'].split()[0])>0 and int(status['CapEff'],16)==0 and status['NoNewPrivs'].strip()=='1';roles[role]=pid
  assert op.systemctl('show',op.unit(c,'issuer-bootstrap'),'-p','MainPID','--value').strip()=='0'
 website=P('/srv/webapps/ksu.codes/current').resolve();assert website.name=='20261024T110552353972Z-299874f5';prototype=website/'public/desktop';m=json.loads((prototype/'release.json').read_bytes());assert len(m['files'])==133 and sha(prototype/'release.json')=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9'
 for n,r in m['files'].items():assert r=={'bytes':(prototype/n).stat().st_size,'sha256':sha(prototype/n)}
 cfg=json.loads((prototype/'config.json').read_bytes());assert cfg['identity']['mode']=='local-development' and not cfg['identity'].get('apiBase') and not cfg.get('guestNetwork')
 assert sha(website/'public/index.html')=='d256863f38fbc41c58f56721487e58e1c9580a8ece09263bad55186bb49389be'
 import common;assert common.caddy(common.load(),'production')==P('/etc/caddy/Caddyfile').read_text()
 pins={n:sha(p) for n,p in [('common.py',host/'ops/common.py'),('sites.toml',host/'sites.toml'),('Caddy','/etc/caddy/Caddyfile')]};assert pins=={'common.py':'9f7fef18df198f783b71d13da1950272edc8518f8726700ab01e18ff299acd4a','sites.toml':'35bd536bf8933f70a52efbb5ff4bbafbae737568b0fac16b60aba565187fd776','Caddy':'5e76e178c0a54dd43c7a240781d57ae4fcbc9f2f66c5e288e96b5173c553b3bb'}
 units=['codi-rooms-ksu.service','codi-rooms-ksu-proxy.socket','codi-rooms-ksu-proxy.service','codi-readers-ksu.service','codi-readers-ksu-proxy.socket','codi-readers-ksu-proxy.service','codi-readers-ksu-refresh.timer']
 for unit in units:assert subprocess.check_output(['systemctl','show',unit,'-p','ActiveState','--value'],text=True).strip()=='inactive'
 with sqlite3.connect('file:/var/lib/codi-rooms/ksu/rooms.sqlite3?mode=ro',uri=True) as db:assert not any(db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['events','rooms','streams','leases','members','work'])
 smoke=host/'reports/private'/('browser-files-smoke-'+str(time.time_ns())+'.json');subprocess.run(['/usr/bin/python3','-B',str(host/'ops/production-smoke.py'),'--address','127.0.0.1','--scope','server-loopback','--output',str(smoke)],check=True,capture_output=True,text=True,timeout=120)
 sites=json.loads(smoke.read_bytes());assert len(sites['sites'])==10 and all(s['result']=='PASS' for s in sites['sites'].values())
 print(json.dumps({'status':'PASS','manifestSHA256':EXPECTED,'nativeConfigSHA256':sha(path),'nativePIDs':roles,'authorityBinding':binding,'rootExpiresAt':datetime.datetime.fromtimestamp(seed['exp'],datetime.timezone.utc).isoformat(),'prototypeFilesVerified':133,'prototypeBackendFree':True,'blogSHA256':sha(website/'public/index.html'),'hostingPins':pins,'chatUnitsStopped':7,'allSixChatTablesEmpty':True,'siteResults':{n:v['result'] for n,v in sites['sites'].items()},'siteSmokeReceipt':str(smoke),'registeredOnlyEgressGuardHealthy':True,'bootPolicyChanged':False,'rootMinted':False}))
'''
def run(release):
 expected=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest()
 code='EXPECTED='+repr(expected)+'\n'+REMOTE
 bootstrap="import json,os,pathlib,sys;c=json.loads(pathlib.Path('/etc/codi-connected/ksu/managed.json').read_bytes());code=sys.stdin.read();os.execv(c['python'],[c['python'],'-I','-B','-c',code])"
 child=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(bootstrap)],input=code,capture_output=True,text=True,timeout=180);assert child.returncode==0,child.stderr[-5000:] or child.stdout[-3000:];result=json.loads(child.stdout)
 for n in ['index.html','assets/desktop/network-release.json','assets/desktop/shared-services.json','assets/desktop/offline-worker.js']:
  with urllib.request.urlopen('https://ksu.codes/'+n,timeout=25) as r:assert r.status==200 and r.read()==(release/n).read_bytes(),n
 result.update(defaultPublicTLS=True,publicAssetsMatched=4,scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wholeGoalComplete=False);return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 try:v=run(a.release.resolve())
 except Exception as e:
  import traceback
  v={'status':'FAIL','error':str(e),'traceback':traceback.format_exc()}
 a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2));raise SystemExit(v['status']!='PASS')
