#!/usr/bin/env python3
"""Bind native25 live-first publication and targeted public/source evidence."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PIN='46c878c394203e962680e1b09acf51cd5bdf625e5eeea3901f8664d6e2db024e'
NAMES=['reader-directory-mail-source-r1','reader-mail-native-build-r1','reader-mail-native-build-r2','reader-mail-native-release-r1','reader-mail-legacy-client-r1','reader-mail-live-source-sync-r1','reader-mail-live-publisher-install-r1','reader-mail-live-stage-r1','reader-mail-live-activate-backend-r1','reader-mail-live-activate-r1','reader-mail-live-verify-r1','reader-mail-public-ui-r1','reader-mail-public-wan-r1','reader-mail-live-final-health-r1','reader-mail-live-smoke-r1','reader-mail-cleanup-verified-r1','reader-mail-root-receipts-verified-r1','reader-mail-wan-cleanup-r1']
def run():
 values={};records={}
 for n in NAMES+['reader-directory-mail-negative-r1']:
  p=ROOT/'.build/checks'/(n+'-result.json');raw=p.read_bytes();v=json.loads(raw);expected='FAIL'if n=='reader-directory-mail-negative-r1'else'PASS'
  if n=='reader-mail-live-smoke-r1':assert len(v['sites'])==10 and all(s['result']=='PASS'for s in v['sites'].values())
  else:assert v['status']==expected,n
  values[n]=v;records[n]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'status':expected,'checks':len(v.get('checks',[]))}
 source=values['reader-directory-mail-source-r1'];assert len(source['checks'])==10 and not source['sourceChangedDuringTest'] and source['ownedBrowserContextsClosed']==4
 for a,b in zip(source['healthyMailboxProbe']['before'],source['healthyMailboxProbe']['after']):assert b-a>=2
 negative=values['reader-directory-mail-negative-r1'];assert len(negative['checks'])==3 and negative['error'].startswith('healthy real RTC readers') and negative['ownedBrowserContextsClosed']==4 and negative['healthyMailboxProbe']['before']==negative['healthyMailboxProbe']['after']
 for name,count in [('reader-mail-public-ui-r1',17),('reader-mail-public-wan-r1',12)]:
  v=values[name];assert len(v['checks'])==count and v['nativeManifestSHA256']==PIN and v['defaultPublicTLS'] and not v['fixtureSPKIOnly'] and v['ownedAccountPolicy']['disabled']
 ui=values['reader-mail-public-ui-r1'];assert ui['fullRoomsReopenCycles']==36
 samples=ui['lifecycleBudgetSamples'];assert len(samples)==4 and all(s['budget']==samples[0]['budget']for s in samples)
 wan=values['reader-mail-public-wan-r1'];assert wan['publicWANTested'] and len(set(wan['publicIPs'].values()))==2 and wan['manualSeedLinks']==0 and wan['completeRTCPartitionRepaired'] and wan['returnedToP2P'] and wan['actualV86Desktops']==3 and wan['ownedBrowserContextsClosed']==3
 pairs=[p for key in ['introducedLinkEvidence','repairedLinkEvidence']for end in wan[key]for p in end['pairs']];assert len(pairs)==4 and all(p['state']=='connected' and p['localType']==p['remoteType']=='relay' and p['relayProtocol']=='tls' and p['turnURL'].startswith('turns:turn.ksu.codes:443')for p in pairs)
 health=values['reader-mail-live-final-health-r1'];assert health['nativeManifestSHA256']==PIN and health['verifiedReleaseFiles']==705 and health['publicPrototypeFilesVerified']==133 and health['publicBlogBytesPreserved'] and health['registeredOnlyEgressPolicyUnchanged'] and health['rootRevision']==3
 cleanup=values['reader-mail-cleanup-verified-r1'];assert cleanup['ownedLocalBrowserContexts']==0 and cleanup['actualPublicQAAccountsDisabled']==2 and cleanup['localForwardMissing'] and cleanup['outside']['driverMissing'] and cleanup['outside']['folderMissing']
 assert len(values['reader-mail-root-receipts-verified-r1']['receipts'])==5
 for name in ['activate','verify']:assert values['reader-mail-live-'+name+'-r1']['nativeManifestSHA256']==PIN
 return {'status':'PASS','scope':__doc__,'receipts':records,'nativeManifestSHA256':PIN,'publicUIOpenCloseCycles':36,'separateNetworkLinuxRecoveryVerified':True,'fresh705Installed133PrototypeBlogAnd10SitesVerified':True,'ownedBrowsersAndOutsideFixtureCleaned':True,'workflow':'User-directed live-first development; VM is not a release gate','wholeGoalComplete':False,'operationalStabilityComplete':False,'largeIslandsOr8000TransportVerified':False,'independentReplicaConvergenceComplete':False,'durableLongChessComplete':False,'sourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+chr(10));print(json.dumps({'status':'PASS','boundReceipts':len(v['receipts']),'wholeGoalComplete':False}))
