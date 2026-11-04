#!/usr/bin/env python3
"""Derive a beta-only issuer from the exact sealed native release. Never deploys."""
import argparse, hashlib, json, os, shutil
from pathlib import Path
PIN='1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51'
def sha(data): return hashlib.sha256(data).hexdigest()
def build(base,out):
 base=base.resolve(strict=True); out=out.absolute()
 if out.exists() or out.is_relative_to(base) or base.is_relative_to(out): raise ValueError('Output must be new and separate')
 raw=(base/'connected-release.json').read_bytes()
 if sha(raw)!=PIN: raise ValueError('Wrong native release manifest')
 manifest=json.loads(raw); expected=set(manifest['files'])|{'connected-release.json'}; found=set()
 for root,dirs,files in os.walk(base,followlinks=False):
  for name in dirs+files:
   p=Path(root)/name
   if p.is_symlink(): raise ValueError('Symlink in release')
  for name in files:
   p=Path(root)/name; rel=p.relative_to(base).as_posix(); found.add(rel)
   if not p.is_file() or p.stat().st_nlink!=1: raise ValueError('Unsafe artifact')
   if rel!='connected-release.json':
    record=manifest['files'].get(rel); data=p.read_bytes()
    if not record or len(data)!=record['bytes'] or sha(data)!=record['sha256']: raise ValueError('Unpinned file '+rel)
 if found!=expected: raise ValueError('Release inventory mismatch')
 rel='scripts/serve-connected.py'; source=(base/rel).read_text()
 def replace(old,new):
  nonlocal source
  if source.count(old)!=1: raise ValueError('Issuer source did not match expected input')
  source=source.replace(old,new,1)
 replace("    a=p.parse_args()\n", "    p.add_argument('--beta-opfs-file-content',action='store_true',help='Enable isolated beta OPFS metadata')\n    a=p.parse_args()\n    if a.beta_opfs_file_content and (not a.user_files or a.base_path!='' or not a.origin or not (a.origin=='https://beta.ksu.codes' or re.fullmatch(r'http://127\\.0\\.0\\.1:[0-9]+',a.origin))):p.error('Beta OPFS requires user files, root mount, and beta or loopback origin')\n")
 marker="                    if a.user_files:config['gateway']={'version':'codi-user-files/1','basePath':a.base_path+'/gateway','fileBytes':128*1024*1024}\n"
 replace(marker,marker+"                    if a.beta_opfs_file_content:config['fileStorage']={'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2}\n")
 shutil.copytree(base,out,copy_function=shutil.copy2)
 payload=source.encode(); (out/rel).write_bytes(payload)
 manifest['files'][rel]={'bytes':len(payload),'sha256':sha(payload)}
 sealed=(json.dumps(manifest,indent=2)+'\n').encode();(out/'connected-release.json').write_bytes(sealed)
 print(json.dumps({'base':PIN,'derived':sha(sealed),'issuer':sha(payload)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.base,a.out)
