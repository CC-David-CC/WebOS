#!/usr/bin/env python3
"""Bind the exact native11 candidate, actual installed tests and browser files UI."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from origin_service.release import verify
CHECKS=ROOT/'.build/checks'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    key='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0';release=ROOT/'.build/releases/connected-files-r2';assert verify(release)['manifestSHA256']==key
    for name,value in json.loads((release/'connected-release.json').read_text())['files'].items():
        if (ROOT/name).is_file() and name!='release.json':assert sha(ROOT/name)==value['sha256'],name
    names=['native-files-result.json','gateway-auth-result.json','connected-release-result.json','managed-turn-policy-result.json','native11-runtime-result.json',
           'gateway-browser-result.json','gateway-files-ui-result.json','files-ui-compat-result.json','persistent-services-deployment-baseline-rollout-hidden-result.json']
    r={name:json.loads((CHECKS/name).read_text()) for name in names}
    for name,value in r.items():
        assert value['status']=='PASS',name
        for source,pin in value.get('sha256',{}).items():assert sha(ROOT/source)==pin,(name,source)
    assert r['native-files-result.json']['nativeManifestSHA256']==key and len(r['native-files-result.json']['checks'])==11
    assert r['native-files-result.json']['fixtureCleanupCompleted']
    assert r['gateway-auth-result.json']['tests']==28 and r['connected-release-result.json']['tests']==14 and r['managed-turn-policy-result.json']['tests']==18
    for name in ['gateway-browser-result.json','gateway-files-ui-result.json','files-ui-compat-result.json']:
        assert r[name]['executedIssuerManifestSHA256']==key and len(r[name]['witnesses'])==2
    full=r['persistent-services-deployment-baseline-rollout-hidden-result.json'];assert full['release']['manifestSHA256']==key
    assert full['nativeRollout']['targetProfileVersion']=='codi-connected-development/11' and full['nativeRollout']['allThreeRolesRunningAndJournalsCleared']
    assert full['disposableInstalledUnitsAndStateRemoved'] and full['pingPolicyRestoredAndForwardingUnchanged'] and not full['cleanupErrors']
    browser=full['browser'];assert browser['bidirectionalRTC'] and browser['separateRoomChatAndMoves'] and browser['pgnExportMatchesAcrossPeersAndExcludesChat']
    assert browser['guestRelayRestart']['sameVmObjects'] and browser['guestRelayRestart']['ramFilesPreserved'] and browser['guestRelayRestart']['twoGuestsPingAfterRestart']
    for witness in browser['guestInternet']:assert witness=={'pingReplies':2,'dnsAndHttp':True}
    frontend=ROOT/'.build/frontends/private-files-r15';front=json.loads((frontend/'frontend.json').read_text())
    for name,value in front['files'].items():assert sha(ROOT/name)==value['sha256']==sha(frontend/name)
    result={'status':'PASS','scope':'Exact local sealed native11 candidate: real installed policy/code recovery, actual issuer+worker+v86 browser files, mixed UI rollback, local TLS RTC/chat/separate chess and guest network; public activation not claimed',
            'nativeManifestSHA256':key,'frontendManifestSHA256':sha(frontend/'frontend.json'),'nativeFilePolicyInstalledOnWebhost':False,'publicFileAPIRouted':False,
            'physicalAndroidVerified':False,'independentWANVerified':False,'receiptSHA256':{name:sha(CHECKS/name) for name in names},'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'native-files-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
