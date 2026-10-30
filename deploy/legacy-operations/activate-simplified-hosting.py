#!/usr/bin/env python3
"""Apply a validated Simplified preview/active policy under the hosting lock.

Executed as root on box-webhost with baseline and candidate hashes supplied by
an operator. Existing issuer, gateway, guest, prototype and website state remain.
"""
import fcntl,hashlib,importlib.util,json,os,pwd,sys,tomllib
from pathlib import Path
MODE,RELEASE,EXPECTED_COMMON,EXPECTED_MANIFEST,CANDIDATE_SHA=sys.argv[1:]
assert MODE in ('preview','active') and len(RELEASE)==64 and os.geteuid()==0
ROOT=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(ROOT/'ops'))
import webctl as ctl
common=ROOT/'ops/common.py';manifest=ROOT/'sites.toml';candidate=Path('/tmp/codi-simplified-f66430fe/common.py')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with (ROOT/'.controller.lock').open('r') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 assert digest(common)==EXPECTED_COMMON and digest(manifest)==EXPECTED_MANIFEST and digest(candidate)==CANDIDATE_SHA
 assert ctl.current_mode()=='production'
 old_common=common.read_bytes();old_manifest=manifest.read_bytes();old_caddy=Path('/etc/caddy/Caddyfile').read_text();old_data=ctl.load();assert old_caddy==ctl.caddy(old_data,'production')
 assert (Path('/srv/codi-connected/simplified')/RELEASE/'index.html').is_file()
 spec=importlib.util.spec_from_file_location('candidate_hosting',candidate);new=importlib.util.module_from_spec(spec);spec.loader.exec_module(new)
 data=tomllib.loads(old_manifest.decode());site=next(x for x in data['sites'] if x['domain']=='ksu.codes');site['codi_simplified']=RELEASE;site['codi_simplified_mode']=MODE;new.validate(data)
 old_module=(ctl.caddy,ctl.dump,ctl.validate);before_common=ctl.snapshot(common);before_manifest=ctl.snapshot(manifest);owner=pwd.getpwnam('dflanag3')
 try:
  ctl.write(common,candidate.read_bytes(),0o644,owner.pw_uid,owner.pw_gid,False)
  ctl.write(manifest,new.dump(data),0o644,owner.pw_uid,owner.pw_gid,False)
  ctl.caddy,ctl.dump,ctl.validate=new.caddy,new.dump,new.validate
  ctl.caddy_apply(data,'production')
  assert Path('/etc/caddy/Caddyfile').read_text()==new.caddy(data,'production')
 except BaseException:
  ctl.write(common,old_common,0o644,owner.pw_uid,owner.pw_gid,False);ctl.write(manifest,old_manifest,0o644,owner.pw_uid,owner.pw_gid,False)
  ctl.caddy,ctl.dump,ctl.validate=old_module;ctl.caddy_apply(old_data,'production');raise
 print(json.dumps({'mode':MODE,'release':RELEASE,'commonSHA256':digest(common),'manifestSHA256':digest(manifest),'caddySHA256':digest(Path('/etc/caddy/Caddyfile')),'backups':[str(before_common),str(before_manifest)]}))
