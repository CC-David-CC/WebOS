#!/usr/bin/env python3
"""Bind scoped low-data/member proofs; this is not live or mixed-link acceptance."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES=[('device-member-data-transport-bundled-r8-result.json',40),('device-member-data-mesh-bundled-r13-result.json',26),('device-member-data-session-bundled-r8-result.json',40),('device-member-data-peer-bundled-r8-result.json',35),('device-member-data-archive-bundled-r8-result.json',41),('device-member-data-core-bundled-r8-result.json',43),('device-member-data-auto-bundled-r8-result.json',17),('device-member-data-members-bundled-r9-result.json',16),('device-member-data-build-r8-result.json',0),('device-member-data-public-inputs-r6-result.json',9),('device-member-data-rebuild-r8-result.json',0),('device-member-data-live-unchanged-expired-root-r1-result.json',0)]
def run():
 spec=importlib.util.spec_from_file_location('data_proof_binding',ROOT/'scripts/device-replica-network-milestone.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 out=m.run(names=[name for name,_ in CASES],build_index=8,service_name='device-member-data-r8');checks=ROOT/'.build/checks'
 for name,count in CASES:
  v=json.loads((checks/name).read_bytes());assert len(v.get('checks',[]))==count,name
  sources=v.get('sourceSHA256',{})
  if isinstance(sources,str):assert name==CASES[-1][0] and sources==hashlib.sha256((ROOT/'scripts/browser-files-live-publish.py').read_bytes()).hexdigest(),name
  else:
   for path,sha in sources.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,(name,path)
 for index,driver in [(0,'device-replica-network-check.py'),(1,'device-member-peers-check.py'),(6,'device-automatic-round-check.py'),(7,'device-membership-check.py')]:
  v=json.loads((checks/CASES[index][0]).read_bytes());assert v.get('driverSHA256',v.get('sourceSHA256',{}).get('scripts/'+driver))==hashlib.sha256((ROOT/'scripts'/driver).read_bytes()).hexdigest()
 mesh=json.loads((checks/CASES[1][0]).read_bytes());assert mesh['actualBrowsers']==9 and mesh['actualBrowserLaunches']==10 and mesh['actualV86Desktops']==0
 assert mesh['idleWindow']['payloadBytes']<=4096 and mesh['idleWindow']['seconds']>=20
 for key,v in mesh.items():
  assert not key.endswith('CleanupError'),key
  if key.endswith('Cleanup'):assert v['owner']['peerOrganization']==[] and v['owner']['tasks']==v['owner']['members']['tasks']==v['owner']['members']['responses']==0 and v['owner']['scheduler']=={'closed':True,'channels':0,'timers':0,'deadlines':0,'jobs':0}
 live=json.loads((checks/CASES[-1][0]).read_bytes())['steps'][0]['receipt']
 # Publisher verify checks preserved release/data, not readiness of every role.
 # An expired development seed legitimately stopped the live steward meanwhile.
 out.update(scope=__doc__,releaseReady=False,actualMesh={'profiles':9,'launches':10,'RTCLinks':mesh['actualRTCLinks'],'v86':0,'identities':'local-development'},idleWindow=mesh['idleWindow'],measurements=mesh['measurements'],liveNative=live['native'],liveReadiness='Steward failed after development Root4 seed expiry; Root5 renewal approval pending. No fresh live identity/Internet acceptance claim.',limits='Local native browser/IDB/crypto/RTC partial mesh, bounded one-hop introductions and fixed4validator committee. No emulated3G/fiber, hard byte caps, automatic link adaptation, generalized islands/multi-hop writes,8k/WAN, long-gap/chess/PoW or full Byzantine liveness acceptance.',retainedFailures=['device-member-data-mesh-bundled-r7-result.json: late join could not find spare one-hop capacity','device-member-data-mesh-bundled-r8-result.json: test assertion syntax error, corrected','device-member-data-mesh-bundled-r9-result.json: temporary refusal discarded acknowledged update hint; deterministic refusal/retry added in current candidate','device-member-data-members-bundled-r7-result.json: one-shot positive post-regrant bind raced transient capacity; only that idempotent binding now uses bounded busy retries; negative ACL probes unchanged','device-member-data-members-bundled-r8-result.json: ordinary submission stalled behind absent leader; native-validated activity propagation and deterministic offline-leader fixture added'],setupBusyRefusals=mesh.get('setupBusyRefusals',0),next='Receiver-controlled byte/relay budgets and mixed asymmetric links; capacity-aware discovery/routing/islands/fallback; joint validators, long-gap no-replay recovery/chess/PoW/8k/WAN; reviewed rollout. Keep live chat paused.')
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'receipts':len(v['receipts']),'releaseReady':v['releaseReady'],'liveReadiness':v['liveReadiness']}))
