#!/usr/bin/env python3
"""Activate an installed UI-only candidate through the existing native rollout controller."""
import argparse,hashlib,json,re,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import fcntl,hashlib,http.client,json,os,subprocess,sys,time
from pathlib import Path
v=json.load(sys.stdin);assert os.geteuid()==0;base=Path('/home/dflanag3/webhost-sites');cfg=Path('/etc/codi-connected/ksu/managed.json');key=v['manifest'];target=Path('/srv/codi-connected/releases')/('native15-'+key[:16]);python='/srv/codi-connected/venvs/517179c/bin/python';controller='/srv/codi-connected/rollout-controllers/f51b11cc8ce2af83aa209fedc4b34e2b34aa88251879494608270182a8e8e6e0/native-rollout.py'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run(args,timeout=60):return subprocess.check_output(list(map(str,args)),text=True,timeout=timeout).strip()
with (base/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);repo=base/'sites/ksu.codes';assert run(['runuser','-u','dflanag3','--','git','-C',repo,'rev-parse','HEAD'])==v['commit'] and not run(['runuser','-u','dflanag3','--','git','-C',repo,'status','--porcelain'])
 before=json.loads(cfg.read_text());assert before['manifestSHA256']==v['baseManifest'] and sha(cfg.read_bytes())==v['configSHA256'];assert sha((target/'connected-release.json').read_bytes())==key
 conn=http.client.HTTPConnection('127.0.0.1',8118,timeout=10);conn.request('GET','/api/v1/desktop-status',headers={'Host':'ksu.codes'});response=conn.getresponse();assert response.status==200;notice=json.loads(response.read(8193))['maintenance'];conn.close();assert notice and notice['id']==v['notice'] and notice['deadline']<=time.time()<notice['expiresAt'] and notice['phase'] in ['scheduled','active']
 paths=[base/'ops/common.py',base/'sites.toml',Path('/etc/caddy/Caddyfile'),Path(before['guestNetwork']['configFile']),Path('/etc/codi-user-files/ksu/managed.json'),Path('/var/lib/codi-connected/guest-cookie-codi-ksu-hidden/secret')];pins={str(p):sha(p.read_bytes()) for p in paths}
 file_units=['codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service'];file_pids={n:run(['systemctl','show',n,'-p','MainPID','--value']) for n in file_units};assert all(int(p)>0 for p in file_pids.values())
 changed=json.loads(run([python,'-I','-B',controller,'upgrade','--operator',target/'scripts/manage-services.py','--operator-manifest-sha256',key,'--config',cfg,'--release',target,'--python',python,'--backup-parent','/var/backups/codi-connected/ksu'],300));assert changed['status']=='upgraded',changed
 after=json.loads(cfg.read_text());assert {k:w for k,w in before.items() if k not in ['release','manifestSHA256']}=={k:w for k,w in after.items() if k not in ['release','manifestSHA256']} and after['manifestSHA256']==key
 assert pins=={p:sha(Path(p).read_bytes()) for p in pins} and file_pids=={n:run(['systemctl','show',n,'-p','MainPID','--value']) for n in file_units}
 prototype=Path('/srv/webapps/ksu.codes/current').resolve()/'public/desktop';assert sha((prototype/'release.json').read_bytes())=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9'
 for n,r in json.loads((prototype/'release.json').read_text())['files'].items():assert r=={'bytes':(prototype/n).stat().st_size,'sha256':sha((prototype/n).read_bytes())}
 pids={r:run(['systemctl','show',after['instance']+'-'+r+'.service','-p','MainPID','--value']) for r in ['issuer','steward','guest']};assert all(int(p)>0 for p in pids.values())
 for r in pids:assert subprocess.run(['systemctl','is-enabled',after['instance']+'-'+r+'.service'],capture_output=True,text=True).stdout.strip()=='disabled'
 result={'status':'PASS','controllerResult':changed,'manifestSHA256':key,'configSHA256':sha(cfg.read_bytes()),'nativePIDs':pids,'privateFileServicePIDs':file_pids,'prototypeFilesVerified':133,'hostingCookieGuestPolicyUnchanged':True,'accountDataRestored':False,'personalFileContentsRead':False};out=Path('/srv/codi-connected')/('ui-native-'+str(time.time_ns())+'-result.json');out.write_text(json.dumps(result,indent=2)+'\n');os.chmod(out,0o600);result['rootReceipt']=str(out);print(json.dumps(result))
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--commit',required=True);p.add_argument('--manifest-sha256',required=True);p.add_argument('--notice-id',required=True);p.add_argument('--base-manifest-sha256',default='ec6a637c197684921a3ac18ee87a1d1d6380a0a5984ece1cdb40884db627bbed');p.add_argument('--config-sha256',default='22eec0f5b47841e8994b72954e3cfa119bad8177333319bc5c93b915f9cb3403');p.add_argument('--output',default='native-ui-activation-result.json');a=p.parse_args();assert re.fullmatch('[a-f0-9]{40}',a.commit) and re.fullmatch('[a-f0-9]{64}',a.manifest_sha256) and re.fullmatch('[a-f0-9]{32}',a.notice_id)
 r=subprocess.run(['ssh','box-webhost','sudo','-n','python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps({'commit':a.commit,'manifest':a.manifest_sha256,'notice':a.notice_id,'baseManifest':a.base_manifest_sha256,'configSHA256':a.config_sha256}),capture_output=True,text=True,timeout=420)
 if r.returncode:raise RuntimeError(r.stderr[-5000:] or r.stdout[-5000:])
 result=json.loads(r.stdout);result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/a.output;assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
