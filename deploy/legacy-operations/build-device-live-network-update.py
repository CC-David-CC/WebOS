#!/usr/bin/env python3
"""Update a current, pinned closed network graph without changing native code.

Builds from the supplied current release, never a chain of obsolete expanded
versions. Replaces generated network/core graphs and drops their obsolete public
cache records. The existing release validator remains byte-identical.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def build(base,pin,destination,core_sources=(),shared_services=(),additional_network_modules=(),bundled_network_modules=(),bundled_service_proofs=()):
    util=module('network_update_records',ROOT/'scripts/build-native-app-update.py')
    contract=module('network_update_contract',base/'origin_service/release.py')
    assert contract.verify(base)['manifestSHA256']==pin
    old=json.loads((base/'assets/desktop/network-release.json').read_bytes())
    assert old['version']=='codi-network-release/9'
    prior=set(old['modules']);current={p.name for p in (ROOT/'network').glob('*.mjs')};additional=list(additional_network_modules);bundled=list(bundled_network_modules)
    assert len(additional)==len(set(additional)) and len(bundled)==len(set(bundled)) and all(re.fullmatch(r'[a-z][a-z0-9-]*[.]mjs',n) for n in additional+bundled)
    assert not prior.intersection(additional+bundled) and not set(additional).intersection(bundled) and prior.issubset(current) and current-prior==set(additional)|set(bundled),'Network additions must be explicitly reviewed; existing modules cannot disappear'
    assert not additional,'The pinned release validator cannot admit standalone network additions; update its contract or use a reviewed bundle'
    # Bundled-only modules are not published as loose network files. Require a
    # matching supplied service artifact and its build receipt to cover them.
    service_hashes={json.loads((Path(p)/'shared-service.json').read_bytes())['files']['index.mjs']['sha256'] for p in shared_services}
    covered=set()
    for receipt in bundled_service_proofs:
        receipt=Path(receipt);assert receipt.is_file() and not receipt.is_symlink()
        value=json.loads(receipt.read_bytes());assert value['status']=='PASS' and value['compiledSHA256'] in service_hashes and isinstance(value['publicInputs'],list) and isinstance(value.get('sourceSHA256'),dict)
        for name in bundled:
            source='network/'+name
            if source in value['publicInputs']:
                assert value['sourceSHA256'].get(source)==util.sha((ROOT/source).read_bytes()),'Bundled source differs from the reviewed build'
                covered.add(name)
    assert set(bundled).issubset(covered),'Bundled-only network modules require matching shared-service build receipts'
    destination=destination.resolve();assert not destination.exists() and destination.is_relative_to(ROOT/'.build/releases')
    stage=Path(tempfile.mkdtemp(prefix='.network-update-',dir=destination.parent));new=set();removed=set()
    try:
        shutil.copytree(base,stage,dirs_exist_ok=True)
        # Current entrypoint, core and network are rebuilt below. No active app
        # bundle imports a previous generated core/network graph.
        obsolete=[p for p in (stage/'assets/desktop').iterdir() if p.is_dir() and re.fullmatch(r'(?:core|network)-v\d+',p.name)]
        for folder in obsolete:
            removed.update(str(p.relative_to(stage)) for p in folder.rglob('*') if p.is_file());shutil.rmtree(folder)
        def put(name,data):
            assert contract.public_name(name),name
            path=stage/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data if isinstance(data,bytes) else data.encode());new.add(name)
        sources={n:(ROOT/'network'/n).read_text() for n in sorted(prior|set(additional))}
        sources['chess-record.mjs']=sources['chess-record.mjs'].replace('../assets/vendor/chess/chess.mjs','../../../vendor/chess/chess.mjs')
        for name,text in sources.items():
            if name=='gossip-vendor.mjs':continue
            for _,target in re.findall(r"(?:\bfrom\s+|\bimport\s*\(|new URL\s*\()(['\"])(.*?)\1",text):
                assert target.startswith('./') and target[2:] in sources or name=='chess-record.mjs' and target=='../../../vendor/chess/chess.mjs',(name,target)
        records={n:{'bytes':len(t.encode()),'sha256':util.sha(t.encode())} for n,t in sources.items()}
        folder='assets/desktop/network-v10/'+util.key(records)
        for name,text in sources.items():put(folder+'/'+name,text)
        core={n:(base/old['coreDirectory']/n).read_text() for n in old['core']}
        assert set(core_sources)<=set(core)-{'networking.js'}
        active_loader=re.search(r'assets/desktop/apps-v2-[a-f0-9]{64}[.]mjs',core['desktop-apps.js'])[0]
        aliases={'assets/desktop/apps.mjs':active_loader}
        registry_name='assets/desktop/shared-services.json';registry_file=base/registry_name
        registry=json.loads(registry_file.read_bytes()) if registry_file.exists() else {'version':'codi-host-services/1','services':[]}
        assert set(registry)=={'version','services'} and registry['version']=='codi-host-services/1'
        service_records={value['name']:value for value in registry['services']};service_replacements={}
        assert len(service_records)==len(registry['services'])
        for service in shared_services:
            service=Path(service).resolve();manifest=json.loads((service/'shared-service.json').read_bytes())
            assert set(manifest)=={'version','name','sourceAlias','path','files'} and manifest['version']=='codi-shared-service/1'
            alias=manifest['sourceAlias'];entry=manifest['path'];prefix=Path(entry).parent
            assert contract.public_name(alias) and alias not in aliases and str(prefix).startswith('assets/desktop/services/') and entry.endswith('/index.mjs')
            assert contract.public_name(entry) and re.fullmatch(r'assets/desktop/services/[a-z][a-z0-9-]{0,31}/[a-f0-9]{64}',str(prefix))
            assert {str(p.relative_to(service)) for p in service.rglob('*') if p.is_file()}=={str(prefix/n) for n in manifest['files']}|{'shared-service.json'}
            for n,r in manifest['files'].items():
                path=service/prefix/n;assert not path.is_symlink() and util.record(path)==r
                put(str(prefix/n),path.read_bytes())
            previous=service_records.get(manifest['name'])
            if previous and previous['path']!=entry:
                service_replacements[previous['path']]=entry;old_prefix=Path(previous['path']).parent
                for n in previous['files']:
                    path=stage/old_prefix/n;assert path.is_relative_to(stage/'assets/desktop/services')
                    if path.is_file():removed.add(str(path.relative_to(stage)));path.unlink()
            service_records[manifest['name']]=manifest;aliases[alias]=entry
        if shared_services:put(registry_name,util.encoded({'version':registry['version'],'services':[service_records[name] for name in sorted(service_records)]}))
        for name in {'networking.js',*core_sources}:
            text=(ROOT/'.build/candidates/device-live-networking.js' if name=='networking.js' else ROOT/name).read_text()
            text=re.sub(r"import\((['\"])\./([^'\"]+)\1\)",lambda m:'import(new URL('+repr(aliases.get(m[2],m[2]))+',document.baseURI))',text)
            text=re.sub(r"(['\"])network/([^'\"?]+)(?:\?[^'\"]*)?\1",lambda m:repr(folder+'/'+m[2]),text)
            core[name]=text
        for name,text in core.items():
            for before,after in service_replacements.items():text=text.replace(before,after)
            core[name]=text
        core['app.js']=core['app.js'].replace(old['directory']+'/',folder+'/')
        for name,text in core.items():
            for _,target in re.findall(r"import\(new URL\((['\"])([^'\"]+)\1,\s*document[.]baseURI\)\)",text):
                target=target.split('?',1)[0]
                assert contract.public_name(target) and (stage/target).is_file(),('Unbound host import',name,target)
        core_records={n:{'bytes':len(t.encode()),'sha256':util.sha(t.encode())} for n,t in core.items()}
        host='assets/desktop/core-v10/'+util.key(core_records)
        for name,text in core.items():put(host+'/'+name,text)
        put('index.html',(base/'index.html').read_text().replace(old['coreDirectory'],host))
        put('assets/desktop/network-release.json',util.encoded({**old,'modules':records,'directory':folder,'core':core_records,'coreDirectory':host}))
        for name in list(new):
            if name.endswith(('.mjs','.js','.html')):
                text=(stage/name).read_text()
                assert not any(prefix+'/' in text for prefix in [str(p.relative_to(stage)) for p in obsolete] if prefix not in [str(Path(folder).parent),str(Path(host).parent)]),name
        cache=json.loads((base/'assets/desktop/cache-manifest.json').read_bytes())
        cache['files']={n:util.record(stage/n) for n in sorted((set(cache['files'])-removed)|new)};cache['id']=util.key(cache['files'])
        put('assets/desktop/cache-manifest.json',util.encoded(cache))
        template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))))
        public=json.loads((base/'release.json').read_bytes());public['files']={n:util.record(stage/n) for n in sorted((set(public['files'])-removed)|new)}
        (stage/'release.json').write_bytes(util.encoded(public))
        full=json.loads((base/'connected-release.json').read_bytes());native=set(full['files'])-set(json.loads((base/'release.json').read_bytes())['files'])-{'release.json'}
        assert all(util.record(stage/n)==full['files'][n] for n in native)
        full['files']={str(p.relative_to(stage)):util.record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'}
        (stage/'connected-release.json').write_bytes(util.encoded(full))
        for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
        result=contract.verify(stage);stage.rename(destination)
        return {**result,'status':'PASS','directory':str(destination),'baseManifestSHA256':pin,'nativeFilesUnchanged':len(native),'networkModules':len(records),'additionalNetworkModules':sorted(additional),'bundledOnlyNetworkModules':sorted(bundled),'removedObsoleteGraphFiles':len(removed-new)}
    finally:
        if stage.exists():shutil.rmtree(stage)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-release',type=Path,required=True);p.add_argument('--base-manifest-sha256',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--core-sources',nargs='*',choices=['desktop-apps.js','app.js','reference.js','terminal.js'],default=[]);p.add_argument('--shared-services',nargs='*',type=Path,default=[]);p.add_argument('--additional-network-modules',nargs='*',default=[]);p.add_argument('--bundled-network-modules',nargs='*',default=[]);p.add_argument('--bundled-service-proofs',nargs='*',type=Path,default=[]);a=p.parse_args()
    print(json.dumps(build(a.base_release.resolve(),a.base_manifest_sha256,a.output,a.core_sources,a.shared_services,a.additional_network_modules,a.bundled_network_modules,a.bundled_service_proofs),indent=2))
