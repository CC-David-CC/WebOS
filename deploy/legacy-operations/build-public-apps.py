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
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
APP_IDS = ('falling-blocks', 'owl-companion', 'physics-playground', 'snake-garden', 'clockwork-room', 'chess-study', 'solitaire', 'sky-courier', 'marble-works', 'stack-balance', 'crystal-defense', 'drone-circuit', 'reactive-control-desk', 'story-cards', 'expression-puppet', 'rhythm-garden', 'lantern-leap', 'garden-defense', 'pocket-rally', 'sling-targets', 'gravity-pinball', 'kinetic-relay', 'tabletop-bot-arena', 'pocket-golf', 'target-garden', 'orbital-courier', 'clockwork-quest', 'memory-garden', 'calculator', 'files', 'help', 'browser', 'codemirror', 'terminal', 'text', 'image-editor', 'document-editor', 'pdf-viewer', 'spreadsheet', 'data-explorer', 'ffmpeg', 'wavesurfer', 'tone', 'audio-editor', 'zip', 'gcode-preview', 'grid-tools', 'mermaid', 'echarts', 'plotly', 'pdfme', 'maplibre', 'transformers', 'trystero', 'tanstack-virtual', 'onnx-runtime', 'webtorrent', 'yjs', 'replicad', 'diagrams-net', 'notebook', 'excalidraw', 'svg-editor', 'arduino-simulator', 'pico-simulator', 'circuitjs', 'electronics-design', 'digital-logic', 'embroidery-studio', 'stitch-converter', 'personal-template')

# Host-loaded system tools are separate bundles, so a selected-app build must
# include them even though the consumer has no direct JavaScript import.
APP_DEPENDENCIES = {'text': ('codemirror',)}

def build(source=None, output=None, apps=APP_IDS, node=None, entries=None, public_inputs=()):
    runtime = node or os.environ.get('CODI_BUILD_NODE') or shutil.which('node')
    if not runtime:
        raise ValueError('Node is required at build time; use --node or CODI_BUILD_NODE')
    source_root = Path(source or ROOT.parent/'apps').resolve()
    if source is None and entries is None:
        apps = list(apps)
        for app in apps:
            for dependency in APP_DEPENDENCIES.get(app, ()):
                if dependency not in apps: apps.append(dependency)
        # Files has an app-local, hash-checked patch of the shared Chonky
        # dependency. Stage it automatically after builder dependencies exist.
        if 'files' in apps:
            subprocess.run([sys.executable, str(source_root/'system/files/prepare.py')], check=True, stdout=subprocess.DEVNULL)
        game_groups = json.loads((source_root/'games/catalog.json').read_text())
        entries = {app: ('individual/templates/index.mjs' if app == 'personal-template'
                         else f'games/{game_groups[app]}/{app}/index.mjs' if app in game_groups
                         else f'system/{app}/index.mjs') for app in apps}
    options = {'source': str(source_root),
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
