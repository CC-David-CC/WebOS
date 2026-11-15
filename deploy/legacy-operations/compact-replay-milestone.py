#!/usr/bin/env python3
"""Bind compact replay component, real RTC/desktop regressions and fault controls."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / '.build/checks'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero(value):
    assert value and all(v == 0 or v is False for v in value.values()), value


def run():
    counts = {'8k': 15, 'neighbors': 19, 'desktop': 23, 'legacy': 46, 'protocol': 155}
    receipts, pins = {}, {}
    for name, count in counts.items():
        path = CHECKS / ('compact-replay-' + name + '-result.json')
        value = json.loads(path.read_bytes())
        assert value['status'] == 'PASS' and len(value['checks']) == count, name
        assert not value.get('productionChanged', False), name
        receipts[name], pins[path.name] = value, digest(path)
    scale = receipts['8k']
    assert scale['completedAuthors'] == scale['participants'] == 8000
    assert scale['actualBrowsers'] == 1 and scale['RTCParticipants'] == 0
    assert not scale['full8kNetworkTested'] and not scale['serverAdmissionTested']
    assert scale['fixture']['generatedAuthors'] == scale['fixture']['distinctSigningKeys'] == 8001
    assert scale['fixture']['privateKeysUploaded'] is False
    zero(scale['cleanupBudget'])
    sample = scale['samples'][-1]
    assert sample['authors'] == sample['replay']['streams'] == 8000
    assert sample['replay']['compact'] and sample['replay']['retainedIdentityProofs'] == 0
    assert sample['accounting']['metadataBytes'] < 8000*4096
    for path, pin in scale['sourceSHA256'].items():
        assert digest(ROOT / path) == pin, path
    assert receipts['neighbors']['actualBrowsers'] == 10
    assert receipts['desktop']['actualV86Desktops'] == 3
    for name in ['neighbors', 'legacy']:
        value = receipts[name]
        assert not value.get('sourceChangedDuringTest', False)
        for usage in value.get('cleanupBudgets', value.get('cleanupBudgetSnapshots', [])):
            zero(usage)
    for name, message in [('queue', 'Expected refusal'), ('key', 'Unneeded JWK properties retained')]:
        path = CHECKS / ('compact-replay-' + name + '-control-result.json')
        value = json.loads(path.read_bytes())
        assert value['status'] == 'FAIL' and message in value['error']
        zero(value['cleanupBudget'])
        assert value['ownedBrowserContextsClosed'] == 1
        pins[path.name] = digest(path)
        control = ROOT / '.build' / ('compact-replay-' + name + '-control/network')
        different = [p.name for p in control.glob('*.mjs') if p.read_bytes() != (ROOT / 'network' / p.name).read_bytes()]
        assert different == ['replay.mjs'] and len(list(control.glob('*.mjs'))) == 33
    path = CHECKS / 'compact-replay-before-result.json'
    before = json.loads(path.read_bytes())
    assert before['status'] == 'FAIL' and before['completedAuthors'] == 1024 and 'replayStreams' in before['error']
    pins[path.name] = digest(path)
    for name, saved in [('scripts/compact-replay-browser-check.py', 'compact-replay-before-browser-check.py'),
                        ('scripts/compact-replay-page.mjs', 'compact-replay-before-page.mjs')]:
        assert digest(CHECKS / saved) == before['sourceSHA256'][name]
    for path, pin in before['sourceSHA256'].items():
        if path.startswith('network/'):
            assert digest(ROOT / '.build/compact-replay-before' / path) == pin
    with urllib.request.urlopen('http://127.0.0.1:19515/sessions', timeout=20) as response:
        assert not json.load(response)['value']
    health = CHECKS / 'compact-replay-final-health-result.json'
    assert json.loads(health.read_bytes())['privateVMChanged'] is False
    pins[health.name] = digest(health)
    return {'status': 'PASS', 'scope': __doc__, 'checkCounts': counts, 'receiptSHA256': pins,
            'certifiedAuthorsInOneWebCryptoReceiver': 8000,
            'replayAccountingBytesAt8000': sample['accounting']['metadataBytes'],
            'elapsedComponentMs': scale['elapsedMs'], 'ownedBrowserContextsRemaining': 0,
            'productionChanged': False, 'privateVMChanged': False,
            'actual8kNetworkTested': False, 'durableReplayFloorsImplemented': False,
            'longLivedMeshAuthorityImplemented': False, 'wholeGoalComplete': False,
            'sourceSHA256': digest(Path(__file__))}


if __name__ == '__main__':
    result = run()
    output = CHECKS / 'compact-replay-milestone-result.json'
    assert not output.exists(), 'Preserve old evidence'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
