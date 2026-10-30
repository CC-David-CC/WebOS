# Simplified branch handoff

This branch is source development only. It has not been deployed. The old
live site is not modified. Historical handoffs and deployment manifests refer
to the original system and are not instructions for deploying this branch.

## Current implementation

- The desktop no longer loads the peer browser network and Chat, Chess and
  Rooms apps were removed. Signing and the browser-to-server guest relay remain.
- System app source is in `apps/system`, personal template source in
  `apps/individual/templates`, and the app builder compiles their explicit
  entries including dependencies.
- Account Files and Text use `active-system/storage/browser/mirror.mjs` to save
  into account-scoped IndexedDB and queue signed server synchronization. It
  retries, keeps unsynchronized changes and exposes divergent versions for a
  user choice. There is no PC download button. Browser storage can be cleared
  or evicted and Linux guest files are not part of this mirror.
- The server's file gateway checks each signed account and its permissions;
  the private files are owned by the service Unix user, not separate Unix users.
  See `active-system/storage/accounts/README.md`.

## Local verification

Install build and test dependencies locally (they are ignored by Git):

    npm ci --prefix active-system/tools/app-builder --ignore-scripts
    npm ci --prefix tests --ignore-scripts
    node tests/mirrored-files.test.mjs
    node tests/files-workflow.test.mjs
    python3 active-system/scripts/build-public-apps.py --output active-system/.build/simplified-apps

The Files/Text workflow test uses an in-memory server and a DOM simulation. The
mirror test covers offline writes, account scoping, two-tab version conflicts,
server conflicts, remote refresh, folders, deletion and lost replies. The
existing real loopback signed file-gateway HTTP suite also passed 13 tests using
its own disposable state, after updating an obsolete test password. These tests
do not establish end-to-end behavior in a real browser against a running
simplified deployment. The workstation's existing ChromeDriver failed to start
Chrome during this work. A local issuer staging smoke check served the login
page, signed-server configuration, app manifest and browser mirror; it did not
start a complete file gateway or test a browser login.

## Remaining before deployment

- Complete removal of old peer, chat and chess server/operator code and stale
  tests; some legacy scripts and origin/steward code remain intertwined with
  the issuer. Do not use old deployment scripts or release profiles as-is.
- Build a coherent standalone server configuration and release/serving path
  for the reorganized apps, mirror, issuer, gateway, and VM assets.
- Exercise login, mirror, account isolation, offline recovery, conflicts,
  browser restarts and two real browser devices with the actual signed gateway.
- Verify the VM and desktop apps in a real browser, and document operational
  backup/recovery of private account files and databases.

## Local preview on this workstation

`run-simplified-local.py` starts a loopback-only issuer, signed file gateway
and desktop at port 18130. It uses ignored `storage/accounts/data/` and
`storage/accounts/state/` directories for account files and permissions, and
`.build/simplified-local/issuer/` for its test login database and signing key.
These are real local preview state and are not included in Git backups. The
local Linux guest has no Internet relay configured. It requires rebuilt app
bundles and VM boot assets; `--speech-assets` optionally copies an existing
speech runtime/model into the ignored staging tree.

A real local Chrome smoke test registered a separate test account, opened the
desktop, created and edited a file, and confirmed it arrived in the correct
server account folder. The same test does not prove behavior across devices or
deployment readiness.

## Chonky Files and Text reload

Files uses Chonky with React bundled solely in the lazily loaded Files app.
The account mirror supports version-checked file moves and right-click file
rename; it journals the operation locally, uses atomic server rename, retries a
lost response and preserves conflicts. Only synced files and synced destination
folders can begin a move; folder moves/renames remain unsupported. Text Reload
checks the server first and an open editor reports changes detected by sync.
External files must be owned by the file service. Common 0644/0664 file modes
are automatically tightened to 0600 when read or scanned; restrictive owner
modes and unsafe links are rejected. One unreadable
server file no longer stops other files from syncing; its name is reported.

`tests/chonky-browser.test.mjs`, `tests/chonky-move.test.mjs` and
`tests/chonky-rename.test.mjs` exercise the
local preview with a disposable account and a running Chrome DevTools endpoint;
they need the explicit `CODI_TEST_USER`, `CODI_TEST_PASSWORD`, and, for the
first test, `CODI_TEST_FILE_ROOT` environment variables. Neither test should
be pointed at a real account.

## Image Editor

`apps/system/image-editor` wraps Filerobot with app-local React 18 and its own
pinned package lock; Files independently bundles React 19. PNG/JPEG/WebP images
open from Files, and Files offers an import button. The editor uses the shared
version-checked mirror, prevents the vendor's download action, disposes on
close, and disables backend translation and cloud image services. Images are
limited to 8 MiB and 20 megapixels. A real isolated-browser test covers opening,
resizing, saving to the account's server folder, closing and reopening without
external requests. Run `npm ci --prefix apps/system/image-editor --ignore-scripts`
before building the public apps.

The local launcher source now sets a larger per-minute gateway request limit to
avoid the earlier prototype limit being exhausted by directory synchronization.
The local preview was restarted with this limit; the gateway's default remains unchanged.


## Document Editor, PDF Viewer and Spreadsheet

The local preview includes three independent, lazily loaded system apps. The
Tiptap Document Editor writes `.doc` documents to the versioned account
mirror, exports a separate PDF and sends a preview to the PDF.js viewer. The
viewer also opens saved PDFs from Files. PDF output is for straightforward
reports; unsupported content or characters are reported, and it is not a
pixel-perfect document layout system. No DOCX or download-to-PC button is added.

Spreadsheet uses Jspreadsheet CE with an app-owned SheetJS worker and stores
`.codisheet` files; XLSX import makes a copy and export creates a separate file.
Basic arithmetic and a small set of functions use a bounded parser; unsupported
formulas show an error. Excel formatting, charts and advanced features are not
preserved. The vendor's dynamic formula evaluator is disabled under the existing
CSP. Each app has its own pinned lockfile; npm dependencies and built assets are
not committed. Run npm ci --ignore-scripts in each app before rebuilding.

Isolated Chrome tests cover document save/reopen, generated multi-page PDF and
viewer, server files, offline sync, conflicts, account separation and cleanup;
touch emulation covers editing and independent windows. A spreadsheet browser
test covers typing, formulas, native save/reopen, XLSX import and export; parser
tests cover malformed and hostile formulas. These are not physical-phone tests.
The tests use disposable accounts and the isolated local preview. The current
local preview at 127.0.0.1:18130 was updated; no public site was changed.


## Data Explorer

`apps/system/data-explorer` packages Perspective and DuckDB-Wasm together as a
lazy app. It opens account-mirrored CSV files, runs browser-local SELECT queries,
and provides Perspective grid, pivot and chart controls backed by DuckDB's
virtual-server adapter. Database contents, query text and viewer settings are
currently temporary; opening DuckDB database files and saving query results are
not implemented. CSV files are limited to 32 MiB. Automatic DuckDB extension
downloads are disabled. The app's first load is roughly 44 MiB; charts need
worker graphics support. The current Perspective virtual server logs an
unhandled unsubscribe request during viewer cleanup. The viewer, DuckDB connection and per-window database worker are disposed;
Perspective may retain a shared chart worker for reuse. The warning is an
upstream limitation.

`tests/data-explorer-browser.test.mjs` covers an isolated signed-in browser,
CSV import, aggregate SQL, grid, grouped bar chart and closing the window.
The loader and builder bundle-size limits were raised for the DuckDB WASM;
packages remain isolated and lazy. No external site was changed.

## FFmpeg background tool

Applications → System Tools shows a disabled FFmpeg item: the entry has no
window, but apps can call the lazy browser-local tool via `host.tools`. Each
caller has its own single-thread worker; no server process or external CDN is
used. A real browser test generated a WAV, converted it to MP3, verified the
menu and lazy loading, and checked app-view cleanup. The 31 MiB GPL-licensed
core loads only when used; review its source and distribution obligations
before publishing. See `apps/system/ffmpeg/README.md` for the API and limits.

## Audio tools

Applications → Audio Tools opens AudioMass as Audio Editor. Its host controls
open an account file and save single-track edits as a separate version-checked
WAV. Multitrack session persistence is not implemented. AudioMass's embedded
PC download actions are disabled; the host Save WAV button saves to Files.
The browser media CSP now permits local blob media for waveform playback.

WaveSurfer.js and Tone.js are lazy system libraries, not windows: app authors
use `host.tools.createWaveSurfer(options)` and `host.tools.loadTone()`. A real
browser test covers AudioMass opening, reverse editing and saving a WAV to the
account folder, Tone offline synthesis, and WaveSurfer rendering. AudioMass is
prepared from a pinned hash-verified upstream archive with `prepare.py`; its
untracked vendor files and all generated bundles stay out of Git. See each app's
README for limitations, dependencies and audio-resource cleanup.

## 3D printing and archives

Applications → 3D Printing contains Kiri:Moto, Mesh:Tool and G-code Preview.
Kiri and Mesh share a pinned, locally built Grid.Space bundle, with model import
and export connected to the account file mirror. Their internal workspace and
printer profiles remain local browser state, namespaced by account; exporting to
Files is needed for server sync. The G-code viewer's 220 × 220 × 250 mm grid is
illustrative and no physical printer is connected. Tests cover STL import, mesh
union and export to Files, Kiri slicing and G-code export, account workspace isolation and G-code
preview. Advanced modes and physical printers are untested.

Files offers Create ZIP and Extract ZIP on selections; extraction goes into a
new folder and checks paths, symlinks, CRCs and size limits. Folder trees can be archived recursively. zip.js is also a lazy shared system tool; see
`apps/system/zip/README.md`. Grid.Space requires the pinned npm dependencies and
`apps/system/grid-tools/prepare.py` before building. Vendor dependencies and
built assets stay out of Git. All work has been on the local preview.

### 2026-10-30 — account file chooser and engineering workflows

The local Simplified preview at `http://127.0.0.1:18130/` serves the shared My files chooser from source commit `a0a5814ec` (backed up to `box-git-distro`, branch `simplified`). The new student guide is `USER_GUIDE.md`; the app contract documents `host.storage.pickFile`. Text, document, spreadsheet, image, PDF, data explorer, notebook, audio, grid/printing, G-code, SVG-edit, diagrams.net and Excalidraw have chooser entry points. Not every chooser has been individually exercised. Keep PC upload as a separate import path.

Browser checks passed for account folder browsing and text save/reopen including chooser cancellation and window disposal; document editing, PDF preview/export, offline sync and conflicts; CSV → DuckDB query → Perspective chart; spreadsheet save/import/export; image resize and save; SVG, diagrams.net and Excalidraw save/reopen. These checks do not establish full third-party application coverage. The actual guest Linux notebook, production Debian guest and SSH relay remain unfinished. Browser notebook requires scoped `unsafe-eval` and shares the desktop origin; it is not an isolation boundary for untrusted notebooks.

SSH policy/audit implementation remains uncommitted local work in `active-system/guest_service/{coordinator,egress,worker,ssh_audit}.py` and `tests/guest_ssh_*`. It is **not deployed or configured**: in particular, the current experimental egress policy permits port 22 while audit is optional, so it must not be deployed before enforcing mandatory metadata logging and trusted source attribution, provisioning, and end-to-end checks. Private destinations remain intended to be denied; LLM hosts need separate controlled services. The experimental Debian root and test artifacts in `.build` are not a release image.

### 2026-10-30 — app workflow worktrees and temporary Linux boundary

Latest direction supersedes the previous Account-mount notes: Linux home is temporary and is not automatically synchronized. Files can browse `temp_linux`, and its explicit Copy to account action makes a separate My files copy; other apps open My files. A real v86 browser test confirmed no automatic transfer, explicit copy and reset on refresh. Files sees Linux home, not the entire Linux root filesystem. The local preview at 18130 serves this behavior.

App checks are recorded in `docs/APP_WORKFLOW_CHECKS.md` and source-only worktree branches are backed up to box-git: `simplified-apps-office`, `simplified-apps-creative`, and `simplified-apps-engineering` under `/home/dflanag3/codi-app-worktrees/`. Verified commits were cherry-picked into `simplified`. Tests discovered and fixed notebook file switching showing stale contents, Excalidraw treating a clean loaded drawing as edited, and Document Editor accepting but not saving `.codidoc`. Those fixes are staged in the local preview. The app matrix lists the different scope of viewers, generators and library-only tools. The checks do not prove all third-party features or production deployment. Existing uncommitted SSH policy/audit work is still incomplete and not deployed.

### 2026-10-30 — Simplified is live at the domain root

User authorized the cutover. `https://ksu.codes/` now serves the public-only
Simplified static release `/srv/codi-connected/simplified/f66430feb99b44df8de20261f617091c0b079c8441d324842ef63c399d97b07e` (payload source `f44b9f285`, full file-hash manifest beside it). Existing live issuer, signed file gateway/account data, guest network and speech services remain; no account state was copied from the local preview. Existing old backend P2P/chess services have not been retired even though Simplified does not use them. `/desktop/` and `/blog/` remain served by the existing website. The local preview is separate.

A temporary cookie-gated preview and then the actual root both passed real HTTPS Chrome login, signed file write/server-disk confirmation, Linux boot, Document Editor, and JupyterLite notebook. Guest `ping -c 1 1.1.1.1` passed through the existing server relay. The disposable deployment test account, its file and account metadata were removed. Cache migration was tested with an old root service worker. All ten server-loopback production smoke checks passed after updating the KSU root marker for the new entry page; independent WAN and physical-phone checks were not performed for this release.

Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `2113960e01087f5f152ff9d29739edf179dd129e603d424164a3f71fd0d57406`, Caddy `741009873464573be63dffa1a913c5cfebde117cf904c9017b9e4f26d0f62ebf`. Use the hosting controller lock and `ops/webctl.py` to validate/regenerate/apply; never hand-edit generated Caddy. The pre-cutover generator and manifest backups are `/var/backups/webhost-sites/change-20261030T182347070194Z/common.py` and `/var/backups/webhost-sites/change-20261030T182347071559Z/sites.toml`. Restore both under lock after validating current pins, reload the corresponding generator, regenerate/validate/apply production Caddy, and rerun all-site smoke; preserve all account databases, keys and files. Caddy reload can interrupt WebSockets.

The browser notebook needs `unsafe-eval` scoped to the notebook bundle and shares the desktop origin; it is not isolated from untrusted notebooks. Linux SSH and its metadata audit are unfinished and not active; the preexisting relay policy allows public ping/DNS/web, not the local uncommitted SSH candidate. The live test reused existing identity/gateway services rather than deploying the local development launcher.

### 2026-10-30 — Text editor update live

Text app user update is live in Simplified release `400e94ae767a6119cb2f54bef1da2484590711a8e03f5191307f0242bad9ddf3`, Text bundle `408a69c9b7bb92fe646a1ed378044c8091d9abc0a7dc7bdac4cb73212cd1a315`, source `fa042ae0d`. Desktop and phone-sized touch browser tests passed for file open/edit/save, browser/server sync, search, Save As collision, dirty protection, in-flight edits, external reload and layout. The physical phone keyboard was not tested. Fixed status-bar clipping/resize-handle overlap and stale shell title. Live desktop and emulated touch sessions edited the same disposable account file, which was verified on server disk; test account/data were removed. All ten server-loopback production smoke checks passed.

The release updates the cache bootstrap/worker to identify release IDs and retire older Codi caches, avoiding a stale Text bundle after refresh. Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `9296d551933a52ad2e691175f81f904af249fca6effb82cbe082b5245604c053`, Caddy `349ccc634af3a1a655c9225918adf564c23c89a0d06fa91f80a40bf36f7e5eef`. Previous release is `f66430feb99b44df8de20261f617091c0b079c8441d324842ef63c399d97b07e`; pre-update manifest backup `/var/backups/webhost-sites/change-20261030T204617466098Z/sites.toml`. Use the controller lock and generated validate/apply for rollback; preserve account state.

### 2026-10-30 — CodeMirror system tool and Text integration live

Source `3471d6330` is live as release `4553df94822a2ba98542d1bc5a4e975ba3d6ae458d97643e6817963fb1a85e28`. CodeMirror 6 is a lazily loaded disabled-looking System Tools capability. Text uses an independent view/history for each window; JupyterLite retains its own bundled CodeMirror as the user requested. Text supports line numbers, Python/JS/TS syntax highlighting, search/replace, undo/redo and indentation. Voice inserts via editor transactions. `docs/EXPERIENCE.md` records the interaction and ownership decisions.

Tests covered desktop and touch-sized Chrome layout, file saves/conflicts/Save As, in-flight edits, replacement/indentation undo, multiple independent editors, keyboard-mode attributes, mocked voice button and delayed-load disposal. JupyterLite ran NumPy locally and independently of Text; live HTTPS checks verified desktop/touch Text sync and a notebook Python calculation. The disposable live account and file were removed. Physical phone/IME/audio testing remains outstanding. All ten server-loopback site smoke checks passed.

Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `107bcb578e6b29dee266148e0200149a6eae7533220094adc72d2fc48dae9288`, Caddy `bcab1fd046fce6facb199f394cc2c17a303eac5b123d04363a31c256b7f5fef6`. Previous release `400e94ae767a6119cb2f54bef1da2484590711a8e03f5191307f0242bad9ddf3` and pre-update manifest backup `/var/backups/webhost-sites/change-20261030T205910760103Z/sites.toml` provide rollback input; use the hosting controller lock and generated validate/apply, preserving all private state.

### 2026-10-30 — Text code-file chooser follow-up

Release `5f4584fc2f254106b39bfc25c779efcba47d73a7b1ebda15082bbe739b117f2e` includes source `221bbff77`, enabling JavaScript and TypeScript files in Text's Open chooser. Local Chrome verified opening and syntax highlighting JavaScript. Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `fd14dd96dca1dc4656d2344113864dfb9e5da09689f4cf4e22fa6a44a40030ff`, Caddy `cc4c40540bba99014c0c9654dc8e6ef04209f3aaaaa3775f740a7142e0ddfdeb`. Previous release `4553df94822a2ba98542d1bc5a4e975ba3d6ae458d97643e6817963fb1a85e28` and manifest backup `/var/backups/webhost-sites/change-20261030T210154442803Z/sites.toml` are rollback inputs; use the hosting controller workflow.

### 2026-10-30 — desktop startup message

Release `2a30ac7ba344873fa8ce67feeb09beb2d5493a4f58c2c9b8cfea580f0eb10f5f` (source `5b4087d7f`) displays “Preparing desktop” during the initial network-link startup. Genuine offline events, repeated status failures, initial recovery, or a startup link that remains unavailable for 15 seconds still display “Connection interrupted”; maintenance retains its own message. Focused lifecycle checks cover preparation, connection, offline and failure. Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `23c009af3cf8b89bf0c829b9b403df41d503bda803bac68ca9ddca13d75f2126`, Caddy `cdf7c1302a1c060cdd2f5888401447dfe343a8e231c1a8a473f1ee8873ad8b79`. Prior release `5f4584fc2f254106b39bfc25c779efcba47d73a7b1ebda15082bbe739b117f2e`; manifest backup `/var/backups/webhost-sites/change-20261030T210519632729Z/sites.toml`.

### 2026-10-30 — guest relay no longer locks desktop

Release `43691c72630d640ed36d150d3b394079e7da03746833263ffdc24bb10491577a`, source `02944cc05`, fixes a false “Connection interrupted”: the desktop status monitor no longer treats the independent Linux guest Internet WebSocket as the availability of the whole desktop. Guest relay has its own status/retry handling; real server status failures still use desktop recovery. A real live-account Chrome test with the candidate app loaded the v86 guest, verified the guest relay connection, deliberately destroyed the relay, and confirmed the desktop remained unblocked. Disposable account removed. Current hosting hashes: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `3bca884707095b6ea40262615957d8384f94f5b311ac801adb1778da5b38982b`, Caddy `27e7c4a6e1b5168da130bb6767cc7832de2aceda34bf9451ff4576558a19898d`. Prior release `2a30ac7ba344873fa8ce67feeb09beb2d5493a4f58c2c9b8cfea580f0eb10f5f`, manifest backup `/var/backups/webhost-sites/change-20261030T210745711711Z/sites.toml`.

### 2026-10-30 — live clock and Browser engine work

Root release `412c5947dac88fc885e55702dce6c15483f057a0a44e84b086693ab83524e29e`, source `f5d6761f9`, updates the desktop clock each second, showing HH:MM:SS and refreshing on focus/visibility. A Chrome simulated-clock check passed a second tick, midnight rollover and focus refresh. Hosting generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `0f17637249c3efb517f262fceb967650258b945941e61a573bdb5ab24562f7f9`, Caddy `6652d24717b7e8fdab6f6009b66ccf8a7c1c30c5e2d0df512fc8686256094d6c`. Previous release `ff5217bffecfabfda063b36b9eec504cc4356095cd0fd4967cab93b263f64efb`, manifest backup `/var/backups/webhost-sites/change-20261030T212458767736Z/sites.toml`.

Browser source is backed up in `apps/system/browser`, with build/update instructions in its README. It is not yet registered or live: no functioning engine has been demonstrated. The 79 JS and 7 Python offline adapter tests passed; two packaged windows in Chrome showed the expected missing-engine error and disposed cleanly. Pinned Gecko build is running unprivileged on r730 at `/mnt/data2tb/codi-browser-engine`; `build-retry.log` records its progress. The initial build failed because the Emscripten compiler was not on PATH; source `db59b9944` fixes that. Live CSP currently blocks runtime blob imports, the app builder/catalog have size and extension limits for engine assets, and no Wisp relay is configured. Resolve and test those explicitly before claiming a usable browser or deployment. The build is independent of the live clock release.

The current seconds-clock release is `9e041eaadd8fdc46159a5f0f730e7b0c6c1960ca5882520cb97f39b549ef0b71` (source `eb8c8d0dc`); `h23` keeps midnight at `00:00:00`. Current manifest hash `69534561b98c0962c6e3fc73aeb24d4dc89818690cd8b787a420e12776461889`; Caddy `432e93b1e02afac80a17682d3571013f8c2e4782ea7f06697722a35603041ca5`; generator unchanged. Previous seconds release `412c5947dac88fc885e55702dce6c15483f057a0a44e84b086693ab83524e29e`, backup manifest `/var/backups/webhost-sites/change-20261030T212554315679Z/sites.toml`.

After the midnight release passed the live clock check, the intermediate minute-only release `ff5217bffecfabfda063b36b9eec504cc4356095cd0fd4967cab93b263f64efb` was removed to recover approximately 442 MiB. The current and previous seconds-clock releases remain. Older notes naming the removed intermediate as a rollback are historical.

### 2026-10-30 — pinned taskbar shortcuts

Live root release `3d2842f5c3e07905e95039074f28752047c58e80dd339ba86936152107d8bee6` (source `e1ac7070e`) defaults each workspace's taskbar to Files then Terminal immediately after Applications; running apps follow. The desktop Home icon was removed. Desktop and touch-sized Chrome checks covered workspace isolation, two terminal windows/count, ordering and visible 44px targets. Hosting generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `3d443c40e93f73510f62d32404a6a027302292c77c987fdbd6ab527f242f2e51`, Caddy `af6abf48193eb26b4c505b079c3e1884570108186111a6475f24f9da10b3cd9e`. Rollback release `9e041eaadd8fdc46159a5f0f730e7b0c6c1960ca5882520cb97f39b549ef0b71`; manifest backup `/var/backups/webhost-sites/change-20261030T212807011384Z/sites.toml`.
