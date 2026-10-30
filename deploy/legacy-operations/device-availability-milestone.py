#!/usr/bin/env python3
"""Bind voted-value retention/old-voter compatibility evidence, not global liveness."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAMES=['device-availability-network-bundled-r2-result.json','device-availability-app-bundled-r1-result.json','device-availability-session-bundled-r1-result.json','device-availability-archive-bundled-r1-result.json','device-availability-core-bundled-r2-result.json','device-availability-build-r1-result.json','device-availability-public-inputs-r1-result.json','device-availability-live-unchanged-r1-result.json']
def run():
 s=importlib.util.spec_from_file_location('replica_evidence_binding',ROOT/'scripts/device-replica-network-milestone.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);out=m.run(names=NAMES,build_index=5,service_name='device-availability-r1');checks=ROOT/'.build/checks';core=json.loads((checks/NAMES[4]).read_bytes());assert core['sourceUnchangedThroughoutRun'] and core['legacyCompiledCoreSHA256']=='c9e569f5917dcea975a5165cf074d1be56835e35c658cf487b8b7edb3c785037' and len(core['checks'])==43
 for name,sha in core['sourceSHA256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
 net=json.loads((checks/NAMES[0]).read_bytes());assert net['maximumConcurrentBrowsers']==4 and net['actualBrowserLaunches']==6 and net['actualV86Desktops']==0 and net['ownedPrepareOnlyCrash']['afterViewAdvanceWithoutPreparedCertificate'] and len(net['checks'])==35
 out.update(scope=__doc__,legacyCompiledCoreSHA256=core['legacyCompiledCoreSHA256'],retention='32distinct logical values/8MiB serialized defaults per validator/slot; strict native journal, same-head dedupe and no discard before verified successor acceptance; explicit refusal under capacity pressure',next='Automatic persisted election/round scheduling, durable/revocable general membership, long-gap checkpoint/no-replay sync, automatic partial mesh/islands/fallback, chess composition, staged8k/freshWAN/full audit')
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
