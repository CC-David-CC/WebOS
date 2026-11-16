#!/usr/bin/env python3
"""Guard-aware 3ad recovery generation; refuses all 830c markers under lock."""
import hashlib,json,os,stat,sys
from pathlib import Path
BASE='bc9f939a9db8849fb7d580e5a71d5c52728b127b74c3bca1ee811b41fdd1f754';LAUNCH='314e493ff52b8999bc2fcf57eef220389dda16722bd2b5bec95a945f136a319d';PRE='6907c787ce89886d84f5863e565ba9ac3dc41a87f8908c637cf3c8330bcecdf1';OLDGUARD='fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783';NEWGUARD='ca25bb27799f0f306d7d901188d894d39ad22ea99ea2c1f1d224a2c6446ab8b9'
sha=lambda b:hashlib.sha256(b).hexdigest()
def one(s,a,b):
 if s.count(a)!=1:raise ValueError('source anchor changed')
 return s.replace(a,b)
def build(src,dst):
 src=Path(src);dst=Path(dst);raw=(src/'inventory.json').read_bytes()
 if sha(raw)!=BASE:raise ValueError('baseline inventory changed')
 pins=json.loads(raw);found=set();inputs={}
 for root,dirs,files in os.walk(src,followlinks=False):
  for n in dirs+files:
   p=Path(root)/n;v=p.lstat()
   if not (stat.S_ISREG(v.st_mode) or stat.S_ISDIR(v.st_mode)):raise ValueError('unsafe source entry')
  for n in files:
   p=Path(root)/n;name=p.relative_to(src).as_posix()
   if name=='inventory.json':continue
   data=p.read_bytes()
   if pins.get(name)!=sha(data):raise ValueError('baseline file changed: '+name)
   inputs[name]=data;found.add(name)
 if found!=set(pins):raise ValueError('baseline inventory incomplete')
 if sha(inputs['ops/beta_files_recover.py'])!=LAUNCH or sha(inputs['ops/beta_files_preflight.py'])!=PRE:raise ValueError('unexpected base sources')
 pre=one(inputs['ops/beta_files_preflight.py'].decode(),OLDGUARD,NEWGUARD).encode()
 launch=inputs['ops/beta_files_recover.py'].decode();launch=one(launch,"'beta_files_preflight':'"+PRE+"'","'beta_files_preflight':'"+sha(pre)+"'")
 anchor=" with lock.held():\n  check_lock()\n"
 guard=" with lock.held():\n  check_lock()\n  for name in ('files-asset-transition.json','files-asset-floor.json'):\n   try:(journal/name).lstat()\n   except FileNotFoundError:continue\n   raise ValueError('Asset transition or floor requires 830c recovery')\n"
 launch=one(launch,anchor,guard);inputs['ops/beta_files_preflight.py']=pre;inputs['ops/beta_files_recover.py']=launch.encode()
 dst.mkdir(mode=0o700)
 for name,data in sorted(inputs.items()):p=dst/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 inventory={n:sha(b) for n,b in sorted(inputs.items())};(dst/'inventory.json').write_text(json.dumps(inventory,sort_keys=True,indent=2)+'\n')
 print('inventory',sha((dst/'inventory.json').read_bytes()),'launcher',sha(launch.encode()),'preflight',sha(pre))
if __name__=='__main__':build(sys.argv[1],sys.argv[2])
