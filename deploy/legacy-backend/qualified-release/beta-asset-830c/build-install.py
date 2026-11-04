#!/usr/bin/env python3
"""Derive narrowly pinned fb27→830c-guard installer; no host installation."""
import hashlib,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parent;out=Path(sys.argv[1]);sha=lambda b:hashlib.sha256(b).hexdigest()
def read(name,pin):
 b=(root/name).read_bytes()
 if sha(b)!=pin:raise ValueError('installation source pin changed: '+name)
 return b.decode()
def one(s,a,b):
 if s.count(a)!=1:raise ValueError('installation source anchor changed')
 return s.replace(a,b)
old='84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e';fb='fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783';guard='ca25bb27799f0f306d7d901188d894d39ad22ea99ea2c1f1d224a2c6446ab8b9';bc='bc9f939a9db8849fb7d580e5a71d5c52728b127b74c3bca1ee811b41fdd1f754';actor='76a7cff14def855ba9dfcdc4a03916772c931df81c9cdafac34653348f4b83b7'
pre=read('main-successor-preflight.py','9bbfd5e256a70fd385286a008af92d3928f6ea1511ad19062b60e14ac526df83');pre=one(pre,bc,actor);pre=one(pre,'len(records)!=28','len(records)!=35');pre=pre.encode()
ins=read('main-install.py','c6bd426cb8cd87564d14b458c1cda85dbc6655794719fb84615e4d7c9c271e96');ins=one(ins,old,fb);ins=one(ins,"NEW='"+fb+"'","NEW='"+guard+"'");ins=one(ins,bc,actor);ins=one(ins,"'files-asset-transition.json'):","'files-asset-transition.json','files-asset-floor.json'):");ins=ins.encode()
launch=read('main-install-launch.py','5c5442d6bb75e00b4520e4b756e6ca4f5bec1f24e19195f834bcadbb0e6f3b3c')
launch=one(launch,'/srv/codi-connected/operators/main-qualified-e7e8-v1','/srv/codi-connected/operators/beta-files-830c-installer-v1');launch=one(launch,'/srv/codi-connected/operators/main-qualified-e7e8-input/successor','/srv/codi-connected/operators/beta-files-830c-input/actor');launch=one(launch,'/srv/codi-connected/operators/beta-recovery-e7-v1','/srv/codi-connected/operators/beta-files-830c-v1')
launch=one(launch,'c6bd426cb8cd87564d14b458c1cda85dbc6655794719fb84615e4d7c9c271e96',sha(ins));launch=one(launch,'9bbfd5e256a70fd385286a008af92d3928f6ea1511ad19062b60e14ac526df83',sha(pre));launch=one(launch,"'main-launcher.py')","'main-launcher.py','asset-launch.py')")
launch=one(launch,"'files-asset-transition.json'):","'files-asset-transition.json','files-asset-floor.json'):")
retirement=(here/'retirement.py').read_bytes();retirement_pin=sha(retirement)
launch=one(launch,"'main-successor-preflight.py':'"+sha(pre)+"'", "'main-successor-preflight.py':'"+sha(pre)+"','retirement.py':'"+retirement_pin+"'")
launch=one(launch,"FLOOR=Path('/var/lib/webhost-ops/opfs-floor.json')",'''FLOOR=Path('/var/lib/webhost-ops/opfs-floor.json')
QUARANTINE=Path('/srv/codi-connected/operators/retired-830c-actors-v1')
RETIRED={'bc9':Path('/srv/codi-connected/operators/beta-recovery-e7-v1/ops/beta_files_recover.py'),'ce18-bundle':Path('/srv/codi-connected/operators/files-bundle-ce18b7794adc2472/ops/beta_files_launch.py'),'ce18-input':Path('/srv/codi-connected/operators/files-install-input-ce18b7794adc2472/ops/beta_files_launch.py'),'main-once':Path('/srv/codi-connected/operators/main-qualified-e7e8-v1/main-launcher.py')}''')
launch=one(launch,"installer=load(PKG,'main-install.py','main_install')", "installer=load(PKG,'main-install.py','main_install');retirement=load(PKG,'retirement.py','asset_retirement')")
launch=one(launch,"   print(json.dumps({'action':'plan','status':'PASS','requiresTrustedFreeze':True,'productionQualified':False}));return", "   retirement.validate(RETIRED,QUARANTINE,pr,lock.check,pending=False)\n   print(json.dumps({'action':'plan','status':'PASS','requiresTrustedFreeze':True,'productionQualified':False}));return")
anchor="  status=installer.install(source=SOURCE,destination=DEST,guard=PKG/'webctl-main-guard.py',target=TARGET,journal=JOURNAL,floor=FLOOR,primitives=pr,verify_successor=successor.verify,check_lock=lock.check,check_fence=fence,check_custody=custody)"
replacement='''  expected={'version':1,'old':installer.OLD,'new':installer.NEW,'inventory':installer.INV,'target':str(TARGET),'destination':str(DEST),'uid':1000,'gid':1000,'mode':0o644}
  def retire_old():
   lock.check();fence();custody();pr.root_path(FLOOR)
   if stat.S_IMODE(FLOOR.stat().st_mode)!=0o600 or json.loads(pr.read_file(FLOOR,4096))!=installer.FLOOR:raise ValueError('Original floor changed')
   for name in ('opfs-transition.json','files-inner-hosting.json','files-issuer-switch.json','files-emergency-gate.json','files-normalization.json','beta-hosting-journal.json','files-asset-transition.json','files-asset-floor.json'):
    try:(JOURNAL.parent/name).lstat()
    except FileNotFoundError:continue
    raise ValueError('Conflicting hosting journal or asset floor: '+name)
   successor.verify(DEST,pr.read_file,lock.check)
   retirement.retire(entries=RETIRED,quarantine=QUARANTINE,journal=JOURNAL,expected=expected,primitives=pr,check_lock=lock.check,check_fence=fence)
  def all_retired():
   retirement.validate(RETIRED,QUARANTINE,pr,lock.check,pending=True)
   for path in RETIRED.values():
    try:path.lstat()
    except FileNotFoundError:continue
    raise ValueError('Legacy actor is still callable')
  if exists:retire_old()
  elif hashlib.sha256(pr.read_file(TARGET,root_owned=False)).hexdigest()==installer.NEW:all_retired()
  else:retirement.validate(RETIRED,QUARANTINE,pr,lock.check,pending=False)
  def progress(name):
   if name=='journaled':retire_old()
   if name=='verified':all_retired()
  status=installer.install(source=SOURCE,destination=DEST,guard=PKG/'webctl-main-guard.py',target=TARGET,journal=JOURNAL,floor=FLOOR,primitives=pr,verify_successor=successor.verify,check_lock=lock.check,check_fence=fence,check_custody=custody,phase=progress)'''
launch=one(launch,anchor,replacement);launch=launch.encode()
# The guard is supplied separately, from the exact independent guard builder.
guard_bytes=Path(sys.argv[2]).read_bytes()
if sha(guard_bytes)!=guard:raise ValueError('asset guard source pin changed')
entries={'main-install-launch.py':launch,'main-install.py':ins,'main-successor-preflight.py':pre,'webctl-main-guard.py':guard_bytes,'retirement.py':retirement}
out.mkdir(mode=0o700)
for name,data in sorted(entries.items()):(out/name).write_bytes(data)
record={n:sha(v) for n,v in sorted(entries.items())};(out/'manifest.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
print('install',sha(launch),'primitive',sha(ins),'preflight',sha(pre),'inventory',sha((out/'manifest.json').read_bytes()))
