"""Independent saved-byte and analytic readback; no fresh native execution."""
import hashlib
import json
import math
from pathlib import Path

root = Path(__file__).parent / 'evidence-r3'
r = json.loads((root / 'receipt.json').read_text())
assert r['status'] == 'PASS' and len(r['rows']) == 15
assert r['authoringSeeds'] is False and r['fakeSuccessfulReplies'] is False
mm = json.loads((root / 'default-mm.jsketcher.json').read_text())
inch = json.loads((root / 'saved-inch.jsketcher.json').read_text())
assert 'presentation' not in mm
assert inch.pop('presentation') == {'version': 1, 'lengthUnit': 'inch'}
assert mm == inch and mm['unit'] == 'millimeter'
for name in ['default-mm', 'saved-inch', 'second-window-default']:
    raw = (root / (name + '.jsketcher.json')).read_bytes()
    row = next(x for x in r['rows'] if x['label'] == name + ' normal native Save and server sync')
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
flip = next(x for x in r['rows'] if x['label'].startswith('Normal public inch setter'))
a, b = flip['before'], flip['after']
for key in ['history', 'source', 'expressions', 'counters', 'materialRevision', 'sketches', 'worker']:
    assert a['native'][key] == b['native'][key], key
assert a['mesh'] == b['mesh'] and a['journal'] == b['journal']
assert a['solids']['bodies'] == b['solids']['bodies']
observations = []


def visit(value):
    if isinstance(value, dict):
        if {'native', 'solids', 'units'} <= value.keys() and value['solids']['bodies']:
            assert len(value['solids']['bodies']) == 1
            body = value['solids']['bodies'][0]['metrics']
            feature = next(x for x in value['native']['history'] if x['type'] == 'WORKER_SELECTED_PROFILE_EXTRUDE_V2')
            depth = feature['params']['depth']
            expected = 25.4 * 50.8 * depth
            tolerance = max(1e-9, 256 * math.ulp(expected))
            assert abs(body['nativeVolume'] - expected) <= tolerance
            assert body['nativeBounds'] == {'min': [0, 0, 0], 'max': [25.4, 50.8, depth]}
            counts = body['nativeTopology']['counts']
            assert (counts['solids'], counts['faces'], counts['edges'], counts['vertices']) == (1, 6, 12, 8)
            observations.append({'depth': depth, 'nativeVolume': body['nativeVolume'], 'analyticVolume': expected})
        for child in value.values():
            visit(child)
    elif isinstance(value, list):
        for child in value:
            visit(child)


visit(r['rows'])
assert len(observations) >= 5
print(json.dumps({'status': 'PASS', 'scope': __doc__, 'canonicalSavedEnvelopeIdenticalExceptPresentation': True,
                  'workerCreationsBeforeAndAfter': len(a['native']['worker']['created']),
                  'workerMessagesBeforeAndAfter': a['native']['worker']['messages'],
                  'observations': observations}, indent=2))
