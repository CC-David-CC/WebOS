#!/usr/bin/env python3
"""Bind credit refusal race repair; scoped correctness, not full efficiency/rollout."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES=[('device-byte-credit-binding-r14-result.json',5,'device-credit-binding-recovery-check.py'),('device-byte-credit-mesh-r14-result.json',26,None),('device-byte-credit-mesh-r14-production-cadence-result.json',26,'device-member-peers-check.py'),('device-byte-credit-native-r14-phase-result.json',14,'device-byte-credit-check.py'),('device-byte-credit-members-r14-result.json',16,'device-membership-check.py'),('device-byte-credit-default-r14-result.json',3,'device-byte-default-check.py'),('device-byte-credit-refusal-r14-result.json',0,'device-credit-refusal-recovery-check.py'),('device-byte-credit-build-r14-result.json',0,None),('device-byte-credit-rebuild-r14-result.json',0,None),('device-byte-credit-boundary-r5-result.json',9,None),('device-byte-credit-live-unchanged-r14-result.json',0,None)]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(v,name):
 if 'ownedProfilesRemoved' in v:assert v['ownedProfilesRemoved'] and v['fixtureRemoved'],name
 if 'ownedProfileRemoved' in v:assert v['ownedProfileRemoved'] and v['fixtureRemoved'],name
 for key,value in v.items():
  assert not key.endswith('CleanupError'),(name,key)
  if key.endswith('Cleanup') and isinstance(value,dict) and 'network' in value:
   budget=value['network'].get('budget',value['network']);assert all(n==0 for k,n in budget.items() if k!='closed'),(name,key)
def burst(v):
 a=v['measurements']['burstStart'];b=v['measurements']['burstAccepted'];assert set(a['participants'])==set(b['participants']) and len(a['participants'])==8;wire={};rpc={}
 for side,p in b['participants'].items():
  old=a['participants'][side];before=old['wire']['categories'];after=p['wire']['categories'];assert sum(c['bytes'] for c in after.values())==p['wire']['bytes']
  for k in set(before)|set(after):
   delta=after.get(k,{}).get('bytes',0)-before.get(k,{}).get('bytes',0);assert delta>=0;wire[k]=wire.get(k,0)+delta
  for k in set(old['rpcProfile'])|set(p['rpcProfile']):
   row=rpc.setdefault(k,{f:0 for f in ['calls','success','failed','inputBytes','outputBytes']})
   for f in row:row[f]+=p['rpcProfile'].get(k,{}).get(f,0)-old['rpcProfile'].get(k,{}).get(f,0)
 return {'bytes':sum(wire.values()),'seconds':round(b['elapsedSeconds']-a['elapsedSeconds'],3),'wireCategories':dict(sorted(wire.items(),key=lambda x:-x[1])),'RPC':rpc,'scope':'Observed8message/8profile window with concurrent validation/history/retries. RPC JSON sizes differ from signed wire categories; not isolated per-message, IP/monthly or statistically controlled cost.'}
def run():
 checks=ROOT/'.build/checks';read=lambda name:json.loads((checks/name).read_text());build=read(CASES[7][0]);code=build['compiledSHA256'];receipts={};values={}
 for name,count,driver in CASES:
  v=read(name);values[name]=v;assert v['status']=='PASS' and len(v.get('checks',[]))==count,name
  actual=v.get('actualCompiledCoreSHA256',v.get('compiledSHA256'));assert actual in [None,code],name
  sources=v.get('sourceSHA256',{})
  if isinstance(sources,str):assert name==CASES[-1][0] and sources==digest(ROOT/'scripts/browser-files-live-publish.py')
  else:
   for path,sha in sources.items():assert digest(ROOT/path)==sha,(name,path)
  if driver:assert v.get('driverSHA256',sources.get('scripts/'+driver))==digest(ROOT/'scripts'/driver),(name,driver)
  clean(v,name);receipts[name]={'sha256':digest(checks/name),'checks':count}
 service=Path(build['directory']);m=json.loads((service/'shared-service.json').read_text());assert digest(service/'shared-service.json')==build['manifestSHA256'] and digest(service/m['path'])==code
 for name,r in m['files'].items():
  p=(service/m['path']).parent/name;assert p.stat().st_size==r['bytes'] and digest(p)==r['sha256']
 qa=ROOT/build['qaHelper'];assert digest(qa/'apps.json')==build['qaCatalogSHA256'];assert json.loads((qa/'apps.json').read_text())['apps'][0]['sha256']==code;assert digest(ROOT/build['allApps']/'apps.json')==build['allAppsCatalogSHA256']
 snap=read('device-byte-credit-mesh-driver-r14-result.json');assert hashlib.sha256(snap['driverSource'].encode()).hexdigest()==snap['driverSHA256']==values[CASES[1][0]]['driverSHA256'];receipts['device-byte-credit-mesh-driver-r14-result.json']={'sha256':digest(checks/'device-byte-credit-mesh-driver-r14-result.json'),'scope':'Exact accelerated-cadence driver before optional production round settings'}
 for index in [1,2]:
  v=values[CASES[index][0]];assert v['byteCreditsEnabled'] and v['actualBrowsers']==9 and v['actualBrowserLaunches']==10 and v['actualV86Desktops']==0;assert v['idleWindow']['seconds']>=20 and v['idleWindow']['payloadBytes']<=4096
  for p in v['afterIntroductions'].values():assert p['admissions']<=6 and p['neighbors']<=6 and p['pending']<=2
 assert values[CASES[2][0]]['productionRoundCadence']
 binding=values[CASES[0][0]];assert binding['actualBrowsers']==2 and binding['actualRTCLinks']==1 and binding['heldDownloadAllocation']==0;assert binding['refusedRead']['elapsedMs']<3000 and any(f['stage']=='authorize' and f['error']=='A fresh native channel binding is required for receive credits' for f in binding['heldCreditFailure'])
 old=read('device-byte-credit-binding-r13-result.json');assert old['status']=='OBSERVED' and len(old['checks'])==5 and old['refusedRead']['elapsedMs']>=14000 and old['heldDownloadAllocation']==0;assert old['driverSHA256']==digest(ROOT/'scripts/device-credit-binding-check.py');clean(old,'old-binding');prior=read('device-byte-credit-build-r13-result.json');assert old['actualCompiledCoreSHA256']==prior['compiledSHA256']
 archived=read('device-byte-credit-controller-r13-source-result.json');assert archived['compiledSHA256']==prior['compiledSHA256'] and hashlib.sha256(archived['sourceText'].encode()).hexdigest()==archived['sourceSHA256']
 for path,sha in old['sourceSHA256'].items():assert (archived['sourceSHA256'] if path=='network/device-channel-bandwidth.mjs' else digest(ROOT/path))==sha,path
 for name in ['device-byte-credit-binding-r13-result.json','device-byte-credit-build-r13-result.json','device-byte-credit-controller-r13-source-result.json']:receipts[name]={'sha256':digest(checks/name),'scope':'Before-fix actual native ordering proof / exact archived diagnostic source'}
 unit=values[CASES[6][0]]['observed'];assert unit['before']=={'replies':9,'allZero':True,'allocated':0,'denied':9,'observations':8,'bounded':True};assert unit['after']['bytes']==16384 and unit['unauthorizedRejected'] and unit['diagnosticsCleared'] and unit['leasesZero']
 live=values[CASES[-1][0]]['steps'][0]['receipt'];assert live['chatDisabled'] and live['chatDatabaseUnchangedAndEmpty'] and not live['rootMinted'] and not live['dataRestored']
 return {'status':'PASS','scope':__doc__,'refusalRaceProofsVerified':True,'compiledSHA256':code,'manifestSHA256':build['manifestSHA256'],'receipts':receipts,'successfulCurrentAssertions':90,'unchangedCompilerBoundaryChecks':9,'bindingRace':{'beforeCompiledSHA256':old['actualCompiledCoreSHA256'],'oldWaitMs':old['refusedRead']['elapsedMs'],'newRefusalMs':binding['refusedRead']['elapsedMs'],'downloadAllocatedBeforeNativeBinding':0,'scope':'Two real local-development browser/IDB/ECDSA/RTC profiles; original verifier paused/resumed, no fake signature/grant. Different owned test identities; not physical WAN latency.'},'quietWindows':[values[CASES[i][0]]['idleWindow'] for i in [1,2]],'acceleratedBurst':burst(values[CASES[1][0]]),'productionRoundCadenceBurst':burst(values[CASES[2][0]]),'releaseReady':False,'lowDataEfficiencyAccepted':False,'wholeGoalComplete':False,'productionChanged':False,'liveChatPaused':True,'liveReadiness':'Preservation only; Root4 expired/steward failed, explicit Root5 recovery approval pending.','limits':'Finite local-development native Chrome/IDB/crypto/RTC, fixed4voters; one-browser fake-peer refusal/ring unit separate. Native14 includes4units. Two mesh26 runs9profiles/10launches/17RTC; production-round run changes scheduler settings only, keeps QA peer sampling/10s allocations/6s credits. Quiet20s excludes IP/RTC/TURN/assets/longer maintenance. No physical3G/fiber/loss/WAN/8k/adaptive routing/durable global/legacy/full-relay acceptance. Prior quiet failures remain evidence, not relabeled passes.','next':'Reduce duplicate full-batch activity announcements (largest measured RPC input bucket) and status work while locally batching, preserving validated-original wakeup with an absent leader and native quorum/hash/ACL/withheld-value recovery. Continue global/relay/durable/legacy budgets, islands/joint validators/long-gap/chess/PoW/8k/WAN/audit/rollout.'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v[k] for k in ['status','compiledSHA256','successfulCurrentAssertions','bindingRace','quietWindows','releaseReady']}))
