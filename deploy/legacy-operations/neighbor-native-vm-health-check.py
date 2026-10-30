#!/usr/bin/env python3
"""Read-only native18 runtime, owned fixture account and cleanup verification."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def run(release):
    spec = importlib.util.spec_from_file_location('neighbor_health_vm', ROOT / 'scripts/upgrade-signin-native-vm.py')
    vm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vm)
    pin = hashlib.sha256((release / 'connected-release.json').read_bytes()).hexdigest()
    before = vm.runtime()
    assert before['manifestSHA256'] == pin
    owned = {}
    for path in sorted((ROOT / '.build/checks').glob('neighbor-native-vm-*-result*.json')):
        value = json.loads(path.read_bytes())
        for account in value.get('ownedTestAccountsDisabled', []):
            name = account['username']
            assert re.fullmatch(r'(?:meshhost[0-9]{12}|qa_doc_[a-f0-9]{12}|vmnet_[a-f0-9]{12})', name)
            assert name not in owned or owned[name] == account['subject']
            owned[name] = account['subject']
    assert len(owned) >= 5
    code = '''import json,sqlite3
from pathlib import Path
c=json.loads(Path('/etc/codi-native-fixture/managed.json').read_bytes());state=Path(c['stateRoot'])
f=json.loads(Path(c['userFiles']['configFile']).read_bytes());out=[]
def connect(p):return sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
with connect(state/'issuer/state/accounts.sqlite3') as accounts,connect(Path(f['stateRoot'])/'permissions.sqlite3') as files:
 for name,subject in OWNED.items():
  row=accounts.execute('SELECT a.subject,p.disabled FROM accounts a JOIN account_policy p USING(subject) WHERE a.username=?',(name,)).fetchone()
  assert row==(subject,1),(name,row)
  home=files.execute('SELECT home_id FROM users WHERE subject=?',(subject,)).fetchone()
  count=sum(1 for p in (Path(f['dataRoot'])/'users'/home[0]).rglob('*') if p.is_file()) if home else 0
  assert count==0,(name,count)
  out.append({'username':name,'subject':subject,'disabled':True,'remainingFiles':count})
pending=any((Path('/etc/codi-native-fixture')/n).exists() for n in ['maintenance.json','native-rollout.json'])
assert c['basePath']=='' and not pending
print(json.dumps({'ownedAccounts':out,'basePath':'','pendingJournals':pending}))
'''.replace('OWNED', repr(owned))
    result = json.loads(vm.remote('/usr/bin/python3 -I -B -c ' + shlex.quote(code)))
    with urllib.request.urlopen('http://127.0.0.1:19515/sessions', timeout=20) as response:
        contexts = json.load(response)['value']
    assert not contexts, 'Owned test contexts must be closed before this health check'
    assert before == vm.runtime()
    return dict(status='PASS', **result, runtime=before, ownedBrowserContextsRemaining=0,
                productionChanged=False, sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Preserve prior evidence; select another output path'
    result = run(args.release.resolve())
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
