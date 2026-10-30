#!/usr/bin/env python3
"""Fetch immutable dependency review snapshots; installs/enables no runtime code."""
from pathlib import Path
import hashlib,json,tarfile,urllib.request
ROOT=Path(__file__).resolve().parent.parent
PINS=[('awslabs/mls-rs','64d4a430ed344d408ab9b115558ac2cd926bb70e',['mls-rs/README.md','LICENSE-apache','LICENSE-mit','mls-rs/Cargo.toml','mls-rs-crypto-webcrypto/Cargo.toml']),('libp2p/js-libp2p','d41cc9fdd9b92596246deba0d4b8ad0078adfc69',['README.md','LICENSE-APACHE','LICENSE-MIT','packages/kad-dht/package.json','packages/kad-dht/README.md'])]
cache=ROOT/'.build/dependency-review';cache.mkdir(parents=True,exist_ok=True)
EXPECTED={'awslabs/mls-rs':'35d9d533f692c9b05ac68f50c45f3558e005d3218b6519b52b8c99dfbe534c55','libp2p/js-libp2p':'263ad8098df3013c474f6ee3ebe54ac772d9f606a60baf34028cc7b50c613403'}
records=[]
for repo,commit,files in PINS:
    url=f'https://codeload.github.com/{repo}/tar.gz/{commit}'
    target=cache/(repo.split('/')[1]+'-'+commit+'.tar.gz')
    if not target.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'CodiServer-dependency-review'})
        with urllib.request.urlopen(req,timeout=60) as response:target.write_bytes(response.read(100*1024*1024))
    if hashlib.sha256(target.read_bytes()).hexdigest()!=EXPECTED[repo]:raise ValueError('Dependency archive hash mismatch')
    record={'repository':'https://github.com/'+repo,'commit':commit,'sourceUrl':url,'archiveSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'files':[],'runtimeEnabled':False}
    with tarfile.open(target) as archive:
        for suffix in files:
            matches=[m for m in archive.getmembers() if '/'.join(m.name.split('/')[1:])==suffix and m.isfile()]
            if len(matches)!=1:raise ValueError('Missing or ambiguous file '+suffix)
            content=archive.extractfile(matches[0]).read()
            out=cache/repo.split('/')[1]/suffix;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(content)
            record['files'].append({'path':suffix,'sha256':hashlib.sha256(content).hexdigest()})
    records.append(record)
(ROOT/'evidence/network-candidates.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps([{'repository':r['repository'],'commit':r['commit'],'archiveSha256':r['archiveSha256']} for r in records],indent=2))
