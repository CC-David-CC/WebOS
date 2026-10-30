#!/usr/bin/env python3
"""Bind source chat checkpoint proofs and separate installed native19 regressions."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CHECKS=ROOT/'.build/checks'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    values={};receipts={}
    for stem in ['hosted-snapshot-r2','hosted-snapshot-core-regression-r1',
                 'hosted-snapshot-browser-regression-r1','hosted-snapshot-ancestor-control-r1',
                 'hosted-snapshot-final-health-r1','hosted-snapshot-export-r1','hosted-native-regressions-r2']:
        p=CHECKS/(stem+'-result.json');values[stem]=json.loads(p.read_bytes());receipts[p.name]=digest(p)
    v=values['hosted-snapshot-r2'];assert v['status']=='PASS' and len(v['checks'])==9 and len(v['browser']['checks'])==22
    assert v['browser']['acceptedHead']==103 and v['browser']['skippedPrefixRecords']>=68
    assert v['browser']['tailRecords']==3 and not v['browser']['fullPrefixReplayed']
    assert v['ownedBrowserContextsClosed']==1 and not v['sourceChangedDuringTest']
    for stem,n in [('hosted-snapshot-core-regression-r1',38),('hosted-snapshot-browser-regression-r1',15)]:
        value=values[stem];assert value['status']=='PASS' and len(value['checks'])==n and not value['sourceChangedDuringTest']
    for stem in ['hosted-snapshot-r2','hosted-snapshot-core-regression-r1','hosted-snapshot-browser-regression-r1']:
        for name,pin in values[stem]['sourceSHA256'].items():assert digest(ROOT/name)==pin,(stem,name)
    control=values['hosted-snapshot-ancestor-control-r1']
    assert control['status']=='FAIL' and len(control['checks'])==8 and len(control['browser']['checks'])==5
    assert 'Expected snapshot refusal' in control['error'] and not control['sourceChangedDuringTest'] and control['ownedBrowserContextsClosed']==1
    p=CHECKS/'hosted-snapshot-ancestor-mutation.json';m=json.loads(p.read_bytes());receipts[p.name]=digest(p)
    original=ROOT/m['file'];modified=ROOT/'.build/hosted-snapshot-control-r1'/m['file']
    assert digest(original)==m['originalSHA256'] and digest(modified)==m['mutatedSHA256']
    assert original.read_text().count(m['before'])==1 and original.read_text().replace(m['before'],m['after'])==modified.read_text()
    for name,pin in control['sourceSHA256'].items():
        p=ROOT/'.build/hosted-snapshot-control-r1'/name if name.startswith('network/') else ROOT/name
        assert digest(p)==pin,(name,p)
        if name!=m['file']:assert digest(ROOT/name)==pin,name
    exported=values['hosted-snapshot-export-r1'];assert exported['status']=='PASS' and exported['installed'] is False
    for kind,manifest,count in [('worker','room-worker.json',9),('operator','room-operator.json',5)]:
        info=exported[kind];folder=ROOT/info['directory'];assert digest(folder/manifest)==info['manifestSHA256']
        records=json.loads((folder/manifest).read_bytes())['files'];assert len(records)==count
        assert {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}==set(records)|{manifest}
        for name,record in records.items():
            p=folder/name;assert record=={'bytes':p.stat().st_size,'sha256':digest(p)} and digest(p)==digest(ROOT/name)
    health=values['hosted-snapshot-final-health-r1'];assert health['status']=='PASS' and health['ownedBrowserContextsRemaining']==0 and not health['pendingJournals']
    assert health['runtime']['manifestSHA256']=='1bb104a87cc83404e53812138e6e60cfa006e218302db2cea6c294232a7c6507'
    assert len(health['ownedAccounts'])==5 and all(a['disabled'] and a['remainingFiles']==0 for a in health['ownedAccounts'])
    regression=values['hosted-native-regressions-r2'];assert regression['status']=='PASS' and regression['checks']=={'terminal':38,'documents':19,'lifecycle':13,'accounts':35}
    assert regression['nativeRuntime']==health['runtime']
    return {'status':'PASS','scope':__doc__,'serverSnapshotChecks':9,'browserSnapshotChecks':22,
        'sourceRegressionChecks':{'core':38,'browser':15},'installedNative19RegressionChecks':regression['checks'],
        'chatStateCheckpointSourceImplemented':True,'chatCheckpointInstalledInVM':False,'chatCheckpointLive':False,
        'freshBrowserFullPrefixReplayRequired':False,'oldHistoryRemainsRetrievable':True,
        'checkpointTrust':'chosen-room-controller; no replica or full skipped-transition audit claim',
        'snapshotBudget':{'maximumTailRecords':32,'maximumReceiptTokenCharacters':64000,'maximumSnapshotTokenCharacters':120000},
        'browserFloorPersistenceImplemented':False,'hostedRoomsDrawerIntegrated':False,'chessSnapshotImplemented':False,
        'P2PCheckpointDeliveryImplemented':False,'actual8kNetworkTested':False,'productionChanged':False,
        'privateVMSnapshotRuntimeChanged':False,'ownedBrowserContextsRemaining':0,'wholeGoalComplete':False,
        'workerCandidate':exported['worker'],'receiptSHA256':receipts,'sourceSHA256':digest(Path(__file__))}


if __name__=='__main__':
    out=CHECKS/'hosted-snapshot-milestone-r1-result.json';assert not out.exists()
    value=run();out.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
