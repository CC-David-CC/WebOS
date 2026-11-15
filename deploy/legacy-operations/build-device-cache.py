#!/usr/bin/env python3
"""Pin only exported public code/boot/model assets; exclude all live API state."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from serve import PUBLIC,NETWORK,RUNTIME
EXCLUDE={'assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json','config.json'}
def build():
    files={name:ROOT/name for name in PUBLIC if name not in EXCLUDE}
    files.update({'network/'+name:ROOT/'network'/name for name in NETWORK})
    files.update({'.build/v86/'+name:ROOT/'.build/v86'/name for name in RUNTIME})
    for path in (ROOT/'assets').rglob('*'):
        if path.is_symlink():raise ValueError('Symlink in public cache inputs')
        if path.is_dir():continue
        name=str(path.relative_to(ROOT))
        if name in EXCLUDE:continue
        if path.suffix.lower() in {'.pem','.key','.db','.sqlite','.sqlite3','.py','.env'} or any(p.startswith('.') for p in path.relative_to(ROOT/'assets').parts):raise ValueError('Nonpublic cache input')
        files[name]=path
    records={}
    for name,path in sorted(files.items()):
        if path.is_symlink() or not path.is_file():raise ValueError('Real public file required')
        records[name]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    key=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    manifest={'version':'codi-public-cache/1','id':key,'files':records}
    template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();assert template.count('__PUBLIC_CACHE_MANIFEST__')==1
    (ROOT/'assets/desktop/offline-worker.js').write_text(template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(manifest,separators=(',',':'))))
    (ROOT/'assets/desktop/cache-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return {'status':'PASS','version':manifest['version'],'id':key,'files':len(records),'totalPublicBytes':sum(v['bytes'] for v in records.values()),'userDataCached':False}
if __name__=='__main__':print(json.dumps(build(),indent=2))
