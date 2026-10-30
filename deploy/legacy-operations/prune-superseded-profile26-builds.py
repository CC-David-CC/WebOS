#!/usr/bin/env python3
"""Remove verified superseded expanded profile26 builds, keeping current and rollback."""
import argparse,hashlib,json,os,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases'
KEEPS={'network-512-profile26-r1':'7f6b827263bfb36b530e1e26c46b4bd4f274e6ef8faa8a995a551faf8d0092aa','system-channel-profile26-r2':'894b758887f3b426944e668c81e089377549011856a2a1452d78d13167ca6893'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(folder):
 manifest=folder/'connected-release.json';raw=json.loads(manifest.read_bytes());expected=raw['files'];actual={str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()};assert actual==set(expected)|{'connected-release.json'}
 for name,record in expected.items():
  p=folder/name;assert not p.is_symlink() and p.stat().st_nlink==1 and p.stat().st_size==record['bytes'] and digest(p)==record['sha256']
 return digest(manifest)
def references():
 refs=set();prefix=str(BASE.resolve())+'/'
 def see(raw):
  if prefix in raw:refs.add(raw.split(prefix,1)[1].split('/',1)[0].split('\0',1)[0])
 for proc in Path('/proc').glob('[0-9]*'):
  try:
   see((proc/'cmdline').read_bytes().decode(errors='ignore'))
   for link in [proc/'cwd',proc/'exe',*(proc/'fd').iterdir()]:
    try:see(os.readlink(link))
    except OSError:pass
  except OSError:pass
 return refs
def main(apply):
 assert BASE.resolve()==BASE and not BASE.is_symlink()
 for name,pin in KEEPS.items():assert verify(BASE/name)==pin
 active=references();removed=[];skipped=[]
 for folder in sorted(BASE.iterdir()):
  if not folder.is_dir() or folder.is_symlink() or folder.name in KEEPS or 'candidate' in folder.name or not ('profile26-' in folder.name or folder.name.startswith(('connected-','device-','channel-index-','channel-notice-','channel-short-','channel-yield-','pending-text-chat-intermediate-','signed-chess-rooms-intermediate-'))):continue
  if folder.name in active:skipped.append({'name':folder.name,'reason':'active process'});continue
  try:
   pin=verify(folder);size=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
  except Exception as error:skipped.append({'name':folder.name,'reason':type(error).__name__});continue
  if apply:
   assert folder.name not in references();shutil.rmtree(folder)
  removed.append({'name':folder.name,'manifest':pin,'bytes':size})
 result={'status':'PASS','applied':apply,'retained':KEEPS,'removed' if apply else 'candidates':removed,'skipped':skipped,'bytes':sum(x['bytes'] for x in removed)}
 if apply:
  out=ROOT/'.build/checks'/('profile26-cleanup-'+str(time.time_ns())+'.json');out.write_text(json.dumps(result,indent=2)+'\n');result['receipt']=str(out)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args();r=main(a.apply);print(json.dumps(r,indent=2))
