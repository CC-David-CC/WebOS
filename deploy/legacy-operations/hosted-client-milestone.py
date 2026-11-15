#!/usr/bin/env python3
"""Bind shared-client/bundled-pane source proofs and inactive native20 candidate."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];CHECKS=ROOT/'.build/checks'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    names=['hosted-client-source-r4','hosted-client-floor-control-r2','hosted-client-core-regression-r1',
           'hosted-client-proof-regression-r1','hosted-client-native-release-r2','hosted-client-native-repro-r2',
           'hosted-client-native-app-compose-r2','hosted-client-worker-export-r1','hosted-client-source-final-health-r1']
    values={};receipts={}
    for name in names:
        p=CHECKS/(name+'-result.json');values[name]=json.loads(p.read_bytes());receipts[p.name]=digest(p)
    positive=values['hosted-client-source-r4'];assert positive['status']=='PASS' and len(positive['checks'])==25 and not positive['sourceChangedDuringTest']
    assert positive['actualPageReload'] and positive['creationRetriesDidNotDuplicateRooms'] and positive['exactCommittedMessageCount']==4 and positive['ownedBrowserContextsClosed']==1
    for name,pin in positive['sourceSHA256'].items():assert digest(ROOT.parent/name)==pin,name
    control=values['hosted-client-floor-control-r2'];assert control['status']=='FAIL' and not control['sourceChangedDuringTest'] and control['ownedBrowserContextsClosed']==1
    assert len(control['phaseOne']['checks'])==8 and len(control['phaseTwo']['checks'])==8 and 'atomic browser storage refuses a stale tab' in control['error']
    p=CHECKS/'hosted-client-floor-mutation-r2.json';mutation=json.loads(p.read_bytes());receipts[p.name]=digest(p)
    original=ROOT/mutation['file'];modified=ROOT/'.build/hosted-client-floor-control-r2'/mutation['file']
    assert digest(original)==mutation['originalSHA256'] and digest(modified)==mutation['mutatedSHA256']
    assert original.read_text().count(mutation['before'])==1 and original.read_text().replace(mutation['before'],mutation['after'])==modified.read_text()
    for name,pin in control['sourceSHA256'].items():
        source=ROOT.parent/name;assert digest(source)==pin,name
        if name.startswith('active-system/.build/hosted-client-floor-control-r2/network/') and source.name!=original.name:assert digest(ROOT/'network'/source.name)==pin,name
    for stem,count in [('hosted-client-core-regression-r1',38),('hosted-client-proof-regression-r1',15)]:
        v=values[stem];assert v['status']=='PASS' and len(v['checks'])==count and not v['sourceChangedDuringTest']
        for name,pin in v['sourceSHA256'].items():assert digest(ROOT/name)==pin,(stem,name)
    native=values['hosted-client-native-release-r2'];assert native['status']=='PASS' and len(native['checks'])==14 and native['networkModules']==37 and native['nativeFiles']==57
    pin='9f90460a952bcf56070bda145b2c960a8e1ca1fcb44c1eab0e51aaf5a392552d'
    assert native['manifestSHA256']==values['hosted-client-native-repro-r2']['manifestSHA256']==values['hosted-client-native-app-compose-r2']['manifestSHA256']==pin
    exported=values['hosted-client-worker-export-r1'];assert exported['status']=='PASS' and not exported['installed']
    for kind,manifest in [('worker','room-worker.json'),('operator','room-operator.json')]:
        folder=ROOT/exported[kind]['directory'];assert digest(folder/manifest)==exported[kind]['manifestSHA256']
        for name,row in json.loads((folder/manifest).read_bytes())['files'].items():assert digest(folder/name)==row['sha256']==digest(ROOT/name)
    h=values['hosted-client-source-final-health-r1'];assert h['status']=='PASS' and h['ownedBrowserContextsRemaining']==0 and not h['pendingJournals']
    assert h['runtime']['manifestSHA256']=='440f0c19892cde73fe893c139a86d9163e729af9f37c41d5ecd5221bbbbcbe8a' and len(h['ownedAccounts'])==7
    return {'status':'PASS','scope':__doc__,'sourceBundledPaneBrowserChecks':25,'actualSourceBrowsers':1,'actualSourceV86Guests':0,
        'legacyCoreChecks':38,'legacyBrowserChecks':15,'inactiveNative20ReleaseChecks':14,'inactiveNative20ManifestSHA256':pin,
        'inactiveNative20DeclaredFiles':519,'inactiveNative20NetworkModules':37,'inactiveWorkerManifestSHA256':exported['worker']['manifestSHA256'],
        'realIndexedDBAndPageReload':True,'modelStaleWriterFromIndependentDatabaseConnection':True,'actualConcurrentTabsTested':False,
        'lostCommittedResponseOriginalReceiptRecoveredOnce':True,'persistentCreationIntentRecoveryImplemented':True,'expiredMissingSubmissionDraftPreserved':True,
        'sourceHostedClientAndBundledPaneImplemented':True,'native20Installed':False,'sharedClientLiveInProduction':False,
        'P2PHostedDeliveryImplemented':False,'hostedChessStateImplemented':False,'actual8kNetworkTested':False,
        'ownedBrowserContextsRemaining':0,'productionChanged':False,'privateVMChanged':False,'wholeGoalComplete':False,
        'receiptSHA256':receipts,'sourceSHA256':digest(Path(__file__))}
if __name__=='__main__':
    out=CHECKS/'hosted-client-milestone-r1-result.json';assert not out.exists();v=run();out.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
