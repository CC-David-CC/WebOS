#!/usr/bin/env python3
"""Bundle selected public apps, including dependencies, CSS, workers and assets.

Requires a build-time Node runtime and `npm ci --ignore-scripts` in
active-system/tools/app-builder. Visitors require neither Node nor npm.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
APP_IDS = ('calculator', 'chat', 'files', 'help', 'rooms', 'terminal', 'text')

def build(source=None, output=None, apps=APP_IDS, node=None, entries=None, public_inputs=()):
    runtime = node or os.environ.get('CODI_BUILD_NODE') or shutil.which('node')
    if not runtime:
        raise ValueError('Node is required at build time; use --node or CODI_BUILD_NODE')
    options = {'source': str(Path(source or ROOT/'served_apps_public').resolve()),
               'output': str(Path(output or ROOT/'assets/desktop').resolve()), 'apps': list(apps), 'entries': entries or {},
               'publicInputs': [str(Path(p).absolute()) for p in public_inputs]}
    # Configuration stays outside the public tree and is never a shell command.
    with tempfile.TemporaryDirectory(prefix='codi-app-build-') as directory:
        config = Path(directory)/'options.json'
        config.write_text(json.dumps(options))
        result = subprocess.run([runtime, str(ROOT/'tools/app-builder/build.mjs'), str(config)],
                                check=True, capture_output=True, text=True)
    return json.loads(result.stdout)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--apps', nargs='+', default=APP_IDS)
    parser.add_argument('--node')
    parser.add_argument('--entries', type=Path, help='JSON map of selected IDs to relative JavaScript source entries')
    parser.add_argument('--public-input', type=Path, action='append', default=[], help='Explicit reviewed shared JS module file; does not permit its directory or transitive imports')
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output, args.apps, args.node, json.loads(args.entries.read_text()) if args.entries else None, args.public_input), indent=2))
