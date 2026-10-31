#!/usr/bin/env python3
"""Stage a Files folder-copy change from the verified live Simplified release."""
import hashlib
import json
import os
from pathlib import Path
import shutil

OLD='d9e8d3aeb81f3cdb2b3ea4c3477a192328d771d4cefbfee0e48d7ddf341260a4'
BUNDLE='36f7c079c7902e8eba002c35b737bfb46fedf1a28e3cd0a7e645f8ec5193c336'
CATALOG='091160aab8a83e091f17f86d11d9672e9815112a8a4836ce6f2d6bde3cf76aa4'
RELEASES=Path('/srv/codi-connected/simplified')
INPUT=Path('/tmp/codi-folder-copy-input')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def replace(path,data):
    tmp=path.with_name('.'+path.name+'.new');tmp.write_bytes(data);tmp.chmod(0o644);os.replace(tmp,path)
def main():
    if os.geteuid()!=0:raise ValueError('root required')
    old=RELEASES/OLD;stage=RELEASES/'.folder-copy-stage'
    if stage.exists() or stage.is_symlink():raise ValueError('stage already exists')
    catalog=INPUT/'apps.json'
    if sha(catalog)!=CATALOG or sha(INPUT/'mirror.mjs')!='4ac199e1e96e4a9a522c4b81a8fc4784602bc73a37f518c8c96073c3009c75e5':raise ValueError('input changed')
    new=json.loads(catalog.read_text())['apps'];assert len(new)==1 and new[0]['id']=='files' and new[0]['bundleSHA256']==BUNDLE
    bundle=INPUT/'apps/files'/BUNDLE
    if {p.relative_to(bundle).as_posix() for p in bundle.rglob('*') if p.is_file()}!=set(new[0]['files']):raise ValueError('unexpected bundle file')
    for name,record in new[0]['files'].items():
        path=bundle/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size!=record['bytes'] or sha(path)!=record['sha256']:raise ValueError('browser file changed: '+name)
    expected=json.loads((old/'assets/desktop/cache-manifest.json').read_text())
    if expected['id']!=OLD:raise ValueError('live release changed')
    for name,record in expected['files'].items():
        p=old/name
        if p.is_symlink() or p.stat().st_size!=record['bytes'] or sha(p)!=record['sha256']:raise ValueError('old asset changed: '+name)
    shutil.copytree(old,stage,copy_function=os.link,symlinks=False)
    browser=stage/'assets/desktop/apps/files';shutil.rmtree(browser)
    shutil.copytree(bundle,browser/BUNDLE)
    for path in [browser/BUNDLE,*(browser/BUNDLE).rglob('*')]:
        if path.is_symlink():raise ValueError('unexpected browser symlink')
        path.chmod(0o755 if path.is_dir() else 0o644)
    path=stage/'assets/desktop/apps.json';data=json.loads(path.read_text())
    i=next(i for i,item in enumerate(data['apps']) if item['id']=='files');data['apps'][i]=new[0]
    replace(path,(json.dumps(data,indent=2)+'\n').encode())
    replace(stage/'storage/browser/mirror.mjs',(INPUT/'mirror.mjs').read_bytes())
    files={}
    for p in sorted(stage.rglob('*')):
        if p.is_symlink():raise ValueError('unexpected symlink')
        if p.is_file() and p.relative_to(stage).as_posix() not in ('assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json'):
            files[p.relative_to(stage).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
    changed={name for name in set(files)|set(expected['files']) if files.get(name)!=expected['files'].get(name)}
    if any(name not in ('assets/desktop/apps.json','storage/browser/mirror.mjs') and not name.startswith('assets/desktop/apps/files/') for name in changed):raise ValueError('unrelated public file changed')
    canonical=json.dumps(files,sort_keys=True,separators=(',',':')).encode()
    manifest={'version':'codi-public-cache/1','id':hashlib.sha256(canonical).hexdigest(),'files':files}
    encoded=json.dumps(manifest,separators=(',',':')).encode()
    replace(stage/'assets/desktop/cache-manifest.json',encoded)
    worker=stage/'assets/desktop/offline-worker.js';lines=worker.read_bytes().splitlines(keepends=True)
    if not lines[1].startswith(b'const RELEASE=') or not lines[1].rstrip().endswith(b';'):raise ValueError('unexpected cache worker')
    lines[1]=b'const RELEASE='+encoded+b';\n';replace(worker,b''.join(lines))
    dest=RELEASES/manifest['id']
    if dest.exists() or dest.is_symlink():raise ValueError('release already exists')
    stage.rename(dest)
    print(json.dumps({'release':manifest['id'],'files':len(files),'bundle':BUNDLE}))

if __name__=='__main__':main()
