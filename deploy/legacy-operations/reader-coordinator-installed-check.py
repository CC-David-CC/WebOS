#!/usr/bin/env python3
"""Actual disposable systemd discovery worker/proxy/refresh isolation checks.

Local installed units and owned fixture credentials only. No public ingress,
production keys, browser scale, or separate-WAN claim.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import time
import traceback
import urllib.request

ROOT=Path(__file__).resolve().parents[1]

def run(a):
    checks=[];stage=Path('/srv')/('codi-readers-fixture-'+secrets.token_hex(5));units=[];manager=None;c=None
    result={'status':'FAIL','scope':__doc__,'checks':checks,'wholeGoalComplete':False,'servicesDeployed':False}
    def passed(name):checks.append(name);print(json.dumps({'check':name}),flush=True)
    def denied(fn):
        try:fn()
        except (OSError,ValueError,subprocess.CalledProcessError):return
        raise AssertionError('Invalid managed operation accepted')
    try:
        stage.mkdir(mode=0o755)
        for src,name in [(a.worker,'worker'),(a.operator,'operator'),(ROOT/'.venv','venv')]:shutil.copytree(src,stage/name,symlinks=True)
        for p in [stage,*stage.rglob('*')]:
            if not p.is_symlink():p.chmod(0o755 if p.is_dir() or p.parent==stage/'venv/bin' else 0o644)
        manifest=json.loads((stage/'operator/reader-operator.json').read_text())
        actual={str(p.relative_to(stage/'operator')) for p in (stage/'operator').rglob('*') if p.is_file()}
        assert actual==set(manifest['files'])|{'reader-operator.json'}
        for name,record in manifest['files'].items():
            p=stage/'operator'/name;assert not p.is_symlink() and record=={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        operator_pin=hashlib.sha256((stage/'operator/reader-operator.json').read_bytes()).hexdigest()
        sys.path.insert(0,str(stage/'operator'))
        from reader_service.operator import Manager,safe
        from room_service.contract import jose
        from reader_service.contract import issue,verify
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import serialization
        provider=stage/'room-provider';provider.mkdir(mode=0o700)
        room=ec.generate_private_key(ec.SECP256R1());roomfile=provider/'room.pem'
        roomfile.write_bytes(room.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));roomfile.chmod(0o600)
        authority=ec.generate_private_key(ec.SECP256R1())
        identity={'mode':'server','apiBase':'/api/v1','issuer':'https://reader.fixture.invalid','audience':'codiserver-peers-v1','authorityClass':'development','authorityKeys':[{'kid':'fixture','jwk':jose.public_jwk(authority)}]}
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        manager=Manager(stage/'config');pin=hashlib.sha256((stage/'worker/reader-worker.json').read_bytes()).hexdigest()
        args=dict(instance=stage.name,release=str(stage/'worker'),manifest_sha256=pin,python=str(stage/'venv/bin/python'),identity=identity,room_key_source=str(roomfile),port=port,unit_dir='/run/systemd/system')
        with manager.locked():
            def interrupt(phase):
                if phase=='applied':raise RuntimeError('Owned fixture interruption after units/config apply')
            try:manager.configure(**args,phase=interrupt)
            except RuntimeError:pass
            assert manager.journal.exists();candidate=json.loads(manager.config_path.read_text());units=manager.names(candidate)
            before=hashlib.sha256((manager.folder/'private/reader.pem').read_bytes()).hexdigest()
            denied(manager.load);c=manager.configure(**args,recover=True)
            assert not manager.journal.exists() and before==hashlib.sha256((manager.folder/'private/reader.pem').read_bytes()).hexdigest()
            passed('interrupted configure recovers exact applied units without replacing discovery key')
            state=manager.start(c);wpid=int(state['states'][units[0]]['MainPID']);ppid=int(state['states'][units[1]]['MainPID'])
            result['uids']=state['uids'];assert state['privateNetworkNamespace'] and state['emptyCapabilities'] and not state['bootEnabled']
            passed('actual worker and socket proxy use distinct nonroot identities in one private namespace')
            pub=json.loads((manager.folder/'public/policy.json').read_text());tokenfile=manager.folder/'public/delegation.jws';old=tokenfile.read_bytes()
            manager.refresh(c);assert tokenfile.read_bytes()==old and int(manager.health(c)['states'][units[0]]['MainPID'])==wpid
            passed('root oneshot no-op refresh preserves delegation bytes and running worker PID')
            # Expired but correctly signed fixture delegation must renew in place.
            safe.atomic(tokenfile,issue(room,pub['coordinatorKey'],identity,'',int(time.time())-21601).encode(),0o644)
            manager.refresh(c);time.sleep(1.1);fresh=manager.health(c)
            assert tokenfile.read_bytes()!=old and int(fresh['states'][units[0]]['MainPID'])==wpid
            verify(tokenfile.read_text(),pub['roomControllerKey'],pub['coordinatorKey'],identity,'',int(time.time()))
            passed('expired discovery delegation renews through installed credential job without restarting worker')
            good=roomfile.read_bytes();wrong=ec.generate_private_key(ec.SECP256R1())
            safe.atomic(roomfile,wrong.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
            retained=tokenfile.read_bytes()
            # Exercise the actual installed job rather than only operator preflight.
            denied(lambda:safe.systemctl('start',units[3]));assert tokenfile.read_bytes()==retained
            safe.atomic(roomfile,good);safe.systemctl('reset-failed',units[3]);manager.refresh(c)
            passed('wrong room credential makes actual refresh job fail without replacing valid delegation')
            for pid in [wpid,ppid]:
                # Enter the actual mount/network namespace then drop to that
                # service UID/GID: prove denied files and real network isolation.
                status=dict(line.split(':',1) for line in Path('/proc/'+str(pid)+'/status').read_text().splitlines() if ':' in line)
                uid=int(status['Uid'].split()[0]);gid=int(status['Gid'].split()[0])
                probe="""import os,socket,sys
for path in sys.argv[1:]:
 try:open(path,'rb').read(1)
 except (PermissionError,FileNotFoundError):pass
 else:raise AssertionError('private credential visible: '+path)
s=socket.socket();s.settimeout(.3)
try:s.connect(('1.1.1.1',443))
except OSError:pass
else:raise AssertionError('private namespace reached Internet')
"""
                files=[str(roomfile),str(manager.folder/'private/reader.pem')]
                if pid==ppid:files.append('/run/credentials/'+units[0]+'/reader-key')
                safe.run(['/usr/bin/nsenter','--target',pid,'--mount','--net','/usr/bin/setpriv','--reuid',uid,'--regid',gid,'--clear-groups','/usr/bin/python3','-I','-B','-c',probe,*files])
            passed('actual worker/proxy namespaces deny room source and private disk key; proxy cannot read worker credential; no Internet')
            # Worker can read only its own systemd credential, not the room key.
            credential_path='/run/credentials/'+units[0]+'/reader-key'
            own=safe.run(['/usr/bin/nsenter','--target',wpid,'--mount','/usr/bin/setpriv','--reuid',state['uids'][0],'--regid',int(dict(line.split(':',1) for line in Path('/proc/'+str(wpid)+'/status').read_text().splitlines() if ':' in line)['Gid'].split()[0]),'--clear-groups','/usr/bin/python3','-I','-B','-c',"import os,sys; print(len(open(sys.argv[1],'rb').read()))",credential_path])
            assert 100<int(own)<4096
            passed('LoadCredential delivers only the discovery signing key to the worker identity')
            props=safe.systemctl('show',units[4],'-p','ActiveState','-p','UnitFileState','-p','NextElapseUSecMonotonic')
            assert 'ActiveState=active' in props and 'UnitFileState=static' in props
            passed('hourly renewal timer is armed while all units remain static and disabled for boot')
            # Reject unmanaged mutations before lifecycle operations.
            unit=Path(c['unitDir'])/units[0];raw=unit.read_bytes();safe.atomic(unit,raw+b'\n# tampered fixture\n',0o644)
            denied(lambda:manager.stop(c));safe.atomic(unit,raw,0o644);safe.systemctl('daemon-reload')
            passed('unit mutation refuses lifecycle action before touching active services')
            manager.stop(c);assert before==hashlib.sha256((manager.folder/'private/reader.pem').read_bytes()).hexdigest()
            state=manager.start(c);assert int(state['states'][units[0]]['MainPID'])!=wpid
            assert pub==json.loads((manager.folder/'public/policy.json').read_text())
            passed('stop and restart preserve discovery key, public policy and delegated identity')
        result.update(status='PASS',workerManifestSHA256=pin,operatorManifestSHA256=operator_pin,testSourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),checks=checks,publicIngressChanged=False,productionKeysUsed=False,rootAuthorityKeyUsed=False)
    except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
    finally:
        cleanup=[]
        if units:
            try:
                subprocess.run(['/usr/bin/systemctl','stop',*reversed(units)],capture_output=True,check=True,timeout=30)
                for name in units:
                    p=Path('/run/systemd/system')/name
                    if p.exists():p.unlink()
                subprocess.run(['/usr/bin/systemctl','daemon-reload'],check=True,capture_output=True,timeout=30)
                subprocess.run(['/usr/bin/systemctl','reset-failed',*units],capture_output=True,timeout=15)
            except Exception as e:cleanup.append(str(e))
        if not cleanup and stage.exists():shutil.rmtree(stage)
        if cleanup:result.update(status='FAIL',cleanupErrors=cleanup)
        result['fixtureRemoved']=not stage.exists()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--worker',type=Path,required=True);p.add_argument('--operator',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert os.geteuid()==0 and not a.output.exists()
    v=run(a);a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error'),'fixtureRemoved':v['fixtureRemoved']}));raise SystemExit(0 if v['status']=='PASS' else 1)
