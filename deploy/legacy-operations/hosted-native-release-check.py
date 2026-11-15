#!/usr/bin/env python3
"""Check the sealed native19 graph, role boundaries and preserved older release contracts."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('hosted_contract_build',ROOT/'scripts/build-hosted-native.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

def run(release):
    checks=[];result={'status':'FAIL','scope':__doc__,'productionChanged':False,'privateVMChanged':False,'checks':checks}
    def check(name,value):assert value,name;checks.append(name)
    def denied(fn):
        try:fn()
        except ValueError:return True
        raise AssertionError('Expected refusal')
    try:
        contract=builder.util.contract(release/'origin_service/release.py');v=contract.verify(release)
        m=json.loads((release/'connected-release.json').read_bytes());p=json.loads((release/'release.json').read_bytes());graph=json.loads((release/'assets/desktop/network-release.json').read_bytes())
        check('native19 seals the complete public and57-file native graph',m['version']==builder.PROFILE and len(contract.V19_NATIVE)==57 and v['files']==468)
        check('new browser graph explicitly selects35modules and renewable mesh4',set(graph['modules'])==builder.MODULES and graph['profile']=='codi-public-mesh/4' and graph['membershipLease']=='codi-mesh-room-lease/1')
        check('issuer holds controller public contract without private worker storage implementation','room_service/contract.py' in contract.V19_NATIVE and not {'room_service/store.py','room_service/http.py','room_service/operator.py'}&contract.V19_NATIVE)
        for path in contract.V19_NATIVE:
            if path.endswith('.py'):ast.parse((release/path).read_text())
        check('all sealed native Python parses',True)
        help=subprocess.run([sys.executable,'-I','-B',str(release/'scripts/serve-connected.py'),'--help'],capture_output=True,text=True,timeout=20)
        check('actual issuer CLI exposes explicit lease and pinned hosted-policy options',help.returncode==0 and all(x in help.stdout for x in ['--mesh-leased-groups','--hosted-room-policy','--hosted-room-policy-sha256']))
        bad=subprocess.run([sys.executable,'-I','-B',str(release/'scripts/serve-connected.py'),'--hosted-room-policy','/not-configured'],capture_output=True,text=True,timeout=20)
        check('partial hosted-policy CLI configuration fails before runtime setup',bad.returncode!=0 and 'required together' in bad.stderr)
        older=[ROOT/'.build/releases/connected-root-cache-r2',ROOT/'.build/releases/connected-mesh-native-r1',ROOT/'.build/releases/connected-neighbor-native-r1']
        for d in older:contract.verify(d)
        check('new verifier preserves native16 root native17 and native18 acceptance',True)
        check('old32and33module graph validators refuse new35module metadata',denied(lambda:contract.verify_mesh_graph(release,p)) and denied(lambda:contract.verify_neighbor_graph(release,p)))
        with tempfile.TemporaryDirectory(prefix='codi-native19-graph-') as directory:
            d=Path(directory)
            for path in ['index.html','assets/desktop/network-release.json','assets/vendor/gossip/manifest.json','assets/vendor/gossip/LICENSES.txt']:
                out=d/path;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(release/path,out)
            for folder in [graph['directory'],graph['coreDirectory']]:shutil.copytree(release/folder,d/folder)
            for name,change in [('wrong-version',lambda g:g.update(version='codi-network-release/3')),
                                ('missing-module',lambda g:g['modules'].pop('hosted-room-authority.mjs')),
                                ('wrong-membership',lambda g:g.update(membershipLease='implicit')),
                                ('wrong-hosted-profile',lambda g:g.update(hostedAuthority='unknown')),
                                ('wrong-directory',lambda g:g.update(directory='assets/desktop/network-v5/'+'0'*64))]:
                changed=json.loads(json.dumps(graph));change(changed);(d/'assets/desktop/network-release.json').write_text(json.dumps(changed))
                check('graph refuses '+name,denied(lambda:contract.verify_hosted_graph(d,p)))
            (d/'connected-release.json').write_bytes((release/'connected-release.json').read_bytes());(d/'release.json').write_bytes((release/'release.json').read_bytes())
            bad=json.loads((d/'connected-release.json').read_bytes());bad['files']['room_service/store.py']={'bytes':0,'sha256':hashlib.sha256(b'').hexdigest()};(d/'connected-release.json').write_text(json.dumps(bad))
            check('native issuer role refuses extra private-worker implementation even with a resealed manifest',denied(lambda:contract.verify(d)))
        check('private state/key/database filenames are never public assets',all(not contract.public_name(n) for n in ['room_service/contract.py','rooms.sqlite3','assets/state/controller.pem','assets/state/rooms.sqlite3']))
        result.update(status='PASS',manifestSHA256=v['manifestSHA256'],files=v['files'],networkModules=len(graph['modules']),nativeFiles=len(contract.V19_NATIVE),installed=False)
    except Exception as error:
        import traceback;result.update(error=str(error),traceback=traceback.format_exc())
    result['sourceSHA256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'scripts/build-hosted-native.py',ROOT/'origin_service/room_authority.py',ROOT/'origin_service/room_management.py']}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.release.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
