#!/usr/bin/env python3
"""Build review-only beta recovery source from exact pinned prior sources."""
import argparse,ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OPS=ROOT/'research/beta-isolated-hosting/ops';HERE=Path(__file__).resolve().parent
EXPECTED='aa34f6c9e53f049d012a45da35989d1aab4797ef983d270ab498d01037fbfd82';OLD='4f9bdcd5d47f6d2e0bf02c80bdb181dd36c62ce7b2046cb0bc0d960fa7cd05ff';GUARD='fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783'
def sha(x):return hashlib.sha256(x).hexdigest()
def one(s,a,b):
 if s.count(a)!=1:raise ValueError('Expected one anchor: '+a[:90])
 return s.replace(a,b)
def build(out):
 out=Path(out)
 launch=(OPS/'beta_files_launch.py').read_bytes();pre=(OPS/'beta_files_preflight.py').read_bytes();succ=(HERE/'beta-successor.py').read_bytes()
 if sha(launch)!=EXPECTED or sha(pre)!=OLD:raise ValueError('Prior beta source pin changed')
 tree=ast.parse(launch.decode())
 pins=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PINS' for t in n.targets))
 inputs={}
 for name,digest in pins.items():
  data=(OPS/(name+'.py')).read_bytes()
  if sha(data)!=digest:raise ValueError('Pinned input mismatch: '+name)
  inputs[name+'.py']=data
 for name,digest in [('sites_live.toml','9bf8afdaab7d321940cc01b9275af81ba2b1ad558a3b966f24e05c6561a317b5'),('beta_files_candidate.json','3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc')]:
  data=(OPS/name).read_bytes()
  if sha(data)!=digest:raise ValueError('Pinned input mismatch: '+name)
  inputs[name]=data
 table=(OPS.parent/'OPFS-ROUTE-TABLE.json').read_bytes()
 if sha(table)!='773dcdfa559d9ad5b5012bb4363248e8434e97dc33d2677bdd376d099c87fc1a':raise ValueError('Route table mismatch')
 pre=one(pre.decode(),"GUARDED_WEBCTL='84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e'", "GUARDED_WEBCTL='"+GUARD+"'").encode()
 src=launch.decode();src=one(src,"import argparse,hashlib,json,os,pwd,socket,stat,sys,types,urllib.error,urllib.request","import argparse,contextlib,hashlib,json,os,pwd,socket,stat,sys,types,urllib.error,urllib.request")
 src=one(src,"'beta_files_preflight':'"+OLD+"'", "'beta_files_preflight':'"+sha(pre)+"',\n 'beta_successor':'"+sha(succ)+"'")
 src=one(src,"parser.add_argument('action',choices=('plan','apply','recover'))", "parser.add_argument('action',choices=('recover',))")
 src=one(src,"load('beta_signed_probe');signed=load('beta_signed_health')", "load('beta_signed_probe');successor=load('beta_successor');signed=load('beta_signed_health')")
 marker=" baseline=hashlib.sha256(x['normalized']['manifest']).hexdigest();floorpath=journal/'opfs-floor.json'\n"
 if src.count(marker)!=1:raise ValueError('Missing floor anchor')
 before,after=src.split(marker)
 tail=" if args.action=='plan':\n";end="if __name__=='__main__':main()\n"
 if after.count(tail)!=1 or not after.endswith(end):raise ValueError('Unexpected launcher dispatch')
 body=after[:after.index(tail)]
 # Holding the existing hosting lock makes selection and all subsequent beta
 # actions one transaction. Nested adapters only validate that held lock.
 opening=''' baseline=hashlib.sha256(x['normalized']['manifest']).hexdigest();floorpath=journal/'opfs-floor.json'
 with lock.held():
  check_lock()
  pending=journal/'main-restriction-journal.json'
  try:pending.lstat()
  except FileNotFoundError:pass
  else:raise ValueError('Main restriction transaction pending')
  host.protected(floorpath);info=floorpath.lstat()
  if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1:raise ValueError('Unsafe beta floor')
  floor_record=json.loads(host.read(floorpath,4096))
  families=successor.families(x,old_bound,new_bound)
  current={'common':host.read(root/'ops/common.py'),'manifest':host.read(root/'sites.toml'),'caddy':host.read('/etc/caddy/Caddyfile')}
  journals=[]
  for name in ('files-inner-hosting.json','files-emergency-gate.json'):
   path=journal/name
   try:st=path.lstat()
   except FileNotFoundError:continue
   host.protected(path)
   if not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode)!=0o600 or st.st_nlink!=1:raise ValueError('Unsafe nested beta journal')
   journals.append(json.loads(host.read(path,8*1024*1024)))
  if len(journals)>1:raise ValueError('Multiple beta route journals require review')
  _,x=successor.select(families,current,floor=floor_record,main_journal_present=False,nested_journal=journals[0] if journals else None)
  @contextlib.contextmanager
  def held_lock():
   check_lock();yield
'''
 # Replace lock entry used by router/binding only; never call HostLock recursively.
 body=one(body,'lock=lock.held,check_lock=check_lock','lock=held_lock,check_lock=check_lock')
 body=one(body,'ManagedBinding(lock.held,check_lock,','ManagedBinding(held_lock,check_lock,')
 dispatch="  print(json.dumps({'status':assembly.recover(baseline,snap.CANDIDATE),'action':'recover'}))\n"
 result=before+opening+''.join(' '+line if line.strip() else line for line in body.splitlines(keepends=True))+dispatch+end
 inputs.update({'beta_files_preflight.py':pre,'beta_successor.py':succ,'beta_files_recover.py':result.encode()})
 out.mkdir(mode=0o700);ops=out/'ops';ops.mkdir(mode=0o700)
 for name,data in sorted(inputs.items()):(ops/name).write_bytes(data)
 (out/'OPFS-ROUTE-TABLE.json').write_bytes(table)
 inventory={str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
 (out/'inventory.json').write_text(json.dumps(inventory,sort_keys=True,indent=2)+'\n')
 print('inventory',sha((out/'inventory.json').read_bytes()),'files',len(inventory))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output');build(p.parse_args().output)
