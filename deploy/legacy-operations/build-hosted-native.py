#!/usr/bin/env python3
"""Seal native19: explicit35-module /4 graph and opt-in hosted authority issuer binding.

Frozen native18/33 and native17/32 verifiers remain unchanged. This builds code
only; no keys, private room state, installation or native policy changes.
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
spec=importlib.util.spec_from_file_location('hosted_native_base',ROOT/'scripts/build-neighbor-native.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
util=base.util
BASE=ROOT/'.build/releases/connected-neighbor-native-r1'
PIN='5ee491cc01f314580ec85ccf940f9e6e1944159c1a29e907e66dd738283fd024'
PROFILE='codi-connected-development/19'
MODULES=base.MODULES|{'mesh-lease-control.mjs','hosted-room-authority.mjs'}
ADDED={'origin_service/room_authority.py','origin_service/room_management.py','room_service/__init__.py','room_service/contract.py'}
NATIVE_CHANGED=util.NATIVE_CHANGES|{'origin_service/maintenance.py'}
record,encoded,key=util.record,util.encoded,util.key
GRAPH=util.GRAPH_VERIFIER.replace('def verify_mesh_graph(','def verify_hosted_graph(').replace(
    "{'version','profile','modules','directory','core','coreDirectory'}","{'version','profile','modules','directory','core','coreDirectory','automaticNeighbors','membershipLease','hostedAuthority'}").replace(
    "metadata['version']!='codi-network-release/2'","metadata['version']!='codi-network-release/4' or metadata['automaticNeighbors']!='codi-peer-introductions/1' or metadata['membershipLease']!='codi-mesh-room-lease/1' or metadata['hostedAuthority']!='codi-hosted-room/1'").replace(
    "metadata['profile']!='codi-public-mesh/3'","metadata['profile']!='codi-public-mesh/4'").replace(
    'expected=frozenset('+repr(sorted(util.MODULES))+')','expected=frozenset('+repr(sorted(MODULES))+')').replace('assets/desktop/network-v3/','assets/desktop/network-v5/').replace('assets/desktop/core-v3/','assets/desktop/core-v5/')
assert len(MODULES)==35 and 'hosted-room-authority.mjs' in GRAPH

def patch_native(stage):
    def change(name,fn):
        p=stage/name;before=p.read_text();after=fn(before);assert after!=before,name;p.write_text(after)
    def extend(text):
        assert "'codi-connected-development/18')" in text
        return text.replace("'codi-connected-development/18')","'codi-connected-development/18','codi-connected-development/19')")
    def verifier(text):
        assert text.count('range(1,19)')==1 and text.count("'codi-connected-development/18':V15_NATIVE}")==1
        text=text.replace('NATIVE=V15_NATIVE',"V19_NATIVE=frozenset(V15_NATIVE|set("+repr(sorted(ADDED))+"))\nNATIVE=V15_NATIVE")
        text=text.replace('range(1,19)','range(1,20)').replace("'codi-connected-development/18':V15_NATIVE}","'codi-connected-development/18':V15_NATIVE,'codi-connected-development/19':V19_NATIVE}")
        anchor=" if manifest['version']=='codi-connected-development/18':verify_neighbor_graph(directory,frontend)";assert text.count(anchor)==1
        return text.replace(anchor,anchor+"\n if manifest['version']=='codi-connected-development/19':verify_hosted_graph(directory,frontend)")+GRAPH
    change('origin_service/release.py',verifier)
    def operator(text):
        text=extend(text).replace('profile-5..18','profile-5..19')
        anchor=" if record['manifestSHA256']!=config['manifestSHA256']:raise ValueError('Pinned release manifest changed')";assert text.count(anchor)==1
        text=text.replace(anchor," if 'hostedRooms' in config:\n  if profile!='codi-connected-development/19':raise ValueError('Disable hosted rooms before rolling code below native19')\n  from origin_service import room_management\n  room_management.validate(sys.modules[__name__],config)\n"+anchor)
        anchor="  if role=='issuer' and config.get('userFiles'):command+=['--user-files']";assert text.count(anchor)==1
        text=text.replace(anchor,"  if role=='issuer' and json.loads((source/'connected-release.json').read_text())['version']=='codi-connected-development/19':command+=['--mesh-leased-groups']\n  if role=='issuer' and config.get('hostedRooms'):\n   from origin_service import room_management\n   manager,backend=room_management.validate(sys.modules[__name__],config)\n   command+=['--hosted-room-policy',manager.folder/'controller-policy.json','--hosted-room-policy-sha256',backend['controllerPolicySHA256']]\n"+anchor)
        anchor=" if set(config)!=expected or config['authorityClass']!='development'";assert text.count(anchor)==1
        text=text.replace(anchor," if 'hostedRooms' in config:expected.add('hostedRooms')\n"+anchor)
        anchor=' if verify_installation:\n  installed(config)';assert text.count(anchor)==1
        text=text.replace(anchor," if 'hostedRooms' in config:\n  from origin_service import room_management\n  room_management.validate(sys.modules[__name__],config,read_inputs=False)\n"+anchor)
        anchor='    files_management.ready(sys.modules[__name__],config)';assert text.count(anchor)==1
        text=text.replace(anchor,anchor+'\n    from origin_service import room_management\n    room_management.ready(sys.modules[__name__],config)')
        anchor="'migrate-guest-signin','recover-guest-signin']:";assert text.count(anchor)==1
        text=text.replace(anchor,"'migrate-guest-signin','recover-guest-signin','configure-hosted-rooms']:")
        anchor="  if name=='configure-guest-network':";assert text.count(anchor)==1
        text=text.replace(anchor,"  if name=='configure-hosted-rooms':\n   cmd.add_argument('--disable',action='store_true');cmd.add_argument('--room-config',type=Path);cmd.add_argument('--room-operator',type=Path)\n"+anchor)
        text=text.replace("args.action in ('configure-user-files','configure-guest-network') and args.disable","args.action in ('configure-user-files','configure-guest-network','configure-hosted-rooms') and args.disable")
        anchor="    elif args.action=='configure-guest-network':";assert text.count(anchor)==1
        text=text.replace(anchor,"    elif args.action=='configure-hosted-rooms':\n     from origin_service import room_management\n     if args.disable and (args.room_config or args.room_operator):raise ValueError('Disable cannot configure another room backend')\n     if not args.disable and (args.room_config is None or args.room_operator is None):raise ValueError('Explicit installed room config/operator required')\n     value=None if args.disable else room_management.policy(sys.modules[__name__],args.room_config,args.room_operator)\n     result=room_management.configure(sys.modules[__name__],config,args.config,value)\n"+anchor)
        return text
    change('scripts/manage-services.py',operator)
    change('origin_service/deployment.py',extend);change('origin_service/turn_management.py',extend)
    def maintenance(text):
        anchor=" if initial.get('version')=='codi-files-transition/1':";assert text.count(anchor)==1
        return text.replace(anchor," if initial.get('version')=='codi-hosted-rooms-transition/1':\n  from origin_service import room_management\n  return room_management.recover(op,config,config_path)\n"+anchor)
    change('origin_service/maintenance.py',maintenance)
    def issuer(text):
        anchor="    public_groups.add_argument('--mesh-auto-neighbors',action='store_true',help='Enable bounded mesh3 peer introductions on the shared pool')";assert text.count(anchor)==1
        text=text.replace(anchor,anchor+"\n    public_groups.add_argument('--mesh-leased-groups',action='store_true',help='Enable explicit mesh4 renewable membership on the shared pool')\n    p.add_argument('--hosted-room-policy',type=Path)\n    p.add_argument('--hosted-room-policy-sha256')")
        anchor="    if bool(a.discovery_policy)!=bool(a.discovery_bundle):p.error('Discovery policy and public bundle must be configured together')";assert text.count(anchor)==1
        text=text.replace(anchor,anchor+"\n    if bool(a.hosted_room_policy)!=bool(a.hosted_room_policy_sha256):p.error('Hosted room public policy and exact digest required together')")
        anchor='            source=None';assert text.count(anchor)==1
        text=text.replace(anchor,anchor+"\n            room_key=None\n            if a.hosted_room_policy is not None:\n                from origin_service.room_authority import load_controller_policy\n                room_key=load_controller_policy(a.hosted_room_policy,a.hosted_room_policy_sha256,origin,a.base_path)")
        anchor="                    if a.mesh_auto_neighbors:config['meshGroups']={'version':'codi-public-mesh/3','automaticNeighbors':'codi-peer-introductions/1'}";assert text.count(anchor)==1
        text=text.replace(anchor,anchor+"\n                    if a.mesh_leased_groups:config['meshGroups']={'version':'codi-public-mesh/4','automaticNeighbors':'codi-peer-introductions/1','membershipLease':'codi-mesh-room-lease/1'}\n                    if room_key is not None:config['hostedRooms']={'version':'codi-hosted-room/1','basePath':a.base_path+'/rooms','controllerKey':room_key,'certificatePath':a.base_path+'/api/v1/room-control/controller','challengePath':a.base_path+'/api/v1/room-control/challenge','authorizePath':a.base_path+'/api/v1/room-control/authorize'}")
        anchor="            with make_server('127.0.0.1',a.port,HeadSupport(application),server_class=BoundedServer,handler_class=Quiet) as server:";assert text.count(anchor)==1
        return text.replace(anchor,"            if room_key is not None:\n                from origin_service.room_authority import RoomAuthority\n                application=RoomAuthority(service,room_key,application)\n"+anchor)
    change('scripts/serve-connected.py',issuer)
    for name in ADDED:
        p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())

def build(destination):
    previous=util.contract(BASE/'origin_service/release.py');assert previous.verify(BASE)['manifestSHA256']==PIN
    destination=Path(destination).resolve();assert not destination.exists() and destination.is_relative_to(ROOT/'.build/releases')
    stage=Path(tempfile.mkdtemp(prefix='.hosted-native-',dir=destination.parent));changed=set()
    try:
        shutil.copytree(BASE,stage,dirs_exist_ok=True)
        def put(name,raw):
            assert previous.public_name(name);p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw if isinstance(raw,bytes) else raw.encode());changed.add(name)
        assert {p.name for p in (ROOT/'network').glob('*.mjs')}==MODULES
        sources={n:(ROOT/'network'/n).read_text() for n in sorted(MODULES)}
        assert sources['chess-record.mjs'].count('../assets/vendor/chess/chess.mjs')==1;sources['chess-record.mjs']=sources['chess-record.mjs'].replace('../assets/vendor/chess/chess.mjs','../../../vendor/chess/chess.mjs')
        for name,text in sources.items():
            if name=='gossip-vendor.mjs':continue
            for _,target in re.findall(r"(?:\bfrom\s+|\bimport\s*\(|new URL\s*\()(['\"])(.*?)\1",text):assert target.startswith('./') and target[2:] in MODULES or name=='chess-record.mjs' and target=='../../../vendor/chess/chess.mjs',(name,target)
        records={n:{'bytes':len(t.encode()),'sha256':util.sha(t.encode())} for n,t in sources.items()};folder='assets/desktop/network-v5/'+key(records)
        vendor=json.loads((ROOT/'assets/vendor/gossip/manifest.json').read_bytes());assert record(ROOT/'network/gossip-vendor.mjs')==vendor['output']
        for name,text in sources.items():put(folder+'/'+name,text)
        graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());old_host=graph['coreDirectory'];core={n:(BASE/old_host/n).read_text() for n in graph['core']}
        core['networking.js']=(ROOT/'networking.js').read_text()
        core['networking.js']=re.sub(r"import\((['\"])\./([^'\"]+)\1\)",lambda m:'import(new URL('+repr(m[2])+',document.baseURI))',core['networking.js'])
        core['networking.js']=re.sub(r"(['\"])network/([^'\"?]+)(?:\?[^'\"]*)?\1",lambda m:repr(folder+'/'+m[2]),core['networking.js'])
        core['app.js']=core['app.js'].replace(graph['directory']+'/',folder+'/')
        records_core={n:{'bytes':len(t.encode()),'sha256':util.sha(t.encode())} for n,t in core.items()};host='assets/desktop/core-v5/'+key(records_core)
        for name,text in core.items():put(host+'/'+name,text)
        put('index.html',(BASE/'index.html').read_text().replace(old_host,host))
        put('assets/desktop/network-release.json',encoded({'version':'codi-network-release/4','profile':'codi-public-mesh/4','automaticNeighbors':'codi-peer-introductions/1','membershipLease':'codi-mesh-room-lease/1','hostedAuthority':'codi-hosted-room/1','modules':records,'directory':folder,'core':records_core,'coreDirectory':host}))
        patch_native(stage)
        cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted(set(cache['files'])|changed)};cache['id']=key(cache['files'])
        template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();assert template.count('__PUBLIC_CACHE_MANIFEST__')==1
        put('assets/desktop/cache-manifest.json',encoded(cache));put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))))
        public=json.loads((BASE/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted(set(public['files'])|changed)};(stage/'release.json').write_bytes(encoded(public))
        full=json.loads((BASE/'connected-release.json').read_bytes());full['version']=PROFILE;full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(encoded(full))
        assert {n for n in previous.V15_NATIVE if record(stage/n)!=record(BASE/n)}==NATIVE_CHANGED
        current=util.contract(stage/'origin_service/release.py');verified=current.verify(stage)
        shutil.move(stage,destination);return {'status':'PASS','version':PROFILE,'directory':str(destination),'manifestSHA256':verified['manifestSHA256'],'files':verified['files'],'networkModules':len(MODULES),'nativeAdded':sorted(ADDED),'nativeChanged':sorted(NATIVE_CHANGED),'installed':False}
    finally:
        if stage.exists():shutil.rmtree(stage)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output),indent=2))
