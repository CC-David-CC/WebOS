#!/usr/bin/env python3
"""Bind automatic fixed-committee recovery proofs; no live or8k claim."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAMES=['device-scheduler-transport-bundled-r2-result.json','device-scheduler-app-bundled-r3-result.json','device-scheduler-session-bundled-r2-result.json','device-scheduler-peer-bundled-r2-result.json','device-scheduler-archive-bundled-r2-result.json','device-scheduler-core-bundled-r2-result.json','device-scheduler-build-r2-result.json','device-scheduler-public-inputs-r1-result.json','device-scheduler-live-unchanged-r1-result.json']
def run():
 s=importlib.util.spec_from_file_location('scheduler_evidence_binding',ROOT/'scripts/device-replica-network-milestone.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);out=m.run(names=NAMES,build_index=6,service_name='device-scheduler-r2');checks=ROOT/'.build/checks';app=json.loads((checks/NAMES[1]).read_bytes());assert len(app['checks'])==17 and app['actualBrowserLaunches']==5 and app['actualRTCLinks']==13 and app['actualV86Desktops']==0;assert app['driverSHA256']==hashlib.sha256((ROOT/'scripts/device-automatic-round-check.py').read_bytes()).hexdigest()
 for key,v in app.items():
  if key.endswith('Cleanup'):assert v['automatic']=={'closed':True,'channels':0,'timers':0,'deadlines':0,'jobs':0},key
  assert not key.endswith('CleanupError'),key
 core=json.loads((checks/NAMES[5]).read_bytes());assert core['sourceUnchangedThroughoutRun'] and len(core['checks'])==43
 out.update(scope=__doc__,limits='4fixed native validators/5actual app-browser launches/13RTCconnections/0v86; test signaling and reconnect setup explicit, automatic round changes and certified catch-up real. No general membership, automatic mesh,8k,WAN or complete Byzantine liveness proof.',next='Durable/revocable general membership and joint committee changes, long-gap/no-replay recovery, automatic partial mesh/islands/bridges/fallback, chess/chat composition, bounded admission PoW, staged8k/resource/bandwidth/freshWAN/full audit')
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
