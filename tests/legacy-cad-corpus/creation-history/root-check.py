"""Independent analytic checks of observed creation-history native metrics."""
import json
import math
from pathlib import Path
import sys

receipt = json.loads(Path(sys.argv[1]).read_text())
assert receipt['status'] == 'PASS', 'A complete actual application run is required'
assert receipt['authoringSeeds'] is False and receipt['fakeSuccessfulReplies'] is False
checks = []


def visit(value, location='receipt'):
    if isinstance(value, dict):
        if {'expected', 'geometry', 'accepted', 'ownership'} <= value.keys():
            e, g = value['expected'], value['geometry']
            depth = e['depth']
            # Four corner bores, one central bore, two rounded and two
            # chamfered vertical corners, disjoint in this ordinary test part.
            ideal = (e['width'] * e['height'] * depth
                     - math.pi * depth * ((e['centerDiameter'] / 2)**2
                                          + 4 * (e['cornerDiameter'] / 2)**2)
                     - 2 * depth * e['fillet']**2 * (1 - math.pi / 4)
                     - depth * e['chamfer']**2)
            error = abs(g['nativeVolume'] - ideal)
            tolerance = max(1e-8, 256 * math.ulp(ideal))
            assert error <= tolerance, (location, g['nativeVolume'], ideal)
            bt = 64 * math.ulp(max(1, e['width'], e['height'], depth))
            for point, expected in ((g['nativeBounds']['min'], [0, 0, 0]),
                                    (g['nativeBounds']['max'], [e['width'], e['height'], depth])):
                assert all(abs(a - b) <= bt for a, b in zip(point, expected))
            counts = g['nativeTopology']['counts']
            assert counts['solids'] == 1 and counts['shells'] == 1
            ownership = value['ownership']
            assert ownership['processing'] is False
            assert ownership['resources']['cleanupFailed'] is False
            assert ownership['resources']['candidates'] == 0
            history = value['accepted']['native']['history']
            # Undo and failed creation can leave unused allocated IDs.
            assert ownership['counters']['featureId'] >= max(
                int(item['params']['featureId']) for item in history)
            checks.append({'path': location, 'nativeVolume': g['nativeVolume'],
                           'analyticVolume': ideal, 'absoluteError': error,
                           'volumeTolerance': tolerance, 'boundTolerance': bt})
        for key, child in value.items():
            visit(child, location + '.' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            visit(child, location + '[' + str(index) + ']')


visit(receipt['rows'], 'rows')
assert len(checks) >= 5
print(json.dumps({'status': 'PASS', 'scope': 'Independent analytic native metrics over observed snapshots; not fresh geometry execution or full Gate1 qualification',
                  'checkedSnapshots': len(checks), 'checks': checks}, indent=2))
