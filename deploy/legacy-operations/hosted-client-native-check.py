#!/usr/bin/env python3
"""Verify native20's explicit shared-client graph and preserved older contracts."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT=Path(__file__).resolve().parents[1]
def module(path):
    s=importlib.util.spec_from_file_location('client_release_contract_'+hashlib.sha256(str(path).encode()).hexdigest(),path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run(release):
    checks=[];v={'status':'FAIL','scope':__doc__,'checks':checks,'installed':False}
    def check(name,ok):assert ok,name;checks.append(name)
    def refused(fn):
        try:fn()
        except (ValueError,KeyError,FileNotFoundError):return True
        raise AssertionError('Expected graph refusal')
    try:
        c=module(release/'origin_service/release.py');verified=c.verify(release);manifest=json.loads((release/'connected-release.json').read_bytes());g=json.loads((release/'assets/desktop/network-release.json').read_bytes());p=json.loads((release/'release.json').read_bytes())
        check('native20 complete release verifies37modules and57native files',manifest['version']=='codi-connected-development/20' and len(g['modules'])==37 and len(c.V19_NATIVE)==57)
        check('explicit shared client and persistent store are hashed graph members',g['version']=='codi-network-release/5' and g['hostedClient']=='codi-hosted-client/1' and {'hosted-room-client.mjs','hosted-room-store.mjs'}<=set(g['modules']))
        for name in ['hosted-room-client.mjs','hosted-room-store.mjs','hosted-room-authority.mjs']:assert g['modules'][name]['sha256']==hashlib.sha256((ROOT/'network'/name).read_bytes()).hexdigest()
        check('shared client store and verifier are the tested source bytes',True)
        for name,pin in [('connected-checkpoint-native-r1','440f0c19892cde73fe893c139a86d9163e729af9f37c41d5ecd5221bbbbcbe8a'),('connected-neighbor-native-r1','5ee491cc01f314580ec85ccf940f9e6e1944159c1a29e907e66dd738283fd024'),('connected-mesh-native-r1','8a90a16ecab32e897f5cd811c6e3aadedcaf574d47debedf9338659346546bdb')]:
            old=ROOT/'.build/releases'/name;check('native20 preserves original '+name+' verification contract',c.verify(old)['manifestSHA256']==pin)
        check('older mesh graph validators refuse the new client profile',all(refused(lambda fn=fn:fn(release,p)) for fn in [c.verify_mesh_graph,c.verify_neighbor_graph,c.verify_hosted_graph]))
        with tempfile.TemporaryDirectory(prefix='codi-client-graph-') as temporary:
            d=Path(temporary)
            for name in ['index.html','assets/desktop/network-release.json','assets/vendor/gossip/manifest.json','assets/vendor/gossip/LICENSES.txt']:
                out=d/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(release/name,out)
            for folder in [g['directory'],g['coreDirectory']]:shutil.copytree(release/folder,d/folder)
            for name,change in [('wrong-version',lambda x:x.update(version='codi-network-release/4')),('wrong-client',lambda x:x.update(hostedClient='implicit')),('missing-store',lambda x:x['modules'].pop('hosted-room-store.mjs')),('extra-module',lambda x:x['modules'].update({'unexpected.mjs':next(iter(x['modules'].values()))})),('wrong-directory',lambda x:x.update(directory='assets/desktop/network-v6/'+'0'*64))]:
                x=json.loads(json.dumps(g));change(x);(d/'assets/desktop/network-release.json').write_text(json.dumps(x));check('client graph refuses '+name,refused(lambda:c.verify_hosted_client_graph(d,p)))
        check('private worker and persisted browser data are never public paths',all(not c.public_name(n) for n in ['room_service/store.py','rooms.sqlite3','controller.pem','assets/state/controller.pem','positions.sqlite3']))
        # The normal app pipeline retained all seven app identities and bundled
        # the updated Rooms siblings/CSS; no special terminal/app loader path.
        host=(release/g['coreDirectory']/'desktop-apps.js').read_text();import re
        loader=re.search(r'assets/desktop/apps-v2-[a-f0-9]{64}\.mjs',host)[0];catalog_name=re.search(r'apps-v2-[a-f0-9]{64}\.json',(release/loader).read_text())[0]
        catalog=json.loads((release/'assets/desktop'/catalog_name).read_bytes());rooms=next(a for a in catalog['apps'] if a['id']=='rooms');body=(release/rooms['path']).read_text()
        check('generic seven-app catalog contains the compiled hosted Rooms view',len(catalog['apps'])==7 and 'hostedRooms' in body and 'hostedCreate' in body and 'Saved public chat' in body and bool(rooms['styles']))
        archive=(release/g['coreDirectory']/'app.js').read_text()
        check('identity archive includes hosted drafts alongside older chat drafts',
              '[data-chat-draft],[data-mesh-draft],[data-routed-draft],[data-hosted-draft],' in archive)
        v.update(status='PASS',manifestSHA256=verified['manifestSHA256'],files=verified['files'],networkModules=37,nativeFiles=57,roomBundleSHA256=rooms['bundleSHA256'])
    except Exception as error:
        import traceback;v.update(error=str(error),traceback=traceback.format_exc())
    v['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();return v

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.release.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
