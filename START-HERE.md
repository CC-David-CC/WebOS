# WebOS fresh rebuild — in progress

Rebuild the entire independently owned suite under this parent. The original
`/path/to/workspace/Documents/KSU.CODES` remains read-only. ksu.codes is the fresh
test target, with test users only. Historical assets and old-user migration are
not prerequisites. Beta and the existing test deployment were not changed by
the latest local qualification.

## Source organization and remaining scope

The parent selects119 component repositories plus1 preserved legacy repository:
85 apps (33 system/CAD,17 Craft,35 games including7 source-only planned cores),
8 engines,5 platform components,18 libraries,2 asset projects and1 tooling project,
plus legacy Rooms. Applications, including Files and WordCraft, live in `apps/`.
Reusable engines live in `engines/`; shared Craft code is `libraries/craft-libs/`.
FFmpeg is an engine; TanStack Virtual is a library. Neither directory alone means
an enabled app. ACAD, original JSketcher and the preserved office substitute remain
separate. Rooms is unused old code, preserved at `legacy/rooms/` without a service.

See [every component path](migration/COMPONENTS.md), the
[current pass/open matrix](migration/STATUS-MATRIX.md), and the
[17 Craft provenance records](migration/CRAFT-APPS.md). There are16 first-party
Craft projects plus community SolidCraft. The parent pins exact Git commits;
component sources are Git links, never parent-owned copies.

Source layout is not complete runtime support. The tracked-source reconciliation
still has5,970 unresolved dispositions and86 unqualified blob candidates among
preserved backend, scripts, tests, research and WIP. This is not a missing-file
count. The remaining16 Craft apps and broader apps/games require real browser
builds, complete assets, lifecycle and shared-operation qualification.

Browser backend source is now organized under `apps/browser/server/`, with an
installable package using Accounts' public JOSE interface. Its56 Python tests
pass with old source hidden; the JS suite retains93 passes and one pre-existing
host-contract failure. Browser remains disabled pending issuer, launcher, Gecko
asset and desktop integration. Mechanical history extraction and functional
changes are separate commits.

Optional Linux guest backend source is organized under `apps/linux/server/`.
Its installed wheel passes28 unchanged quota tests and6 signed protocol tests
with app/old source hidden. Native operator manifests and kernel/systemd/QEMU
acceptance remain unqualified; Linux stays disabled and outside the minimum.
The old network client is preserved under `apps/linux/legacy/` pending a public
account/session interface port.

## Current working slice

Bring up Calculator → Files → Text → WordCraft, as specified in
[migration/REBUILD-SEQUENCE.md](migration/REBUILD-SEQUENCE.md).

- Calculator: real Desktop mouse/keyboard input, independent windows, move/resize,
  focus, minimize/restore and close/reopen checks pass.
- Files: real signed server storage; folder creation, upload, revision-checked
  rename/move/delete, exact downloads, reload, retained-state restart and retrieval
  from another clean browser context pass.
- Text: real CodeMirror editing; two independent account documents, save/reopen,
  Save As, close guards, reload and second-context retrieval pass. UTF-8 BOM and
  uniform line endings are retained; mixed-ending normalization and remaining
  legacy features remain explicit follow-up work.
- WordCraft: real WASM authoring, heading/paragraph/list formatting, save/reopen
  from Files, reload and second-context retrieval pass. Native commands and
  keyboard edits share the same live document and undo. Stale saves are rejected;
  Save As/PDF identities remain distinct; closing Files does not stop editor saves;
  Cancel and failed Save preserve an unsaved editor.
- Help: independent public view with Desktop, Account files and Documents topics;
  mouse/keyboard selection, separate windows and lifecycle checks pass.

The latest selected WordCraft is `a41d6f9286458a5b460b02fd2f65f2110b969d1c`,
with egui renderer `2d0ae4b4270e76c431fd62d3512237579ed6c26f`, shared font input
`e5f6cc5577fab9534095a6dfe2d409b2d9f72b1d`, and shared repository selection
`3b3271f4eac12daaa42a83411c9f6964aec8f3a3`. Applications retain their own exact
shared-library dependency revisions; the provider must contain them all.

WordCraft passes all9 required CI stages. Its unchanged mathematical PDF test
passes with the declared math-font input and system font directories hidden.
The complete development artifact has27 payload files totaling92,417,572bytes;
source/input identities, every digest and the math-font license were verified.
Actual browser `font.list` confirms STIX Two Math in the running WASM. Clean
account/conflict and formatted-authoring workflows pass with original, primary
and recovery source hidden and external networking disabled. These are local
qualification results, not a deployment or all-app support claim.

The120-repository source assembly also passed a fresh recursive clone,7 complete
source/layout tests,57 planned-game tests and signed Desktop/account-file checks.
LFS smudge was disabled for source cloning; release payload checks remain separate.
A physical second-machine acceptance test remains OPEN.

## Human and agent operations

Files, Text and WordCraft bind permission checks to captured commands/resources;
WordCraft requires an explicit caller. Desktop routes operations to the actual
live view using exact desktop/session/instance/resource identities. Synthetic
capability routing tests are not server-authenticated agent acceptance.

Accounts `037e047e0db88be67057ee262e3d6bd5ab3b59ff` includes a tested optional
proof-bound delegation core. Owner/session liveness, independent agent keys,
exact scope, short one-use intent grants and revocation are enforced there.
All21 retained-identity/delegation tests pass. The launcher does not mount it.
Owner consent UI, HTTP admission, authenticated transport, unforgeable browser
invocation context and scoped agent file authority remain OPEN. Never substitute
a human file capability for an agent's authority. Login UI cannot authenticate itself.

## Planned game sources

Math Path, Fraction Farm, Word Weaver, Market Math, Rule Detective, Pocket Conquest
and Tile Islands have independent repositories. Shared validation/report/odds
modules belong to `libraries/learning-game-core/`. Exact mechanical histories and
separate public-package changes are retained. All57 original rule/report/snapshot
tests pass; rules, assertions and fixture bytes are unchanged apart from imports.

They have no Desktop view, renderer, audio or server storage adapter and are not
enabled games. Save-version incompatibilities remain explicit. Read
[migration/LEARNING-GAMES.md](migration/LEARNING-GAMES.md).

## Build and run locally

Use Node24, Python with uv, and for WordCraft Rust/Cargo1.95.0 with its wasm32
target and Trunk0.21.14. Install only in the new assembly. Public output, private
state, backend environments and build caches must be outside source and disjoint.

```sh
npm ci --ignore-scripts
python3 scripts/bootstrap_backend.py --venv /absolute/new/private/backend-env
python3 apps/wordcraft/webos/build.py \
  --output /absolute/new/wordcraft-site \
  --cache /absolute/private/wordcraft-cache \
  --fonts assets/craft-fonts --translations assets/craft-i18n \
  --egui-origin /absolute/local/bare/egui.git \
  --craft-libs-origin /absolute/local/bare/craft-libs.git
node scripts/build_development.mjs /absolute/new/public --wordcraft /absolute/new/wordcraft-site
/absolute/new/private/backend-env/bin/python scripts/run_development.py \
  --public-root /absolute/new/public --private-root /absolute/new/private/state --port 8130
```

The WordCraft recipe rejects dirty source, wrong input pins and unknown outputs.
Both Git providers are explicit local bare repositories; mappings are scoped to
the build subprocess, with no global Git edits or assumed private server address.
The artifact receipt records exact source, dependencies, tools and payload hashes.
There is no assumed1GiB suite or artifact budget. Account-file limits, browser
cache, resident memory and source/build storage are separate concerns.

Useful checks, each with a new external output directory:

```sh
npm run test:planned-games
python3 -m unittest discover -s tests -p test_assembly.py -v
WEBOS_TEST_OUTPUT=/absolute/new/files-check WEBOS_TEST_PYTHON=/absolute/private/backend-env/bin/python node tests/desktop_files_browser.mjs
WEBOS_TEST_OUTPUT=/absolute/new/text-check WEBOS_TEST_PYTHON=/absolute/private/backend-env/bin/python node tests/text_browser.mjs
WEBOS_TEST_OUTPUT=/absolute/new/help-check WEBOS_TEST_PYTHON=/absolute/private/backend-env/bin/python node tests/help_browser.mjs
WEBOS_TEST_OUTPUT=/absolute/new/authoring-check WEBOS_TEST_PYTHON=/absolute/private/backend-env/bin/python WEBOS_WORDCRAFT_SITE=/absolute/verified/wordcraft-site node tests/wordcraft_authoring_browser.mjs
```

Accounts now has67 layered tests:42 unchanged retained-core regressions,21
existing policy/delegation checks and4 current-public-policy checks. Four old
assertions differ when applied directly to the current policy; the comparison is
recorded explicitly in the component README and phase28 evidence. No production
implementation changed in this test-source phase.

## Git, deployment and continuity

Verified sibling local bare origins are under `../.webos-local-git/`. These are
not an off-device backup. External Git publication still requires verified
identity/destination and authorization. Trusted local source clone:

```sh
GIT_LFS_SKIP_SMUDGE=1 git -c protocol.file.allow=always clone --recurse-submodules ../.webos-local-git/workspace.git /absolute/new/checkout
python3 scripts/setup_lfs.py --executable /absolute/path/to/git-lfs
```

The setup helper configures filters only in the new egui checkout; it does not
materialize payloads. All2144 historical LFS payloads are retained locally;
consumer release-asset materialization remains a separate verified step. Preserve the unrelated historical input-lock update and baseline
browser test still present in the primary worktree. Do not reset or clean them.

Latest ownership checkpoint: `run-20261115-28-accounts-reference-tests/checkpoint.json` and
`RESUME.md` under the owner-only `/path/to/workspace/Projects/.webos-migration/`.
Phase28 records42 retained identity-core tests,4 current-policy checks,4 core retentions and the current ledger.
Phase27 records optional guest backend extraction and installed-wheel checks.
Phase26 records Browser backend extraction and isolated tests.
Phase25 records static Python role review and16 verified Accounts/Storage retentions.
Phase24 remains the last browser-qualified working-system checkpoint.
Phase23 records the120-source clone and planned-core extraction.
Phase22 records shared/native CI and artifact verification; phase18 holds the
committed build source and artifact. Earlier failed checks remain retained.
Phases21/20 cover Accounts/live routing; earlier phases retain preservation.

ksu.codes still serves the earlier phase15 release, including WordCraft0d48;
newer local Help, authority/routing and native/font changes are not deployed.
Read [deploy/TEST-STATUS.md](deploy/TEST-STATUS.md) for the actual hosted revisions,
backend state, evidence and rollback. Hosted acceptance scripts allow only the
user-designated ksu.codes test origin and use disposable accounts. The updated
authoring test requires the newly built math font, so the old hosted release does
not inherit the latest local qualification. No automatic service restart or
production change is implied by a local commit.
