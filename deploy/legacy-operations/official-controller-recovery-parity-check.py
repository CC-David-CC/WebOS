#!/usr/bin/env python3
"""Compare experimental JS and Python proposal verification; no state changes."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'codiserver-server-v0.3.0')]
from steward.official_controller_recovery_proposal import verify_official_recovery_proposal
cases=json.loads(subprocess.check_output([ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node',ROOT/'scripts/official-controller-recovery-parity-corpus.mjs'],text=True))
assert len(cases)>=15
for case in cases:
    try:verify_official_recovery_proposal(case['wire'],case['acceptance'],case['trusted']);actual=True
    except (ValueError,TypeError,KeyError):actual=False
    assert actual==case['expected'],f"JS/Python differ for {case['name']}: {actual} vs {case['expected']}"
assert sum(case['expected'] for case in cases)==2
print(json.dumps({'status':'PASS','cases':len(cases),'accepted':2,'scope':'local Web Crypto and Python cryptography; proposal-only, no durable authority'}))
