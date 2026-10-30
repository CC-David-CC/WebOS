#!/usr/bin/env python3
"""Apply the operator-requested live chat pause, preserving all non-chat state.

Existing test room contents were explicitly deleted separately. Never restore
old room databases or reactivate chat as a rollout rollback.
"""
import argparse,fcntl,hashlib,importlib.util,json,os,re,socket,sqlite3,time
from pathlib import Path
OLD='952fe21dfa990b63323f0d9dad597cab8d9a5604ea7fe519bf5547aef4e0a063'
NEW='6ded1364d04182b48d3fc8b65f6d1dd24a5d322d3cf91b1dda853d05794e1bf9'
PINS={'common.py':'26da0e71121f385f54abf36247afd0bb575b3c5926906403cc09d735bd0e1bd9','sites.toml':'9bccf2519656c22f6f0043aa03b673fbfeac9c21e4f3928934922208914afa7e','Caddy':'2a7cbaf41186112fdc47c95af7abdbbf3689faf5b149ee72031a161743b94270'}
NEXT={'common.py':'9f7fef18df198f783b71d13da1950272edc8518f8726700ab01e18ff299acd4a','sites.toml':'35bd536bf8933f70a52efbb5ff4bbafbae737568b0fac16b60aba565187fd776','Caddy':'5e76e178c0a54dd43c7a240781d57ae4fcbc9f2f66c5e288e96b5173c553b3bb'}
HELPER=Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main(commit):
 assert os.geteuid()==0 and socket.gethostname()=='box-webhost' and re.fullmatch('[a-f0-9]{40}',commit)
 assert sha(HELPER)==HELPER.parent.name
 m=module('chat_pause_helpers',HELPER);m.protected(HELPER)
 m.NATIVE_DIR=Path('/srv/codi-connected/releases/native25-'+NEW[:16])
 packet=m.REPO/'tools/codiserver/chat-paused-r1'
 with (m.HOST/'.controller.lock').open('rb') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  git=lambda *args:m.run(['runuser','-u','dflanag3','--','git','-C',m.REPO,*args])
  assert git('rev-parse','HEAD')==commit and not git('status','--porcelain')
  c=json.loads(m.CONTROL.read_bytes());assert c['manifestSHA256']==OLD and c['basePath']=='' and c['origin']=='https://ksu.codes'
  before=m.capture(c);assert m.hosting_pins()==PINS
  units=['codi-readers-ksu-refresh.timer','codi-readers-ksu-refresh.service','codi-readers-ksu-proxy.socket','codi-readers-ksu-proxy.service','codi-readers-ksu.service','codi-rooms-ksu-proxy.socket','codi-rooms-ksu-proxy.service','codi-rooms-ksu.service']
  for u in units:assert m.run(['systemctl','show',u,'-p','ActiveState','--value'])=='inactive',u
  database=Path('/var/lib/codi-rooms/ksu/rooms.sqlite3')
  def counts():
   with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as db:return {t:db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['events','streams','leases','members','work','rooms']}
  assert not any(counts().values());dbpin=sha(database)
  m.install(packet/'release',m.NATIVE_DIR,'connected-release.json',NEW)
  contract=module('chat_pause_contract',m.NATIVE_DIR/'origin_service/release.py');verified=contract.verify(m.NATIVE_DIR);assert verified['manifestSHA256']==NEW
  old=json.loads((Path(c['release'])/'connected-release.json').read_bytes())['files'];new=json.loads((m.NATIVE_DIR/'connected-release.json').read_bytes())['files']
  assert all(old[n]==new[n] for n in contract.V19_NATIVE)
  common,webctl=m.hosting_modules();backups=[str(webctl.snapshot(p)) for p in [m.HOST/'ops/common.py',m.HOST/'sites.toml',Path('/etc/caddy/Caddyfile')]]
  candidate=packet/'hosting/ops/common.py';assert sha(candidate)==NEXT['common.py'];owner=webctl.owner()
  webctl.write(m.HOST/'ops/common.py',candidate.read_bytes(),0o644,owner.pw_uid,owner.pw_gid)
  common,webctl=m.hosting_modules();data=common.load(packet/'hosting/sites.toml')
  assert hashlib.sha256(common.dump(data).encode()).hexdigest()==NEXT['sites.toml']
  assert hashlib.sha256(common.caddy(data,'production').encode()).hexdigest()==NEXT['Caddy']
  # Managed render/validate/apply; ingress stays closed even if the code rollout fails.
  webctl.caddy_apply(data,'production');webctl.save_manifest(data);assert m.hosting_pins()==NEXT
  notice=[m.PYTHON,'-I','-B',Path(c['release'])/'scripts/desktop-maintenance.py','--directory',Path(c['stateRoot'])/'public']
  m.run([*notice,'scheduled','--in-seconds','10','--duration','180','--message','Development update in 10 seconds. Save your work. Chat is disabled and test messages were deleted. Unsaved browser work is not backed up.']);time.sleep(10)
  native=m.native('upgrade','--release',m.NATIVE_DIR,'--python',m.PYTHON)
  m.run([*notice,'cancelled','--duration','120','--message','Chat is disabled while its replacement is built. Reload for the unavailable notice. Unsaved browser work was not backed up.'])
  after=json.loads(m.CONTROL.read_bytes());assert after['manifestSHA256']==NEW
  state=m.preserved(before,after)
  assert sha(database)==dbpin and not any(counts().values())
  for u in units:assert m.run(['systemctl','show',u,'-p','ActiveState','--value'])=='inactive',u
  return {'status':'PASS','sourceCommit':commit,'manifestSHA256':NEW,'releaseVerification':verified,'hostingPins':m.hosting_pins(),'native':native,'state':state,'emptyRoomCounts':counts(),'chatUnitsInactive':units,'hostingBackups':backups,'nonChatStatePreserved':True,'rootMinted':False,'chatDataRestored':False,'reopenRequiresExplicitNewRelease':True}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--commit',required=True);a=p.parse_args()
 try:v=main(a.commit)
 except Exception as e:
  import traceback
  v={'status':'FAIL','error':str(e),'traceback':traceback.format_exc(),'recovery':'Keep chat routes blocked and services stopped. Inspect native rollout journal; do not restore deleted chat data.'}
 out=Path('/srv/codi-connected')/('chat-paused-activation-'+str(time.time_ns())+'-result.json');fd=os.open(out,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as f:json.dump(v,f,indent=2)
 print(json.dumps({'status':v['status'],'receipt':str(out),'sha256':sha(out),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
