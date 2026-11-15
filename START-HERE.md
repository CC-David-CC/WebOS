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
- WordCraft: real WASM authoring with a heading, paragraph and list; confirmed
  account save; close/reopen from Files; reload and second-context retrieval
  preserve exact paragraph styles and list structure. The clean pinned assembly
  passed too. Stale saves are rejected; Save As/PDF identities stay separate;
  closing Files does not stop editor saves. Delegated agents remain unqualified.

These workflows also pass on **https://ksu.codes**, the fresh test deployment,
using disposable accounts and clean browser contexts. A physical second-client
machine test remains separate. Delegated agent authorization and broader suite
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
Latest active checkpoint: `run-20261115-18-native-ci/checkpoint.json` and
`RESUME.md`; phase17 records clean qualification of the selected authority
fixes; phase16 retains red/green evidence. Phase15 records the current test deployment and renderer
qualification; phase13 records earlier local/clean-clone acceptance. Earlier phases retain
preservation and extraction evidence.

The tested WordCraft source/build integration is committed. The primary
checkout still retains a historical-input lock update and a historical baseline
browser test outside this milestone. Preserve that unrelated work. Original source has not been modified. The fresh ksu.codes test route now
points to the new loopback service; beta.ksu.codes remains unchanged. Read
`deploy/TEST-STATUS.md` for the actual release, hosted evidence and rollback.

## WordCraft artifact and acceptance

Selected WordCraft source is `d7a2ab62d793225463750e440796ba8084e3cc46`, with
shared egui renderer `2d0ae4b4270e76c431fd62d3512237579ed6c26f`.
This renderer passed local regression and clean-checkout authoring checks.
The renderer update is served on ksu.codes using the earlier WordCraft0d48
source. Hosted startup, account and formatting checks passed there. The newer
selected authority fixes are locally qualified but not deployed. The existing
backend stayed running. See `deploy/TEST-STATUS.md`.
`webos/build.py` builds the complete browser graph with Rust/Cargo1.95.0,
Trunk0.21.14 and source-pinned fonts/translations. Supply the explicit
`--egui-origin` local bare fork provider as documented in WordCraft
`webos/README.md`; no global Git configuration or private server is assumed. The verified development
artifact contains26 files totaling91,525,526bytes. Its component-build receipt
checks source identity, tool versions and every artifact digest. Build output
is external, never written into the original workspace.

With a verified source-matching artifact directory, run
`tests/wordcraft_authoring_browser.mjs` or `tests/wordcraft_browser.mjs` using
`WEBOS_WORDCRAFT_SITE`, `WEBOS_TEST_PYTHON` and a new `WEBOS_TEST_OUTPUT`.
The authoring test checks new-document formatting, save/reopen, reload and
second-context persistence. The broader test checks actual typing/native
commands, undo/redo, conflicts, Files-independent saving and close guards.

For the hosted test site, create a fresh account through the Login UI. The browser
acceptance scripts can target the user-designated test site by setting
`WEBOS_TEST_ORIGIN=https://ksu.codes`; this mode creates disposable test accounts
and does not start or stop the remote server. Other remote origins are refused.

## Qualified operation-authority changes

The parent now selects Files `2cf80ef94bd2d340807d6966d1267a7527785245`,
Text `d7c53dd5754aca023f21a28e9b236377c44d090a` and WordCraft
`d7a2ab62d793225463750e440796ba8084e3cc46`. Permission decisions bind to captured
commands and resources; WordCraft requires an explicit caller. All24 focused
tests pass. A new source-pinned WordCraft artifact and a clean pinned assembly
passed actual Files, Text, WordCraft account/conflict and formatted authoring
browser workflows. Original/primary/recovery source was hidden and external
networking disabled. All112 component pins have retaining refs in their verified
local bare origins; this browser qualification covers the ten-component first
slice, not the entire suite.

The baseline native WordCraft CI stopped on three Clippy diagnostics in two
unchanged Rust files; later CI steps were not run. That remains an explicit
quality gate. A separate isolated native review in phase18 simplifies those
conditions and runs required CI without lowering lint thresholds. It has not
changed these selected pins. The ksu.codes deployment remains the phase15
release. Delegated-agent transport is not yet enabled or qualified.
