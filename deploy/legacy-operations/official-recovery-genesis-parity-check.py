#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'codiserver-server-v0.3.0')]
from steward.official_recovery_genesis import verify_recovery_genesis
cases=json.loads(subprocess.check_output([ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node',ROOT/'scripts/official-recovery-genesis-parity-corpus.mjs'],text=True))
for case in cases:
    try:actual=verify_recovery_genesis(case['wire'],channel=case['channel'],genesis_hash=case['genesisHash'])
    except (ValueError,TypeError,KeyError):actual=None
    assert actual==case['expected'],f"Mismatch for {case['name']}: {actual} vs {case['expected']}"
assert len(cases)==10 and sum(c['expected'] is not None for c in cases)==1
print(json.dumps({'status':'PASS','cases':len(cases),'scope':'local independent genesis verifier; no live server integration'}))
