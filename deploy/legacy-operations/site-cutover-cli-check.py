#!/usr/bin/env python3
"""Exercise sealed root CLI refusals in the existing private VM, without migration."""
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent.parent
REMOTE = r'''
import hashlib,json,os,pathlib,shutil,subprocess,sys,time
P=pathlib.Path;v=json.load(sys.stdin);base=P('/srv/codi-site-fixture');source=P(v['operator']);cfg=P('/etc/codi-native-fixture/managed.json');before=hashlib.sha256(cfg.read_bytes()).hexdigest()
assert not any((cfg.parent/n).exists() for n in ['site-cutover.json','maintenance.json','native-rollout.json'])
plan=sorted((base/'plans').glob('plan-*.json'))[-1];plan_pin=hashlib.sha256(plan.read_bytes()).hexdigest();python='/srv/codi-network-fixture/venv/bin/python';folder=base/('negative-cli-'+str(time.time_ns()));folder.mkdir(mode=0o700);checks=[]
def check(name,tool,operator_pin,plan_path=plan,pin=plan_pin,match=''):
 r=subprocess.run([python,'-I','-B',str(tool/'scripts/site-cutover.py'),'plan','--operator-sha256',operator_pin,'--plan',str(plan_path),'--plan-sha256',pin],capture_output=True,text=True,timeout=45)
 assert r.returncode!=0 and match in r.stderr,(name,r.stdout,r.stderr)
 checks.append({'name':name,'returnCode':r.returncode,'reason':match})
try:
 check('wrong operator digest',source,'0'*64,match='Operator manifest digest differs')
 check('wrong plan digest',source,v['operatorSHA256'],pin='0'*64,match='Plan differs from its reviewed pin')
 for name,kind,match in [('unlisted file','extra','Incomplete/unlisted operator files'),('empty symlink directory','directory','Protected root-owned operator/plan path required'),('declared symlink file','file','Protected root-owned operator/plan path required')]:
  target=folder/kind;shutil.copytree(source,target)
  if kind=='extra':(target/'extra.py').write_text('# not declared\n')
  elif kind=='directory':
   empty=folder/'empty';empty.mkdir();(target/'foreign').symlink_to(empty,target_is_directory=True)
  else:
   file=target/'site_cutover/coordinator.py';file.unlink();file.symlink_to(source/'site_cutover/coordinator.py')
  check(name,target,v['operatorSHA256'],match=match)
 public=folder/'public-plan.json';public.write_bytes(plan.read_bytes());public.chmod(0o644)
 check('nonprivate plan mode',source,v['operatorSHA256'],plan_path=public,match='Keep the on-server plan private with mode0600')
 assert hashlib.sha256(cfg.read_bytes()).hexdigest()==before and not any((cfg.parent/n).exists() for n in ['site-cutover.json','maintenance.json','native-rollout.json'])
 print(json.dumps({'status':'PASS','checks':checks,'nativeConfigUnchanged':True,'nativeOrHostingOperationStarted':False,'fixtureOnly':True}))
finally:shutil.rmtree(folder)
'''


if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('site_cli_vm', ROOT/'scripts/prepare-native-network-vm.py')
    vm = importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)
    context = json.loads((ROOT/'.build/checks/site-cutover-vm-context.json').read_text())
    child = subprocess.run([*vm.ssh_args(), '/usr/bin/python3 -I -B -c '+shlex.quote(REMOTE)],
                           input=json.dumps(context), capture_output=True, text=True, timeout=180)
    if child.returncode:
        raise ValueError(child.stderr[-5000:] or child.stdout[-3000:])
    result = json.loads(child.stdout)
    (ROOT/'.build/checks/site-cutover-cli-result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
