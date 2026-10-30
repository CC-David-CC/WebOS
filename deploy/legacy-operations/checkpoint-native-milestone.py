#!/usr/bin/env python3
"""Bind actual installed private checkpoint worker/native proofs; no whole-goal pass."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];CHECKS=ROOT/'.build/checks'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    pins={};values={}
    for name in ['hosted-room-code-vm-r1','checkpoint-native-release-r1',
                 'checkpoint-native-build-r1','checkpoint-native-repro-r1',
                 'checkpoint-native-vm-upgrade-r1','hosted-native-browser-checkpoint-r1',
                 'checkpoint-native-vm-mesh-r1','checkpoint-native-final-health-r1']:
        path=CHECKS/(name+'-result.json');v=json.loads(path.read_bytes());assert v['status']=='PASS',name
        values[name]=v;pins[path.name]=digest(path)
    code=values['hosted-room-code-vm-r1'];api=values['hosted-native-browser-checkpoint-r1'];mesh=values['checkpoint-native-vm-mesh-r1'];health=values['checkpoint-native-final-health-r1']
    assert len(code['checks'])==22 and code['actualCodeProcessDeaths']==7
    assert code['allPriorKeysAccountsCookieFilesAndUsagePreserved'] and not code['dataRestored'] and not code['rootMinted'] and code['ownedNegativeWorkerRemoved']
    assert len(api['checks'])==13 and api['chatSnapshotsTested'] and api['ownedBrowserContextsClosed']==1 and api['ownedAccountPolicy']['disabled']
    assert api['sourceSHA256']==digest(ROOT/'scripts/hosted-native-browser-check.py')
    assert len(mesh['checks'])==23 and mesh['automaticIntroductionsEnabled'] and mesh['leasedMembershipEnabled']
    assert len(values['checkpoint-native-release-r1']['checks'])==15
    pin='440f0c19892cde73fe893c139a86d9163e729af9f37c41d5ecd5221bbbbcbe8a'
    assert all(values[n]['manifestSHA256']==pin for n in ['checkpoint-native-build-r1','checkpoint-native-repro-r1','checkpoint-native-release-r1'])
    assert values['checkpoint-native-vm-upgrade-r1']['nativeManifestSHA256']==health['runtime']['manifestSHA256']==mesh['nativeManifestSHA256']==pin
    assert values['checkpoint-native-vm-upgrade-r1']['runtime']==health['runtime']==mesh['runtimeBefore']
    assert health['ownedBrowserContextsRemaining']==0 and len(health['ownedAccounts'])==7 and not health['pendingJournals']
    assert all(a['disabled'] and a['remainingFiles']==0 for a in health['ownedAccounts'])
    assert health['defaultPublicTLS'] and not health['fullAllSiteOrPrototypeByteAuditRepeated']
    spec=importlib.util.spec_from_file_location('_checkpoint_retention',ROOT/'room_service/operator.py');op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
    assert op.retained(code['workerState'],health['roomState'])
    assert any(r[0]==api['ownedRoom'] and r[6]==2 for r in health['roomState']['rooms'])
    operator=ROOT/'.build/hosted-room-operator-upgrade-r2';assert digest(operator/'room-operator.json')==code['operatorManifestSHA256']
    for name,rec in json.loads((operator/'room-operator.json').read_bytes())['files'].items():assert digest(ROOT/name)==rec['sha256'] and digest(operator/name)==rec['sha256']
    assert code['workerManifestSHA256']=='b0dfa2c28d31db9af64bdaecec19c26b5cd1ee9b2d0624699404d75dd788d8d0'
    return {'status':'PASS','scope':__doc__,'installedWorkerCodeChecks':22,'actualWorkerCodeProcessDeaths':7,
        'installedChromeAPIChecks':13,'installedThreeDesktopMeshChecks':23,'releaseChecks':15,
        'installedPrivateNativeManifestSHA256':pin,'installedPrivateNativeRuntime':health['runtime'],
        'installedPrivateWorkerManifestSHA256':code['workerManifestSHA256'],'installedPrivateOperatorManifestSHA256':code['operatorManifestSHA256'],
        'chatCheckpointInstalledAndBrowserVerifiedInPrivateVM':True,'snapshotLiveInProduction':False,
        'hostedRoomsDrawerIntegrated':False,'durableBrowserFloorStoreImplemented':False,'P2PHostedTransportImplemented':False,
        'fullChessStateImplemented':False,'actual8kNetworkTested':False,'productionChanged':False,
        'ownedQAAccountsDisabledAndEmpty':7,'ownedBrowserContextsRemaining':0,'wholeGoalComplete':False,
        'receiptSHA256':pins,'sourceSHA256':digest(Path(__file__))}


if __name__=='__main__':
    out=CHECKS/'checkpoint-native-milestone-r1-result.json';assert not out.exists()
    v=run();out.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
