#!/usr/bin/env python3
"""Exercise rollout retention against the observed forward revision and mutations."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'scripts/mesh-native-vm-rollout-check.py'
spec = importlib.util.spec_from_file_location('neighbor_floor_contract', source)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)
diagnostic = ROOT / '.build/checks/neighbor-native-vm-production-rollback-diagnostic.json'
value = json.loads(diagnostic.read_bytes())
before, after = value['priorSuccessfulRolloutDurableAfter'], value['currentDurableState']
assert before != after
contract.retained_durable(before, after)
publisher = next(k for k in before['floors'] if Path(k).name == 'publisher.sqlite3')
authority = next(k for k in before['floors'] if Path(k).name == 'authority.sqlite3')
checks = ['observed legitimate publisher revision advance accepted']


def reject(name, mutate):
    changed = copy.deepcopy(after)
    mutate(changed)
    try:
        contract.retained_durable(before, changed)
    except AssertionError:
        checks.append(name)
    else:
        raise AssertionError(name)


reject('publisher revision rewind rejected', lambda x: x['floors'][publisher].__setitem__(3, before['floors'][publisher][3]-1))
reject('publisher binding replacement rejected', lambda x: x['floors'][publisher].__setitem__(0, 'other'))
reject('seed revision change rejected', lambda x: x['floors'][publisher].__setitem__(1, before['floors'][publisher][1]+1))
reject('seed hash replacement rejected', lambda x: x['floors'][publisher].__setitem__(2, 'other'))
reject('frozen flag change rejected', lambda x: x['floors'][publisher].__setitem__(4, 1-before['floors'][publisher][4]))
reject('authority revision rewind rejected', lambda x: x['floors'][authority].__setitem__(1, before['floors'][authority][1]-1))
reject('permission database replacement rejected', lambda x: x['fileDatabases'].__setitem__('permissions.sqlite3', 'other'))
reject('floor disappearance rejected', lambda x: x['floors'].pop(publisher))
result = {'status': 'PASS', 'checks': checks, 'sourceSHA256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'contractSHA256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'diagnosticSHA256': hashlib.sha256(diagnostic.read_bytes()).hexdigest()}
output = ROOT / '.build/checks/neighbor-native-rollout-floor-contract-result.json'
assert not output.exists(), 'Preserve previous evidence'
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
