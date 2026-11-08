#!/usr/bin/env python3
"""Offline actual-receipt oracle. Never author, mutate, or run an application."""
import argparse
import hashlib
import json
import math
import re
import subprocess
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

BUDGET = Fraction(1, 20_000_000)  # 5e-8 mm = 0.05 nm = 50 pm, exact.
PRE = 'Authored anti-parallel pair before global wrap raw'
POST = 'Source edit crosses normalized branch without changing authored180 raw'
LITERAL = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z')

class Refusal(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

def need(condition, message, code='ORACLE_BINDING_MISMATCH'):
    if not condition:
        raise Refusal(code, message)

def one(rows, label):
    need(len(rows) == 1, 'Expected exactly one ' + label)
    return rows[0]

def number(value, constant=False):
    if constant and isinstance(value, str):
        need(len(value) <= 64 and LITERAL.fullmatch(value), 'Unsupported nonliteral constant', 'ORACLE_UNSUPPORTED')
        value = float(value)
    need(type(value) in (int, float), 'Expected represented numerical input', 'ORACLE_UNSUPPORTED')
    value = float(value)
    need(math.isfinite(value) and abs(value) <= 1e8, 'Numerical input outside bounded oracle domain', 'ORACLE_UNSUPPORTED')
    return Fraction.from_float(value)

def point(value):
    need(isinstance(value, dict) and set(value) == {'x', 'y'}, 'Expected explicit XY point')
    return tuple(number(value[k]) for k in ('x', 'y'))

def text(value):
    with localcontext() as ctx:
        ctx.prec = 110
        return str(Decimal(value.numerator) / Decimal(value.denominator))

def norm_interval(v):
    q = v[0] * v[0] + v[1] * v[1]
    need(q > 0, 'Zero direction has no branch reference', 'ORACLE_UNSUPPORTED')
    with localcontext() as ctx:
        ctx.prec = 100
        s = (Decimal(q.numerator) / Decimal(q.denominator)).sqrt()
        lo, hi = s.next_minus(ctx), s.next_plus(ctx)
        for _ in range(8):
            a, b = Fraction(lo), Fraction(hi)
            if 0 < a and a * a <= q <= b * b:
                return a, b
            lo, hi = lo.next_minus(ctx), hi.next_plus(ctx)
    raise Refusal('ORACLE_REFERENCE_UNRESOLVED', 'Could not certify the reference square-root enclosure')

def peer_interval(anchor, length, direction):
    lo, hi = norm_interval(direction)
    result = []
    for origin, delta in zip(anchor, direction):
        k = -length * delta
        result.append((origin + k / hi, origin + k / lo) if k >= 0 else (origin + k / lo, origin + k / hi))
    return result

def error_interval(actual, expected):
    lo, hi = expected
    low = lo - actual if actual < lo else actual - hi if actual > hi else Fraction(0)
    high = max(abs(actual - lo), abs(actual - hi))
    if low <= BUDGET < high:
        raise Refusal('ORACLE_REFERENCE_UNRESOLVED', 'Reference interval straddles the frozen coordinate budget')
    return {'actualMm': text(actual), 'referenceIntervalMm': [text(lo), text(hi)],
            'errorLowerMm': text(low), 'errorUpperMm': text(high),
            'errorUpperPm': text(high * 10**9), 'within50pm': high <= BUDGET}, high

def admitted(row):
    a = row.get('admission')
    need(isinstance(a, dict) and a.get('version') == 1 and a.get('state') in ('accepted', 'redundant'), 'Unadmitted reference constraint')

def row_for(source, kind, refs):
    row = one([r for r in source['stages'][0]['constraints'] if r.get('typeId') == kind and r.get('objects') == refs], kind + ' ordered source row')
    admitted(row)
    return row

def successful(receipt, command):
    return [(i, c) for i, c in enumerate(receipt['commands']) if c.get('ok') is True and c.get('command') == command]

def pair_binding(receipt, anchor):
    candidates = []
    for index, command in successful(receipt, 'append-sketch-primitive'):
        args = command.get('args', {})
        if args.get('kind') == 'Segment' and args.get('data', {}).get('a') == {'x': anchor[0], 'y': anchor[1]}:
            candidates.append((index, command))
    index, command = one(candidates, 'actual public Segment append at fixture anchor')
    identity = command['result']['primitive']['id']
    binding = one([b for b in receipt['bindings'] if b['id'] == identity], 'publicly inspected Segment binding')
    need(binding['aId'] != binding['bId'] and not binding['locked'], 'Unsupported endpoint binding')
    need(tuple(map(number, binding['a'])) == point(command['args']['data']['a']), 'Append/binding anchor mismatch')
    need(tuple(map(number, binding['b'])) == point(command['args']['data']['b']), 'Append/binding end mismatch')
    return binding, index, command

def capture(receipt, label, bindings):
    index, row = one([(i, r) for i, r in enumerate(receipt['rows']) if r.get('label') == label], 'full accepted observation ' + label)
    need('before' in row and 'inspection' in row, 'Missing full accepted observation', 'ORACLE_OBSERVATION_UNAVAILABLE')
    native = row['before']['accepted']['native']
    raw = native['source']
    need(isinstance(raw, str) and len(raw.encode()) <= 1_048_576, 'Source outside bounded oracle envelope', 'ORACLE_UNSUPPORTED')
    source = json.loads(raw)
    own = one([s for s in native['sketches'] if s.get('id') == receipt['binding']['faceId']], 'native source face')
    need(own['source'] == raw, 'Captured source differs from its face-bound native source')
    need(source['version'] == 3 and len(source['stages']) == 1 and source['stages'][0]['generators'] == [] and source['constants'] == '', 'Unsupported source stage/constant domain', 'ORACLE_UNSUPPORTED')
    need(row['before']['accepted']['solids']['unit'] == 'millimeter', 'Physical unit mismatch')
    plane = one(native['history'], 'source PLANE history')
    need(plane['type'] == 'PLANE' and plane['params']['orientation'] == 'XY' and plane['params']['datum'] is None and number(plane['params']['depth']) == 0, 'Unsupported source placement', 'ORACLE_UNSUPPORTED')
    frame = {'origin': [0, 0, 0], 'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1]}
    inspection = row['inspection']
    need(inspection['faceId'] == receipt['binding']['faceId'] and inspection['boundaryFrame'] == frame and source['metadata']['boundaryFrame'] == frame, 'Source/inspection frame binding mismatch')
    need(all(source['boundary'][k] == [] for k in ('lines', 'arcs', 'circles', 'nurbses')), 'Unsupported fixed boundary', 'ORACLE_UNSUPPORTED')
    observed = {'retained-source': {}, 'replayed-inspection': {}}
    for key, binding in bindings.items():
        obj = one([o for o in source['objects'] if o['id'] == binding['id'] and o['type'] == 'Segment'], 'actual source Segment')
        public_obj = one([o for o in inspection['objects'] if o['id'] == binding['id']], 'inspected Segment')
        need(public_obj['type'] == 'Segment' and obj['stage'] == public_obj['stage'] == 0, 'Segment ownership mismatch')
        retained_ends, replayed_ends = [], []
        for field, endpoint_id in (('a', binding['aId']), ('b', binding['bId'])):
            p = one([p for p in inspection['points'] if p['id'] == endpoint_id and p['parentId'] == binding['id']], 'bound inspected endpoint')
            value = point({'x': p['x'], 'y': p['y']})
            # Inspection projects a separately solved replay; retain both actual
            # datasets, never substitute one for the accepted stored source.
            retained_ends.append(point(obj['data'][field]))
            replayed_ends.append(value)
        observed['retained-source'][key] = retained_ends
        observed['replayed-inspection'][key] = replayed_ends
    return {'rowIndex': index, 'row': row, 'source': source, 'inspection': inspection, 'observed': observed,
            'sourceSha256': hashlib.sha256(raw.encode()).hexdigest()}

def reference(receipt, snapshot, a, b):
    source, inspection = snapshot['source'], snapshot['inspection']
    datum_id, bottom_id = receipt['binding']['datumId'], receipt['binding']['bottomId']
    datum = one([p for p in inspection['points'] if p['id'] == datum_id and p['parentId'] == bottom_id], 'public datum endpoint')
    bottom = one([o for o in source['objects'] if o['id'] == bottom_id and o['type'] == 'Segment'], 'actual datum Segment')
    need(point({'x': datum['x'], 'y': datum['y']}) in [point(bottom['data'][k]) for k in ('a', 'b')], 'Datum/source endpoint mismatch')
    lock = row_for(source, 'LockPoint', [datum_id])
    need(set(lock['constants']) == {'x', 'y'}, 'Unsupported datum lock')
    origin = tuple(number(lock['constants'][k], True) for k in ('x', 'y'))
    need(origin == (0, 0), 'Fixture datum is not explicitly fixed at origin', 'ORACLE_UNSUPPORTED')
    relevant = [lock]
    anchors, lengths = {}, {}
    for key, binding in [('A', a), ('B', b)]:
        values = []
        for axis, kind in [('x', 'SignedDistanceX'), ('y', 'SignedDistanceY')]:
            row = row_for(source, kind, [datum_id, binding['aId']])
            need(set(row['constants']) == {'distance'}, 'Unsupported signed anchor constants')
            distance = number(row['constants']['distance'], True)
            values.append(origin[len(values)] + distance)
            need(any(c['args'].get('faceId') == receipt['binding']['faceId'] and c['args'].get('axis') == axis and c['args'].get('ids') == row['objects'] and number(c['args']['distance']) == distance for _, c in successful(receipt, 'apply-closed-sketch-signed-distance')), 'Anchor lacks its genuine public authoring receipt')
            relevant.append(row)
        anchors[key] = tuple(values)
        need(anchors[key] == tuple(map(number, binding['a'])), 'Authored anchor differs from public Segment binding')
        row = row_for(source, 'LengthRelation', [binding['id'], bottom_id])
        need(set(row['constants']) == {'factor', 'offset'} and number(row['constants']['factor'], True) == 0, 'Only actual factor-zero fixed length is supported', 'ORACLE_UNSUPPORTED')
        length = number(row['constants']['offset'], True)
        need(0 < length <= 1e6 and length == number(binding['length']), 'Fixed length/source binding mismatch')
        lengths[key] = length
        need(any(c['args'].get('faceId') == receipt['binding']['faceId'] and c['args'].get('ids') == row['objects'] and number(c['args']['factor']) == 0 and number(c['args']['offset']) == length for _, c in successful(receipt, 'apply-closed-sketch-length-relation')), 'Length lacks its actual public authoring receipt')
        relevant.append(row)
    parallel = row_for(source, 'Parallel', [a['id'], b['id']])
    need(set(parallel['constants']) == {'angle'} and number(parallel['constants']['angle'], True) == 180, 'Only ordered canonical antiparallel180 is supported', 'ORACLE_UNSUPPORTED')
    relevant.append(parallel)
    known = {id(row) for row in relevant}
    targets = {a['id'], b['id'], a['aId'], a['bId'], b['aId'], b['bId']}
    need(all(id(row) in known for row in source['stages'][0]['constraints'] if targets.intersection(row.get('objects', []))), 'Additional constraints make this reference domain unsupported', 'ORACLE_UNSUPPORTED')
    for row in relevant:
        index = source['stages'][0]['constraints'].index(row)
        public = one([r for r in inspection['constraints'] if r['stage'] == 0 and r['index'] == index], 'inspected source equation')
        for field in ('typeId', 'objects', 'constants', 'admission'):
            need(public.get(field) == row.get(field), 'Source/public equation binding mismatch: ' + field)
    need(any(c['args'].get('faceId') == receipt['binding']['faceId'] and c['args'].get('kind') == 'parallel' and c['args'].get('ids') == [a['id'], b['id']] and len(c.get('result', {}).get('group', {}).get('rows', [])) == 1 and c['result']['group']['rows'][0].get('angleDegrees') == 180 for _, c in successful(receipt, 'apply-closed-sketch-orientation')), 'Ordered branch lacks actual public creation receipt')
    meaning = [{k: row.get(k) for k in ('typeId', 'objects', 'constants', 'stage')} for row in relevant]
    return anchors, lengths, origin, point({'x': datum['x'], 'y': datum['y']}), meaning

def evaluate(receipt, snapshot, bindings, requested, observation):
    observed = snapshot['observed'][observation]
    a, b = bindings['A'], bindings['B']
    anchors, lengths, origin, datum, meaning = reference(receipt, snapshot, a, b)
    direction = tuple(requested[k] - anchors['A'][k] for k in (0, 1))
    expected_b = peer_interval(anchors['B'], lengths['B'], direction)
    coordinates = [('datum.' + axis, datum[i], (origin[i], origin[i])) for i, axis in enumerate(('x', 'y'))]
    for key in ('A', 'B'):
        for i, axis in enumerate(('x', 'y')):
            coordinates.append((key + '.a.' + axis, observed[key][0][i], (anchors[key][i], anchors[key][i])))
            target = (requested[i], requested[i]) if key == 'A' else expected_b[i]
            coordinates.append((key + '.b.' + axis, observed[key][1][i], target))
    errors, maximum = {}, Fraction(0)
    for field, actual, expected in coordinates:
        result, upper = error_interval(actual, expected)
        errors[field] = result
        maximum = max(maximum, upper)
    va = tuple(observed['A'][1][i] - observed['A'][0][i] for i in (0, 1))
    vb = tuple(observed['B'][1][i] - observed['B'][0][i] for i in (0, 1))
    dot, cross = va[0] * vb[0] + va[1] * vb[1], va[0] * vb[1] - va[1] * vb[0]
    norm = norm_interval(direction)
    _, length_error = error_interval(lengths['A'], norm)
    return {'label': snapshot['row']['label'], 'rowIndex': snapshot['rowIndex'], 'observationKind': observation, 'retainedSourceSha256': snapshot['sourceSha256'],
            'replayedSerializedSourceAvailable': False, 'requestedAEndExact': observed['A'][1] == requested,
            'inspectionRevision': snapshot['inspection']['revision'],
            'evaluatedSolidsRevision': snapshot['row']['before']['accepted']['solids']['revision'],
            'sourceAnchorsMm': {k: [text(x) for x in v] for k, v in anchors.items()},
            'sourceLengthsMm': {k: text(v) for k, v in lengths.items()},
            'requestedAEndMm': [text(v) for v in requested], 'coordinateErrors': errors,
            'maxCoordinateErrorUpperMm': text(maximum), 'maxCoordinateErrorUpperPm': text(maximum * 10**9),
            'actualVectorDotMm2': text(dot), 'actualVectorCrossMm2': text(cross),
            'requestedANormVersusSourceLengthUpperMm': text(length_error),
            'requestedANormVersusSourceLengthUpperPm': text(length_error * 10**9),
            'within50pmPerCoordinate': maximum <= BUDGET, 'opposedDirectedBranch': dot < 0,
            'requestedLengthCompatibleWithin50pm': length_error <= BUDGET}, meaning

def custody(receipt, args):
    need(receipt['sourcePins'] == receipt['sourceHashesAfter'], 'Executing producer changed during workflow')
    requirements = [(args.core_repo, args.producer_core, 'test/line-orientation-public-workflow/' + name) for name in ('desktop-driver.mjs', 'example.mjs', 'README.md')]
    requirements += [(args.desktop_repo, args.producer_desktop, name) for name in ('test/agent-cad-corpus/sweep/signed-harness.mjs', 'apps/system/jsketcher/examples/cad-agent.mjs')]
    verified = []
    for repo, commit, filename in requirements:
        need(re.fullmatch('[0-9a-f]{40}', commit), 'Full frozen producer commit required')
        pin = one([v for k, v in receipt['sourcePins'].items() if k.endswith('/' + filename)], 'pinned producer source')
        body = subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + filename])
        need(hashlib.sha256(body).hexdigest() == pin, 'Frozen Git producer hash mismatch: ' + filename)
        verified.append({'file': filename, 'commit': commit, 'sha256': pin})
    return verified

def check(args):
    with args.receipt.open('rb') as fp:
        raw = fp.read(128 * 1024 * 1024 + 1)
    need(len(raw) <= 128 * 1024 * 1024, 'Receipt exceeds offline intake bound', 'ORACLE_UNSUPPORTED')
    receipt = json.loads(raw)
    need(receipt.get('status') in ('PASS', 'FAIL'), 'Whole workflow has not reached a terminal state', 'ORACLE_NOT_RUN')
    need(receipt['pins']['source'] == args.runtime_core and receipt['pins']['desktop'] == args.runtime_desktop, 'Wrong actual runtime pins')
    need(all(receipt[k] is False for k in ('privateAuthoring', 'sourceSeeds', 'fakeSuccessfulReplies')), 'Receipt is outside actual public-authoring scope')
    verified = custody(receipt, args)
    need(any(r.get('label') == POST for r in receipt['rows']), 'No full post-edit vector observation exists', 'ORACLE_OBSERVATION_UNAVAILABLE')
    a, ai, ac = pair_binding(receipt, (560, 150))
    b, bi, bc = pair_binding(receipt, (590, 150))
    need(a['id'] != b['id'] and a['aId'] != b['aId'] and a['bId'] != b['bId'], 'Ambiguous actual pair identity')
    bindings = {'A': a, 'B': b}
    pre, post = capture(receipt, PRE, bindings), capture(receipt, POST, bindings)
    need(pre['rowIndex'] < post['rowIndex'], 'Observation chronology mismatch')
    index, command = one([(i, c) for i, c in successful(receipt, 'edit-closed-sketch-points')
                          if c['args'].get('faceId') == receipt['binding']['faceId']
                          and len(c['args'].get('points', [])) == 1
                          and c['args']['points'][0].get('id') == a['bId']
                          and c['args'].get('revision') == pre['inspection']['revision']], 'actual A endpoint edit bound to pre-state')
    need(command['args']['revision'] == pre['inspection']['revision'], 'Requested edit is not bound to captured pre-state')
    need(post['inspection']['revision'] != pre['inspection']['revision'], 'Changed public edit lacks new source revision')
    requested = point({k: command['args']['points'][0][k] for k in ('x', 'y')})
    initial = point(ac['args']['data']['b'])
    retained_pre = pre['observed']['retained-source']
    need(post['observed']['retained-source']['A'][1] == requested, 'Published A endpoint differs from exact requested source coordinates')
    # One reference per phase. Pre-edit A is free-angle conditional input from
    # retained source; post-edit A is the actual public requested endpoint.
    # Never use replay A as a separate reference to hide its coordinate error.
    observations, meanings = [], []
    for snapshot, target, description in [(pre, retained_pre['A'][1], 'Retained pre-edit free-angle A; no independent A-end accuracy claim'),
                                           (post, requested, 'Actual public requested endpoint plus independently checked source anchors')]:
        for view in ('retained-source', 'replayed-inspection'):
            result, meaning = evaluate(receipt, snapshot, bindings, target, view)
            result['directionReference'] = description
            if snapshot is pre: result['initialPublicAppendAEndMm'] = [text(v) for v in initial]
            observations.append(result)
            meanings.append(meaning)
    need(retained_pre['A'][1][0] < number(a['a'][0]) and retained_pre['A'][1][1] > number(a['a'][1])
         and requested[0] < number(a['a'][0]) and requested[1] < number(a['a'][1]), 'Actual request did not cross the left directed angular chart as specified')
    need(all(meaning == meanings[0] for meaning in meanings), 'Anchor, length or branch authored intent changed during coordinate edit')
    reconstruction = []
    for snapshot in (pre, post):
        changes = {}
        maximum = Fraction(0)
        for key in ('A', 'B'):
            for end, field in enumerate(('a', 'b')):
                for axis, coordinate in enumerate(('x', 'y')):
                    delta = abs(snapshot['observed']['retained-source'][key][end][axis] - snapshot['observed']['replayed-inspection'][key][end][axis])
                    changes[key + '.' + field + '.' + coordinate] = {'displacementMm': text(delta), 'displacementPm': text(delta * 10**9), 'within50pm': delta <= BUDGET}
                    maximum = max(maximum, delta)
        reconstruction.append({'label': snapshot['row']['label'], 'coordinateChanges': changes, 'maxDisplacementPm': text(maximum * 10**9), 'within50pm': maximum <= BUDGET})
    passed = all(o['within50pmPerCoordinate'] and o['opposedDirectedBranch'] and o['requestedLengthCompatibleWithin50pm'] for o in observations) and all(r['within50pm'] for r in reconstruction)
    return {'oracleVersion': 2, 'status': 'PASS_SCOPED_ANTIPARALLEL_50PM_COORDINATES' if passed else 'FAIL_SCOPED_ANTIPARALLEL_COORDINATES',
            'wholeWorkflowStatus': receipt['status'], 'receiptSha256': hashlib.sha256(raw).hexdigest(),
            'runtime': {'core': args.runtime_core, 'desktop': args.runtime_desktop}, 'verifiedProducerGitObjects': verified,
            'coordinateBudget': {'millimeter': '0.00000005', 'nanometer': '0.05', 'picometer': '50'},
            'reference': 'Represented binary64 input values, exact rational arithmetic, certified enclosing Decimal100 square root; no production geometry/math imports',
            'binding': {'faceId': receipt['binding']['faceId'], 'A': a, 'B': b,
                        'publicAppendCommandIndices': [ai, bi], 'publicEndpointEditCommandIndex': index,
                        'publicEndpointEditRequest': command['args']},
            'observations': observations, 'retainedToInspectionReconstruction': reconstruction,
            'inspectionContract': 'Cold solved read-only replay; supported connected coordinates may reconstruct within50pm and are not promised bit-identical to retained source or former transient endpoint drivers',
            'limits': ['Only this terminal workflow pre/post A170-to190 ordered antiparallel pair; no other operation accuracy signoff.',
                       'The public requested A vector and original literal length differ slightly; compatibility error is reported, not called an exact joint solution.',
                       'Revision tokens from sketch inspection and evaluated solids are distinct domains and are recorded separately.',
                       'Retained source and replayed public inspection are distinct actual observations, each checked against the same independent reference. Inspection does not promise exact transient endpoint coordinates; exactness is separately reported, while retained requested A must remain exact.',
                       'No full replayed serialized sketch was recorded; its point/constraint/frame observations are available, not a fabricated replay-source hash.',
                       'This checks genuine recorded full vectors; it is not a live Native probe or an adversarial receipt-authentication certificate.',
                       'No BRep, atomistic, nanoscale material, fabrication or universal solver accuracy claim.']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt', type=Path)
    for name in ('runtime-core', 'runtime-desktop', 'producer-core', 'producer-desktop'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--core-repo', type=Path, required=True)
    parser.add_argument('--desktop-repo', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(args)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['status'].startswith('PASS_') else 1)
    except (Refusal, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'ORACLE_REFUSED', 'code': getattr(error, 'code', 'ORACLE_INPUT_ERROR'), 'message': str(error)}))
        raise SystemExit(2)
