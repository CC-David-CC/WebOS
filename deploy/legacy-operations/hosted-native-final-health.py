#!/usr/bin/env python3
"""Read-only private native19/20/21 room retention, QA cleanup and public entry checks.

Fixture SPKI/browser acceptance is separate. Public entry requests use ordinary
TLS; these three requests do not repeat the full all-site/prototype byte audit.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def run(release):
    spec = importlib.util.spec_from_file_location('hosted_health_vm', ROOT / 'scripts/upgrade-signin-native-vm.py')
    vm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vm)
    before = vm.runtime()
    pin = hashlib.sha256((release / 'connected-release.json').read_bytes()).hexdigest()
    assert before['manifestSHA256'] == pin
    assert json.loads((release / 'connected-release.json').read_bytes())['version'] in ['codi-connected-development/19','codi-connected-development/20','codi-connected-development/21']
    owned = {}
    receipts = sorted({
        path for pattern in ['hosted-native-vm-*-result.json', 'checkpoint-native-vm-*-result.json',
                             'hosted-client-native-vm-*-result.json']
        for path in (ROOT / '.build/checks').glob(pattern)
    })
    for path in receipts:
        value = json.loads(path.read_bytes())
        if value.get('status') != 'PASS':
            continue
        for account in value.get('ownedTestAccountsDisabled', []):
            name = account['username']
            assert re.fullmatch(r'(?:meshhost[0-9]{12}|qa_doc_[a-f0-9]{12}|vmnet_[a-f0-9]{12})', name)
            assert name not in owned or owned[name] == account['subject']
            owned[name] = account['subject']
    for path in sorted((ROOT / '.build/checks').glob('hosted-native-browser-*-result.json')):
        browser = json.loads(path.read_bytes())
        if not browser.get('subject'):
            continue
        assert re.fullmatch(r'vmhosted_[a-f0-9]{12}', browser['createdTestAccount'])
        owned[browser['createdTestAccount']] = browser['subject']
    assert owned
    recovery = json.loads((ROOT / '.build/checks/hosted-native-vm-binding-recovery-r1-result.json').read_bytes())
    assert recovery['status'] == 'PASS'
    code = '''import importlib.util,json,sqlite3,subprocess
from pathlib import Path
c=json.loads(Path('/etc/codi-native-fixture/managed.json').read_bytes());state=Path(c['stateRoot'])
assert c['basePath']=='' and c.get('hostedRooms')
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
backend=c['hostedRooms'];p=Path(backend['operatorRelease'])/'room_service/operator.py'
spec=importlib.util.spec_from_file_location('_hosted_health_operator',p);op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
manager=op.Manager(Path(backend['configFile']).parent)
with manager.locked():
 room_config=manager.load();health=manager.health(room_config);room_state=manager.inspect(room_config)
assert op.retained(EXPECTED,room_state),'Old accepted room state or replay floor regressed'
assert sum(row[6] for row in room_state['rooms'])>=2
pending=[]
for base,names in [(Path('/etc/codi-native-fixture'),['maintenance.json','native-rollout.json']),(Path(backend['configFile']).parent,['pending.json'])]:
 pending.extend(str(base/name) for name in names if (base/name).exists())
assert not pending,pending
print(json.dumps({'ownedAccounts':out,'roomHealth':health,'roomState':room_state,'pendingJournals':pending,'basePath':''}))
'''.replace('OWNED', repr(owned)).replace('EXPECTED', repr(recovery['workerState']))
    result = json.loads(vm.remote('/srv/codi-network-fixture/venv/bin/python -I -B -c ' + shlex.quote(code)))
    snapshot = json.loads(vm.remote('/srv/codi-network-fixture/venv/bin/python -I -B /srv/codi-network-fixture/tools/native-network-vm-lifecycle-check.py --snapshot'))
    assert snapshot['worker']['active'] and snapshot['worker']['kernelMatches'] and not snapshot['worker']['guardFault']
    assert not snapshot['nativeJournalPresent'] and not snapshot['anonymousQEMUChildren']
    with urllib.request.urlopen('http://127.0.0.1:19515/sessions', timeout=20) as response:
        assert not json.load(response)['value'], 'Close owned browser contexts first'
    entries = []
    for path in ['/', '/blog/', '/desktop/']:
        with urllib.request.urlopen('https://ksu.codes' + path, timeout=30) as response:
            raw = response.read()
            assert response.status == 200
            entries.append(dict(path=path, status=200, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)))
    assert entries[1]['sha256'] == json.loads((ROOT / '.build/checks/root-live-health-result.json').read_bytes())['blogSHA256']
    assert before == vm.runtime()
    return dict(status='PASS', scope=__doc__, observedAt=datetime.now(timezone.utc).isoformat(),
                runtime=before, **result, guestWorker=snapshot['worker'], anonymousQEMUChildren=[],
                ownedBrowserContextsRemaining=0, productionChanged=False, defaultPublicTLS=True,
                publicEntries=entries, fullAllSiteOrPrototypeByteAuditRepeated=False,
                sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Preserve prior evidence'
    value = run(args.release.resolve())
    args.output.write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps({'status': value['status'], 'ownedAccounts': len(value['ownedAccounts']), 'runtime': value['runtime']}))
