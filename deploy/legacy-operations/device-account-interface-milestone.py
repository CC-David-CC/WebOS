#!/usr/bin/env python3
"""Bind the packaged contact/enrollment UI and unchanged membership regressions."""
import hashlib,importlib.util,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CHECKS=ROOT/'.build/checks'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('interface_cleanup',ROOT/'scripts/device-account-admission-milestone.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
def inventory(folder):return {str(p.relative_to(folder)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(folder.rglob('*')) if p.is_file()}
def run():
 read=lambda n:json.loads((CHECKS/n).read_bytes());build=read('device-account-interface-build-r1-result.json');code=build['compiledSHA256'];ui=read('device-account-interface-r6-result.json');members=read('device-account-interface-members-r1-result.json');receipts={}
 for name,v,count,driver in [('device-account-interface-r6-result.json',ui,20,'device-account-interface-check.py'),('device-account-interface-members-r1-result.json',members,16,'device-membership-check.py')]:
  assert v['status']=='PASS' and len(v['checks'])==count and v['actualCompiledCoreSHA256']==code
  for path,digest in v['sourceSHA256'].items():assert sha(ROOT/path)==digest,(name,path)
  assert v['driverSHA256']==sha(ROOT/'scripts'/driver)
  helpers.clean(v);assert not v.get('cleanupError') and not v.get('cleanupErrors')
  if 'cleanup' in v:assert all(v['cleanup'].values())
  if 'ownedProfilesRemoved' in v:assert v['ownedProfilesRemoved'] and v['fixtureRemoved']
  receipts[name]={'sha256':sha(CHECKS/name),'checks':count}
 for path,digest in ui['appSourceSHA256'].items():assert sha(ROOT.parent/path)==digest,path
 for path,digest in ui['fixtureSourceSHA256'].items():assert sha(ROOT/path)==digest,path
 assert ui['actualBrowserProfiles']==3 and ui['actualBrowserLaunches']==5 and ui['actualRTCLinks']==3
 assert members['byteCreditsEnabled'] and members['heldReadRevocation']['readerHeightBeforeRelease']==members['heldReadRevocation']['readerHeightAfterRefusal']==7
 assert ui['appCatalogSHA256']==members['appCatalogSHA256']
 service=Path(build['directory']);manifest=json.loads((service/'shared-service.json').read_bytes());assert sha(service/'shared-service.json')==build['manifestSHA256'] and sha(service/manifest['path'])==code
 rebuild=read('device-account-interface-rebuild-r1-result.json');assert rebuild['status']=='PASS' and rebuild['compiledSHA256']==code and rebuild['manifestSHA256']==build['manifestSHA256'] and inventory(service)==rebuild['files'];receipts['device-account-interface-rebuild-r1-result.json']={'sha256':sha(CHECKS/'device-account-interface-rebuild-r1-result.json')}
 qa=ROOT/build['qaHelper'];assert sha(qa/'apps.json')==build['qaCatalogSHA256']
 allapps=ROOT/'.build/public-apps/device-account-interface-all-r1';catalog=json.loads((allapps/'apps.json').read_bytes());by={a['id']:a for a in catalog['apps']};assert set(by)=={'calculator','chat','files','help','rooms','terminal','text'}
 subset={**catalog,'apps':[by[k] for k in ['chat','rooms','calculator']]};assert hashlib.sha256((json.dumps(subset,indent=2)+'\n').encode()).hexdigest()==ui['appCatalogSHA256']
 for app in catalog['apps']:
  folder=allapps/Path(app['path']).parent.relative_to('assets/desktop');assert inventory(folder)==app['files'];assert sha(folder/'index.mjs')==app['sha256']
 retained={}
 for name,driver,module in [('device-account-interface-r1-result.json','device-account-interface-r1-before-driver.py','device-account-interface-output-clear-before.mjs'),('device-account-interface-r2-result.json','device-account-interface-r2-driver.py','device-account-interface-output-clear-before.mjs'),('device-account-interface-r3-result.json','device-account-interface-r3-driver.py','device-account-interface-metadata-block-before.mjs'),('device-account-interface-r4-result.json','device-account-interface-r4-driver.py','device-account-interface-metadata-block-before.mjs'),('device-account-interface-r5-result.json','device-account-interface-r5-driver.py','device-account-interface-anon-before.mjs')]:
  old=read(name);assert old['driverSHA256']==sha(CHECKS/driver);assert old['appSourceSHA256']['served_apps_public/shared/account-channel-view.mjs']==sha(CHECKS/module)
  assert old['cleanup'] and all(old['cleanup'].values()) and not old.get('cleanupErrors');helpers.clean(old)
  retained[name]={'status':old['status'],'checks':len(old['checks']),'sha256':sha(CHECKS/name)}
 assert retained['device-account-interface-r1-result.json']['status']=='FAIL' and retained['device-account-interface-r2-result.json']['status']=='FAIL'
 with urllib.request.urlopen('http://127.0.0.1:19515/sessions') as response:assert not json.load(response)['value']
 return {'status':'PASS','scope':__doc__,'compiledSHA256':code,'manifestSHA256':build['manifestSHA256'],'successfulCurrentAssertions':36,'appCatalogSHA256':ui['appCatalogSHA256'],'allAppsCatalogSHA256':sha(allapps/'apps.json'),'receipts':receipts,'retainedEarlierResults':retained,'inventories':{str(folder.relative_to(ROOT)):inventory(folder) for folder in [service,qa,allapps]},'ownedBrowserSessions':0,'releaseReady':False,'sourceOnly':True,'productionChanged':False,'wholeGoalComplete':False,'limits':'UI20 uses real registered identities/HTTP/IDB/RTC and rendered controls, one configured voter/3profiles/5launches. Anonymous mount makes no private metadata requests/folders. Held HTTP is delayed, not a fabricated response. Membership16 separately exercises4actual voters/local-development anonymous users with credits. No multi-voter enrollment/WAN/phone/full desktop/8k/efficiency/automatic discovery or live/rollback pass. Old f948 protocol/admission87 remains historical; these source modules are unchanged apart from an additive guarded peerIdentity facade in DeviceChannelSession.','next':'Automatic contact/peer discovery and account-device policy, remaining low-data/global/relay/rollback/routing/islands/joint-voter/long-gap/chess/PoW/8k/WAN/audit/reviewed rollout obligations; keep live chat paused.'}
if __name__=='__main__':
 result=run();out=CHECKS/'device-account-interface-milestone-r1-result.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','compiledSHA256','successfulCurrentAssertions','ownedBrowserSessions','releaseReady']}))
