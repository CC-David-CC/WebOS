#!/usr/bin/env python3
"""Seal explicit native20/37-module shared hosted client over frozen native19.

Preserves all old profile verifiers and private service state. Build only.
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
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/connected-checkpoint-native-r1'
PIN='440f0c19892cde73fe893c139a86d9163e729af9f37c41d5ecd5221bbbbcbe8a'
s=importlib.util.spec_from_file_location('hosted_client_build_tools',ROOT/'scripts/build-native-app-update.py');util=importlib.util.module_from_spec(s);s.loader.exec_module(util)
PROFILE='codi-connected-development/20'

def contract(path):
    s=importlib.util.spec_from_file_location('hosted_client_release_'+util.sha(str(path).encode()),path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def build(destination):
    previous=contract(BASE/'origin_service/release.py');assert previous.verify(BASE)['manifestSHA256']==PIN
    old_graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());old_modules=set(old_graph['modules']);modules=old_modules|{'hosted-room-client.mjs','hosted-room-store.mjs'}
    assert len(modules)==37 and {p.name for p in (ROOT/'network').glob('*.mjs')}==modules
    destination=Path(destination).resolve();assert not destination.exists() and destination.is_relative_to(ROOT/'.build/releases')
    stage=Path(tempfile.mkdtemp(prefix='.hosted-client-native-',dir=destination.parent));new=set()
    try:
        shutil.copytree(BASE,stage,dirs_exist_ok=True)
        def put(name,raw):
            assert previous.public_name(name),name;p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw if isinstance(raw,bytes) else raw.encode());new.add(name)
        sources={n:(ROOT/'network'/n).read_text() for n in sorted(modules)}
        sources['chess-record.mjs']=sources['chess-record.mjs'].replace('../assets/vendor/chess/chess.mjs','../../../vendor/chess/chess.mjs')
        for name,text in sources.items():
            if name=='gossip-vendor.mjs':continue
            for _,target in re.findall(r"(?:\bfrom\s+|\bimport\s*\(|new URL\s*\()(['\"])(.*?)\1",text):assert target.startswith('./') and target[2:] in modules or name=='chess-record.mjs' and target=='../../../vendor/chess/chess.mjs',(name,target)
        records={n:{'bytes':len(t.encode()),'sha256':util.sha(t.encode())} for n,t in sources.items()};folder='assets/desktop/network-v6/'+util.key(records)
        for name,text in sources.items():put(folder+'/'+name,text)
        old_core=old_graph['coreDirectory'];core={n:(BASE/old_core/n).read_text() for n in old_graph['core']}
        core['networking.js']=(ROOT/'networking.js').read_text()
        core['networking.js']=re.sub(r"import\((['\"])\./([^'\"]+)\1\)",lambda m:'import(new URL('+repr(m[2])+',document.baseURI))',core['networking.js'])
        core['networking.js']=re.sub(r"(['\"])network/([^'\"?]+)(?:\?[^'\"]*)?\1",lambda m:repr(folder+'/'+m[2]),core['networking.js'])
        core['app.js']=core['app.js'].replace(old_graph['directory']+'/',folder+'/')
        # The frozen host predates hosted chat. Preserve its existing account
        # archive behavior while including this new per-window unsent draft.
        selector='[data-chat-draft],[data-mesh-draft],[data-routed-draft],'
        assert core['app.js'].count(selector)==1
        core['app.js']=core['app.js'].replace(selector,selector+'[data-hosted-draft],')
        core_records={n:{'bytes':len(t.encode()),'sha256':util.sha(t.encode())} for n,t in core.items()};host='assets/desktop/core-v6/'+util.key(core_records)
        for name,text in core.items():put(host+'/'+name,text)
        put('index.html',(BASE/'index.html').read_text().replace(old_core,host))
        put('assets/desktop/network-release.json',util.encoded({'version':'codi-network-release/5','profile':'codi-public-mesh/4','automaticNeighbors':'codi-peer-introductions/1','membershipLease':'codi-mesh-room-lease/1','hostedAuthority':'codi-hosted-room/1','hostedClient':'codi-hosted-client/1','modules':records,'directory':folder,'core':core_records,'coreDirectory':host}))
        def change(name,fn):
            p=stage/name;old=p.read_text();text=fn(old);assert text!=old,name;p.write_text(text)
        def extend(text):
            assert "'codi-connected-development/19')" in text
            return text.replace("'codi-connected-development/19')","'codi-connected-development/19','codi-connected-development/20')")
        def verifier(text):
            graph='\ndef verify_hosted_client_graph('+text.split('\ndef verify_hosted_graph(',1)[1]
            graph=graph.replace("'membershipLease','hostedAuthority'}","'membershipLease','hostedAuthority','hostedClient'}").replace("metadata['version']!='codi-network-release/4'","metadata['version']!='codi-network-release/5' or metadata['hostedClient']!='codi-hosted-client/1'")
            graph=graph.replace('expected=frozenset('+repr(sorted(old_modules))+')','expected=frozenset('+repr(sorted(modules))+')').replace('assets/desktop/network-v5/','assets/desktop/network-v6/').replace('assets/desktop/core-v5/','assets/desktop/core-v6/')
            assert 'hosted-room-client.mjs' in graph and 'hostedClient' in graph
            text=text.replace('range(1,20)','range(1,21)').replace("'codi-connected-development/19':V19_NATIVE}","'codi-connected-development/19':V19_NATIVE,'codi-connected-development/20':V19_NATIVE}")
            anchor=" if manifest['version']=='codi-connected-development/19':verify_hosted_graph(directory,frontend)";assert text.count(anchor)==1
            return text.replace(anchor,anchor+"\n if manifest['version']=='codi-connected-development/20':verify_hosted_client_graph(directory,frontend)")+graph
        change('origin_service/release.py',verifier)
        def operator(text):
            text=extend(text).replace('profile-5..19','profile-5..20')
            anchor="profile!='codi-connected-development/19'";assert text.count(anchor)==1;text=text.replace(anchor,"profile not in ('codi-connected-development/19','codi-connected-development/20')")
            anchor="['version']=='codi-connected-development/19':command+=['--mesh-leased-groups']";assert text.count(anchor)==1
            return text.replace(anchor,"['version'] in ('codi-connected-development/19','codi-connected-development/20'):command+=['--mesh-leased-groups']")
        change('scripts/manage-services.py',operator);change('origin_service/deployment.py',extend);change('origin_service/turn_management.py',extend)
        (stage/'room_service/contract.py').write_bytes((ROOT/'room_service/contract.py').read_bytes())
        cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:util.record(stage/n) for n in sorted(set(cache['files'])|new)};cache['id']=util.key(cache['files'])
        put('assets/desktop/cache-manifest.json',util.encoded(cache));template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))))
        public=json.loads((BASE/'release.json').read_bytes());public['files']={n:util.record(stage/n) for n in sorted(set(public['files'])|new)};(stage/'release.json').write_bytes(util.encoded(public))
        full=json.loads((BASE/'connected-release.json').read_bytes());full['version']=PROFILE;full['files']={str(p.relative_to(stage)):util.record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(util.encoded(full))
        verified=contract(stage/'origin_service/release.py').verify(stage)
        changed=[n for n in sorted(previous.V19_NATIVE) if util.record(BASE/n)!=util.record(stage/n)]
        assert set(changed)=={'origin_service/release.py','origin_service/deployment.py','origin_service/turn_management.py','scripts/manage-services.py','room_service/contract.py'}
        stage.rename(destination);return {'status':'PASS','version':PROFILE,'directory':str(destination),'manifestSHA256':verified['manifestSHA256'],'files':verified['files'],'networkModules':37,'nativeFiles':len(previous.V19_NATIVE),'nativeChanged':changed,'installed':False}
    finally:
        if stage.exists():shutil.rmtree(stage)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output),indent=2))
