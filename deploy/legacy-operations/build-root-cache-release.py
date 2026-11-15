#!/usr/bin/env python3
"""Seal the mount-aware cache client over the current native16 artifact."""
import argparse,hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'.build/releases/connected-terminal-scroll-r2'
PIN='3071d17fa17666e2d9317e96e2e9a79d629e2a16be2e44b9afb0ed9947efd211'
OUTPUT=ROOT/'.build/releases/connected-root-cache-r1'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,indent=2)+'\n').encode()
def record(path):
    raw=path.read_bytes();return {'bytes':len(raw),'sha256':sha(raw)}
def key(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':')).encode())


def build():
    spec=importlib.util.spec_from_file_location('root_cache_contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(BASE)['manifestSHA256']==PIN
    assert not OUTPUT.exists();stage=Path(tempfile.mkdtemp(prefix='.root-cache-',dir=OUTPUT.parent));changed=set()
    try:
        shutil.copytree(BASE,stage,dirs_exist_ok=True)
        def put(name,data):
            assert contract.public_name(name),name
            p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);changed.add(name)
        client=(ROOT/'assets/desktop/device-cache.mjs').read_bytes();client_path='assets/desktop/device-cache-v2/'+sha(client)+'.mjs';put(client_path,client)
        graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());previous=graph['coreDirectory'];core={n:(BASE/previous/n).read_bytes() for n in graph['core']}
        text=core['app.js'].decode();anchor="new URL('assets/desktop/device-cache.mjs',document.baseURI)";assert text.count(anchor)==1
        core['app.js']=text.replace(anchor,"new URL('"+client_path+"',document.baseURI)").encode()
        graph['core']={n:{'bytes':len(raw),'sha256':sha(raw)} for n,raw in core.items()};folder='assets/desktop/core-v2/'+key(graph['core']);graph['coreDirectory']=folder
        for n,raw in core.items():put(folder+'/'+n,raw)
        put('assets/desktop/network-release.json',encoded(graph));put('index.html',(BASE/'index.html').read_text().replace(previous,folder).encode())
        cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted(set(cache['files'])|changed)};cache['id']=key(cache['files'])
        template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/cache-manifest.json',encoded(cache));put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
        public=json.loads((BASE/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted(set(public['files'])|changed)};(stage/'release.json').write_bytes(encoded(public))
        full=json.loads((BASE/'connected-release.json').read_bytes());before_public=json.loads((BASE/'release.json').read_bytes())['files'];native=set(full['files'])-set(before_public)-{'release.json'}
        for n in native:assert record(stage/n)==record(BASE/n)
        exceptions={'index.html','assets/desktop/network-release.json','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'}
        for n,r in before_public.items():
            if n not in exceptions:assert record(stage/n)==r
        full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(encoded(full))
        for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
        value=contract.verify(stage);stage.rename(OUTPUT)
        return value|{'directory':str(OUTPUT),'status':'PASS','baseManifestSHA256':PIN,'clientPath':client_path,'nativeFilesIdentical':len(native),'networkProtocolIdentical':True,'appsAndGuestImageIdentical':True,'oldPublicAssetsPreservedExcept':sorted(exceptions),'productionChanged':False}
    finally:
        if stage.exists():shutil.rmtree(stage)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=OUTPUT);args=parser.parse_args();OUTPUT=args.output.resolve();assert OUTPUT.is_relative_to(ROOT/'.build/releases')
    result=build();(ROOT/'.build/checks/root-cache-build-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
