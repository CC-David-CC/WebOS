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
- Help: restored as an independently owned public view with Desktop, Account
  files and Documents topics. Mouse/keyboard selection, two independent windows,
  close/reopen and explicit authorized operations pass local and clean-checkout
  checks. The historical beta/Linux guide remains preserved separately.
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

The Calculator/Files/Text/WordCraft workflows also passed on **https://ksu.codes**,
the fresh test deployment,
using disposable accounts and clean browser contexts. Help and the newer
operation-authority changes are local only. A physical second-client
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
WEBOS_TEST_OUTPUT=/a/new/private/help-check WEBOS_TEST_PYTHON=/a/new/private/backend-env/bin/python node tests/help_browser.mjs
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
outside Git and web roots, under `/path/to/workspace/Projects/.webos-migration/`.
Latest active checkpoint: `run-20261115-21-scoped-delegation/checkpoint.json` and
`RESUME.md`. Phase20 records live view routing. Phase18 records the separate
native/font review; phase22 tracks the shared update-dialog translation failure
that its next full CI exposed.
Phase17 records clean qualification of the selected authority
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
unchanged Rust files. A separate isolated phase18 review simplifies those
conditions without lowering lint thresholds. Formatting and Clippy passed;
its first run reported3,547 test passes,1 failure and5 ignored. The PDF
`chart_and_equation_text_keep_their_pdf_bytes` failure was traced experimentally
to a missing math font. The unchanged test passes with pinned STIX Two Math,
including with system font directories hidden. A maintained shared font commit
`e5f6cc5577fab9534095a6dfe2d409b2d9f72b1d` contains the unmodified font,
license, provenance and tested manifest. Its checks also pass from a clean clone.
It is ahead of the parent's selected font pin during review; do not reset it.

The next full WordCraft review run passed formatting, Clippy and4,969 main tests
(8 ignored), then failed the translation audit: shared craft-update draws an
untranslated network-error detail when offline. Phase22 investigates the fix in
that shared library, without changing the audit. Language, doctests, assets,
layers and wasm were not run. Native/font review has not changed the selected
WordCraft pin. The ksu.codes deployment remains the phase15
release. Delegated-agent transport is not yet enabled or qualified.

The selected Help commit is `e68a507ea52235d282e1e2496f24e9ff8f98c948`.
Its five boundary checks and actual desktop browser workflow pass, including a
clean eleven-component checkout with original/primary/recovery source hidden
and external networking off. The complete graph accepts the verified WordCraft
artifact; adding Help changed no registry package versions. Help is not yet
included in the hosted phase15 release. Its command interface does not enable
or qualify delegated-agent authentication.

## Live application operation routing

The selected Desktop is `365f11113645634dc18c002873ec6efeab0267df`.
Its public view-inspection/command methods require exact desktop, session,
instance and `view:<instance>` resource targets. The unchanged caller reaches
the application's existing public command implementation, which still applies
its resource policy. Request capture preserves explicit upload bytes; view
replacement, close and disposal invalidate pending decisions. Uncertain outcomes
are reported for commands completing after view removal.

All13 Desktop checks pass, along with clean-checkout browser checks for live
Help state shared by mouse and commands, reader/mutation denial, cross-window
refusal, signed Login/Help and the real WordCraft account/conflict workflow.
The capability-routing test uses synthetic in-page callers. The parent still
accepts only its human capability: Accounts-issued delegation, an authenticated
agent transport and agent file authority remain incomplete. These new Desktop
bits are not deployed to ksu.codes. Native CI continues separately in phase18.


## Accounts delegation core selected locally

Accounts `76dad308d12d0750538602e77ba34212478d5256` adds an optional,
proof-bound delegation core. Registered owners approve exact desktop/session/
instance/resource/command scope for an independent agent key. Short operation
grants bind exact intent bytes, require owner consumption, and are single use.
Owner logout, persisted revocation, disabled accounts and password-generation
changes invalidate authority. Ordinary inspection omits credentials.

All21 Accounts tests pass from a clean eleven-component checkout with the
original, primary and recovery source hidden and external networking disabled.
Real signed account-file browser checks, retained-state restart, Login/Help and
three issuer-origin checks pass too. All112 parent pins remain retrievable
from local bare origins. The restart test now retains its original issuer port;
the development listener permits address reuse after stopping. Prior failed
runs remain in phase21 evidence.

This core is not mounted by the launcher. Owner consent UI, authenticated agent
transport, unforgeable browser invocation context and scoped agent file authority
remain required. Existing human file authority must not stand in for an agent.
The test deployment is unchanged; this selection is local only.
