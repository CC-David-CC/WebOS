#!/usr/bin/env python3
"""Actual transaction/renderer with disposable files and simulated systemd."""
import importlib.util,json,pathlib,sys,tempfile
root=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(root));sys.path.insert(0,str(root/'codiserver-server-v0.3.0'))
spec=importlib.util.spec_from_file_location('managed_test',root/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
from origin_service import opfs_management as tx,maintenance,deployment
maintenance.guard=lambda *a:None;maintenance.guard_epoch=lambda *a:None;maintenance.sync_directory=lambda *a:None;deployment.active=lambda *a:['issuer'];deployment.syntax=lambda *a:None
op.installed=lambda *a:None;op.stop=lambda *a:None;op.ready=lambda *a:None;op.systemctl=lambda *a:'active\n'
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d);(p/'units').mkdir();(p/'state/public').mkdir(parents=True);identity={'issuer':'https://ksu.codes','mode':'server'};(p/'state/public/origin-discovery.json').write_text(json.dumps({'identity':identity}));config={'release':str(root),'stateRoot':str(p/'state'),'basePath':'','origin':'https://ksu.codes','ports':{'issuer':8118,'steward':8120,'guest':8132},'python':'/usr/bin/python3','instance':'codi-test','unitDir':str(p/'units'),'maintenance':1,'userFiles':{'fixture':True}}
 target=p/'config.json';unit=p/'units/codi-test-issuer.service'
 def atomic(path,raw,*args):pathlib.Path(path).write_bytes(raw)
 op.atomic=atomic;op.read_owned=lambda path,*a:pathlib.Path(path).read_bytes()
 def current():return json.loads(target.read_text())
 def reset():target.write_text(json.dumps(config));unit.write_bytes(op.render(config,'issuer'))
 def actual(c):return {'identity':identity,**({'fileStorage':tx.EXPECTED} if c.get('opfsFileContentOrigin') else {})}
 op.issuer_config=actual
 reset();assert tx.configure(op,current(),target,config['origin'])['status']=='opfs-switch-configured';assert current()['opfsFileContentOrigin']==config['origin'];assert b'--opfs-file-content-origin' in unit.read_bytes();assert not (p/'maintenance.json').exists()
 for phase in ('prepared','switching','starting','committed'):
  reset()
  def die(value):
   if value==phase:raise SystemExit('simulated process death')
  try:tx.configure(op,current(),target,config['origin'],phase=die)
  except SystemExit:pass
  else:raise AssertionError('missing interruption')
  result=tx.recover(op,current(),target)
  if phase=='committed':assert result['status']=='opfs-switch-committed-recovered' and current().get('opfsFileContentOrigin')==config['origin']
  else:assert result['status']=='opfs-switch-rolled-back' and 'opfsFileContentOrigin' not in current()
  assert not (p/'maintenance.json').exists()
 # A failed/stopped steward is skipped by real active() while issuer remains active.
 systemctl_before=op.systemctl
 def states(*args):
  role=args[1]
  if 'issuer-bootstrap' in role:return 'ActiveState=inactive\nMainPID=0\n'
  if 'issuer.service' in role:return 'ActiveState=active\nMainPID=42\n'
  if 'steward' in role:return 'ActiveState=failed\nMainPID=0\n'
  return 'ActiveState=inactive\nMainPID=0\n'
 op.systemctl=states
 # The earlier test substitutes active; load a fresh actual deployment module.
 import importlib.util
 spec2=importlib.util.spec_from_file_location('deployment_actual',root/'origin_service/deployment.py');dep=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(dep)
 assert dep.active(op,config)==['issuer'];op.systemctl=systemctl_before
 reset();original=op.atomic;hits=[0]
 def fail_between(path,raw,*args):
  original(path,raw,*args)
  if pathlib.Path(path)==unit and hits[0]==0:hits[0]+=1;raise SystemExit('death after unit before config')
 op.atomic=fail_between
 try:tx.configure(op,current(),target,config['origin'])
 except SystemExit:pass
 else:raise AssertionError('unit interruption not injected')
 op.atomic=original;assert b'--opfs-file-content-origin' in unit.read_bytes();assert tx.recover(op,current(),target)['status']=='opfs-switch-rolled-back';assert b'--opfs-file-content-origin' not in unit.read_bytes()
 reset();op.issuer_config=lambda c:{'identity':identity,'fileStorage':{'bad':True}} if c.get('opfsFileContentOrigin') else {'identity':identity}
 assert tx.configure(op,current(),target,config['origin'])['status']=='opfs-switch-rolled-back';assert 'opfsFileContentOrigin' not in current()
 reset();op.issuer_config=actual;original=op.atomic
 def fail_after_commit(path,raw,*args):
  original(path,raw,*args)
  if pathlib.Path(path).name=='maintenance.json' and json.loads(raw).get('phase')=='committed':raise OSError('directory fsync after replace')
 op.atomic=fail_after_commit
 try:tx.configure(op,current(),target,config['origin'])
 except ValueError as error:assert 'committed' in str(error)
 else:raise AssertionError('commit sync failure was hidden')
 assert current().get('opfsFileContentOrigin')==config['origin']
 assert json.loads((p/'maintenance.json').read_text())['phase']=='committed'
 op.atomic=original
 assert tx.recover(op,current(),target)['status']=='opfs-switch-committed-recovered'
 assert current().get('opfsFileContentOrigin')==config['origin'] and not (p/'maintenance.json').exists()
 print('PASS actual transaction/renderer with simulated systemd: apply, four phase deaths, unit/config split, bad metadata rollback and post-replace commit failure')
