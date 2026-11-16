#!/usr/bin/env python3
"""CLI dispatch guard; disposable files and real flock, no host operations."""
import fcntl,hashlib,importlib.util,json,os,sys,tempfile,tomllib,types
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'));sys.modules['scaffold']=types.SimpleNamespace(scaffold=lambda *a:None)
spec=importlib.util.spec_from_file_location('guarded_webctl',root/'ops/webctl_floor_candidate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
import common
real=tomllib.loads((root/'ops/sites_live.toml').read_text());real['codi_beta_maintenance']=False;real['codi_beta_opfs']='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
assert hashlib.sha256(m._beta_block(common.caddy(real,'production')).encode()).hexdigest()==m.BETA_V2_BLOCK_SHA
with tempfile.TemporaryDirectory(prefix='webctl-floor-') as temp:
 t=Path(temp);t.chmod(0o700);m.ROOT=t;m.BETA_FILES_FLOOR=t/'opfs-floor.json';m.BETA_FILES_JOURNAL=t/'opfs-transition.json';m.ACTIVE_CADDY=t/'Caddyfile';m.root_required=lambda:None;calls=[]
 block='beta.ksu.codes {\n respond "known-v2"\n}\n';m.BETA_V2_BLOCK_SHA=hashlib.sha256(block.encode()).hexdigest();m.ACTIVE_CADDY.write_text('# webhost-sites mode: production\n'+block);m.ACTIVE_CADDY.chmod(0o600)
 data={'sites':[],'codi_beta_opfs':'3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc','codi_beta_maintenance':False}
 def load():
  with (t/'.controller.lock').open('r') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);raise AssertionError('manifest loaded outside host lock')
   except BlockingIOError:pass
  calls.append('load');return dict(data)
 m.load=load;m.caddy=lambda d,mode:block if not d.get('tampered') else block+'beta.ksu.codes {\n}\n';m.render=lambda value:calls.append('render')
 def call(args):
  saved=sys.argv;sys.argv=['webctl',*args]
  try:m.main()
  finally:sys.argv=saved
 call(['render']);assert calls==['load','render'];calls.clear()
 commands=[['render'],['validate'],['private'],['prepare'],['activate'],['caddy-rollback','/tmp/x'],['add','example.test','--theme','x','--description','x'],['deploy','example.test'],['up','example.test'],['down','example.test'],['restart','example.test'],['rollback','example.test'],['workers','example.test','2']]
 for symlink in (False,True):
  if symlink:m.BETA_FILES_JOURNAL.symlink_to(t/'missing')
  else:m.BETA_FILES_JOURNAL.write_text('pending')
  for args in commands:
   try:call(args);raise AssertionError('pending journal accepted: '+str(args))
   except RuntimeError as error:assert 'pending beta Files' in str(error)
   assert not calls
  m.BETA_FILES_JOURNAL.unlink()
 m.BETA_FILES_FLOOR.write_text(json.dumps({'version':1,'baseline':'a'*64,'candidate':data['codi_beta_opfs']}));m.BETA_FILES_FLOOR.chmod(0o600)
 call(['render']);assert calls==['load','render'];calls.clear()
 # Exercise a genuine non-beta legacy maintenance dispatch after the floor.
 data['sites']=[{'domain':'other.example','slug':'other','workers':1,'enabled':False}];m.CONFIG=t;m.validate=lambda value:None;m.owner=lambda:types.SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid());m.dump=lambda value:'fixture manifest';m.write=lambda *a,**kw:calls.append('write')
 call(['workers','other.example','2']);assert calls==['load','write','write','render'];calls.clear()
 for args in (['prepare'],['private'],['caddy-rollback','/tmp/x']):
  try:call(args);raise AssertionError('unsafe mode change accepted')
  except RuntimeError as error:assert 'cannot replace' in str(error)
  assert calls==['load'];calls.clear()
 data['tampered']=True
 try:call(['render']);raise AssertionError('untrusted beta output accepted')
 except ValueError:pass
 assert calls==['load'];calls.clear();data.pop('tampered')
 m.ACTIVE_CADDY.write_text('# webhost-sites mode: production\n'+'beta.ksu.codes {\n respond "wrong"\n}\n')
 try:call(['render']);raise AssertionError('untrusted live beta accepted')
 except ValueError:pass
 assert calls==['load'];calls.clear()
 m.BETA_FILES_FLOOR.write_text('{bad')
 try:call(['render']);raise AssertionError('malformed floor accepted')
 except ValueError:pass
 assert calls==['load'];calls.clear();m.BETA_FILES_FLOOR.unlink();m.BETA_FILES_FLOOR.symlink_to(t/'missing')
 try:call(['render']);raise AssertionError('symlink floor accepted')
 except OSError:pass
 assert calls==['load']
 print('PASS locked CLI permits pinned v2-preserving post-floor unrelated worker maintenance, blocks pending/unknown beta and unsafe mode changes')
