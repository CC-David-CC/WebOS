# WebOS rebuild — entire suite, in progress

The goal is a working, independently reproducible assembly of the entire existing WebOS suite and all 17 selected maintained upstream forks. Runtime, Desktop, Login, Accounts, Storage, Files, and WordCraft are the first milestone. They do not define the final scope.

Read `migration/scope.json` for the registered catalog, source ownership candidates, asset gaps, and remaining requirements. The old builder registers 75 IDs including 28 games; those counts describe that registry, not all discovered source or qualified applications. Nonregistered source and historical WIP remain in scope.

## Verified source assembly

The assembly currently pins 81 source components. ACAD, original JSketcher, and four engines retain their independent histories. All 17 selected upstream fork histories are attached as source baselines; they are not qualified releases. Help, Calculator, and Files were mechanically extracted from verified recovery copies, preserving earlier source paths and commit maps. Their current app trees retain the exact original Git tree identities. Six existing unit scripts passed in the recovered monorepo, extracted repositories, and a fresh recursive clone. Help has no extracted unit script. A fresh recursive local clone passed for the first 26 source components and was advanced to include Runtime. Organized-layout clone verification is recorded separately. WordCraft passed its unmodified WASM compile check; its isolated fresh-clone check also passed with the original workspace hidden and networking disabled. These results do not prove browser integration, full asset builds, persistence, or human/agent parity.

The `.gitmodules` entries and Git links select component commits. They are the source version authority. Component source is never copied into parent-owned files. Whole-system tests and composition belong to this parent. Mechanical extraction and functional changes are separate commits.

## Remaining scope

Preserve and account for every existing app, game, tool, library, required asset, and WIP state. Keep ACAD, original JSketcher, old editors, and the selected replacement forks distinct. All 17 selected maintained forks now have source submodules with original histories, licenses, and structures retained on local `webos/integration` branches. Their browser builds and host operations still require individual qualification. Source presence does not establish support.

Build real server-backed account files with existing identity and file ownership compatibility. Human, authorized agent, and test operations share the same domain implementations. One authoritative live document per session and server-authoritative saved revisions are mandatory. No browser cache may masquerade as a confirmed server save. Linux/v86, Terminal, MailCraft, and Craft Anything are not minimum dependencies; preserve existing excluded source separately.

A partial development assembly now boots Login → Desktop → Files against real signed account storage. WordCraft and delegated agents are not connected, so the seven-component minimum and full-suite gates remain incomplete. No existing-user continuity result is claimed.

## Local Git and recovery

Local sibling bare origins are under `../.webos-local-git/`. They are not an off-device backup. For a trusted fresh local clone, use:

```sh
git -c protocol.file.allow=always clone --recurse-submodules ../.webos-local-git/workspace.git /a/new/disposable/path
```

Private recovery/evidence is under `/path/to/workspace/Projects/.webos-migration/`. Start with `run-20261114-02/phase-checkpoint.json` and its evidence reports, then the earlier `run-20261114-01/checkpoint.json`. Raw capture includes tracked source/Git metadata, not all ignored assets or live account data. Do not publish private logs, credentials, account databases, or user documents.

The original workspace and deployment stay unchanged. No external publication, production change, service restart, or account-data migration is authorized. Continue local work while separately gated actions remain pending.

SolidCraft includes a separate brand/interface license. Preserve its notices and resolve the distribution gate before publishing or deploying it. No legal conclusion or distribution permission is implied by the local source checkout.

## Disk layout and source checks

Platform components live at `platform/{runtime,desktop,login,accounts,storage}/`. All applications live under `apps/`, including Files, WordCraft and original JSketcher. Reusable engines live under `engines/`. Shared library, asset and build-tool projects live under `libraries/`, `assets/` and `tooling/` after ownership review. Each meaningful component remains an independent repository; these grouping directories are not grouped source repositories. `tests/`, `scripts/`, and `deploy/` belong to the parent.

Disk organization is incomplete. Many existing beta apps and tools still await extraction. Existing editors remain in scope alongside their replacements. Shared Craft libraries and FFmpeg are now attached; their host/build wiring remains separate work. The current priority is complete source organization, followed by remaining integration work.

Run `python3 scripts/inspect_assembly.py` to inspect actual source wiring without network calls. Add `--require-core` to require all seven core sources. Run `python3 -m unittest discover -s tests -v` for source composition acceptance. All seven required component sources are present. Source composition tests remain separate from browser/backend acceptance.

The original app inventory default is 1GiB per app bundle. It is not the suite disk budget. The new release must configure installation policy from actual artifact graphs and keep code, assets, downloads, browser cache, memory, and account-file budgets distinct. The stale 512MiB Runtime regression was corrected against the historical approved policy, with exact/over-1GiB coverage, in a commit after mechanical extraction.

## Core backend progress

Desktop, Accounts, and Storage source histories are now attached. Their extracted baselines were checked against every selected current blob/mode. Storage retains research OPFS under its separate historical namespace; merge topology was preserved after a byte-identity check caught a filtered merge regression. The original source remains unchanged.

Accounts and Storage now expose installable Python packages. Four Accounts retained-state tests and four Storage durable/revision/permission tests pass using real generated temporary SQLite/filesystem state. They also pass from a clean recursive clone with the old workspace and primary new checkout both hidden and networking disabled. This is domain-level evidence, not signed HTTP/browser/agent acceptance or production-user compatibility.

`python3 scripts/bootstrap_backend.py --venv /absolute/new/private/environment` prepares Runtime, Accounts and Storage packages and locked third-party dependencies outside source, starting no server. See deploy/README.md. Login is now independently extracted and built. The Desktop public window/workspace controller and Files server-backed view now boot in development. Next connect WordCraft with real asynchronous save confirmation and editor operations.

## Signed development foundation

The public browser packages are installed with `npm ci` in this parent workspace. Accounts owns private credentials and exposes public inspection plus an epoch-bound human file capability. Storage consumes that capability and builds its real hashing/verification worker. Runtime owns their shared stateless wire contract. Login mounts synchronously and reports asynchronous readiness/cancellation; it never authenticates itself. Agent delegation remains pending.

`scripts/run_development.py --public-root /absolute/built/public --private-root /absolute/new/private/state --port 18140` composes the real Accounts and Storage services on loopback. Run it with the environment prepared by `scripts/bootstrap_backend.py`. Build the development frontend first with `node scripts/build_development.mjs /absolute/new/public/output`. It includes independent Login, Desktop and Files plus the complete verification-worker graph. WordCraft is not connected yet. The launcher refuses unknown or incomplete private state, retains keys and files on restart, and changes no production service.

Real Chromium tests `tests/login_browser.mjs` and `tests/account_files_browser.mjs` require `WEBOS_TEST_PYTHON` and a new external `WEBOS_TEST_OUTPUT` directory. The signed-file test passed using five clean browser contexts, including a graceful server restart followed by sign-in and retrieval of the same account-owned bytes/revision. It also verifies stale-save rejection, cross-account denial, unsigned request denial, logout fencing, closed-view service retention, and zero guest dependencies/page errors. These are component integration tests, not Desktop, WordCraft, agent parity, production-user continuity, or a second physical machine.

Latest private evidence: `run-20261114-04/account-files-browser-r2/result.json`, `run-20261114-04/login-browser-r2/result.json`, and `run-20261114-04/checkpoint.json` under the private migration root. Earlier `run-20261114-03/checkpoint.json` covers baseline backend isolation; earlier preservation records remain authoritative for their stated scope.

## Assembled Desktop and Files progress

`tests/desktop_files_browser.mjs` builds the actual development frontend and tests it with disposable signed Accounts/Storage state in two clean Chromium contexts. It verifies human upload, cross-client listing, exact-revision rename/delete, cancelled delete, interrupted upload reported as unconfirmed, workspace/window controls, close/reopen, and sign-out cleanup. The development launcher and these tests stop their temporary servers on exit. No production service is changed.

The first Desktop/Files port is functional but does not claim all legacy features. Read each component README for preserved features still needing a deliberate port. The launcher lists only integrated apps. Opening an editor reports that integration is unavailable; it does not pretend a document was opened. Full WordCraft browser assets, durable editor save/Save As/export, scoped agents, resource policy, all remaining suite extraction/integration and existing-user continuity remain explicit work.

## Next independently owned game

Solitaire now lives in `apps/solitaire/` as its own pinned repository. Its 24-file original source tree, three historical directory locations, package lock, design/WIP and tests were preserved with a commit map. Typecheck and all 16 existing tests passed both before filtering and in a fresh independent clone. A separate metadata commit adds generated-output exclusions and a migration note. Its old Desktop/mirror host still requires a functional port; it is not enabled or claimed as browser-qualified. Earlier whole-system game tests remain preserved and assigned to parent porting work. Private extraction evidence is in `run-20261114-05/`.

## Shared Craft source and FFmpeg

Shared Craft source now has explicit owners: `libraries/craft-libs/`, `libraries/egui/`, `assets/craft-fonts/`, `assets/craft-i18n/`, and `tooling/craft-common-actions/`. These preserve full upstream Git histories and selected immutable revisions. The 16 consuming Craft apps retain their existing manifest/lock pins, including different revisions within one app. A library checkout does not silently replace those dependencies. The reusable workflow source is preserved only; no publishing workflow was run. Its missing top-level license remains a distribution review item.

`engines/ffmpeg/` preserves the existing six-file background tool, worker, dependency lock and license notice with exact source blobs/modes and filtered history. It has no standalone window in the original implementation. Audio/editor callers and build-asset wiring still need deliberate ports. The `@ffmpeg/core` dependency remains pinned to 0.12.10; extraction is not a qualified engine build.

The `egui` history uses Git LFS. Install Git LFS on a development machine before materializing its image assets. Local sibling origins retain all 2,144 historical payloads (277,667,063 bytes), with SHA256/size verified. With `git-lfs` on PATH, a trusted recursive local clone can enable filters for that command only:

```sh
git -c protocol.file.allow=always -c filter.lfs.process='git-lfs filter-process' -c filter.lfs.required=true clone --recurse-submodules ../.webos-local-git/workspace.git /a/new/disposable/path
```

After cloning, run `python3 scripts/setup_lfs.py` (or supply `--executable /absolute/path/to/git-lfs`) to retain the clean/smudge filters in the egui checkout only. This prevents materialized images being mistaken for source modifications during later status checks. No global Git configuration or hook changes are required. Source wiring checks alone do not verify LFS payload materialization. Private preservation, extraction maps and asset verification for this step are under `run-20261115-07-shared-source/`. Full disk organization remains incomplete; the remaining beta tools, games, editors and nonregistered source remain in scope.

## Existing beta shared tools

The existing beta integration modules for CodeMirror, glTF Transform, WaveSurfer, Tone, zip, Mermaid, ECharts, Plotly, pdfme, MapLibre, Transformers, Trystero, TanStack Virtual, WebTorrent and Yjs now each have an independent repository under `libraries/`. ONNX Runtime lives at `engines/onnx-runtime/`. Their current source blobs/modes, package locks and owned history were preserved mechanically. These repositories own the existing WebOS integration source; their npm dependencies retain upstream ownership and license obligations. Their historical background-tool `mount()` rejection remains unchanged, and is not a working desktop window.

No component test scripts exist in those sixteen original package manifests. Source identity and clone checks do not claim browser behavior or complete external model/WASM assets. The remaining existing user-facing editors, games, CAD integration, nonregistered source and platform leftovers are still pending organization. Original OpenCascade browser integration ownership also requires reconciliation with the already independent OpenCascade engine source.

## All existing registered game source now under apps/

All 28 registered games now have independent repositories under `apps/`, including the earlier Solitaire extraction and 27 additional games. Their source, designs/WIP, dependencies, artwork and owned historical paths were preserved. The 27 new mechanical baselines reproduce all 597 current file blobs/modes exactly, with per-repository commit maps retained privately. Separate metadata commits add generated-output exclusions and provenance notes.

The old sibling-layout baseline passed all 25 configured game test commands and all 23 configured typechecks. Independent extracted checks passed except for a mixed Snake/Owl test importing Owl private source. Separate commits moved the two unchanged Owl cases into Owl's own suite, preserving all three original case bodies/assertions and the total passing count: Snake 11 plus Owl 2 equals the original Snake suite's 13. Both independent suites now pass, and Owl's runner is explicitly pinned. No application behavior was changed by that test ownership repair.

All 12 declared asset files across these games resolved in both the baseline and independent test copies with equal hashes. Falling Blocks retains its authored coach RML, instructions and tracked `coach.riv`; that artifact matches the existing pinned SHA256. Its Rive CLI rebuild/render tests were not run. No package test script existed for Falling Blocks or Owl before the ownership split; source presence is not a complete asset-build or rendering proof.

These games are organized source, not enabled applications in the new Desktop. Deliberate ports of their old host/account-save/lifecycle interfaces, complete browser builds and shared human/agent operations remain separate work. The remaining existing editors, tools, nonregistered source, platform leftovers and asset ownership still require organization. Private extraction and test evidence is in `run-20261115-08-games/`.
