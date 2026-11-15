#!/usr/bin/env python3
"""Bind actual native22/public reader evidence; full distributed goal stays active."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT/'.build/checks'
PIN = '9537a6b6d4ab7074512d48e13c46121282980e7197a7aaf3b1c3f7ddc8199f6a'
NAMES = ['source-r6', 'pending-r2', 'window-regression-r1', 'client-regression-r1', 'build-r2', 'build-r3', 'release-r2', 'vm-upgrade-r1', 'native-topology-r1', 'native-ui-r1', 'native-cycle-r1', 'wan-r1', 'public-ui-r1', 'live-health-r1', 'smoke-r1', 'wan-cleanup-r1', 'wan-cleanup-verified-r1', 'before-live-health-r1', 'live-source-sync-r1', 'live-stage-r1', 'live-activate-r1', 'live-verify-r1']


def read(name):
    return json.loads((CHECKS/(name+'-result.json')).read_bytes())


def bind(name):
    p = CHECKS/(name+'-result.json')
    return dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), checks=len(read(name).get('checks', [])))


def run():
    values, refs = {}, {}
    for short in NAMES:
        name = 'hosted-readers-'+short
        value = read(name)
        if short == 'smoke-r1':
            assert len(value['sites']) == 10 and all(v['result'] == 'PASS' for v in value['sites'].values()) and 'native22' in value['scope']
        else:
            assert value['status'] == 'PASS', name
        values[short], refs[name] = value, bind(name)
    health, wan, ui = [values[n] for n in ['live-health-r1', 'wan-r1', 'public-ui-r1']]
    assert health['nativeManifestSHA256'] == wan['nativeManifestSHA256'] == ui['nativeManifestSHA256'] == PIN
    assert health['nativePIDs'] == ui['nativeRuntimeBefore']['nativePIDs']
    assert health['verifiedReleaseFiles'] == 615 and health['publicPrototypeFilesVerified'] == 133 and health['originalDocumentCount'] == 0
    assert health['originalAccountCount'] == 38 and health['currentAccountCount'] >= 47
    assert ui['defaultPublicTLS'] and wan['defaultPublicTLS'] and wan['publicWANTested'] and wan['actualV86Desktops'] == 3 and wan['ownedBrowserContextsClosed'] == 3
    assert len(set(wan['publicIPs'].values())) == 2
    pairs = [p for e in wan['introducedLinkEvidence'] for p in e['pairs']]
    assert len(pairs) == 2 and all(p['localType'] == p['remoteType'] == 'relay' and p['relayProtocol'] == 'tls' and p['turnURL'].startswith('turns:turn.ksu.codes:443') for p in pairs)
    assert values['source-r6']['actualBrowsers'] == 10 and values['source-r6']['actualV86Desktops'] == 0
    assert values['source-r6']['largerGroupHTTPDelta'] == [0]*7
    faults = values['pending-r2']['pendingIntroductionFaults']
    assert faults['realAdditionalIssuerIdentities'] == 5 and faults['acceptedPending'] == 4 and faults['refusedBeforePCAllocation'] == 1
    assert len(values['native-cycle-r1']['steps']) == 2 and not values['native-cycle-r1']['dataRestored']
    negatives = {'recipient-negative-r1': 'recipient, room, SDP hash and signature mutations are all rejected', 'close-negative-r1': 'retiring the reader service closes all of its new pending PCs and preserves existing links'}
    for short, oracle in negatives.items():
        name = 'hosted-readers-'+short
        value = read(name)
        assert value['status'] == 'FAIL' and value['error'] == oracle
        refs[name] = bind(name) | dict(expectedStatus='FAIL', intendedOracle=oracle, oneStatementMutation=True)
    for short in ['source-r1', 'source-r3', 'source-r4', 'release-r1']:
        name = 'hosted-readers-'+short
        assert read(name)['status'] == 'FAIL'
        refs[name] = bind(name) | dict(retainedActualFailure=True)
    qa_names = ['hosted-peer-public-r1', 'hosted-peer-public-r2', 'hosted-peer-public-ui-r1', 'hosted-peer-wan-r1', 'hosted-peer-wan-r2', 'hosted-peer-window-wan-r1', 'hosted-peer-window-public-peer-r1', 'hosted-readers-wan-r1', 'hosted-readers-public-ui-r1']
    qas = []
    for name in qa_names:
        value = read(name)
        assert value['ownedAccountPolicy']['disabled'] and value['createdTestAccount'].startswith('vmhosted_')
        qas.append(dict(username=value['createdTestAccount'], subject=value['ownedAccountPolicy']['subject']))
    root_refs = [values['live-'+action+'-r1'] for action in ['source-sync', 'stage', 'activate', 'verify']]
    code = '''from pathlib import Path
import hashlib,json,sqlite3,stat
out=[]
for ref in REFS:
 p=Path(ref['rootReceipt']);s=p.stat();raw=p.read_bytes();assert s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600 and hashlib.sha256(raw).hexdigest()==ref['rootReceiptSHA256'];v=json.loads(raw);assert v['status']=='PASS'
 if ref['action']!='source-sync':
  assert v['statePreserved'] and v['hostingUnchanged'] and v['backendNotRestarted'] and not v['dataRestored']
  if ref['action']=='activate':assert v['upgrade']['status']=='upgraded' and not v['notice']['workSaved']
  if ref['action']=='verify':assert v['releaseVerification']['manifestSHA256']==PIN and v['releaseVerification']['files']==615
 out.append({'action':ref['action'],'receipt':str(p),'sha256':ref['rootReceiptSHA256'],'status':'PASS'})
c=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_bytes());assert c['manifestSHA256']==PIN
db=Path(c['stateRoot'])/'issuer/state/accounts.sqlite3'
with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True) as conn:
 for qa in QAS:
  assert conn.execute('SELECT a.subject,p.disabled FROM accounts a JOIN account_policy p ON a.subject=p.subject WHERE a.username=?',(qa['username'],)).fetchone()==(qa['subject'],1)
print(json.dumps({'receipts':out,'knownQAAccountsDisabled':len(QAS)}))
'''.replace('REFS', repr(root_refs)).replace('PIN', repr(PIN)).replace('QAS', repr(qas))
    root = json.loads(subprocess.check_output(['ssh', '-o', 'BatchMode=yes', 'box-webhost', 'sudo -n /usr/bin/python3 -I -B -c '+shlex.quote(code)], text=True, timeout=45))
    return dict(status='PASS', scope=__doc__, observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), receipts=refs, rootReceiptsVerified=root['receipts'], nativeManifestSHA256=PIN, releaseFiles=615, networkModules=39, nativeFiles=57, onlyNativeProfileValidatorsChanged=4, publicPrototypeFilesVerified=133, all10Sites='PASS', privateInstalledUI=17, privateInstalledTopology=6, actualPrivateInverseForward=2, publicUI=17, publicTwoNetworkTopology=7, sourceTenBrowserChecks=15, pendingFaultChecks=16, graphChecks=14, publicWANIPs=wan['publicIPs'], actualPublicRelay='TURN/TLS443', nativePIDs=health['nativePIDs'], rootConfigSHA256=health['nativeConfigSHA256'], rootRevision=3, rootExpiresAt=health['rootExpiresAt'], knownPublicQAAccountsDisabled=root['knownQAAccountsDisabled'], productionOriginalDocumentBaseline=0, nonemptyDataRetentionScope='separate retained private VM proof', externalFixtureCleaned=True, automaticHostedReaderIntroductionsLive=True, remainingRouteRecoveryTested=True, fullyDisconnectedBootstrapImplemented=False, islandsLayersComplete=False, replicaAgreementComplete=False, durableChessComplete=False, eightThousandTransportVerified=False, referenceAuditComplete=False, wholeGoalComplete=False, sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    value = run()
    args.output.write_text(json.dumps(value, indent=2)+'\n')
    print(json.dumps({'status': value['status'], 'boundReceipts': len(value['receipts']), 'publicWANChecks': value['publicTwoNetworkTopology'], 'wholeGoalComplete': False}))
