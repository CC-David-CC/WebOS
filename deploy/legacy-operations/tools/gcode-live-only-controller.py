#!/usr/bin/env python3
"""Reviewed-candidate controller wrapper. Never runs an action implicitly.

verify is read-only. activate/rollback are explicit operator actions and must
not be used without reviewing the candidate, pins, backups and this source.
"""
import copy,fcntl,hashlib,json,os,pwd,sys,tomllib
from pathlib import Path

ROOT=Path('/home/dflanag3/webhost-sites')
BACKUP=Path('/var/backups/webhost-sites/gcode-only-stage-YnPDYBZz')
OLD='5abfd489f72fa3e18d6301890ad2fb6560ac3831351696348b8444f5527c74a5'
NEW='2aa7c157438b8bb28333b70b4ffd5783d4f3467a10120c642dbfd30368fc76dd'
COMMON='15f8425440e73b316a9460b93149fa7145aad1a07c560d7cfab8d4fb841fef92'
PINS={'old':('4641feb1447a67a3739500640426d52aca42dc2ecb8b0060989118a1bb1ac1c2','89018dc280838a254a3c34e7193580aa85f27eae3d7254d3bea65ba27ad7e794'),'new':('fa03767cd5a24d76b482a7d5038ff4f0aa2405a7ce8510b57a509cf63d241642','486c2395a249cef19bb8a3606ecd2b5e8aced3362517ba1df6d87f1b762c49c4')}
MANIFEST=ROOT/'sites.toml';COMMON_PATH=ROOT/'ops/common.py';CADDY=Path('/etc/caddy/Caddyfile')
RELEASES=Path('/srv/codi-connected/simplified')
DIFF_PIN='ba8144832f86b4844648118dfd3a6329f6a5f5ad25ac77bedea523e685369765'
CACHE_PIN='b8cea99c75a4f200a5c270f68be3448fc2ee46653892119bbabe4573ff8ec09d'
WORKER_PIN='bb9a6c4e557d48bc62870b0ebda935f9e36d0de51c5ec63fc231304efb4754e8'
OLD_CACHE_PIN='765352586e1d1f0e2610b23c0417163bc5cb250ddc0c034099aa9ba72ea2e3dd'
OLD_WORKER_PIN='dca78f052d3afbf543b46191cfa6b39028346af828401785cac45c2d46c02ed1'
def digest(data):return hashlib.sha256(data).hexdigest()
def require(condition,message):
 if not condition:raise RuntimeError(message)
def file_hash(path):return digest(path.read_bytes())

def main():
 require(os.geteuid()==0,'Root required')
 require(len(sys.argv)==2 and sys.argv[1] in ('verify','activate','rollback'),'Choose verify, activate, or rollback explicitly')
 action=sys.argv[1]
 sys.path.insert(0,str(ROOT/'ops'));import webctl as ctl
 with (ROOT/'.controller.lock').open('r') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  require(ctl.current_mode()=='production','Hosting mode changed')
  require(file_hash(COMMON_PATH)==COMMON,'Hosting generator changed')
  current_manifest=MANIFEST.read_bytes();current_caddy=CADDY.read_bytes()
  state='new' if action=='rollback' else 'old'
  require((digest(current_manifest),digest(current_caddy))==PINS[state],'Hosting pins changed')
  current=ctl.load();site=next(s for s in current['sites'] if s['domain']=='ksu.codes')
  require(site.get('codi_simplified')==(NEW if state=='new' else OLD) and site.get('codi_simplified_mode')=='active','Active release changed')
  require(ctl.caddy(current,'production').encode()==current_caddy,'Managed Caddy differs')
  baseline=(BACKUP/'sites.toml').read_bytes()
  require(digest(baseline)==PINS['old'][0],'Rollback baseline changed')
  require(file_hash(BACKUP/'common.py')==COMMON and file_hash(BACKUP/'Caddyfile')==PINS['old'][1],'Rollback files changed')
  require(file_hash(BACKUP/'release-diff.json')==DIFF_PIN,'Diff receipt changed')
  require((RELEASES/OLD/'index.html').is_file(),'Old release unavailable')
  candidate=RELEASES/NEW
  require(not candidate.is_symlink() and (candidate/'index.html').is_file(),'Candidate unavailable')
  require(file_hash(candidate/'assets/desktop/cache-manifest.json')==CACHE_PIN,'Candidate manifest changed')
  require(file_hash(candidate/'assets/desktop/offline-worker.js')==WORKER_PIN,'Candidate worker changed')
  cache=json.loads((candidate/'assets/desktop/cache-manifest.json').read_text())
  require(cache.get('id')==NEW,'Candidate identifier changed')
  # Reverify every candidate file rather than relying only on its identifier.
  for name,info in cache['files'].items():
   require(not Path(name).is_absolute() and '..' not in Path(name).parts,'Invalid candidate path')
   path=candidate/name
   require(path.is_file() and not path.is_symlink() and path.stat().st_size==info['bytes'] and file_hash(path)==info['sha256'],'Candidate file changed: '+name)
  old=RELEASES/OLD
  require(not old.is_symlink() and file_hash(old/'assets/desktop/cache-manifest.json')==OLD_CACHE_PIN and file_hash(old/'assets/desktop/offline-worker.js')==OLD_WORKER_PIN,'Rollback release manifest changed')
  prior=json.loads((old/'assets/desktop/cache-manifest.json').read_text())
  require(prior.get('id')==OLD,'Rollback identifier changed')
  for name,info in prior['files'].items():
   require(not Path(name).is_absolute() and '..' not in Path(name).parts,'Invalid rollback path')
   path=old/name
   require(path.is_file() and not path.is_symlink() and path.stat().st_size==info['bytes'] and file_hash(path)==info['sha256'],'Rollback file changed: '+name)
  if action=='verify':
   print(json.dumps({'verified':True,'active':OLD,'candidate':NEW,'activationPerformed':False}));return
  target=copy.deepcopy(current);target_site=next(s for s in target['sites'] if s['domain']=='ksu.codes');target_site['codi_simplified']=NEW if action=='activate' else OLD
  ctl.validate(target);expected=PINS['new' if action=='activate' else 'old']
  require((digest(ctl.dump(target).encode()),digest(ctl.caddy(target,'production').encode()))==expected,'Generated target differs from reviewed pins')
  account=pwd.getpwnam('dflanag3');backup=ctl.snapshot(MANIFEST)
  try:
   ctl.write(MANIFEST,ctl.dump(target),0o644,account.pw_uid,account.pw_gid,False)
   ctl.caddy_apply(target,'production')
   require((file_hash(MANIFEST),file_hash(CADDY))==expected,'Applied configuration differs')
  except BaseException:
   ctl.write(MANIFEST,current_manifest,0o644,account.pw_uid,account.pw_gid,False)
   ctl.caddy_apply(current,'production')
   raise
  print(json.dumps({'action':action,'release':target_site['codi_simplified'],'manifest':expected[0],'caddy':expected[1],'controllerBackup':str(backup)}))

if __name__=='__main__':main()
