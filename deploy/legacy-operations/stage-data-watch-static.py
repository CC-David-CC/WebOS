#!/usr/bin/env python3
"""Stage a Data Explorer source notice from the verified live Simplified release."""
import hashlib
import json
import os
from pathlib import Path
import shutil

OLD='3798c7e6da8fdfa054c389e856f4c4b839467256b4d1722e4bc6ce7e8e736d8e'
BUNDLE='ab32d4dc968a0a425f0f45208cac64e9ef0b989280229895994a105f8edaad4b'
CATALOG='3be5610c8fbce30c98b437773df9e4f155a3d5b00fde29dd1421ae165cdb0cc6'
RELEASES=Path('/srv/codi-connected/simplified')
INPUT=Path('/tmp/codi-data-watch-input')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def replace(path,data):
    tmp=path.with_name('.'+path.name+'.new');tmp.write_bytes(data);tmp.chmod(0o644);os.replace(tmp,path)
def main():
    if os.geteuid()!=0:raise ValueError('root required')
    old=RELEASES/OLD;stage=RELEASES/'.data-watch-stage'
    if stage.exists() or stage.is_symlink():raise ValueError('stage already exists')
    catalog=INPUT/'apps.json'
    if sha(catalog)!=CATALOG:raise ValueError('input changed')
    new=json.loads(catalog.read_text())['apps'];assert len(new)==1 and new[0]['id']=='data-explorer' and new[0]['bundleSHA256']==BUNDLE
    bundle=INPUT/'apps/data-explorer'/BUNDLE
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
    browser=stage/'assets/desktop/apps/data-explorer';shutil.rmtree(browser)
    shutil.copytree(bundle,browser/BUNDLE)
    for path in [browser/BUNDLE,*(browser/BUNDLE).rglob('*')]:
        if path.is_symlink():raise ValueError('unexpected browser symlink')
        path.chmod(0o755 if path.is_dir() else 0o644)
    path=stage/'assets/desktop/apps.json';data=json.loads(path.read_text())
    i=next(i for i,item in enumerate(data['apps']) if item['id']=='data-explorer');data['apps'][i]=new[0]
    replace(path,(json.dumps(data,indent=2)+'\n').encode())
    files={}
    for p in sorted(stage.rglob('*')):
        if p.is_symlink():raise ValueError('unexpected symlink')
        if p.is_file() and p.relative_to(stage).as_posix() not in ('assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json'):
            files[p.relative_to(stage).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
    changed={name for name in set(files)|set(expected['files']) if files.get(name)!=expected['files'].get(name)}
    if any(name!='assets/desktop/apps.json' and not name.startswith('assets/desktop/apps/data-explorer/') for name in changed):raise ValueError('unrelated public file changed')
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
    print(json.dumps({'release':manifest['id'],'files':len(files),'data-explorer':BUNDLE}))

if __name__=='__main__':main()
