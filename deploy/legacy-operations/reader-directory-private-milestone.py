#!/usr/bin/env python3
"""Bind scoped directory source/installed-private evidence; production remains22."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NATIVE='a2086017e7dcc87a7c1126bb7c71b62fd5ae0e7c1f94567444491850d1862a34'
LIVE='9537a6b6d4ab7074512d48e13c46121282980e7197a7aaf3b1c3f7ddc8199f6a'
WORKER='3a6d3c5184e52858abe324e37fd4ca410f66d7d289468efe6f169352d347727b'
OPERATOR='53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc'
NAMES=['reader-rendezvous-api-r4','reader-rendezvous-mounted-r1','reader-directory-islands-r2','reader-rendezvous-legacy-api-r1','reader-rendezvous-legacy-client-r1','reader-rendezvous-legacy-peers-r1','reader-directory-native-release-r1','reader-rendezvous-export-contract-r1','reader-rendezvous-private-stage-r1','reader-rendezvous-private-code-r1','reader-directory-private-upgrade-r1','reader-directory-private-linux-r1','reader-directory-private-ui-quiescent-r1','reader-directory-private-cycle-r1','reader-directory-before-live-health-r1']

def run():
    records={};values={}
    def load(name,status='PASS'):
        path=ROOT/'.build/checks'/(name+'-result.json');raw=path.read_bytes();v=json.loads(raw);assert v['status']==status,name
        values[name]=v;records[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'status':status,'checks':len(v.get('checks',[]))};return v
    for name in [*NAMES,'reader-directory-private-final-health-r1','current-feature-operations-inspect-r1']:load(name)
    for name,length in [('reader-rendezvous-api-r4',20),('reader-rendezvous-mounted-r1',20),('reader-directory-islands-r2',9),('reader-rendezvous-private-code-r1',22),('reader-directory-private-linux-r1',11),('reader-directory-private-ui-quiescent-r1',17),('reader-directory-private-cycle-r1',2)]:assert len(values[name]['checks'])==length
    code=values['reader-rendezvous-private-code-r1'];assert code['workerManifestSHA256']==WORKER and code['operatorManifestSHA256']==OPERATOR and code['actualCodeProcessDeaths']==7 and not code['dataRestored'] and not code['rootMinted'] and code['allPriorKeysAccountsCookieFilesAndUsagePreserved']
    upgraded=values['reader-directory-private-upgrade-r1'];assert upgraded['nativeManifestSHA256']==NATIVE and upgraded['rootCustodyAndPermissionRowsUnchanged'] and upgraded['keysAccountsCookieFilesAndCountersPreserved']
    linux=values['reader-directory-private-linux-r1'];assert linux['nativeManifestSHA256']==NATIVE and linux['actualV86Desktops']==3 and linux['manualSeedLinks']==0 and linux['completeRTCPartitionRepaired'] and linux['returnedToP2P']
    ui=values['reader-directory-private-ui-quiescent-r1'];assert ui['nativeManifestSHA256']==NATIVE and ui['fullRoomsReopenCycles']==36 and ui['actualPageReload'] and ui['workspaceDOMAndDraftsPreserved']
    samples=ui['lifecycleBudgetSamples'];assert len(samples)==4 and all(s['budget']==samples[0]['budget'] and s['hostedViews']==samples[0]['hostedViews'] and s['meshViews']==samples[0]['meshViews'] for s in samples)
    for v,count in [(linux,3),(ui,1)]:assert v['ownedBrowserContextsClosed']==count and v['ownedAccountPolicy']['disabled']
    cycle=values['reader-directory-private-cycle-r1'];assert [s['nativeManifestSHA256']for s in cycle['steps']]==[LIVE,NATIVE] and cycle['roomStateUnchanged'] and cycle['rootCustodyAndPermissionsRetained'] and not cycle['dataRestored']
    live=values['reader-directory-before-live-health-r1'];assert live['nativeManifestSHA256']==LIVE and live['verifiedReleaseFiles']==615 and live['publicPrototypeFilesVerified']==133 and live['publicBlogBytesPreserved'] and not live['servicesRestarted']
    health=values['reader-directory-private-final-health-r1'];assert health['runtime']==cycle['runtime'] and health['roomHealth']['status']=='PASS' and health['ownedLocalBrowserContexts']==0 and len(health['ownedTestAccounts'])==4 and all(p['testVerifiedDisabled']for p in health['ownedTestAccounts'])
    # Preserve failed oracles as failures. The diagnostic explains the exact
    # baseline error; the revised test admits no incremental resource growth.
    old=load('reader-directory-private-ui-r1','FAIL');assert len(old['checks'])==8 and old['error']=='twelve full Rooms reopen cycles release both mesh and hosted observers'
    diagnostic=load('reader-directory-private-ui-diagnostic-r1','FAIL');a,b=[s['value']for s in diagnostic['lifecycleBudgetSamples']];assert a['hostedViews']==b['hostedViews'] and a['meshViews']==b['meshViews'] and b['budget']['metadataBytes']-a['budget']['metadataBytes']==4096
    assert all(a['budget'][k]==b['budget'][k]for k in a['budget']if k!='metadataBytes') and a['hosted']['delivery']['directory']['bootstrap']==0 and b['hosted']['delivery']['directory']['bootstrap']==1
    for kind,count in [('recipient',9),('replay',6)]:
        v=load('reader-rendezvous-'+kind+'-control-r1','FAIL');assert len(v['checks'])==count and v['intendedOracleFailed']
    stage=load('reader-rendezvous-private-stage-before-r1','FAIL');assert not stage['activated']
    islands=load('reader-directory-islands-r1','FAIL');assert len(islands['checks'])==5
    return dict(status='PASS',scope=__doc__,receipts=records,nativeManifestSHA256=NATIVE,workerManifestSHA256=WORKER,operatorManifestSHA256=OPERATOR,liveNativeManifestSHA256=LIVE,
        productionCandidateActivated=False,privateLinuxCompleteSplitRepair=True,privateUIReopenCycles=36,actualWorkerProcessDeaths=7,privateActualCodeInverse=True,retainedNonemptyCurrentData=True,
        resourceFailureExplainedWithoutProductChange=True,publicWAN23Verified=False,physicalPhone23Verified=False,largeIslandsOr8000TransportVerified=False,
        operationalStabilityComplete=False,wholeGoalComplete=False,sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
    value=run();a.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':value['status'],'boundReceipts':len(value['receipts']),'productionCandidateActivated':False,'wholeGoalComplete':False}))
