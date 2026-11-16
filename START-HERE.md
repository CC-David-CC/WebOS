# WebOS fresh rebuild — in progress

Rebuild the entire independently owned suite under this parent. The original
`/path/to/workspace/Documents/KSU.CODES` remains read-only. ksu.codes is the fresh
test target, with test users only. Historical assets and old-user migration are
not prerequisites. Beta and the existing test deployment were not changed by
the latest local qualification.

## Source organization and remaining scope

The parent selects123 component repositories plus1 preserved legacy repository:
85 apps (33 system/CAD,17 Craft,35 games including7 source-only planned cores),
9 engines,7 platform components,19 libraries,2 asset projects and1 tooling project,
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

For Craft Cargo commands in this layout, see
[shared build inputs](migration/CRAFT-BUILD-INPUTS.md). All 17 workspace metadata
checks pass. The selected shared fonts now include the verified Latin catalogue;
DeckCraft's font crate and complete browser target pass offline WebAssembly
compile checks with required fonts. Metadata and compilation alone are not
runtime acceptance; its new optional account view is qualified separately below.
DeckCraft also has a [standalone source-built browser pass](migration/DECKCRAFT-BROWSER-BASELINE.md):
real slide rendering, command insertion and undo. Its [confirmed-save fork](migration/DECKCRAFT-HOST-SAVE.md)
now passes all8 native CI stages and real-browser acknowledgement/view tests,
including shared captured-save identity and explicit failure/unknown outcomes;
those synthetic host results do not establish account persistence. Its
[native document-target check](migration/DECKCRAFT-DOCUMENT-TARGETS.md) now rejects
stale explicit targets at dispatch and exposes real IDs/revisions for inspection.
Its [correlated file-adoption results](migration/DECKCRAFT-CORRELATED-OPEN.md) now
identify the actual opened document, including back-to-back requests and converted
copies. All six standalone browser regressions pass. Its optional
[Desktop/Files/account integration](migration/DECKCRAFT-ACCOUNT-INTEGRATION.md) now
passes real signed account save/reopen, independent views, second-context retrieval
and stale-write protection from a clone-built artifact. Enable it with a verified
`--deckcraft` site; exports, delegated agents and broader acceptance remain OPEN.

Source layout is not complete runtime support. The tracked-source reconciliation
still has 1,165 unresolved dispositions and zero unqualified blob candidates among
preserved backend, scripts, tests, research and WIP. This is not a missing-file
count. The other15 Craft apps and broader apps/games still need browser/host
qualification; WordCraft and DeckCraft also retain explicit lifecycle, export
and delegated-operation gates. Browser build status is
recorded individually in the matrix.

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

Shared peer discovery/signaling source is owned at `platform/rendezvous/`. Its
37 unchanged lease-state tests and nine installed-module imports pass with old
and component sources hidden. It is disabled; signed transport, operational
custody and browser/agent integration remain OPEN. Official Chat/Chess publication
source is organized at `platform/publication/`, with legacy interface imports and
full build/operational qualification explicitly OPEN. Its unsigned reconstruction
fixture passes with old source hidden. An additional28 publication command/test
files are preserved under `platform/publication/legacy/scripts/`; none was run or
installed as an entrypoint. Neither service is enabled.

A separate [historical-output disposition](migration/HISTORICAL-EVIDENCE.md)
accounts for315 preserved reports/logs. Their old PASS/FAIL text is not current
acceptance evidence. Possible fixture/build-input reuse remains explicit review;
no raw output was copied into active source or discarded.

The [legacy CAD corpus catalogue](migration/CAD-CORPUS.md) records276
byte-identical parent-owned test sources and separately preserved old runtime
metadata. These drivers are unexecuted and need a deliberate public-interface,
fixture and source-path port; they are not current ACAD/JSketcher acceptance.

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

Accounts `224bf1a8b48415b3a8750473c26af07a79d5a298` includes a tested optional
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

Latest ownership checkpoint: `run-20261115-59-storage-mirror-references/checkpoint.json` and
`RESUME.md` under the owner-only `/path/to/workspace/Projects/.webos-migration/`.
Phase33 retains243 legacy CAD acceptance sources and34 frozen metadata records with explicit port/review gates.
Phase32 verifies315 historical outputs in private recovery, separate from current acceptance.
Phase31 records28 publication command/test sources preserved unchanged and unexecuted.
Phase30 records32 unchanged publication modules, their structural fixture, and complete ownership of the former44-file steward area.
Phase29 records rendezvous extraction,37 unchanged lease tests and registry/chart reconciliation.
Phase28 records42 retained identity-core tests,4 current-policy checks and4 core retentions.
Phase27 records optional guest backend extraction and installed-wheel checks.
Phase26 records Browser backend extraction and isolated tests.
Phase25 records static Python role review and16 verified Accounts/Storage retentions.
Phase34 is the latest local human browser/account-file workflow evidence; phase24 is the last recorded test-site observation.
Phase23 records the120-source clone and planned-core extraction.
Phase22 records shared/native CI and artifact verification; phase18 holds the
committed build source and artifact. Earlier failed checks remain retained.
Phases21/20 cover Accounts/live routing; earlier phases retain preservation.

The last recorded test-site observation served the earlier phase15 release, including WordCraft0d48; this phase did not recheck it.
newer local Help, authority/routing and native/font changes are not deployed.
Read [deploy/TEST-STATUS.md](deploy/TEST-STATUS.md) for the actual hosted revisions,
backend state, evidence and rollback. Hosted acceptance scripts allow only the
user-designated ksu.codes test origin and use disposable accounts. The updated
authoring test requires the newly built math font, so the old hosted release does
not inherit the latest local qualification. No automatic service restart or
production change is implied by a local commit.

Phase35 completes retention of all276 identified legacy CAD corpus code files, including33 reviewed synthetic-fixture paths. Their interfaces and fixture closure still need porting before execution. The latest basic human build evidence is private phase34: real WordCraft account save/reopen/reload/second-browser-context PASS with original source hidden; no new deployment, physical second-machine or delegated-agent acceptance claimed.

Phase36 retains760 unchanged historical desktop browser-test sources with selected histories, syntax checked and disabled pending deliberate ports. See [legacy desktop tests](migration/LEGACY-DESKTOP-TESTS.md). No current app or browser qualification follows from this extraction.

Phase37 verifies nine previously unresolved identity/file-client/verifier/loader-test records already retained in selected component histories, using exact blob/mode and rename-lineage witnesses. No duplicate extraction or behavior change. See [history reconciliation](migration/HISTORY-RECONCILIATION.md).

Phase38 adds independent shared network-policy source at `libraries/network-policy/`:11 retained source/config/test paths, original and installed-wheel10 passes/1 existing optional database skip. No firewall, listener or desktop policy enabled. See [network policy](migration/NETWORK-POLICY.md).

Phase39 retains1075 unchanged historical operations/build/check Python sources and selected histories at `deploy/legacy-operations/`, disabled pending deliberate authorization/target/interface/side-effect ports. Syntax/history only; no old driver executed. See [legacy operations](migration/LEGACY-OPERATIONS.md).

Phase40 retains85 original desktop visual/license inputs with history in Desktop, including74 launcher icons and wallpaper. Asset bytes/modes, PNG data and representative decoding are verified; active rendering is unchanged. See [desktop assets](migration/DESKTOP-ASSETS.md).

Phase41 assigns53 remaining legacy backend/configuration/documentation paths across seven existing components and parent deployment composition, preserving source/history and keeping all old entrypoints inactive. Current implementations and minimum dependencies are unchanged. See [backend ownership](migration/BACKEND-OWNERSHIP.md).

Phase42 adds the independent local speech engine with34 verified static inputs (97,100,582 bytes), an offline graph builder and successful real CPU/WASM spoken-sample recognition. Inputs live at `artifacts/inputs/speech/`; no user audio is copied and Desktop voice is not enabled. See [speech engine](migration/SPEECH-ENGINE.md).

Phase43 retains Terminal’s original PTY/startup glue, unchanged three-assertion reference test and historical notes. Real guest/current host/agent integration remain OPEN, and no optional guest dependency is enabled. See [terminal source](migration/TERMINAL-SOURCE.md).

Phase44 assigns79 original Node reference-test files to18 application owners, porting only owned imports/fixture URLs with unchanged assertions. Original/current totals match:296 pass,3 captured ACAD failures retained, no skipped/cancelled cases. This is unit/reference scope, not new app hosting. See [app reference tests](migration/APP-REFERENCE-TESTS.md).

Phase45 retains four legacy cross-component references and four shared browser-test helpers in the parent, restoring0 source import edges without copying component implementations. Three original Node reference tests pass in private snapshots; one old DOM/mirror reference remains unrun and all current interface ports remain explicit. See [component boundaries](migration/COMPONENT-BOUNDARIES.md).

Phase46 retains 35 additional original cross-component browser test sources with histories, resolving 41 relative helper imports. Node syntax and exact byte/mode checks pass; no legacy browser driver was executed and no application integration status changed. See [browser helper consumers](migration/BROWSER-HELPER-CONSUMERS.md).

Phase47 retains 145 original CAD case notes beside the archived cross-component test source, with original bytes/modes and selected histories. Historical PASS claims do not qualify the new build; old run outputs remain private and required test-input closure is still open. See [CAD case documentation](migration/CAD-CASE-DOCUMENTATION.md).

Phase48 retains eight statically referenced original CAD review inputs, closing12 known read sites. Three original offline recorded-data reviewer tests pass in isolated snapshot and clean assembly; no native/browser/account-storage acceptance is claimed. Required fixture closure remains open for dynamic and Python paths. See [CAD reference inputs](migration/CAD-REFERENCE-INPUTS.md).

Phase49 retains79 original JavaScript operator/browser-fixture sources with their selected histories, after language-specific syntax and bounded literal screening. No old operator or driver executed and no component functionality changed. See [legacy JavaScript operations](migration/LEGACY-JS-OPERATIONS.md).

Phase50 retains350 original Python operator/check sources after bounded AST/literal and selected-history review.57 other current Python sources remain private for context review. No old operator/driver ran and no app functionality changed. See [context-reviewed Python source](migration/LEGACY-PYTHON-CONTEXT.md).

Phase52 organizes33 original game design sources: seven rule documents in their individual game repositories and26 shared integration/experience references in the parent. Source bodies/histories retained; no gameplay or current rule/API compatibility claim. See [game design ownership](migration/GAME-DESIGN-OWNERSHIP.md).

Phase53 organizes106 original guidance sources: seven lifecycle/file-operation notes in their app repositories and99 shared catalogs/workspace/cross-component references in the parent. All bodies/modes/histories retained; current behavior and historical instruction safety are separate gates. See [app guidance ownership](migration/APP-GUIDANCE-OWNERSHIP.md).

Phase54 retains76 original system fixture/operator/guidance sources and selected histories, including27 HTML pages and disabled host-operation definitions. Four inline scripts parse, wrappers/Python/JSON pass source checks; no old operator/page/service ran. Two JSON literal-context cases and earlier57 Python holds remain private. See [system reference ownership](migration/SYSTEM-REFERENCE-OWNERSHIP.md).

Phase55 retains283 original test/fixture sources with histories. Python/JS/HTML source checks and exact byte/mode/assembly checks pass; old routes/dependencies/fixture/generated compiler inputs remain explicit ports.13 more current Python literal cases remain private. No old test, fixture, app module, browser, Worker, compiler or guest ran. See [test orchestration source](migration/TEST-ORCHESTRATION-SOURCE.md).

Phase56 assigns12 original Node test sources and one frozen vector fixture to actual owners. Eight locator-only ports report15 passing Node subtests; the original baseline has25 passes and one pre-existing stale negative-control failure, retained unchanged and unqualified. Browser relay and cross-component references remain inert. See [owned Node references](migration/OWNED-NODE-REFERENCES.md).

Phase57 verifies127 historical records in existing private recovery without copying them into Git/web roots.109 possible source/design/input/unclear records remain unresolved. Current tracked-source counts come from [the generated summary](migration/SOURCE-RECONCILIATION-SUMMARY.json). A fresh minimum frontend build reuses fully rehashed WordCraft from unchanged selected source; no new browser or full-suite acceptance follows. See [private evidence retention](migration/PRIVATE-EVIDENCE-RETENTION.md).

Phase58 retains nine original native build/design/prototype-control references with histories and exact source bodies. One engine pin changes by reference files only;123 other pins and all active implementations are unchanged. Six copied upstream records remain unqualified despite byte matches, and no old build/control/publisher ran. See [native reference ownership](migration/NATIVE-REFERENCE-OWNERSHIP.md).

Phase59 owns seven legacy mirror cache-unit tests in Storage with locator-only assertion-preserving ports and a new explicitly pinned dev-only dependency environment. Captured, current and clean reference outcomes match:3 pass,4 fail, command exit1; no failing case is omitted or assertion weakened. This is not account synchronization or an all-green Storage claim. See [mirror reference outcomes](migration/STORAGE-MIRROR-REFERENCES.md).

The [existing snapshot-reference review](migration/OWNED-SNAPSHOT-REFERENCES.md) qualifies31 already-owned references and1 private empty output channel without copying raw material or changing component pins. Unresolved supporting-source dispositions remain1,165; byte-candidate guesses are now zero.

The [private terminal-reference review](migration/PRIVATE-TERMINAL-REFERENCES.md) resolves62 captured output records without copying raw data or changing runtime/component pins. Seventy-six weaker terminal-like cases from that batch remain pending; current unresolved supporting records total1,165.

The [isolated-host test extraction](migration/ISOLATED-HOST-TEST-SOURCE.md) preserves41 additional unchanged sources and52 relevant commits. All51 historical Python blobs were reviewed and all41 current files restored independently. Old namespace/service/operator drivers remain inert and unexecuted; no component pin or runtime change.

The [isolated-host deployment source](migration/ISOLATED-HOST-OPERATOR-SOURCE.md) preserves26 additional unchanged helpers and47 relevant commits. All28 historical Python blobs were reviewed and all26 current files restored independently. Privileged host operators remain inactive/unexecuted; configuration/input closure and public-interface ports remain OPEN. No component pin or runtime change.

The [host-context and Microduck ownership review](migration/HOST-CONTEXT-AND-MICRODUCK-SOURCE.md) preserves2 exactly reviewed template/probe sources under parent deployment and1 app-specific hosting policy in Microduck. All3 remain inactive; only Microduck's source/documentation pin changes. Existing missing-fixture failures and functional gates remain OPEN.

The [historical host reference inputs](migration/HOST-REFERENCE-INPUTS.md) preserve24 more records:17 review documents,6 config/pin/manifests and1 inactive browser driver. All27 installer and31 bootstrap source hashes resolve to matching independently owned bytes. This is source-input preservation, not a runnable historical installer or current acceptance. All124 pins unchanged.

The [historical OPFS release source](migration/OPFS-RELEASE-SOURCE.md) preserves15 additional candidate builder/test/model/document records and9 relevant commits. All25 historical blobs were reviewed; all15 files restored independently. Two existing journal/native-fixture owners remain distinct. One pre-existing whitespace warning is retained without changing source bytes; all124 pins/runtime unchanged.

The [private CAD data catalogue](migration/PRIVATE-CAD-DATA-REFERENCES.md) assigns626 frozen records across38 owned historical test cases to private reference preservation. Inputs, native snapshots, containers, records and text channels remain distinct, outside Git/web roots. Twelve representative restores pass; per-file producer/use/privacy/geometry and current acceptance remain OPEN. Thirteen records in two documentation-only cases remain unresolved. All124 pins unchanged.
