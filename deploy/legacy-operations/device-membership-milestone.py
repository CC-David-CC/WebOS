#!/usr/bin/env python3
"""Bind scoped ordinary-member proofs; live chat and full goal remain unfinished."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAMES=['device-membership-transport-bundled-r4-result.json','device-membership-auto-bundled-r3-result.json','device-membership-session-bundled-r2-result.json','device-membership-peer-bundled-r2-result.json','device-membership-archive-bundled-r2-result.json','device-membership-core-bundled-r2-result.json','device-membership-build-r3-result.json','device-membership-public-inputs-r1-result.json','device-membership-bundled-r5-result.json','device-membership-live-unchanged-r1-result.json']
def run():
 s=importlib.util.spec_from_file_location('member_evidence_binding',ROOT/'scripts/device-replica-network-milestone.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);out=m.run(names=NAMES,build_index=6,service_name='device-membership-r3');checks=ROOT/'.build/checks'
 counts={0:37,1:17,2:40,3:35,4:41,5:43,7:9,8:16}
 for index,count in counts.items():
  v=json.loads((checks/NAMES[index]).read_bytes());assert len(v['checks'])==count,(NAMES[index],count)
 for index,driver in [(0,'device-replica-network-check.py'),(1,'device-automatic-round-check.py'),(8,'device-membership-check.py')]:
  v=json.loads((checks/NAMES[index]).read_bytes());assert v.get('driverSHA256',v.get('sourceSHA256',{}).get('scripts/'+driver))==hashlib.sha256((ROOT/'scripts'/driver).read_bytes()).hexdigest()
 members=json.loads((checks/NAMES[8]).read_bytes());assert members['actualBrowsers']==6 and members['actualBrowserLaunches']==7 and members['actualV86Desktops']==0 and members['actualRTCLinks']==10
 for name,sha in members['sourceSHA256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
 for key,v in members.items():
  if key.endswith('Cleanup'):assert v['owner']['members']['responses']==v['owner']['members']['tasks']==0 and v['owner']['scheduler']=={'closed':True,'channels':0,'timers':0,'deadlines':0,'jobs':0}
  assert not key.endswith('CleanupError'),key
 core=json.loads((checks/NAMES[5]).read_bytes());assert core['sourceUnchangedThroughoutRun']
 out.update(scope=__doc__,limits='Explicit connections:6native member profiles/7browser launches/10RTC links/4fixed validators plus1ordinary writer and1observer;0v86/local-development identities. No automatic mesh, joint validator changes, long-gap fast-forward,8k/WAN or complete Byzantine liveness proof.',next='Joint validator membership, automatic introductions/partial meshes/islands/bridges/reconnect/fallback, long-gap/no-replay recovery, separate chess/chat composition, browser admission work, adversarial scale/resource/WAN/full audit and reviewed live rollout')
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
