#!/usr/bin/env python3
"""Read exact installed touch-scroll release, preserved sites and public assets."""
import hashlib,json,subprocess,time,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import hashlib,json,pathlib,subprocess,sys
P=pathlib.Path
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
c=P('/etc/codi-connected/ksu/managed.json');v=json.loads(c.read_text());r=P(v['release'])
assert v['manifestSHA256']=='3071d17fa17666e2d9317e96e2e9a79d629e2a16be2e44b9afb0ed9947efd211'==sha(r/'connected-release.json')
assert v['basePath']=='/hidden' and v['origin']=='https://ksu.codes'
m=json.loads((r/'connected-release.json').read_text())['files']
for n,record in m.items():
 p=r/n;st=p.lstat();assert not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022
 assert record=={'bytes':st.st_size,'sha256':sha(p)}
assert not any((c.parent/n).exists() for n in ['native-rollout.json','maintenance.json'])
w=P('/srv/webapps/ksu.codes/current').resolve();assert sha(w/'public/index.html')=='55f2928da214010b2ed7d647a354c0052ae03e9d06bafc09c1ea3b67e8608a38'
assert sha(w/'public/desktop/release.json')=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9'
a=json.loads((w/'public/desktop/release.json').read_text())['files'];assert len(a)==133
for n,record in a.items():
 p=w/'public/desktop'/n;assert record=={'bytes':p.stat().st_size,'sha256':sha(p)}
b=P('/home/dflanag3/webhost-sites');sys.path.insert(0,str(b/'ops'));import common
assert common.caddy(common.load(),'production')==P('/etc/caddy/Caddyfile').read_text()
hosting={n:sha(p) for n,p in [('generator',b/'ops/common.py'),('manifest',b/'sites.toml'),('Caddy','/etc/caddy/Caddyfile')]}
assert hosting=={'generator':'718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4','manifest':'c946c1e71461a49692332f4287633f64ab6e4bebb97283a4263d53bf98f10715','Caddy':'694518124e11bd918471cfc4b10ad3164d557bba0d003cc1de01fe7ce214dbad'}
smoke=b/'reports/private/terminal-scroll-native16-20261024.json'
subprocess.run(['/usr/bin/python3','-B',str(b/'ops/production-smoke.py'),'--address','127.0.0.1','--scope','server-loopback','--output',str(smoke)],check=True,capture_output=True,text=True,timeout=120)
s=json.loads(smoke.read_text());assert len(s['sites'])==10 and all(x['result']=='PASS' for x in s['sites'].values())
pids={}
for role in ['issuer','steward','guest']:
 unit=v['instance']+'-'+role+'.service'
 def run(*args):return subprocess.check_output(['systemctl',*args,unit],text=True).strip()
 assert run('is-active')=='active' and run('show','-p','UnitFileState','--value')=='disabled';pid=int(run('show','-p','MainPID','--value'));pids[role]=pid
 assert str(r).encode() in P('/proc',str(pid),'cmdline').read_bytes()
 status=dict(line.split(':',1) for line in P('/proc',str(pid),'status').read_text().splitlines())
 assert int(status['Uid'].split()[0])>0 and int(status['CapEff'],16)==0 and status['NoNewPrivs'].strip()=='1'
print(json.dumps({'status':'PASS','manifestSHA256':v['manifestSHA256'],'configSHA256':sha(c),'release':str(r),'nativePIDs':pids,'nativeUnitsDisabledForBoot':True,'noPendingMaintenanceOrRollout':True,'verifiedReleaseFiles':len(m),'prototypeFilesVerified':len(a),'homepageUnchanged':True,'hostingSHA256':hosting,'siteResults':{n:m['result'] for n,m in s['sites'].items()},'siteSmokeReceipt':str(smoke),'servicesRestarted':False}))
'''

if __name__=='__main__':
 r=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-'],input=REMOTE,text=True,capture_output=True,timeout=180)
 if r.returncode:raise SystemExit(r.stderr or r.stdout)
 result=json.loads(r.stdout);release=ROOT/'.build/releases/connected-terminal-scroll-r2'
 for name in ['index.html','assets/desktop/network-release.json','assets/desktop/offline-worker.js']:
  with urllib.request.urlopen('https://ksu.codes/hidden/'+name,timeout=20) as response:assert response.status==200 and response.read()==(release/name).read_bytes()
 result.update(defaultPublicTLS=True,publicAssetsMatched=3,sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 out=ROOT/'.build/checks/terminal-scroll-live-health-result.json'
 if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
