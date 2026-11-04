#!/usr/bin/env python3
"""Research-only exact 3ad/830c generator. Never mutates hosting."""
import argparse,ast,hashlib,json,os,stat
from pathlib import Path
OLD='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
NEW='830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0'
SOURCE='d11755a183bc5c12803b6fdc84fa54f4803c0f10c415c07bb9eecc82699132a1'
HERE=Path(__file__).resolve().parents[2];GEN=HERE/'beta-isolated-hosting/ops/common.py'
def digest(data):return hashlib.sha256(data).hexdigest()
def inventory(root,expected,count):
 root=Path(root);raw=(root/'manifest.json').read_bytes()
 if digest(raw)!=expected:raise ValueError('candidate manifest pin mismatch')
 value=json.loads(raw);records=value['files'];found=set()
 if len(records)!=count:raise ValueError('candidate file count changed')
 for base,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   path=Path(base)/name;v=path.lstat()
   if not (stat.S_ISREG(v.st_mode) or stat.S_ISDIR(v.st_mode)):raise ValueError('unsafe asset entry')
  for name in files:
   path=Path(base)/name;rel=path.relative_to(root).as_posix()
   if rel=='manifest.json':continue
   h=hashlib.sha256();size=0
   with path.open('rb') as stream:
    while chunk:=stream.read(1024*1024):h.update(chunk);size+=len(chunk)
   if records.get(rel)!={'bytes':size,'sha256':h.hexdigest()}:raise ValueError('asset changed: '+rel)
   found.add(rel)
 if found!=set(records):raise ValueError('asset inventory incomplete')
 return value

def replace_one(s,a,b):
 if s.count(a)!=1:raise ValueError('generator source anchor changed')
 return s.replace(a,b)

def build(old_path,new_path,out):
 old=inventory(old_path,OLD,87);new=inventory(new_path,NEW,171)
 if new.get('parent')!=OLD:raise ValueError('candidate parent changed')
 oldf=old['files'];newf=new['files'];changed={k for k in oldf if oldf[k]!=newf.get(k)}
 if changed!={'assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js','patches/desktop-apps.diff','shell/desktop-apps.js'}:raise ValueError('unexpected old asset changes')
 if set(oldf)-set(newf):raise ValueError('old asset removed')
 src=GEN.read_bytes()
 if digest(src)!=SOURCE:raise ValueError('generator source pin mismatch')
 s=src.decode();tree=ast.parse(s)
 assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OPFS_PUBLIC_FILES' for t in n.targets))
 oldroutes=ast.literal_eval(assignment.value)
 expectedold={'/'+p:r['sha256'] for p,r in oldf.items() if p.startswith(('assets/','storage/'))}
 routes={'/'+p:r['sha256'] for p,r in newf.items() if p.startswith(('assets/','storage/'))}
 if oldroutes!=expectedold or len(routes)!=len(newf)-5:raise ValueError('unexpected public route inventory')
 line=s.splitlines(keepends=True)[assignment.lineno-1]
 s=replace_one(s,line,line+'OPFS_NEW_PUBLIC_FILES = '+repr(dict(sorted(routes.items())))+'\n')
 s=replace_one(s,"data['codi_beta_opfs']!='"+OLD+"'", "data['codi_beta_opfs'] not in ('"+OLD+"','"+NEW+"')")
 s=replace_one(s,"' '.join(OPFS_PUBLIC_FILES)","' '.join(OPFS_PUBLIC_FILES if data['codi_beta_opfs']=='"+OLD+"' else OPFS_NEW_PUBLIC_FILES)")
 prefix="f'\\t@beta_opfs_unknown path /assets/desktop/apps/files/{bundle}/* /storage/browser/releases/{graph}/*'"
 unknown="f'\\t@beta_opfs_unknown path /assets/desktop/apps/files/{bundle}/* /storage/browser/releases/{graph}/* /assets/desktop/apps/files/b7e943c563ea83ad91988e595e1afcada8f31d71eda01e9915d104f32774d7b7/* /assets/desktop/apps/text/241776677999e79b759ab00e077569a93f081ccb1cc9c04e42a192e9e6b9bcb3/* /storage/browser/releases/3daf09a753455be1dc07ce183097b6535a999d2cc2124f9d0e6df25c7180be3a/*'"
 # Preserve the exact original 3ad rendering. The 830c rendering rejects
 # unlisted paths under both old and new immutable graph prefixes.
 s=replace_one(s,prefix,'('+prefix+" if data['codi_beta_opfs']=='"+OLD+"' else "+unknown+')')
 out=Path(out);out.mkdir(mode=0o700);(out/'common.py').write_text(s)
 table={'old':OLD,'new':NEW,'newRoutes':dict(sorted(routes.items()))}
 (out/'routes.json').write_text(json.dumps(table,sort_keys=True,indent=2)+'\n')
 print('generator',digest(s.encode()),'route-table',digest((out/'routes.json').read_bytes()),'routes',len(routes))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--old',required=True);p.add_argument('--new',required=True);p.add_argument('--out',required=True);a=p.parse_args();build(a.old,a.new,a.out)
