#!/usr/bin/env python3
"""Stage a Falling Blocks save snapshot change from the verified live Simplified release."""
import hashlib
import json
import os
from pathlib import Path
import shutil

OLD='b89faee1a69374bb846c2e9165ec652e668a18451929be98f3f96b57106a3e04'
BUNDLE='21ffaa41aaa27c869c9a8d072e06b2f82d60a7faddcea5dce9f78e7123f4f505'
CATALOG='265630136c84f9fe5b140a626c26e9ceeb9352583a5f101dcf05ed1780ca769f'
RELEASES=Path('/srv/codi-connected/simplified')
INPUT=Path('/tmp/codi-blocks-snapshot-input')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def replace(path,data):
    tmp=path.with_name('.'+path.name+'.new');tmp.write_bytes(data);tmp.chmod(0o644);os.replace(tmp,path)
def main():
    if os.geteuid()!=0:raise ValueError('root required')
    old=RELEASES/OLD;stage=RELEASES/'.blocks-snapshot-stage'
    if stage.exists() or stage.is_symlink():raise ValueError('stage already exists')
    catalog=INPUT/'apps.json'
    if sha(catalog)!=CATALOG:raise ValueError('input changed')
    new=json.loads(catalog.read_text())['apps'];assert len(new)==1 and new[0]['id']=='falling-blocks' and new[0]['bundleSHA256']==BUNDLE
    bundle=INPUT/'apps/falling-blocks'/BUNDLE
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
    browser=stage/'assets/desktop/apps/falling-blocks';shutil.rmtree(browser)
    shutil.copytree(bundle,browser/BUNDLE)
    for path in [browser/BUNDLE,*(browser/BUNDLE).rglob('*')]:
        if path.is_symlink():raise ValueError('unexpected browser symlink')
        path.chmod(0o755 if path.is_dir() else 0o644)
    path=stage/'assets/desktop/apps.json';data=json.loads(path.read_text())
    i=next(i for i,item in enumerate(data['apps']) if item['id']=='falling-blocks');data['apps'][i]=new[0]
    replace(path,(json.dumps(data,indent=2)+'\n').encode())
    files={}
    for p in sorted(stage.rglob('*')):
        if p.is_symlink():raise ValueError('unexpected symlink')
        if p.is_file() and p.relative_to(stage).as_posix() not in ('assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json'):
            files[p.relative_to(stage).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
    changed={name for name in set(files)|set(expected['files']) if files.get(name)!=expected['files'].get(name)}
    if any(name!='assets/desktop/apps.json' and not name.startswith('assets/desktop/apps/falling-blocks/') for name in changed):raise ValueError('unrelated public file changed')
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
    print(json.dumps({'release':manifest['id'],'files':len(files),'falling-blocks':BUNDLE}))

if __name__=='__main__':main()
