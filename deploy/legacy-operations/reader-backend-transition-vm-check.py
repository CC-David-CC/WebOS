#!/usr/bin/env python3
"""Actual retained VM backend composition deaths/recovery/inverse, no data restore."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import sqlite3

CONTROL=Path('/etc/codi-native-fixture/managed.json');ROOT=Path('/srv/codi-room-fixture')
WORKER='3a6d3c5184e52858abe324e37fd4ca410f66d7d289468efe6f169352d347727b'
OLD='3907eac6785bc4ad6ca02436949539d0d06de9cdbf78b51f0b96e2d40d6a7a85'
OPERATOR='53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc'
OLD_OP='41776629f6224f12c55e8dae011b0f2f9ca81c574530babe49a2ad50362e0d3f'
NATIVE='ba89487b3ea3fbca334abd3cc8f3467b8dd604bab51a141ed221236a4c1871f5'
NATIVE_DIR=Path('/srv/codi-network-fixture/candidate-'+NATIVE[:16]);PYTHON='/srv/codi-network-fixture/venv/bin/python'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--result',type=Path);p.add_argument('--fault');p.add_argument('--inner-binding',choices=['bind','unbind']);p.add_argument('--fault-stage');a=p.parse_args();assert os.geteuid()==0
spec=importlib.util.spec_from_file_location('backend_composition',Path(__file__).with_name('reader-backend-transition.py'));b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
t=b.Transition(CONTROL,'/etc/codi-rooms-fixture/managed.json',ROOT/'operators'/OPERATOR,OPERATOR,NATIVE_DIR,NATIVE)

def run(args,check=True):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=check,timeout=240)

if a.inner_binding:
    spec=importlib.util.spec_from_file_location('transition_native_inner',NATIVE_DIR/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
    from origin_service import room_management
    def died(name):
        if name==a.fault_stage:os._exit(96)
    with op.locked(CONTROL):
        c=op.load(CONTROL);value=None if a.inner_binding=='unbind' else room_management.policy(op,t.room_config,t.operator)
        room_management.configure(op,c,CONTROL,value,phase=died)
    raise AssertionError('Expected inner binding death')

if a.fault:
    original=t.cli
    def injected(action,*args):
        kind='unbind' if '--disable' in args else 'bind'
        if action=='configure-hosted-rooms' and a.fault.startswith('inner-'+kind+':'):
            child=run([PYTHON,'-I','-B',Path(__file__),'--inner-binding',kind,'--fault-stage',a.fault.split(':',1)[1]],check=False)
            assert child.returncode==96,(child.returncode,child.stderr);os._exit(97)
        return original(action,*args)
    t.cli=injected
    def died(name):
        if name==a.fault:os._exit(97)
    t.apply(ROOT/'workers'/WORKER,WORKER,phase=died)
    raise AssertionError('Expected composed process death')

assert a.result and not a.result.exists()
checks=[];value={'status':'FAIL','scope':__doc__,'checks':checks,'productionChanged':False,'dataRestored':False,'rootMinted':False}
def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
def refused(fn):
    try:fn()
    except (ValueError,OSError,subprocess.SubprocessError):return True
    raise AssertionError('Expected refusal')
def snap():return json.loads(run([PYTHON,'-I','-B','/srv/codi-network-fixture/tools/native-network-vm-lifecycle-check.py','--snapshot']).stdout)
def custody():
    c=t.read_native();root=Path(c['stateRoot'])/'operator/root'
    keys={str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in root.rglob('*')if f.is_file()}
    f=json.loads(Path(c['userFiles']['configFile']).read_bytes());rows={}
    with sqlite3.connect('file:'+str(Path(f['stateRoot'])/'permissions.sqlite3')+'?mode=ro',uri=True) as db:
        for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            quoted='"'+name.replace('"','""')+'"';values=[[{'bytes_sha256':hashlib.sha256(v).hexdigest()}if isinstance(v,bytes)else v for v in row]for row in db.execute('SELECT * FROM '+quoted)]
            values.sort(key=lambda row:json.dumps(row,sort_keys=True));rows[name]=hashlib.sha256(json.dumps(values,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'rootFiles':keys,'permissionTables':rows}
try:
    before=snap();keys=custody();original_native=t.read_native();original_room,baseline=t.room();assert original_native['manifestSHA256']==NATIVE and original_room['manifestSHA256'] in [OLD,WORKER] and sum(r[6]for r in baseline['rooms'])>=2
    if original_room['manifestSHA256']==OLD:
        prepared=t.apply(ROOT/'workers'/WORKER,WORKER)
        check('explicit initial backend upgrade retains existing room data before the inverse tests',prepared['status']=='reader-backend-upgraded' and t.room()[1]==baseline and custody()==keys and snap()['keysAndAccountDBSHA256']==before['keysAndAccountDBSHA256'])
        original_native=t.read_native()
    def preserve():
        c,state=t.room();current=snap();assert state==baseline and custody()==keys
        assert current['keysAndAccountDBSHA256']==before['keysAndAccountDBSHA256'] and current['privateFixtureFileSHA256']==before['privateFixtureFileSHA256']
        assert all(current['pids'][r]==before['pids'][r]for r in ['steward','guest','files','filesProxy'])
        stable=lambda c:{k:v for k,v in c.items()if k!='hostedRooms'}
        assert stable(t.read_native())==stable(original_native)
        for role,rows in before['usage'].items():
            fresh={(r[0],r[1]):r[2:]for r in current['usage'][role]}
            for row in rows:assert all(x>=y for x,y in zip(fresh[(row[0],row[1])],row[2:]))
        assert not t.journal.exists() and not t.manager.journal.exists() and not current['nativeJournalPresent'];return c,current
    inverse=t.apply(ROOT/'workers'/OLD,OLD,ROOT/'operators'/OLD_OP,OLD_OP);c,_=preserve()
    check('actual inverse selects worker1 and original strict operator while retaining nonempty current state',inverse['status']=='reader-backend-upgraded' and c['manifestSHA256']==OLD and t.read_native()['hostedRooms']['operatorManifestSHA256']==OLD_OP)
    stable=snap()['pids']
    check('wrong worker pin is refused before journals or running processes change',refused(lambda:t.apply(ROOT/'workers'/WORKER,'0'*64)) and not t.journal.exists() and snap()['pids']==stable)
    with t.locked():check('concurrent transition is refused before running processes change',refused(lambda:t.apply(ROOT/'workers'/WORKER,WORKER)) and snap()['pids']==stable)
    points=[*b.PHASES,'inner-worker:config','inner-worker:committed','inner-unbind:starting','inner-bind:committed']
    for point in points:
        child=run([PYTHON,'-I','-B',Path(__file__),'--fault',point],check=False);assert child.returncode==97,(point,child.returncode,child.stderr,child.stdout)
        check('actual '+point+' death leaves a composed journal and refuses ordinary reapply',t.journal.exists() and refused(lambda:t.apply(ROOT/'workers'/WORKER,WORKER)))
        recovered=t.recover();c,_=preserve();committed=point=='committed'
        assert c['manifestSHA256']==(WORKER if committed else OLD)
        assert t.read_native()['hostedRooms']['operatorManifestSHA256']==(OPERATOR if committed else OLD_OP)
        check('explicit '+point+' recovery retains current keys files history floors and restores correct worker/binding',recovered['status']==('committed-reader-backend-recovered' if committed else 'interrupted-reader-backend-reverted'))
        if committed:t.apply(ROOT/'workers'/OLD,OLD,ROOT/'operators'/OLD_OP,OLD_OP);preserve()
    forward=t.apply(ROOT/'workers'/WORKER,WORKER);c,_=preserve()
    check('final forward update selects worker2 and the compatible exact operator',forward['status']=='reader-backend-upgraded' and c['manifestSHA256']==WORKER and t.read_native()['hostedRooms']['operatorManifestSHA256']==OPERATOR)
    stable=snap()['pids'];steady=t.manager.states(c);noop=t.apply(ROOT/'workers'/WORKER,WORKER)
    check('lost final receipt retry is an exact PID-preserving no-op',noop['status']=='reader-backend-already-current' and snap()['pids']==stable and t.manager.states(c)==steady)
    value.update(status='PASS',actualComposedDeaths=len(points),actualNativeInnerDeaths=2,actualWorkerInnerDeaths=2,roomHealth=t.manager.health(c),finalNativePIDs=stable,nonemptyRoomStateRetained=True,allKeysAccountsFilesUsageAndRootCustodyRetained=True,sourceSHA256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(__file__).with_name('reader-backend-transition.py')]})
except Exception as error:
    import traceback;value.update(error=str(error),traceback=traceback.format_exc())
finally:a.result.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:value.get(k)for k in ['status','error','actualComposedDeaths','finalNativePIDs']}))
raise SystemExit(0 if value['status']=='PASS' else 1)
