# WebOS fresh rebuild — in progress

Build the entire independently owned WebOS suite under this parent assembly.
The current user decision is a fresh system on **ksu.codes**, a test location
with test users only. Historical assets and old-user data migration are not
prerequisites. Preserve the original laptop workspace and private recovery.

Bring up **Calculator → Files → Text → WordCraft**, in that order. See
`migration/REBUILD-SEQUENCE.md` for the required acceptance checks. The other
organized apps, games, engines and selected Craft forks remain in scope;
source presence does not establish functional support.

## Current verified behavior

- Calculator: actual Desktop hosting with mouse/keyboard, independent windows,
  move/resize, minimize/restore/focus and close/reopen. Also launched through
  the authenticated assembly.
- Files: real signed server storage; create folder, upload, revision-checked
  rename/move/delete, exact downloaded bytes, reload and retrieval from a
  second clean browser context. Uncertain writes are not reported saved.
- Text: actual shared CodeMirror editor, two independent documents opened from
  Files, edit/save/close/reopen, Save As preserving the original, Cancel/Save
  on unsaved-close, reload and retrieval from a second clean browser context.
  Saves use the same Storage service and exact saved revision as Files.
- WordCraft: preserved baseline and separate review work exist; the new account
  authoring workflow is not yet qualified. This is the next product stage.

These are local development results, not a deployed-site or physical second-
machine acceptance claim. Delegated agent authorization and broader suite
integration remain incomplete. Text preserves UTF-8 BOM and uniform line
endings; mixed-ending save normalization and other legacy Text features remain
explicit follow-up work.

## Source organization

The parent selects111 component repositories plus1 preserved legacy repository
through Git submodules. `migration/COMPONENTS.md` lists every path. Apps live
under `apps/`, including Files and WordCraft; shared engines, libraries,
assets and tooling have their own role directories. Hosted Rooms is unused old
code at `legacy/rooms/`, excluded from current platform and rebuild requirements.

Selected commits in Git links are authoritative. Mechanical extraction and
functional changes have separate commits. Existing independent ACAD and
original JSketcher histories remain separate. All17 selected Craft histories
are retained;16 are first-party and SolidCraft is community-owned. The frozen
beta artifact cache is reference material, not the new release.

## Local development and checks

Use Node24 and Python with `uv`. Install only in the new assembly:

```sh
npm ci --ignore-scripts
python3 scripts/bootstrap_backend.py --venv /a/new/private/backend-env
node scripts/build_development.mjs /a/new/private/public
/a/new/private/backend-env/bin/python scripts/run_development.py --public-root /a/new/private/public --private-root /a/new/private/state --port 8130
```

The backend environment's Python must run the server. Public output and private
state must be separate external directories. Use disposable test accounts.
Browser tests create and stop their own real development server:

```sh
WEBOS_TEST_OUTPUT=/a/new/private/calculator-check node tests/calculator_browser.mjs
WEBOS_TEST_OUTPUT=/a/new/private/files-check WEBOS_TEST_PYTHON=/a/new/private/backend-env/bin/python node tests/desktop_files_browser.mjs
WEBOS_TEST_OUTPUT=/a/new/private/text-check WEBOS_TEST_PYTHON=/a/new/private/backend-env/bin/python node tests/text_browser.mjs
python3 -m unittest discover -s tests -p test_assembly.py -v
```

Every output path must be new. Use current component packages and shared public
interfaces. Do not import private source across repositories or build against
the original workspace. Tests with two browser contexts are not two machines.

## Recovery, Git and continuity

Local sibling bare origins are under `../.webos-local-git/`; these are not an
off-device backup. No external Git publication is implied. Trusted local clone:

```sh
git -c protocol.file.allow=always clone --recurse-submodules ../.webos-local-git/workspace.git /a/new/disposable/checkout
python3 scripts/setup_lfs.py --executable /absolute/path/to/git-lfs
```

The LFS setup affects only the new egui checkout. Verified local origins retain
all2144 historical LFS payloads. Recovery and raw evidence stay owner-only,
outside Git and web roots, under `/home/dflanag3/Projects/.webos-migration/`.
Latest active checkpoint: `run-20261115-13-fresh-bringup/checkpoint.json` and
`RESUME.md`; earlier phases retain preservation and extraction evidence.

The primary checkout retains separate WordCraft review/build WIP and a completed
historical-input lock update. Do not stage all files or silently promote that
work. Original source has not been modified; no ksu.codes deployment change has
been made in this bring-up phase. Verify the test deployment target and prepared
artifacts before changing server configuration or starting the new test system.
