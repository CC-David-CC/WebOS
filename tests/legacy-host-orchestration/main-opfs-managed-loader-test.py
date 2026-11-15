#!/usr/bin/env python3
"""Disposable root-owned managed config: actual load/renderer, no systemd actions."""
import importlib.util,json,os,pathlib,stat,sys,tempfile
root=pathlib.Path(sys.argv[1]); sys.path.insert(0,str(root/'codiserver-server-v0.3.0'))
spec=importlib.util.spec_from_file_location('candidate_operator',root/'scripts/manage-services.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
assert os.geteuid()==0
base={'version':'codi-managed-instance/4','authorityClass':'development','instance':'codi-test-main','release':str(root),'python':'/srv/codi-test-venv/bin/python','stateRoot':'/srv/codi-test-state','unitDir':'/srv/codi-test-units','origin':'https://ksu.codes','basePath':'','ports':{'issuer':8118,'steward':8120,'guest':8132},'manifestSHA256':'a'*64,'maintenance':1,'turn':None,'userFiles':{'configFile':'/srv/codi-test-files/config.json','configSHA256':'b'*64,'operatorRelease':'/srv/codi-test-operator','operatorManifestSHA256':'c'*64},'opfsFileContentOrigin':'https://ksu.codes'}
with tempfile.TemporaryDirectory(dir='/var/lib',prefix='codi-main-load-test-') as d:
 p=pathlib.Path(d)/'config.json'
 def run(config):p.write_text(json.dumps(config));os.chmod(p,0o600);return m.load(p,verify_installation=False)
 loaded=run(base);assert loaded==base
 assert b' "--opfs-file-content-origin" "https://ksu.codes"' in m.render(loaded,'issuer')
 for patch in ({'opfsFileContentOrigin':'https://other.example'},{'opfsFileContentOrigin':'http://ksu.codes'},{'opfsFileContentOrigin':'https://ksu.codes/'},{'basePath':'/hidden'},{'userFiles':False},{'opfsFileContentOrigin':None}):
  try:run({**base,**patch})
  except ValueError:pass
  else:raise AssertionError('Invalid configuration accepted '+repr(patch))
 old=dict(base);del old['opfsFileContentOrigin'];assert run(old)==old;assert b'--opfs-file-content-origin' not in m.render(old,'issuer')
 print('PASS actual managed load with root-owned disposable v4 config, valid explicit origin, six refusals and unconfigured rendering; installation verification disabled')
