#!/usr/bin/env python3
"""Render the reviewed component roles against the actual source catalog. No builds."""
import argparse
import csv
import io
import json
from collections import Counter
from pathlib import Path

from catalog_sources import ROOT, catalog


RECIPES = {
    'js': ('Browser JS bundle', 'platform/runtime/active-system/tools/app-builder/build.mjs'),
    'python-js': ('Owned Python package and browser modules', 'scripts/bootstrap_backend.py'),
    'python': ('Owned Python package', None),
    'craft-web': ('Upstream Cargo/browser packaging; parent supplies shared fonts', 'scripts/craft_cargo.py'),
    'cargo': ('Shared Cargo workspace or workflow source', None),
    'native': ('Owned native/engine build definitions', None),
    'model': ('JavaScript model/library source; component package test command', None),
    'historical': ('Retained source; no activation recipe authorized', None),
    'cad': ('Owned CAD worker/webpack build definitions', None),
    'guest': ('Original guest image builders; isolated toolchain/port required', None),
    'gecko': ('Pinned engine fetch/build plus adapter bundle', 'apps/browser/tools/build_engine.sh'),
    'notebook': ('JupyterLite/Pyodide preparation plus adapter bundle', 'apps/notebook/prepare.py'),
    'microduck': ('Pinned rig/policy/engine preparation plus adapter bundle', 'apps/microduck/tools/build-runner.mjs'),
    'prototype': ('Node research probe; no browser production recipe', 'apps/pcb-design/probe.mjs'),
    'speech': ('Locked-input fetch and offline component build', 'engines/speech/scripts/build.mjs'),
}

OWNED_ENTRIES = {
    'accounts': ['src/webos_accounts/service.py', 'browser/client.mjs', 'pyproject.toml'],
    'storage': ['src/webos_storage/__init__.py', 'src/webos_storage/client.mjs', 'pyproject.toml'],
    'publication': ['src/webos_publication/__init__.py', 'README.md'],
    'rendezvous': ['src/steward/__init__.py', 'pyproject.toml'],
    'network-policy': ['pyproject.toml', 'README.md'],
    'desktop': ['active-system/index.html', 'active-system/app.js', 'active-system/style.css'],
    'v86': ['Makefile', 'src/browser/starter.js'],
    'usd-brep': ['BUILDING.md', 'build.sh'],
    'occt-interpreter': ['Dockerfile', 'README.md'],
    'manifold': ['CMakeLists.txt', 'pyproject.toml'],
}


def existing_entries(component):
    folder = ROOT / component['path']
    # Package exports may intentionally name generated dist files. They are not
    # source entries and must not be linked as if source were missing/retained.
    entries = component['sourceEntries'] + [entry for entry in component['packageEntrypoints'] if (folder / entry).is_file()]
    entries = OWNED_ENTRIES.get(component['id'], entries)
    if component['kind'] == 'upstream-craft-app' and not entries:
        browser = folder / 'apps' / (component['id'] + '-web') / 'Cargo.toml'
        if browser.is_file():
            entries = [str(browser.relative_to(folder)), 'Cargo.toml']
        else:
            entries = ['Cargo.toml', 'packaging/web/package.sh']
    if not entries:
        entries = [name for name in ['pyproject.toml', 'Cargo.toml', 'CMakeLists.txt', 'Makefile', 'Dockerfile', 'package.json', 'README.md'] if (folder / name).is_file()]
    entries = list(dict.fromkeys(str(Path(entry)) for entry in entries))
    for entry in entries:
        if not (folder / entry).is_file():
            raise ValueError('Missing source entry: ' + component['path'] + '/' + entry)
    return entries


def report():
    source = catalog()['components']
    reviewed = json.loads((ROOT / 'migration/COMPONENT-ROLES.json').read_text())
    roles = reviewed['components']
    if len(roles) != len({row['path'] for row in roles}):
        raise ValueError('Duplicate reviewed component')
    roles = {row['path']: row for row in roles}
    if set(roles) != {row['path'] for row in source}:
        raise ValueError('Reviewed roles must cover every current Git-link owner exactly once')
    rows = []
    for component in source:
        row = dict(roles[component['path']])
        if row['id'] != component['id'] or row['recipe'] not in RECIPES:
            raise ValueError('Invalid reviewed role identity or recipe')
        row['entries'] = existing_entries(component)
        recipe_file = RECIPES[row['recipe']][1]
        if recipe_file and not (ROOT / recipe_file).is_file():
            raise ValueError('Missing build definition: ' + recipe_file)
        row['recipeDefinition'] = recipe_file
        row['preparationDefinitions'] = [name for name in ['prepare.py', 'prepare_local_source.py', 'stage.py', 'build-source.sh'] if (ROOT / row['path'] / name).is_file()]
        rows.append(row)
    order = reviewed['categoryOrder']
    if set(order) != {r['category'] for r in rows} or len(order) != len(set(order)):
        raise ValueError('Category ordering must cover exactly the reviewed categories')
    rows.sort(key=lambda row: (order.index(row['category']), row['priority'], row['id']))
    return reviewed, rows


def markdown(reviewed, rows):
    counts = Counter(row['category'] for row in rows)
    apps = sum(row['path'].startswith('apps/') for row in rows)
    lines = ['# WebOS source and application matrix', '',
             f'All locations are relative to `/path/to/webos/`. Each row is one independent Git repository selected by the parent. **{len(rows)} source owners across {apps} app repositories and {len(rows) - apps} supporting repositories.** The app total includes 7 planned game cores, 1 PCB research prototype and 1 application template.', '',
             'The original Desktop/Workspace viewer is `platform/desktop/active-system/`. All 92 files matched the captured original at source correction. Later authorized test-site integration changes bootstrap/account/app wiring; CSS, reference data and artwork remain unchanged. The unsolicited replacement is removed. See deploy/VIEWER-TEST.md for the scoped running composition; this inventory is not an all-app deployment claim.', '',
             'Priority measures contribution to a functional personal WebOS, not popularity. These are reviewed planning priorities, not a dependency resolver. A specialized app still needs its own lower-priority engine. Categories describe ownership and purpose; the interfaces column separately describes human use, browser work, server authority and cross-app/file interaction.', '',
             '| Priority | Meaning |', '|---|---|']
    lines += ['| P' + key + ' | ' + value + ' |' for key, value in reviewed['priorities'].items()]
    lines += ['', 'Every row has source on disk. The state distinguishes what remains before producing or integrating it:', '', '| State | Meaning |', '|---|---|']
    lines += ['| ' + key + ' | ' + value + ' |' for key, value in reviewed['states'].items()]
    lines += ['', '**S does not mean built, runnable in the current desktop, account synchronized, agent complete or deployed.** Full builds were deliberately not run for this organization pass. Required dependency acquisition and historical build evidence are distinct from this source check.', '',
              '| Category | Repositories |', '|---|---|']
    lines += ['| ' + category + ' | ' + str(count) + ' |' for category, count in counts.items()]
    for category in counts:
        lines += ['', '## ' + category, '', '| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |', '|---|---|---|---|---|---|']
        for row in (r for r in rows if r['category'] == category):
            entry_links = [f'[{entry}](../{row["path"]}/{entry})' for entry in row['entries'][:2]]
            prep = row['preparationDefinitions']
            if prep:
                entry_links.append(f'[{prep[0]}](../{row["path"]}/{prep[0]})')
            entry_links.append('Recipe: ' + row['recipe'])
            cells = [f'P{row["priority"]} / {row["state"]}', row['id'] + ' — ' + row['purpose'], f'[{row["path"]}/](../{row["path"]}/)', row['interfaces'], '<br>'.join(entry_links), row['gap']]
            lines.append('| ' + ' | '.join(cell.replace('|', '\\|') for cell in cells) + ' |')
    lines += ['', '## Build and interaction notes', '',
              '- **Files versus Storage:** Files is a human-facing application and file launcher. Storage owns account persistence/revision semantics; Accounts owns authentication and grants. An app file hook is not proof of a confirmed server save or cross-machine acceptance.',
              '- **Runtime versus Desktop:** Runtime owns shared lifecycle/launcher/operation modules. Desktop owns the original workspace viewer. Its old relative bootstrap paths need assembly composition across the new owners; no substitute viewer is provided.',
              '- **Human-only views:** Help is primarily presentation. Most games also contain account-file progress hooks, so calling them purely visual would be inaccurate. Shared engines/tools provide APIs rather than windows. App-specific human/agent parity is not qualified by this inventory.',
              '- **Craft core:** `libraries/craft-libs/` owns many shared crates (documents, media, UI, platform, web-host, fonts and formats); `libraries/egui/`, `assets/craft-fonts/`, `assets/craft-i18n/` and `tooling/craft-common-actions/` have separate roles. Different apps pin different upstream crate revisions; the shared checkout does not silently replace those pins.',
              '- **Craft branches:** all 17 apps and 5 shared Craft projects have an upstream-tracking main branch, with selected working source on a WebOS branch. Upstream heads were fetched on 2026-11-16. No newer upstream source was merged into selected WebOS pins. SolidCraft is the Tangency Labs community project; the other 16 selected apps are Storytold projects.',
              '- **Visible entries versus repositories:** `apps/grid-tools/` contains both Kiri:Moto and Mesh:Tool from one owned upstream project. FFmpeg, TanStack Virtual, CodeMirror and other System Tools menu entries are capabilities, not separate end-user apps. Historical Chat/Chess publication service source is not a current chat app. `legacy/rooms/` is unused old code.',
              '- **Optional guest:** Linux, Terminal and v86 are organized separately and are not dependencies of the minimum future file/editing workflow. The preserved original bootstrap still mentions them; changing that behavior is future integration work.', '',
              '### Recipe keys', '',
              'Recipes below identify source-owned instructions, not commands run during this pass. Read scripts before executing inherited preparation/build operators. Use new external build output directories. Never run deployment/publishing workflows as a source check.', '',
              '| Key | Definition |', '|---|---|']
    for key, (description, source) in RECIPES.items():
        lines.append('| ' + key + ' | ' + description + (f'; [{source}](../{source})' if source else '; see the row’s owned build definitions and README') + ' |')
    lines += ['',
              'The retained JS builder accepts an explicit JSON configuration with `source` set to the assembly root, selected `apps`, explicit `entries` relative to that root, and an external `output`. Its inherited defaults and `deploy/legacy-operations/build-public-apps.py` assume the former grouped layout and must not be used unchanged. Per-component pinned packages, prepare scripts, declared assets, workers, notices and hash-checked patches remain required. This is a located recipe, not a tested all-app production command.', '',
              'The 17 Craft Cargo workspaces previously passed metadata inspection only; that is not browser build proof. The selected WordCraft and DeckCraft branches have historical build/operation evidence, but the rejected desktop’s acceptance does not qualify the original viewer. Read [Craft build inputs](CRAFT-BUILD-INPUTS.md).', '',
              'The locked local input check passed for 6,230 files / 1,115,334,296 bytes. A reference bundle is not source reproducibility. [Declared asset coverage](ASSET-COVERAGE.md) identifies 17 missing Notebook wheel paths and 130 historical ACAD-host generated paths. Neither requires copying obsolete running-site data to claim source organization. Their future production recipes still need explicit inputs/reconstruction.', '',
              'The parent also retains historical cross-system tests, deployment definitions and operator sources under `tests/legacy-*`, `deploy/legacy-*` and `migration/legacy-*`. Private original recovery and unresolved historical records remain outside the source tree.', '',
              'Refresh from reviewed roles and current source paths with `PYTHONDONTWRITEBYTECODE=1 python3 scripts/report_components.py --write`. Exact selected revisions remain in the parent Git links. [Machine-readable roles](COMPONENT-ROLES.json), [full source catalog](SOURCE-CATALOG.json) and [CSV matrix](APP-MATRIX.csv) accompany this chart.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    reviewed, rows = report()
    if args.write:
        (ROOT / 'migration/APP-MATRIX.md').write_text(markdown(reviewed, rows))
        stream = io.StringIO(newline='')
        fields = ['category', 'priority', 'state', 'id', 'purpose', 'path', 'interfaces', 'recipe', 'entries', 'gap']
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({field: '; '.join(row[field]) if isinstance(row[field], list) else row[field] for field in fields})
        (ROOT / 'migration/APP-MATRIX.csv').write_text(stream.getvalue())
    print(json.dumps({'components': len(rows), 'categories': dict(Counter(row['category'] for row in rows)), 'states': dict(Counter(row['state'] for row in rows)), 'allSourceEntriesExist': True, 'buildsRun': 0, 'wrote': args.write}))


if __name__ == '__main__':
    main()
