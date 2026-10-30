#!/usr/bin/env python3
"""Install the receipt-window candidate through the retained private controller."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('window_vm_retention', ROOT/'scripts/upgrade-hosted-peer-native-vm.py')
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)


def run(release):
    targets = {label: ROOT/('.build/checks/hosted-peer-window-upgrade-'+label+'-snapshot.json') for label in ['before', 'after']}
    assert all(not path.exists() for path in targets.values())
    before = stage.custody()
    value = stage.vm.upgrade(release)
    assert stage.custody() == before, 'Receipt-window code upgrade changed root custody or permissions'
    for label, target in targets.items():
        shutil.copyfile(ROOT/('.build/checks/signin-native-upgrade-'+label+'-snapshot.json'), target)
    return value | {'rootCustodyAndPermissionRowsUnchanged': True, 'custody': before}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    value = {'status': 'FAIL', 'scope': __doc__}
    try:
        value.update(run(args.release.resolve()))
    except Exception as error:
        import traceback
        value.update(error=str(error), traceback=traceback.format_exc())
    args.output.write_text(json.dumps(value, indent=2)+'\n')
    print(json.dumps({k: value.get(k) for k in ['status', 'error', 'nativeManifestSHA256', 'rootCustodyAndPermissionRowsUnchanged']}))
    raise SystemExit(0 if value['status'] == 'PASS' else 1)
