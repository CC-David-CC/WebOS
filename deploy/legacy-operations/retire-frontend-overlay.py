#!/usr/bin/env python3
"""Retire only KSU's byte-identical six-file overlay through managed hosting.

The native14 public files already equal this overlay. Native services, prototype,
homepage, certificates and all other routes/configuration must remain unchanged.
"""
import argparse,hashlib,json,re,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import copy,fcntl,hashlib,http.client,json,os,pwd,socket,ssl,subprocess,sys,tempfile,time
from pathlib import Path
v=json.load(sys.stdin);base=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(base/'ops'));import common,webctl as ctl
ctl.root_required()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args,timeout=60):return subprocess.check_output(list(map(str,args)),text=True,timeout=timeout).strip()
def request(path):
 c=http.client.HTTPSConnection('ksu.codes',timeout=10);c.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),10),server_hostname='ksu.codes')
 try:c.request('GET',path);r=c.getresponse();return r.status,dict(r.getheaders()),r.read(4194305)
 finally:c.close()
with (base/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 repo=base/'sites/ksu.codes';assert run(['runuser','-u','dflanag3','--','git','-C',repo,'rev-parse','HEAD'])==v['commit'] and not run(['runuser','-u','dflanag3','--','git','-C',repo,'status','--porcelain'])
 source=base/'ops/common.py';manifest=base/'sites.toml';old=manifest.read_bytes();assert digest(source.read_bytes())=='718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4' and digest(old)=='da1383b2b4f7fa25911c204c212981d54b05355f53e07ff8284242971b387bd9'
 data=ctl.load();assert ctl.current_mode()=='production';prior={mode:ctl.caddy(data,mode) for mode in ['prepare','production']};assert Path('/etc/caddy/Caddyfile').read_text()==prior['production']
 proposed=copy.deepcopy(data);site=next(s for s in proposed['sites'] if s['domain']=='ksu.codes');key=site.pop('codi_frontend');assert key=='97b80a77ce3f377aecdea64928730d35c947ce13c3c6e8a968123fa218778381'
 common.validate(proposed);raw=common.dump(proposed).encode();extra='\t\t\t@codi_frontend path /app.js /style.css /terminal.js /assets/terminal-initramfs.cpio.gz /desktop-apps.js /networking.js\n\t\t\thandle @codi_frontend {\n\t\t\t\troot * /srv/codi-connected/frontends/'+key+'\n\t\t\t\tfile_server\n\t\t\t}\n'
 for mode in prior:assert prior[mode].count(extra)==1 and ctl.caddy(proposed,mode)==prior[mode].replace(extra,'')
 assert '\t\tredir * /hidden/ 308' in ctl.caddy(proposed,'production')
 for site in data['sites']:assert ctl.unit(site)==ctl.unit(next(s for s in proposed['sites'] if s['domain']==site['domain']))
 fd,name=tempfile.mkstemp(prefix='.codi-unified-',suffix='.Caddyfile',dir='/etc/caddy');os.close(fd)
 try:ctl.write(name,ctl.caddy(proposed,'production'),0o640,0,pwd.getpwnam('caddy').pw_gid,False);ctl.caddy_validate(name)
 finally:Path(name).unlink()
 cfg=Path('/etc/codi-connected/ksu/managed.json');native_raw=cfg.read_bytes();c=json.loads(native_raw);assert c['manifestSHA256']=='8810761ee7e47e15b055ccda8ed83cd15c017f839770b980dbfaa0d7ab62e0ce'
 release=Path(c['release']);metadata=json.loads((release/'connected-release.json').read_text())['files'];frontend=json.loads((Path('/srv/codi-connected/frontends')/key/'frontend.json').read_text())['files'];assert len(frontend)==6
 for n,record in frontend.items():
  assert record==metadata[n];s,h,b=request('/hidden/'+n);assert s==200 and {'bytes':len(b),'sha256':digest(b)}==record
 pids={r:run(['systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value']) for r in ['issuer','steward','guest']};assert all(int(p)>0 for p in pids.values())
 website=Path('/srv/webapps/ksu.codes/current').resolve();prototype=website/'public/desktop';pm=json.loads((prototype/'release.json').read_text());assert len(pm['files'])==133 and digest((prototype/'release.json').read_bytes())=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9'
 for n,r in pm['files'].items():assert r=={'bytes':(prototype/n).stat().st_size,'sha256':digest((prototype/n).read_bytes())}
 report={'status':'PASS','action':v['action'],'sourceCommit':v['commit'],'generatorSHA256':digest(source.read_bytes()),'beforeManifestSHA256':digest(old),'candidateManifestSHA256':digest(raw),'nativePIDs':pids,'prototypeDeclaredFilesVerified':133,'sixPublicAssetsEqualNative':True,'publicAssetBytesChanged':False,'nativeServicesRestarted':False,'routerFirewallPortsOrBootChanged':False}
 if v['action']=='plan':print(json.dumps(report));raise SystemExit(0)
 assert v['action']=='apply';status,_,body=request('/hidden/api/v1/desktop-status');notice=json.loads(body)['maintenance'];assert status==200 and notice and notice['id']==v['noticeId'] and notice['phase'] in ['active','scheduled'] and notice['deadline']<=int(time.time())<notice['expiresAt']
 info=manifest.stat();backup=str(ctl.snapshot(manifest));changed=False
 try:
  changed=True;ctl.write(manifest,raw,info.st_mode&0o777,info.st_uid,info.st_gid,False);ctl.caddy_apply(ctl.load(),'production')
  for n,r in frontend.items():
   s,h,b=request('/hidden/'+n);assert s==200 and {'bytes':len(b),'sha256':digest(b)}==r
  s,h,b=request('/hidden');assert s==308 and h['Location']=='/hidden/'
  for n in ['release.json','app.js','config.json']:
   s,h,b=request('/desktop/'+n);assert s==200 and b==(prototype/n).read_bytes()
  smoke=base/'reports/private/codi-unified-native-assets-20261024.json';run(['/usr/bin/python3',base/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',smoke],120)
  assert cfg.read_bytes()==native_raw and Path('/srv/webapps/ksu.codes/current').resolve()==website and pids=={r:run(['systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value']) for r in pids}
  report.update(manifestBackup=backup,manifestSHA256=digest(manifest.read_bytes()),caddySHA256=digest(Path('/etc/caddy/Caddyfile').read_bytes()),allSiteSmoke=str(smoke),siteDomains=sorted(s['domain'] for s in data['sites'] if s['enabled']))
  receipt=Path('/srv/codi-connected/unified-assets-'+str(time.time_ns())+'-result.json');fd=os.open(receipt,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(fd,'w') as out:json.dump(report,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
  report['rootReceipt']=str(receipt);print(json.dumps(report))
 except BaseException:
  if changed:ctl.write(manifest,old,info.st_mode&0o777,info.st_uid,info.st_gid,False);ctl.caddy_apply(ctl.load(),'production')
  raise
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action',choices=['plan','apply'],default='plan');p.add_argument('--commit',required=True);p.add_argument('--notice-id');a=p.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.commit)
 if a.action=='apply':assert re.fullmatch('[0-9a-f]{32}',a.notice_id or '')
 r=subprocess.run(['ssh','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps({'action':a.action,'commit':a.commit,'noticeId':a.notice_id}),capture_output=True,text=True,timeout=240)
 if r.returncode:raise RuntimeError(r.stderr[-4000:] or r.stdout[-4000:])
 result=json.loads(r.stdout.strip().splitlines()[-1]);result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('unified-assets-'+a.action+'-result.json')
 if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
