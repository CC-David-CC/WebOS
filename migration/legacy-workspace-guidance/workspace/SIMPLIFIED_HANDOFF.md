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

Browser build supplement: the adapter's `native/embed-host.cpp` compiled by itself with the pinned Emscripten and generated Gecko headers. During that check an incorrect environment caused Emscripten to clear its shared sysroot while the main build was compiling, producing missing-header failures. The affected build group was stopped; incremental rebuild is running on r730, with log `/mnt/data2tb/codi-browser-engine/build-resume.log`. Native compile alone does not prove final linking or execution. The superseded release `412c5947dac88fc885e55702dce6c15483f057a0a44e84b086693ab83524e29e` was removed after the current taskbar release passed smoke tests; current release and `9e041eaa...` rollback remain.


### 2026-10-30 — Browser real-engine and relay prototype

Source work through the Browser app remains local/source-only, not live. The exact pinned Gecko/SpiderMonkey was built on r730 under `/mnt/data2tb/codi-browser-engine`, with generated 227 MiB WASM and 13 MiB data copied locally to ignored `apps/system/browser/engine/`; no binaries are tracked by Git. Isolated Chrome tests rendered an offline fixture, exercised click and typing, tested two independent windows and observed nested worker targets disappearing after close. The shared-memory TextDecoder bug was fixed. The isolated desktop test opened an account-mirror HTML file through the real chooser. A real Gecko fixture loaded an HTTP page through the source-only Wisp v1 relay; a YouTube request was rejected before DNS, while local signed device records included the requested domains. Fixture authentication and connector are test-only.

User chose server-relayed networking, a blacklist for named video/news/social domains, and a prefilled but disabled whitelist for engineering suppliers. `apps/system/browser/relay/policy.json` holds the lists. Device domain-request events are signed/hash-chained in IndexedDB per account by default and stay on the device until requested; cross-tab signature/tamper tests pass. Optional independent server-side signed ledger is off by default (`serverAuditEnabled: false`); tests verify per-user/all-user summaries and checkpoints. Neither report-request transport nor production account binding of device keys exists. The Wisp prototype requires injected authenticated registered identities and trustworthy client source; no production authenticator, service installation, live route, trusted certificate test or download-to-My-files exists. The current live CSP blocks worker blob imports; the local test allows them only on the worker. Do not publish the Browser app or claim enforcement until the production integration and risk checks are complete. Domain lists cannot block content rehosted on unrelated domains or indirect proxies.

### 2026-10-30 — independent IP and country rules

The user requested separate incoming-login and outgoing-destination IP/CIDR
and geographic blocks, including Linux guest and other relayed services.
`active-system/network_policy/` contains independent empty-default lists,
local DB-IP Country Lite lookup, a spoof-resistant ingress adapter requiring a
verified proxy-provided client IP, a guest policy composition adapter, and a
scoped nftables rules generator for explicit service UIDs. Browser Wisp tests
also enforce the outbound check before connect and during active streams.
Seven focused policy tests and nineteen Browser Python tests pass. A real local
issuer rejected a blocked loopback login despite a forged header and admitted
requests again after an atomic policy change. nft syntax and actual UID-scoped
blocking were verified in disposable network namespaces, as was a country
ruleset derived from the local October 2026 DB-IP data. Dataset SHA256 is
`dbd70ccfa2a13627eaf4913d19920a1a229f1b3c5439ac01c509995b6364202a`;
`maxminddb==2.8.2` is installed in the development venv and recorded in the
requirements lock, not installed on webhost. DB-IP attribution and updater
instructions are in the network-policy README. Country data is an estimate.

This remains prototype/source only: current ksu.codes login and outbound
services do not enforce these new lists. Before rollout, verify the existing
HAProxy PROXY protocol to Caddy chain and explicitly overwrite/verify the
trusted client-IP header, build/deploy a compatible issuer release without the
unrelated uncommitted SSH audit work, install a guarded atomic firewall table
and verify every relayed egress UID, arrange country database/key custody and
rollback, and test real registered logins, active connections and all sites.
Do not claim system-wide blocking from the existence of the adapters.

Browser usage-report source now includes a request-scoped coordinator and a
Python verifier for the browser's WebCrypto-signed hash chain. Local tests
verified a real Chrome-generated report in Python, detected modifications and
checkpoint truncation, enforced explicit administrator/account scope, and
combined two users while counting repeat device snapshots once. No network
transport, production session adapter, administrator UI or online request
exists yet; no browser usage is automatically stored on the server. Optional
independent server audit remains disabled by default.

### Network rule management — development only

`active-system/network_policy/manage.py` provides validated, locked, atomic
operator edits to independent incoming-login and outgoing IP/CIDR/country
lists. Focused tests cover separate rules, invalid edits and optional real
local country lookups. The feature is **not active on the live site**: trusted
client-IP ingress, production service wiring, coverage of every egress path,
and rollout/rollback remain required. Login rules do not revoke sessions.
The Browser relay and browser-local domain-report work also remain development
only; no device records are uploaded automatically and optional server audit is
off by default.

### Browser relay authorization and stream concurrency — development

A purpose-separated `browser_service.authorization` and issuer middleware
`origin_service.browser_authority` now issue and verify short-lived,
registered-account-only browser grants, bound to the signing key, connection
challenge and pinned policy. The reference issuer can enable the middleware
with an explicit `--browser-relay-policy-sha256`; it remains off by default.
The real issuer/ES256/SQLite test passes 28 cases including replay, key theft,
anonymous denial, service-token confusion, policy changes and durable session
recovery. This is not yet connected to Browser, the Wisp endpoint or live
services; admission, renewal, safe service deployment and browser end-to-end
checks remain. A grant is a short lease, so connection renewal and cleanup must
be designed and tested rather than silently extending it.

The Wisp prototype now starts connection requests concurrently with bounded
per-stream early-data buffering, instead of letting slow DNS/connect block
other streams. Tests check concurrent progress and cancellation/capacity
cleanup. Source is backed up; this relay is not live.

### Local Browser relay integration

The isolated launcher supports `--browser-relay` and advertises an explicitly
pinned Browser authorization policy. The desktop obtains a challenge, proves a
registered session to the issuer, and authenticates a purpose-bound grant to
the relay. The relay uses a per-window HttpOnly, SameSite=Strict, scoped cookie
(Secure on HTTPS); it renews a short lease, closes on expiry/revocation, and
invalidates admissions at restart. This does not put account keys or bearer
secrets in the renderer's URL. 31 real issuer/SQLite and local HTTP/WebSocket
authorization tests and the Browser offline/unit suite pass. The actual Gecko
engine rendered an external HTTPS page through this path in an isolated local
desktop; this is not a production or broad site-compatibility test. Traffic
policy, deployment, trusted external source attribution, stronger operational
limits, file downloads, report transport, license/source distribution and
mobile testing still require work. The local test state is disposable and the
live site remains unchanged.

### Explicit Browser URL downloads — local development

The local relay now supports a bounded, registered-session-only explicit
Download URL action. Every HTTP(S) request and redirect checks domain policy,
resolves once, rejects non-public/mixed answers, pins the connection to the
checked IP and checks outgoing IP policy during transfer. It enforces an 8 MiB
limit matching the account file service and does not copy Gecko cookies or
request headers. Downloaded bytes are written to the browser/server-backed
My files mirror; this is a URL action, not interception of ordinary Gecko
clicked downloads. The latter remains unfinished. Fixture tests exercise
redirect policy, IP denial, size and expired lease, and a real HTTPS download
was saved to My files in the isolated desktop. Production service wiring,
traffic controls, broader website behavior and phone tests remain outstanding.

### Phone windows and terminal startup — live

Root release `bfcccab6fcdfd33221aeb5e57dd59d8eb788217b0c0172bb1cf45b3c533a807b`
uses the prior live assets plus the tested phone window and terminal changes.
On compact screens all applications start maximized; the normal maximize
control still restores a movable window. Desktop window sizing is unchanged.
Each new independent PTY runs the real shell `help` command and suppresses
only the initial BusyBox ash banner. A local real-v86 phone-emulation test
verified the command output and absence of the banner; 12 app types were
checked at phone and desktop widths. Public asset hashes match and all ten
hosted sites passed loopback production smoke. Physical phone testing remains
separate. The previous release is
`3d2842f5c3e07905e95039074f28752047c58e80dd339ba86936152107d8bee6`;
manifest backup `/var/backups/webhost-sites/change-20261030T225146530854Z`.
Current hosting generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`,
manifest `8dbc923802a0fd3f66eaef45bf8105c6257ecb02a592de2956233ee1f369818b`,
and derived Caddy `525b9b8e4997c53fb5522659a80bb9f8497c63abf3c6b955d6204c1aef79b551`.
Use the hosting controller lock and generated configuration for rollback.

### 128 MiB file work — not live

Development raises the prior 8 MiB file limits to 128 MiB in the mirror,
gateway, Files, ZIP, Browser URL download and affected app adapters. The
encoded request allowance, transfer pacing and default account disk quota were
also adjusted. A real registered browser wrote and read back a 128 MiB file
with identical SHA-256; 128 MiB plus one byte was rejected by the client. The
response now streams base64 in bounded chunks and the browser codec avoids a
per-byte `Uint8Array.from` over a 128 MiB string. The isolated combined local
issuer/proxy/gateway reached approximately 759 MiB high-water RSS during the
round trip; the existing live gateway is capped at 384 MiB. Uploads still use
large JSON/base64 request buffers, so concurrency and memory need more work
before rollout. Current live config still advertises and enforces 8 MiB. Some
apps have independently lower format/processing limits (including Text,
Data Explorer and Audio Editor); they have not been raised by this change.

### Streaming account transfers — local development

The gateway now accepts a purpose-bound, account-signed binary upload with
small authenticated metadata, streams bytes to a private temporary file,
checks the exact declared length and SHA-256, and atomically publishes through
`UserStore.put_stream`. A separate capability endpoint permits older services
to keep using the legacy JSON/base64 client path. Reads use an authorized open
file descriptor and bounded base64 output chunks; an already-open descriptor
continues to read the selected version across atomic replacement. File
permissions, preconditions and quotas are checked before publication. Temporary
uploads are unlinked file objects and cannot become account files on failure.

Local results: 34 private storage tests, 16 HTTP/issuer/gateway tests including
corruption, replay, account isolation and concurrent separate-account uploads;
a real Chrome registered account wrote and read 128 MiB with matching SHA-256
and confirmed the binary endpoint was used. A 128 MiB plus one byte request was
rejected by the browser. The combined isolated issuer/gateway/proxy process
reported a high-water RSS of 115484 KiB on that round trip. This is a single
local measurement, not a production concurrency capacity claim; large reads
still use browser-side JSON/base64 buffers, and production ingress, service
memory limits, temporary-disk placement, interrupted uploads and multi-user
stress need validation. The live file service remains the older 8 MiB release.

A subsequent actual loopback test uploaded two 128 MiB files concurrently from
separate signed accounts in 35.1 seconds, verified each disk hash, and measured
115700 KiB high-water memory from `/proc/self/status`. A first version of the
test used `getrusage` and reported an inherited 1117892 KiB peak; the current
process's `VmHWM` exposed that measurement error, and the full test was rerun.
An additional test disconnects a partially sent authenticated upload and
confirms no partial account file is published. These are local tests; the 128
MiB changes are still not live, and production ingress/deployment remains.
The stopped disposable previews on ports 18137 and 18138 were removed only
after checking exact paths, owner, filesystem and absence of running services.

### Browser touch and keyboard — development

The Browser canvas translates touch taps into page clicks and touch drags into
wheel scrolling; the toolbar Keyboard button activates an app-owned text bridge
and asks the desktop to enable the on-screen keyboard. Unit tests cover touch,
text/editing keys and desktop mouse events. An isolated real-Gecko mobile
emulation test tapped a guest input, typed `abc`, confirmed the guest changed
its URL fragment in response, and observed a rendered page change after a
touch drag. This is not a physical Android keyboard or full IME, accessibility,
text selection or drag-and-drop test. Browser and relay are not live yet.

### Browser relay private ingress candidate — development

`active-system/scripts/serve-browser-relay.py` provides an operator entrypoint
for a protected Unix-socket service. It validates a pinned issuer policy,
requires a service-owned 0750 socket directory, sets the socket 0660, checks
Linux `SO_PEERCRED` for the configured proxy UID, and requires exactly one
well-formed ingress-provided client address. Runtime IP/country and domain
policies remain independent. The relay now bounds shared active streams,
tries alternative already-vetted addresses when an earlier address is
unreachable, and checks revised domain/IP policy during active traffic.
Browser URL downloads spool to private temporary disk and stream to the
client with per-window, per-account and shared concurrency caps.

Local tests include actual subprocess startup, pin rejection and socket
cleanup, wrong peer UID/address rejection, a registered real-issuer grant
through the Unix socket to an external HTTP endpoint, dynamic domain/IP
blocking, alternate-address fallback, stream-cap cleanup, and a real Gecko
HTTPS/download workflow. A separate loopback Caddy fixture on box-webhost ran
as the actual Caddy UID; PROXY v1 and v2 source addresses replaced duplicate
forged client-IP headers and the upstream observed that UID. This fixture did
not exercise an independent public network or activate the live route.

`prepare-browser-hosting.py` derives an opt-in managed generator candidate for
the private socket route, scoped Browser worker CSP, larger file body limit,
and trusted login header. With all flags absent it reproduces the captured
baseline byte-for-byte; KSU-only validation/round-trip tests pass and the
rendered production Caddy configuration validates. No candidate was installed
or activated. Before production, install and harden the service with the right
socket directory/group, prove the complete live HAProxy-to-Caddy address path,
secure the login filter against direct issuer-port spoofing, cover guest and
other server egress, arrange database and license/source custody, and perform
live rollback/restart and phone tests. The optional server audit is still off.

### Private relay staged on box-webhost — 2026-10-30

The isolated Browser relay is installed and running privately, with no public
route and no boot enablement. Its root-owned runtime manifest is
`fefb814d50b46db56a948e01a9f3879c6fc3d9287ae32ee3a7b9e9a09a49dc52`;
its separate dependency environment is pinned by lockfile SHA-256
`a5ee6aa9a1c18535aad36a52b7ec57ca9c1e1fca03cbb02d4c423fd7ec317326`.
The static `codi-browser-relay.service` runs as `codi-browser` with a private
socket in `/run/codi-browser`. A request from Caddy's UID received HTTP 200;
the same request from root was rejected with HTTP 403 by peer-credential
checking. After restart the socket became available and again returned 200;
an immediate probe raced startup and initially failed to connect. The public
relay route returns 404. This is only private-ingress verification, not a
live Browser release or a complete production security test. Configuration
is in `/etc/codi-browser`; the initially empty access-policy file matches
the checked-in default, and the separate domain policy retains its existing
blacklist and disabled whitelist. Geo-IP data is the DB-IP Country Lite
October 2026 snapshot; attribution and updates are still required.

### Issuer ingress protection candidate — 2026-10-30

The issuer currently listens on `127.0.0.1:8118`; the managed Caddy route is
the only configured local consumer found. The network-policy kernel module now
generates a separate atomic nftables table that permits a designated proxy UID
to connect to that loopback port and rejects other local socket UIDs. In an
isolated network namespace, real connections from two distinct unprivileged
UIDs worked before the rule; afterward only the designated UID worked, and
reapplying the ruleset twice preserved the restriction. A root socket was also
rejected. Removing the test table restored access. This does not defend against
an administrator who can alter firewall state. Both the namespace test and
the nine network-policy tests passed; the latter require the development venv
for the installed Geo-IP reader. An initial run with system Python failed only
because that interpreter lacks `maxminddb`.

That original whole-port proposal was not installed: subsequent inspection
found another consumer, leading to the split-port approach described below.
An actual public proxy-chain test, issuer integration and rollback are still
required before login IP restrictions can be considered live.

### Browser source snapshots staged — 2026-10-30

Seven hash-verified source artifacts now reside privately under
`/srv/codi-browser/source-staging/engine-6736dce5/` on box-webhost. They cover
the exact clean Firefox source revision, Firefox-WASM base and actual local
patch, the added native adapter, the patched Emscripten checkout without
dependencies or caches, the installed Wisp source/license, and the relevant
Codi app/integration source at commit `6749ae260`. The archive checksums,
scope and remaining licensing review are in
`apps/system/browser/docs/SOURCE_PROVISION.md`. Zstandard integrity and an
actual base-plus-patch byte comparison passed; the Firefox archive is 918 MiB.
Temporary transfer and duplicate archive staging directories were removed
after the copies were verified; the original build checkout remains. The
sources are not public yet, and this preparation does not establish complete
third-party license compliance or authorize distributing the engine without
the remaining notices and source review.

### Split login and Browser issuer candidate — 2026-10-30

Further inspection found that the existing Linux guest relay reads issuer
configuration directly from port 8118. Restricting that entire port to Caddy
would break the guest. The profile-28 candidate therefore keeps the existing
issuer port for configuration and other APIs, rejects `/api/v1/auth` there,
and binds a separate login-only listener on port 8117. The managed-hosting
candidate routes that exact path to the new listener and overwrites its client
IP header. The proposed nftables proxy-UID boundary applies to 8117 only.
`render-issuer-ingress-service.py` produces the atomic rules and a static
systemd unit; these have passed isolated nftables syntax and systemd unit
validation. The guard is now installed and active on box-webhost for port
8117 only; a real temporary socket test admitted Caddy UID 997 and denied a
root-owned client, and restarting the guard preserved the rule. The current
issuer remains on 8118 and the public site continued to answer. The candidate
issuer unit requires this guard before startup.

`build-browser-issuer-release.py` verifies the exact live profile-27 manifest
before producing an isolated profile-28 candidate. It preserves the existing
public asset tree, adds the registered Browser authority and the split login
listener, and retains the existing live guest and steward unit renderings. The
current candidate manifest SHA-256 is
`d09ddbbb04ce0e294a97b44ae1d8a8a555d302385c5d42b7fb7fd867bfab4878`,
installed privately at `/srv/codi-connected/releases/browser-issuer-profile28-r2`.
An isolated real issuer started, advertised the Browser policy, denied auth
on its ordinary port, accepted only login on the separate port, and enforced
an updated IP rule without restart. Unit and network policy tests pass. Caddy
validated the candidate hosting configuration, and its adapted route order
put the exact login path before the general API route. This is not a complete
registered-user, external-ingress or deployment test; no candidate hosting or
issuer change has been activated. The first candidate attempted a separate
issuer Python environment, but managed preflight rejected it because the
existing Linux guest backend is pinned to the original environment. The
revised candidate keeps that environment and reads `maxminddb` from the
root-owned, immutable Browser environment only after validating its package
path. Real server checks resolved test addresses through that path, and the
candidate passed the managed installation, guest binding, dependency and
systemd syntax preflight. A separate isolated run of the installed candidate
as the actual `codi-issuer` service account verified configuration, the
Browser challenge handler, split login and an IP block using the existing
Python environment. A test rejects user-writable fallback modules. The
superseded candidate and unused environment were removed. The later entry
records the subsequent file gateway upgrade.

### Additional trusted-ingress gap — 2026-10-30

The split login guard does not by itself protect the original address: a real
unprivileged local connection to Caddy port 8443 sent a fabricated PROXY
header, and Caddy recorded that fabricated `203.0.113.99` client address. Do
not enable or claim live client-IP login enforcement until this HAProxy-to-Caddy
boundary is fixed. HAProxy runs as `DynamicUser=codi-shared-ingress`; its UID
can change, so a permanent nftables rule cannot safely pin the currently
observed numeric UID.

`render_caddy_proxy_guard` and `render-caddy-proxy-guard.py` prepare a distinct
atomic nftables table, a root guard service and a Caddy startup dependency.
Namespace tests prove both Caddy ports accept only the specified UID. A
temporary real-host rule using the current UID blocked an unprivileged direct
connection while three sites remained available through HAProxy; it was then
removed. A separate systemd fixture verified that a service with
`DynamicUser=yes` uses a matching locked static account after restart. The
static account migration, durable guard installation, controlled rollback and
full live/independent-network tests have not yet been performed. Candidate
rules for UID 966 were rendered and syntax-checked; that UID must be confirmed
free again immediately before any migration.

### Trusted Caddy ingress guard active — 2026-10-30

The controlled transition was exercised with real services and rolled back
successfully before final application. It then installed a locked static
`codi-shared-ingress` account at UID/GID 966, preserving the existing ingress
unit and its restrictions, and installed the `codi_caddy_proxy_guard` nftables
table plus `codi-caddy-proxy-guard.service`. A Caddy dependency starts the
guard first. The operator and exact inputs are root-owned in
`/srv/codi-ingress/operators/caddy-guard-db05e87a4`; its result receipt is
`/var/lib/codi-ingress/caddy-proxy-guard-result.json`. Both the real rollback
exercise and the final apply preserved the expected status codes for all ten
sites, including hardware.ksu.codes' intentional 401. The old unprivileged
direct connection to Caddy port 8443 now fails. HAProxy and Caddy were each
restarted and the guard remained active; HAProxy retained UID 966. A request
from i36 over its independently addressed Ethernet connection was recorded by
Caddy as its correct public IP, `104.180.210.36`. This is address-chain
evidence, not yet a live login-filter test. Caddy's generated file remains
SHA-256 `525b9b8e4997c53fb5522659a80bb9f8497c63abf3c6b955d6204c1aef79b551`.

The private Browser relay is now also a `Wants`/`After` dependency of Caddy,
so a Caddy start pulls it in without making unrelated sites depend on its
success. The issuer and hosting candidate are still not active. The previous
paragraph records the discovery and temporary test before this installation.

### Coordinated backend transition exercise — 2026-10-30

The first actual issuer/hosting rollback exercise did not reach the hosting
switch: managed readiness detected that profile 28's TURN policy expectation
omitted the existing ICE preference. The native controller restored profile 27,
all three native services and the website; both transition journals cleared.
This exposed a missed profile list in `origin_service/turn_management.py`.
The candidate builder now updates that list, and a regression test compares
the old and new public TURN policies. The corrected local profile-28 r3
manifest is `957e6fec98101f5a57c7f8ebab633050d27759d5c0d673049b4da3527d39715d`.
It supersedes the r2 candidate; r3 has not yet been installed or tested in a
live managed transition. The live login and Browser routes remain unchanged.

### Browser backend and login IP filter live — 2026-10-30

The corrected profile-28 r3 and managed Caddy routing passed a real
coordinated upgrade/rollback exercise, then were activated. The issuer is
`/srv/codi-connected/releases/browser-issuer-profile28-r3`, manifest SHA-256
`957e6fec98101f5a57c7f8ebab633050d27759d5c0d673049b4da3527d39715d`.
The current hosting generator is
`25d58c0602e296aabce40c24d64d52408140e0c78e63347f6485aa240f39da64`,
manifest `a8ac8177967396495711247402ce6b346865d1d2aab84d7e7310817e0c9d7d1c`,
and derived Caddy file `ce813404d53fd8d9344eef3a49af868fbce53d70f01612cfd78c0e89e552edcd`.
The root-owned transition operator is
`/srv/codi-browser/operators/backend-b7c31de02`, with receipt
`/var/lib/codi-ingress/browser-backend-result.json`. The previous native
release remains available for managed rollback. The failed r2 candidate,
obsolete operator and temporary transfer directories were removed.

From the external address `104.180.210.36`, a temporary incoming-login block
returned 403 even with forged `X-Codi-Client-IP` and `X-Forwarded-For`
headers; the Browser relay challenge remained available. Restoring the empty
policy returned the same invalid login request to its expected 400 response.
The original policy hash was confirmed after restoration. A real headless
Chrome registered a disposable account, obtained a signed Browser relay grant,
downloaded an allowed HTTPS page, rejected YouTube, IPv4/IPv6 loopback literals
and a hostname resolving to loopback, and opened Wisp. It then signed in again
in a fresh browser context and removed its exact test account. The reproducible
check is `tests/live_browser_relay_account_check.py`.
After separate live relay and issuer service restarts, the same registered
account/relay test passed again; both guard units and services were active.

Only the backend, login filter and Browser outgoing policy are live. The
Browser app/engine are not yet published; ordinary clicked downloads remain
unfinished. Country blocking and an existing live transfer under a rule
change still need testing, as do the other server egress paths. The desktop
remains limited to 8 MiB pending the frontend/proxy rollout described below.
A login block does not revoke an existing session.

### Browser sources published and 128 MiB worker candidate — 2026-10-30

`https://ksu.codes/browser-sources/` now serves the Gecko-generated license
inventory, Emscripten/runtime and Wisp/adapter notices, and exact pinned
source archives through a fixed filename allowlist. Source downloads use
Caddy's file server and support byte ranges; they are not copied into the
desktop release or Git. The notice generator validates the original Gecko
notice and exact Emscripten/Wisp archive hashes. A real hosting rollback
exercise passed before activation, all ten sites preserved their expected
statuses, twelve public source/notice links responded to HEAD, and a separate
external host obtained a 32-byte range with HTTP 206. Unlisted paths returned
404. The prior small obsolete source archive and transfer fixtures were removed.
Current hosting generator SHA-256 is
`9bb5e958f27985891b8c927215e4927ddd514870309e271ec0f29790e2de8c68`,
manifest `3ff13521fdca82c339d39fff09be45258e41f132d893a9e7c9fc51796636d93f`,
and Caddy `a4d05c0e404188ddf2192dd5f9efb53076aa499f76d5dc2b36e87c6ee7e3df63`.
The root source-route operator is `/srv/codi-browser/operators/sources-37218ff39`.

The Browser app has a source/notice link and simplified startup/status text in
source, and its 83 focused tests pass; it is still not deployed. The engine
link log reports 37 unresolved functions, including file-picker and audio
functions. Its impact and the actual linked-component/license inventory need
review before claiming general website support or complete compliance.

`build-large-file-worker.py` verifies the exact currently deployed gateway
manifest, exports the six reviewed changes, preserves the existing live Python
dependency lock, and refuses uncommitted worker inputs. Its reproducible
candidate manifest SHA-256 is
`53588b25c06c7b88e038bcca4cca13b8de9bcabc35b952d463c1d7ff3727b5c0`.
A fresh local test streamed two signed 128 MiB uploads concurrently in 35.1 s
with approximately 115672 KiB process high-water memory. The worker passed
the existing root file operator's runtime and policy preflight, was upgraded,
rolled back to the previous worker and upgraded again through the journaled
private-file code helper. Each transition reported preserved permission and
folder bindings without restoring account/file data. The new worker is now
active at `/srv/codi-gateway/releases/53588b25c06c7b88e038bcca4cca13b8de9bcabc35b952d463c1d7ff3727b5c0`;
the previous worker remains available for rollback. Its public upload
capability reports 134217728 bytes. A real registered browser performed a
signed binary write, read with hash verification and delete; its exact empty
test folder, gateway records and disposable account were then removed. Issuer
metadata, browser mirror and proxy limits still restrict the desktop to 8 MiB,
so a live 128 MiB round trip remains unproven. The static release builder now
hashes files in chunks instead of reading the entire WASM asset into memory.

### Large-file ingress and notebook names — 2026-10-30

The assembled local desktop completed an authenticated 128 MiB binary
write/read with matching SHA-256. The live gateway ingress was then changed
using `activate-large-file-ingress.py`: its exact KSU-only flag change was
applied, rolled back and reapplied with all ten site statuses preserved.
Current hosting manifest is
`a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`
and Caddy is `0abb1284887d57115a48fc6c6a554207930294c0582c420cc1f13e168e5ad016`.
The earlier hosting pins above are historical. A real signed registered
browser directly used the live gateway to write, read and delete 128 MiB with
matching SHA-256 `fb3251b1618f009f9fb644d1302b668a65a131e58521ef86e4d5080625dd138a`;
its exact disposable account and folder were removed. The live desktop and
issuer still retain the earlier file limit, so the live desktop mirror's
end-to-end 128 MiB transfer has not been verified.

Notebook temporary names previously used the desktop window number; source now
uses a fresh random UUID per window. The new notebook build is only in the local
candidate, not live. JupyterLite config namespaces browser working storage by
the current account; server My files uses an authenticated account-to-folder
mapping. Browser storage namespaces are not a security boundary against a
person with access to that same browser profile. A real test with two accounts
open in separate tabs of the same browser profile passed: their notebook
storage namespaces and UUID names differed, the second notebook listing did
not show the first, and the second account could not read the first account's
My files test document. After accepting the notebook's browser leave-page
confirmation, signing out and back into the first account also passed; its
own saved test document remained available. An earlier test timed out because
it did not respond to that confirmation, not because isolation was verified.

The Browser source archive for the `0fc6bf9a7` desktop candidate is now
available at `/browser-sources/codi-browser-source-0fc6bf9a7.tar.zst` with
SHA-256 `47ac4d287646b42b808680e2be422e4a7a7bf62dcd928b6ae911bf4a2c91bbe4`.
The prior snapshot remains available, and the public index and notice manifest
include both. The exact allowlist addition was rollback-exercised and deployed
with all ten hosted site statuses preserved; the new source download's hash was
verified over HTTPS. The pre-update source-index files are retained in the
root-only `/var/lib/codi-ingress/browser-source-index-0fc-backup.json`.
Hosting generator is now
`d32c182fe5043a1671d460bd27325cf72750d94e771dbd070f523537eee407e8`,
manifest remains `a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`,
and Caddy is `c098afe8572a12105527e17773c14f551075c52854617838b5477ab136ea55a0`.
Browser desktop deployment and complete engine-license review remain pending.
The next assembled candidate, with the Arduino application, has cache ID
`4ac8781a92ed58b9fc0d878d927055d86d44fa3fe4aaadd4a2858757ce63d80a`.
Its matching `adece7482` Browser/source-integration archive has SHA-256
`2e64c1c3856f622af986157059eca6f8f14a8c73e275829d397372b70701c127`
and is published alongside the previous versions at `/browser-sources/`.
The archive's desktop source and the candidate `app.js` were compared by hash.
The source-allowlist update passed a rollback exercise and all-site checks.
Current hosting generator is
`6ac5e114fe7ed8949f2c8ce3876cafa1745353ef0409c4d2bc13600067ea3226`,
manifest remains `a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`,
and Caddy is `9de277b1a34fa28f76899a883fdf8fdb1d6d5478fdb9c33e6739ce12014b14ab`.
The candidate's Browser passed real desktop and phone-emulated Chromium tests
for authenticated networking, My files download, keyboard input and touch
scrolling. This does not qualify a physical phone or general website behavior.
`build-large-file-issuer.py` creates a profile-28 candidate from the exact
live issuer by updating the advertised file limit, its managed-policy health
check and the release manifest. Earlier candidates omitted rollback
compatibility and must not be deployed. Candidate `profile28-large-files-r3`
has manifest SHA-256 `0aaf61849fa03e41376d63a36496c83e83adbc97c14aeafe366100ff9e530af2`.
Its isolated tests passed, including advertised 128 MiB, metadata validation
against both old and new issuer releases, separate login listener, rule
updates and unchanged TURN policy. The root-owned release was staged from the
verified prior release, then its managed upgrade and rollback were exercised
before final activation. `/config.json` now advertises 134217728 bytes from
`/srv/codi-connected/releases/browser-issuer-profile28-large-r3`; all ten
site status checks passed. The live desktop remains on its old static release
and its mirror's 128 MiB end-to-end path has not yet been verified.

Real live signed-account tests then exercised outgoing CIDR and country rule
updates: each update closed an existing Wisp stream and rejected a new stream,
and traffic resumed after restoring the original rule file. The country test
blocked AU/CA, covering the selected host's resolved IPv4/IPv6 addresses. A
separate test from i36's public address (104.180.210.36, US in the installed
DB-IP database) added an incoming US login block: login returned 403 despite
forged client-IP headers, while an already signed-in Browser relay still
downloaded an allowed site. Login returned its normal 400 invalid-body response
after restore. Tests used an automatic two-minute conflict-safe recovery timer;
the original policy hash was verified, the timer and temporary helper removed,
and the exact disposable account cleaned up after each run. A login rule does
not revoke an existing session.

### Electronics apps — local work in progress

The requested electronics tools are tracked in `docs/ELECTRONICS_APPS.md` as
separate applications. `apps/system/arduino-simulator` is the first local
implementation: pinned AVR8js and Wokwi Elements, a compiled ATmega328P Blink
HEX and its C/Arduino source examples, a worker per window, pin 13 LED display,
serial output and opening HEX from My files. It does not compile sketches or
simulate analog circuits. Desktop and phone-emulated Chromium tests passed
real firmware-driven LED changes, opening firmware through My files and two
independent windows with one closed. It is not deployed. Pico, writable flash,
analog circuit simulation, PCB design and digital logic apps remain unfinished.
### Browser report relay activation — 2026-10-30

The Browser relay is running the root-owned runtime with manifest SHA-256
`6b2ea6b67591faf490e164dd79b80cabd2fd58f8e13c3f56998dc0947b3516c9`,
source commit `6078c8e18`. Requested reports are enabled on this service;
`dflanag3` is the only configured administrator, in root-owned
`/etc/codi-browser/report-admins.json`. Report data uses the service-owned
0700 `/var/lib/codi-browser-reports` directory and 0600 SQLite database.
No request is active merely because this service is enabled. The separate
continuous server-side access audit remains disabled. The prior unit is at
`/var/backups/codi-browser-relay-before-report-6078.service` for rollback.
After restart, a public challenge advertised report support and a new
disposable registered account passed signed relay admission, HTTPS download,
blacklist and private-address denial, Wisp connection, account-file
write/read/delete and a fresh-context login; the account was removed. The
report workflow passed against a local real Browser and two registered
accounts. The report UI and Browser desktop app are not deployed yet, and a
live end-to-end report and restart recovery test is still required.

### Updated Browser and relay source provision — 2026-10-30

Public `/browser-sources/` now includes the snapshot from commit `2ed6d0259`,
which contains the currently running report-enabled relay and tracked Browser
app source. Its archive SHA-256 is
`49f1c63f6160a58d9d6624d5baa35589fae1a74580f32cbb8883f71f9a203b0b`;
the public download was independently hash-checked. The managed source-route
update and rollback exercise passed all ten site status checks. Generator
SHA-256 is `3ac0cf3bc1dda9063c0cd3494c71d83a706681b7a8cdc682a0d8f77dcace8ff3`,
manifest `a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`,
and derived Caddy `9db5c7c717501259da4e969c930441bf74f66127ceb0720c03c4c5dc3f4d88d2`.
Index rollback data is `/var/lib/codi-ingress/browser-source-index-2ed-backup.json`.
The Gecko component and LGPL review remains incomplete; source availability
alone is not a finding that the engine's distribution obligations are met.

### Browser font notice — 2026-10-30

The Gecko resource package includes four Liberation Sans fonts. Their
SIL OFL 1.1 notice was missing from the browsable notices and is now appended
to `/browser-sources/emscripten-licenses.txt`, with the index updated. The
notice input is pinned to the exact Firefox checkout's license hash. The
public response matched SHA-256
`4b87b95e8c51dde5861703e11ce57c416f178497fab403b73033f6db48f550ad`.
Previous notices are retained in
`/var/lib/codi-ingress/browser-source-font-notice-backup.json`.
The source notice builder now requires this license explicitly. Link-script
inspection and symbol checks narrowed the LGPL questions but do not complete
the full third-party license review.

### Report-enabled desktop candidate — 2026-10-30

The static candidate `.build/simplified-release-reports-r1` contains the
report-enabled Browser bundle and has cache ID
`5d9f737d4fe4190f4edcd740ab4ac3b2c395a4a683ed23c1072ec438528ecd74`.
The Builder's optional `--desktop-app-source` supplied a reviewed `app.js`
snapshot from commit `2ed6d0259`, preserving the separate uncommitted Crafts
menu work. That file's SHA-256 is
`bc0da0094bc80c1cdd6524a9491b60209449d7fb2d82c7fdf24db646470e85e5`.
An independent Browser-only rebuild matched the candidate's full Browser
catalog entry and bundle SHA-256
`2af8a8f2a644daf6bd7039170ddef2dc93f9799f7c6bdc8238f5506cd97f8079`.
The candidate is not live; engine licensing and live end-to-end tests remain.

### Browser status and window sizing — 2026-10-30

An actual desktop Browser test exposed that `window-content` overrode the
desktop's title-bar height calculation, clipping Browser status and
diagnostics. It also found that navigation left the status on “Loading…”
after the native navigation command returned. The local Browser now respects
the desktop's content height, lets its viewport shrink, and reports
“Navigation requested.” after the command returns; that wording does not
claim the destination has finished loading. Both desktop and phone-emulated
tests now assert that status fits inside the window. The desktop test passed
account-file HTML open, relay request and renewal, visible non-stuck status,
and URL download with server synchronization. The phone-emulated test passed
status visibility, typing and touch scroll. These changes are not live. The
prior report-enabled static candidate is superseded. The replacement
`.build/simplified-release-reports-r2` has cache ID
`8138c0e892580c8aafc3637738b4d9d577898c923e9ceb108f7fd337477d6c27`
and Browser bundle SHA-256
`4b26e64f6b9edf41155cf206c4ee5b24ddf77bfb4011bb552ae6a12185beb9a2`.
The matching source archive from `0488c275e`, SHA-256
`841993d069a9d824942224b2e34012a1dc56ce6c24f3407b920adaa4f2d7e0cd`,
is published at `/browser-sources/` and its public download matched that hash.
The managed hosting change passed a rollback exercise and all ten site status
checks. Hosting generator SHA-256 is
`19b71614139100907f21c6b28383532a163c06aa8b951e5d540e5d241e4c37f6`,
manifest remains `a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`,
and Caddy SHA-256 is
`40df5f82ebbbf37ccc30d498a43a1a9f2480b120aad61d0f54b93b1affeef789`.
The previous notices are saved under
`/var/lib/codi-ingress/browser-source-index-0488-backup.json`. The prior
generated candidate and independent build were removed.

### Browser policy-denial feedback — local work, 2026-10-30

The existing live relay enforces blocked destinations but reported the same
generic Wisp close reason for a policy block, capacity limit, and network
failure. The local relay now emits Wisp's standard `HostBlocked` (0x48) and
`ConnThrottled` (0x49) reasons; active streams stopped by a new policy also
receive `HostBlocked`. The Browser worker reports these to the window, which
shows a plain message that a site or resource was blocked, or that the
connection limit was reached. A real local Gecko window navigating to
youtube.com displayed the block message. Ten relay tests passed, including
hostname and changed outbound-policy blocks and capacity behavior; report
HTTP and download tests also passed. This change is not live. Its new relay
runtime, Browser bundle and matching source snapshot must be published and
tested on the live path before this feedback can be considered live. They
supersede the earlier desktop candidate. The immutable relay manifest
SHA-256 is `2046bb480628f3124bba74b2cd249b00eee665709b15cc12e1eca7dbd5434cad`,
the desktop cache ID is
`2c386e8748f45b836a070bf336287275ae432b0003f362ad17645574e15e0539`,
and the prepared source archive from `802621ec2` has SHA-256
`128c33ee16a6dde95f5c594b19ef6c8a05cb9b251024e95ac859f888b3a26c90`.
The exact source archive is now public at `/browser-sources/` and its HTTPS
download was hash-checked. The new relay runtime is live and retains the
existing report configuration and private database. A signed disposable
account confirmed Wisp `HostBlocked` for YouTube, and a live temporary
outgoing rule closed an existing stream and denied a new one. The original
policy was restored and checked, the scheduled recovery timer stopped, and
the temporary test account and helper were removed. The Browser desktop UI
is still not deployed, so its user-visible feedback is not live. The previous
relay unit is saved at `/var/backups/codi-browser-relay-before-blocked-802.service`.
Source hosting generator SHA-256 is
`2329d2b8925501ea5b59c9a0182b24db66e076b6abc1d4305ad820da45a4079b`,
Caddy is `887fdcb7da1b2ba05c6d3204fa0c4cf38a8a8d4d4a9743cc3e269116283209c7`,
and notice rollback data is `/var/lib/codi-ingress/browser-source-index-802-backup.json`.

### Browser compiled-component notices — 2026-10-30

The actual Gecko link list contains 1,860 object inputs. Its identified
third-party groups include ICU, Abseil, msgpack, zstd and several media
libraries. The public runtime notice file now includes the exact pinned-source
license files for the named libraries, including the IJG text referenced by
libjpeg-turbo; the existing Gecko page supplies ICU's notice. The downloaded
combined notice SHA-256 is
`4d04c982f8713a75b6c787679e0f93ff7ac076b08c5fd5ce0d82da515bf6d35e`.
The pinned collection and notice-builder tests pass; previous notices remain
in `/var/lib/codi-ingress/browser-source-component-notice-backup.json`. This
does not prove a complete object-level, Rust dependency, or legal audit.

### Browser target-built Rust notices — 2026-10-30

The Gecko target build's Cargo fingerprints identified 477 distinct crate
names, of which 335 match vendored package names. The public runtime notice
file now includes the declared licenses and available top-level notice files
for matching vendored versions. This is a conservative target-build list,
not a claim those crates all survive final linking. There were 38 matching
vendored versions with no separate top-level notice file and 142 unmatched
names including workspace/toolchain crates; these need further review. The
collector and pinned notice-builder tests pass. The public combined file
SHA-256 is `0c225076a90714c0badf93424d3ae6ee8c57d2d773d17af6641af63643cb042a`;
previous notices are saved in
`/var/lib/codi-ingress/browser-source-rust-notice-backup.json`.

### Browser Rust standard library notices — 2026-10-30

A tracked-source scan matched 464 of the 477 target fingerprint names to
Firefox Cargo manifests; the other 13 include Rust standard-library and
compiler crates. It matched 131 names beyond the earlier vendored-package
scan. Some workspace packages omit a license field, so their source still
needs review. The exact build used Rust 1.95.0; its standard-library copyright
and dependency notice is appended unchanged to the public runtime notices.
The public response SHA-256 is
`b1a5cd60fa71ae515da2e05ffb88358b1f2d4925cba2d79ae4ee8b6e6b1eeb6c`.
The pinned notice tests pass, and prior notices are saved in
`/var/lib/codi-ingress/browser-source-rust-stdlib-notice-backup.json`.
This is target-build evidence, not a final-link or complete legal audit.

### Browser workspace headers and Pulse notice — 2026-10-30

The 22 target workspace manifests without a declared license have Mozilla
license headers on all 47 observed tracked Rust source file paths (some paths
overlap between manifests). `audit_workspace_headers.py` reproduces the
check; non-Rust files and final-link inclusion were not established. The
vendored `pulse` and `pulse-ffi` crates refer to a missing ISC license file;
the exact Cargo.lock-pinned upstream `cubeb-pulse-rs` LICENSE was retrieved
and added to the public notices. The combined public response SHA-256 is
`cfec82baaa9cc83eb238288f493d2116a14603c34aadebab15c7796c4d7cd9c3`;
prior notices remain in `/var/lib/codi-ingress/browser-source-pulse-notice-backup.json`.
Notice-generation tests passed. Other attribution and release checks remain.

### Private Browser desktop release staging — 2026-10-30

The tested static candidate with policy feedback is staged privately at
`/srv/codi-connected/simplified/2c386e8748f45b836a070bf336287275ae432b0003f362ad17645574e15e0539`.
All 4,941 cached files and both cache-control files were independently
hash-checked on the server; no account or service state was copied. The
current live desktop route was not changed. The staged candidate's source is
already published, while the remaining attribution review and live desktop
tests must be completed before calling the release ready. The active desktop
is still `bfcccab6fcdfd33221aeb5e57dd59d8eb788217b0c0172bb1cf45b3c533a807b`.

### Browser desktop active — 2026-10-31 UTC

`https://ksu.codes/` now serves Simplified desktop cache
`2c386e8748f45b836a070bf336287275ae432b0003f362ad17645574e15e0539`.
The managed hosting generator SHA-256 remains
`2329d2b8925501ea5b59c9a0182b24db66e076b6abc1d4305ad820da45a4079b`,
manifest is `517ebeb6523eea4c9ff61ee18a84f8e5dce3d81729fe679eda1706f72a94ace3`,
and Caddy is `bc4089a16acfebf62d6249cd9455d26c08f4d21f012e3fd93a0a3db97c2aa393`.
Hosting input snapshots are `/var/backups/webhost-sites/change-20261031T011746938217Z`
and `/var/backups/webhost-sites/change-20261031T011746938685Z`; the previous
desktop release remains `bfcccab6fcdfd33221aeb5e57dd59d8eb788217b0c0172bb1cf45b3c533a807b`.
Use the managed hosting lock and generated validation/apply workflow for rollback.

Fresh real HTTPS Chromium tests with disposable registered accounts passed
Browser launch, visible blocked-site feedback, HTML open from My files, relay
navigation, lease renewal, explicit URL download and server synchronization.
Phone-emulated Chromium passed visible status, typing and touch scrolling.
Those test accounts and their exact files were removed. The separate desktop
prototype and the other hosted sites returned their expected status codes.
These checks do not cover a physical phone, ordinary clicked downloads,
authenticated site downloads, general website compatibility, or audio.
The broader component/license review and live requested-report workflow are
not complete. Existing Linux guest egress is outside the new Browser IP rules.

### Live requested Browser report and restart — 2026-10-31 UTC

`CODI_TEST_REPORT=1 tests/live_browser_relay_account_check.py` used a fresh
registered account and actual live Browser to visit example.com. It checked
that the server held no report for that account before a test request,
created the explicit request through the coordinator as its service account,
observed the signed device report and domain summary, restarted the relay,
and confirmed the summary remained identical. It then removed the request,
its reports, and the disposable account. The relay is active and its report
database passed SQLite `quick_check`. This tests the real client and service
but creates the request as an operator rather than logging into the admin UI;
the admin UI workflow was tested separately in the local two-account fixture.

### Live Browser policy operator — 2026-10-31 UTC

`sudo codi-browser-policy` on box-webhost now manages incoming-login and
outbound IP/country rules, Browser blacklist/whitelist entries, and the
whitelist switch. It uses the protected live relay's pinned validation code,
a per-file lock and atomic validated replacement. It does not enable server
audit or cover Linux guest egress. See `apps/system/browser/docs/LIVE_POLICY.md`
for commands and scope. The installed source at
`/srv/codi-browser/operators/policy-1e7ae703d/manage.py` has SHA-256
`79870a7f49e4c3d1c66f82dcfda217acdb2b02e6bf8a1e6155da5237791ee5ef`;
the root-owned entrypoint is `/usr/local/sbin/codi-browser-policy`. Local
fixture tests passed; the installed operator successfully edited isolated
copies of the live policies, displayed the live rules, rejected an IP literal
as a domain, and left both live policy hashes unchanged. Live rule enforcement
and active-stream changes were tested separately using the guarded fixture.


## Browser and file mirror update

The live Simplified frontend is release `d360a4ef6c221d2f120b20bd1c38e89be100f62a514ff573a3130abe64ff34d8`.
The file mirror stores large browser records as Blobs and checks the server's
file version before downloading again. Local tests verify unchanged files do
not trigger another full download, and external same-size edits are detected.
A live 128 MiB mirror test timed out on its first attempt. A repeat passed
through browser storage, upload, verified server read, deletion, and sign-in
from a fresh browser context. The intermittent timeout remains unexplained.

The live gateway defaults are 50 GiB per account and 200 GiB shared per day;
the per-transfer and 128 MiB file limits remain separate. Gateway release is
`0685f9925f2d00cb2433d6d3d9066ee86da7f901a2c3302e3c1f1e1842ab2152`.
Browser routing and management details are in
`apps/system/browser/docs/LIVE_POLICY.md` and `DOMAIN_REPORTS.md`.

## Embroidery apps live

Release `bc92bb0d2f7f033b868b97d4d04b04204df8d2191d3216681c6f54052990832b`
serves Embroidery Studio and Stitch Converter under Applications → Crafts.
The prior release was `d360a4ef6c221d2f120b20bd1c38e89be100f62a514ff573a3130abe64ff34d8`.
Desktop and phone-sized local and live registered-account checks opened both
apps, generated PES and DST examples, and saved to My files. The live test
account and its files were removed. Physical-machine compatibility and sewing
remain unverified; StitchFoundry is an upstream pre-release.

The first deployment preserved app-builder temporary-directory modes (0700),
which gave the web server 403 responses for app assets. The release directory
permissions were corrected to public read/traverse, after which the live test
passed. `build-simplified-static.py` now normalizes public directory and file
permissions to prevent a repeat. Caddy generator SHA-256 remains
`bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5`;
manifest is `49c3d119bda77e7bd6fb93c487cf848f13e78a9c75edb47b73ad081f639d58ee`
and Caddy is `f8e953dd50445f2efb417af9290bca0bb7cd96aec70daa4b9ed20c3196468555`.
Hosting rollback snapshots are under `/var/backups/webhost-sites/` as
`change-20261031T014355641269Z` and `change-20261031T014355650311Z`.

The existing Arduino Simulator is also served by the current release under
Applications → Electronics. A live registered test ran its compiled Blink HEX,
observed the simulated LED change, opened firmware from My files, and verified
independent windows; its disposable account and file were removed. Pico remains
separate unfinished development.

A live registered-account mirror test also instrumented two subsequent syncs
of an unchanged file: both used version checks and neither requested a file
read. The disposable test account and its file were removed. Run the check with
`CODI_TEST_NO_REPEAT=1 ../active-system/.venv/bin/python tests/live_browser_relay_account_check.py`.

## Digital Logic and Pico live

Current release `fef98d4b459cf9b6e6e8d86c906143f5bf81d3b6fd404a0a866954851d470175`
adds Digital Logic and Pico Simulator under Applications → Electronics and
keeps open application submenus intact during desktop updates. Existing app
bundles are unchanged. All release files were hash-verified and public asset
permissions checked before activation. Rollback release is
`bc92bb0d2f7f033b868b97d4d04b04204df8d2191d3216681c6f54052990832b`;
hosting snapshots are `change-20261031T015446474999Z` and
`change-20261031T015446476222Z` under `/var/backups/webhost-sites/`.
Generator SHA-256 remains `bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5`,
manifest is `df3b55c5c353c438cce9137100e5451555d5bf1ebf67270382eff80cd2ababdf`,
and Caddy is `6f7000bafe0f6a0eea0afc54fa3983fbd404ffc4499369dd06e13d77f5c83131`.

Local desktop and phone-sized tests exercised Digital Logic's gate simulation
and actual account save/sync/reopen. Live registered testing repeated the save,
server read and reopen. It supports basic feed-forward gates in JSON, not a
schematic editor, sequential logic or analog circuits. Pico's live Blink test
passed. Its MicroPython save/sync/reload was tested locally using privately
supplied ROM and UF2; neither is distributed. Explicit project saves retain
simulated flash, not CPU state. SSI support is partial. Both test accounts used
on the live site were removed. See each app's README for test scope and terms.

The live Pico Blink and Digital Logic account save/reopen checks also pass in
an emulated phone viewport. Obsolete local generated release candidates were
removed after deployment; source and the live rollback remain. The Raspberry Pi
ROM and MicroPython firmware were not included in Git or the release.

## Circuit Simulator live

Release `a690fd6f65795434dd6e6ce7f44c53627462cfdd0b8dc91581d64c22d3940875`
adds Circuit Simulator (CircuitJS) under Electronics; existing app bundles
are unchanged. It includes the GPL corresponding-source archive and notices.
Local tests exercised the graphical divider at 5 V, editing it to 6.67 V,
account sync, phone-sized reopen and iframe cleanup. Live desktop and
phone-sized checks independently verified the 5 V simulation, source archive,
and server-backed save. Their disposable accounts and files were removed.
This is CircuitJS, not ngspice; complex circuits run on the browser main thread.

The previous release is `fef98d4b459cf9b6e6e8d86c906143f5bf81d3b6fd404a0a866954851d470175`.
Hosting snapshots are `change-20261031T020934080997Z` and
`change-20261031T020934086998Z` under `/var/backups/webhost-sites/`.
Generator SHA-256 remains `bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5`,
manifest is `0931fc48033969107f3fe18992926845a187f1cff4cecd39b0c14bb24cd5399a`,
and Caddy is `34218a7e4da124cb8085be7c8a109df53240876429dcd79c2440c5c022422f02`.
Two activation attempts with mistyped expected manifest hashes were rejected
before changes; the exact current pin then validated and activated normally.

## Electronics Design live

Release `67f4c5a44ab04a28147a895ec1d52a58fcb1a48dacbd5b24da9a646b4d1f6558`
adds Electronics Design under Electronics; previous app bundles are unchanged.
The editor's WASM was built locally from the pinned source inputs documented in
`apps/system/electronics-design/README.md`; notices are included. Registered
local and live desktop and phone-sized tests opened a project, captured Save As,
synced to the server, closed and reopened. A local 9 MiB project round-tripped;
the 128 MiB limit itself and physical touch were not tested. Use the editor's
Save As / Share and then the host's Save to My files; native Save alone is
transient. The example is not a production-ready board.

Previous release: `a690fd6f65795434dd6e6ce7f44c53627462cfdd0b8dc91581d64c22d3940875`.
Hosting backups: `change-20261031T021402839361Z` and
`change-20261031T021402839858Z` under `/var/backups/webhost-sites/`.
Generator SHA-256 remains `bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5`,
manifest is `8351825cf04e6b1b1ff0a36fabfb56bb2a6a35aca6180c4884ea55098713e851`,
and Caddy is `7e49a881f9ea0b6d46cc846ce270ec76f1aa996d91973c5513fc03893e014b42`.

## ngspice Circuit Lab research

The separate ngspice Circuit Lab remains unshipped. A clean build from pinned
ngspice 45.2 and wrapper sources passed divider and RC tests and an isolated
account sync and phone-sized reopen. A development-tree test modified and
relinked numparam and reran the solver. The portable corresponding-source,
relink materials and complete release notices are not yet verified. Build and
relink recipes and exact limits are recorded in `apps/system/circuit-lab/README.md`;
research build outputs and test accounts were removed. Live Circuit Simulator
continues to provide the separate CircuitJS engine.

The later ngspice candidate produced a 48,509,541-byte source/relink archive,
SHA-256 `194eb712ba6ad296baff16b1760ceefc67eab828e7df39555cd94125c018915a`.
It passed an independent-directory modified-component relink and the combined
app passed simulation, account sync, phone-sized reopen, and lazy source-link
tests. Two clean builds matched on the same Linux machine. Final distribution
review of source, notices and LGPL relinking sufficiency remains open, so
Circuit Lab is not live. The archive and SDK were generated test artifacts and
removed; the pinned recipes and tests are tracked for rebuilding.

## Signed upload pause handling

The live private-file worker now uses a 60-second idle timeout specifically
for authenticated binary upload metadata and content. Control requests retain
their 5-second timeout; the 900-second overall transfer deadline, transfer
quota, per-use size, and concurrency limits remain. The live worker is
`be4a9ef3a613c2e90517fae427d4d2256b97b74ee2134c10cafe263fc2440eac`,
with previous worker
`0685f9925f2d00cb2433d6d3d9066ee86da7f901a2c3302e3c1f1e1842ab2152`
available for rollback. The journaled code upgrade reported preserved account
and permission bindings. Local tests passed a real signed upload with a
5.2-second pause and a separate bounded idle-timeout case, plus all 18 gateway
HTTP tests. A live signed upload through ksu.codes survived a 5.5-second pause,
read back the exact content, and was removed with its disposable account.
This fixes a confirmed short timeout but does not prove that timeout caused the
previous intermittent 128 MiB failure. Longer upload idle time also means a
stalled authenticated upload can occupy one of the bounded slots longer.

After the upload-idle update, a fresh live 128 MiB browser-mirror upload,
server read with SHA-256 verification, synchronized deletion, and fresh-browser
sign-in all passed. The disposable account was removed. An unchanged-file
sync in the same run again made no redundant file downloads.

## Browser clicked downloads live

Release `f3681cd5867e0f779049812f9fc178db90d4c2f8169699a1d66b1fba69d35919`
adds Gecko clicked downloads to a per-window temporary queue. Users choose
Save to My files to retain one; the account mirror then synchronizes it to the
server. The queue permits three active/waiting files up to 128 MiB each and
warns on reset or close. Browser crashes can still lose temporary downloads.
Existing-name collisions do not overwrite files. The Browser's direct URL
download remains separate and does not share Gecko cookies.

Local real-Gecko desktop and emulated-phone tests passed a cookie-protected
delayed download, explicit save/cancel, server sync, collisions, empty files,
interruption, advertised and streaming size limits, reset, independent windows,
and worker termination. Live fresh-account desktop and emulated-phone tests
clicked a data-URL download and verified the saved server copy; they do not
prove a live third-party authenticated download or physical phone behavior.
The live signed relay, blocked destination, gateway write/read, unchanged-file
sync with zero repeat reads, and fresh-browser sign-in also passed. Disposable
accounts were removed. Source commit `29a71d717` is on box-git.

Public modified source and Mozilla modules are at
`/browser-sources/codi-browser-source-29a71d717.tar.zst`, SHA-256
`f231dfee54279c20c6bca77988b556d6fcad7c8886792eb78c63e1f9c10b680b`;
the source route rollback exercise passed. See Browser's `CLICKED_DOWNLOADS.md`
and `SOURCE_PROVISION.md` for limits and outstanding license-audit scope.
Previous release `67f4c5a44ab04a28147a895ec1d52a58fcb1a48dacbd5b24da9a646b4d1f6558`
is retained. Hosting backups are `change-20261031T031853664991Z` and
`change-20261031T031853665753Z`. Current generator SHA-256 is
`2d04ab00dc0e17003f94155b4f812b640ed2f9ed897e4f3685b8cb2bbbda41cb`,
manifest `1eff3c244aa5e528f0fe91962e835b2e551c77846a44a410d1066d6c606a7137`,
and Caddy `a34f149de23c2c88c61c3999035fb23fef758aca4ae6c33dface3ed75e3ece01`.

## Browser RLBox attribution

The shipped Gecko object's RLBox thread-local implementation includes
vendored RLBox headers. The Firefox license page named RLBox but the combined
notices lacked its exact pinned copyright text, so the Mozilla revision's
`third_party/rlbox/LICENSE` was added to the public combined notices.
The notice builder verifies its exact SHA-256 and has an input-rejection test.
The public notice SHA-256 is
`28b3c6267097ecfa2e40dc56de5715348ca011652a2b26817f7cbba15e2570b7`.
The source index was regenerated and the current source link is correctly
under Source code. Prior public notices were backed up under
`/var/lib/codi-ingress/browser-source-rlbox-notice-backup.json`. This closes
one identified attribution gap, not the full linked-component/legal review.

The next inventory pass found additional linked graphics and utility object
groups, including ANGLE, Skia, Cairo, FreeType, Brotli, HarfBuzz, WOFF2,
Graphite and Expat. Their pinned source licenses and FreeType 2.14.2's
upstream FTL text are now in the combined notice; the public index explicitly
credits FreeType. The generator and its tests verify both new input hashes.
The public combined notice SHA-256 is
`35258b272eca7cb0f23e53c847733c536197ee3ce8884b66d693b425433b6d1a`;
the prior files are in `/var/lib/codi-ingress/browser-source-graphics-notice-backup.json`.
See `SOURCE_PROVISION.md` for reproducible collection and audit limits.

## Identity renewal pin repair

The enabled hourly `codi-ksu-live-root-renew.timer` was repeatedly starting a
job pinned to the old issuer config and native release, so the guarded job
failed with `Managed config pin changed`. The current signed seed then expired
at 2026-10-31 20:00:39 UTC; this was a future expiry at the time of repair.
The issuer was serving normally. A read-only run of the protected operator
using the current config and release hashes validated the installed release
and reported root revision 10, `nextStep: wait`, and no pending journal.

`active-system/scripts/reconcile-browser-renewal-pins.py` took the managed
hosting lock, verified both current pins and the old unit, backed it up to
`/var/backups/codi-renew-before-browser-issuer-r3.service`, validated and
atomically installed the two pin changes, and reloaded systemd. A manual
`systemctl start codi-ksu-live-root-renew.service` then exited successfully
with `not-due`, root revision 10; the hourly timer remains active. A oneshot
unit appears inactive after a successful run, so check its `Result` and
`ExecMainStatus` rather than expecting it to remain running. Actual renewal
at the future due time was not forced or tested in this repair. Subsequent
issuer/config upgrades must reconcile this unit's config and release pins.

## Additional upstream Rust notices

Review of 26 checksum-verified registry crate archives found that 25 had no
root license file; `remove_dir_all` had two using the spelling `LICENCE`,
which the original collection script missed. For crates with an available original GitHub
source revision, 27 license files from 16 pinned revisions were collected,
hash-pinned and appended to the public Browser notices. The pinned source
list and reproducible collector are in `apps/system/browser/docs/` and
`apps/system/browser/tools/`; `prepare_notices.py` requires the exact input.
The public combined notice SHA-256 is
`a817feabfa8bc5cd56dd24619f0c9c3c9688fa58b69694c082c24d615cd37ea7`;
the prior public files are in
`/var/lib/codi-ingress/browser-source-rust-upstream-notice-backup.json`.
Some upstream packages lack separate license files or have unavailable
revisions, and non-GitHub sources were not resolved by this pass. The Rust
target-build set is conservative rather than a final-link inventory.

The registry audit was subsequently made reproducible in
`tools/audit_missing_rust_crates.py`, which verifies every package against the
pinned Cargo lockfile and detects both LICENSE and LICENCE. It caught the
collector's missed `remove_dir_all` files; the collector and public notice
were corrected. The two corrected files match the already published upstream
copies byte for byte. Only that crate's block changed in the combined notice,
whose current public SHA-256 is
`7775f6197a7a14a397ad6180b43b4c553aaacef77ac4e0136a34fc15f3f3f829`.
The prior file set is under
`/var/lib/codi-ingress/browser-source-licence-correction-backup.json`.

A real local Wisp WebSocket test now also exercises DNS rebinding between
streams: an allowed public answer connects using the exact vetted numeric IP,
then private IPv4, mixed public/private IPv6 and mapped IPv4-in-IPv6 answers
are rejected before the connector is called. All 11 Wisp tests passed. The
tested `wisp.py` and `policy.py` SHA-256 values matched the installed live
relay files. This is a local controlled-DNS test, not a claim that a real
external DNS provider performed the rebind during the live test.

## Optional server audit integration — source work in progress

The live Browser policy still has `serverAuditEnabled: false`; no server
metadata ledger was enabled. Review found that the existing `AuditLedger` and
Wisp hooks were not wired into the relay service, so simply turning the flag
on would fail startup rather than enable recording. Source work now adds
private credential/database arguments, constructs the ledger only when the
policy explicitly enables it, and includes its source in exported runtimes.
Local tests verify default-off makes no file, enabled mode requires a private
32-byte Ed25519 credential, and an enabled Wisp stream records metadata but
not payload. The URL downloader now also emits per-hop events for redirects,
completion and policy denials without recording paths or contents. Ledger
integrity is verified on startup. This work is **not deployed or ready to
enable**: protected systemd credential provisioning, operator controls,
end-to-end failure/recovery and live opt-in tests remain. Do not set
`serverAuditEnabled` on the live policy yet: the current live runtime has no
configured audit callback and would reject traffic.

The optional service renderer now adds a private `StateDirectory` and a
systemd `LoadCredential` only in explicit audit mode; the default unit has
neither. A real isolated systemd test found that its per-unit credential is
root-owned mode 0440 with directory/ACL isolation, not mode 0400. The key
validator now permits that layout only at the exact Browser service
credential path and requires root:root ownership and no writable/world bits.
An isolated transient unit using the actual service name and a disposable
key successfully opened and signed the test ledger. A real local process
test also started with audit disabled (no ledger created), enabled it, and
restarted with the same ledger. A local HTTP integration test verified signed
per-hop redirect metadata without paths or file contents. Temporary test key,
unit and database were removed. The live configuration remains off; safe
operator switching and live opt-in/recovery testing are not done.

The local candidate now includes an audit report tool that verifies the
ledger and reports either per-account or aggregate domain totals; it can check
an independently saved head for rollback. Tests cover account scope,
wrong heads, an absent or unrelated database, and a real transient systemd
reporter using a disposable credential. It also includes journaled switch
primitives with local tests for successful change, failed restart rollback,
process interruption and refusal to overwrite an independently changed
policy. The privileged wrapper, protected key provisioning, end-to-end live
recovery, and deployment remain outstanding. The primitive requires its
caller to hold the hosting and policy locks and validate ownership/units.

The source-only runtime candidate built from commit `f4a43b30e` has manifest
`c54118ec1a534860f8293d74cd92dbe0744d31c72fa602f52fef986437ae4b37`.
The exported, pinned process passed both default-off startup and an explicit
enabled startup with a private test key and ledger. It is not installed or
active on box-webhost. Any further source changes require a new candidate and
matching public source provision before activation.

The source-only privileged audit operator is built as a three-file protected
bundle with manifest SHA-256
`55b97370580f079fb0b644323f015d54d36e4767547b9ade1b90069fc20b4fe2`.
It pins the above runtime, validates root-owned operator/runtime content and
service units, holds the hosting and destination-policy locks, and preserves
keys and ledgers when disabling or rolling back. Fixture tests cover key
preservation and refusal of a tampered operator file. A test initially created
Python bytecode in the staged runtime; the verifier correctly rejected the
extra file. The test now disables bytecode, the test-only cache was removed,
and the corrected package check passed. This operator is not installed and
has not been exercised against real service transitions; live audit remains
disabled. The privileged wrapper and actual transition/rollback still require
an isolated installed-systemd exercise before any live switch.

The current rebuilt operator additionally disables Python bytecode before
importing pinned runtime files; its manifest SHA-256 is
`2fe3f429322c16adbe60890aa04ea2c95d67afbd3d94b9a3d4778e73c5615258`.
Its package and tampering checks passed. It supersedes the prior candidate;
the current runtime candidate is unchanged.

An isolated root-owned temporary systemd unit subsequently passed a real
enable transition, automatic rollback after a failed restart, and recovery
after a simulated process interruption; the fixture unit was removed. The
runtime `c54118ec…` and operator `2fe3f429…` have been copied to protected
`/srv/codi-browser/releases/` and `/srv/codi-browser/operators/` paths. The
operator's read-only `status` check passed and reported audit disabled,
no key or ledger, no pending journal, and `serviceMatchesMode: false` because
the live service still runs the previous runtime. Neither candidate has been
activated. A release-matched public source archive, guarded runtime upgrade,
live opt-in and rollback tests, and default-off restoration remain necessary.

The source archive for runtime `c54118ec…` is now public at
`/browser-sources/codi-browser-source-f4a43b30e.tar.zst`, SHA-256
`3e090e5a9508f0ff53aae97791ff21c71dc38afb5d84bc9cc2cc54f304aeb42c`;
its route was rollback-exercised and the public download hash checked. Current
hosting generator SHA-256 is
`29305c1d0d5387886816d156986dc53ad82e1e6b287ad6c7ea8b4b2559a8d7c2`,
manifest remains `1eff3c244aa5e528f0fe91962e835b2e551c77846a44a410d1066d6c606a7137`,
and Caddy SHA-256 is
`5a1052be870c92e98696464174e12f8b5faed66b8dfa535dd22e544a1b5a150f`.
The relay still uses the previous runtime with audit off.

## Optional server audit live, default off

The audit-capable relay runtime `c54118ec1a534860f8293d74cd92dbe0744d31c72fa602f52fef986437ae4b37`
is now live with recording disabled. Its protected operator is
`/srv/codi-browser/operators/ed662839765996e6f5138ddb1eaedce6b2c4f40c2d4ae9ec6e2d4c7a0dc7d374`;
`sudo codi-browser-audit` is the installed entrypoint. The first runtime
rollback exercise hit a readiness race: systemd became active before its Unix
socket. The old unit was restored, its journal recovered, and bounded routed
health retries were added. The second real upgrade/rollback exercise passed,
followed by the guarded upgrade. Previous unit backup is
`/var/backups/codi-browser-relay-before-audit-runtime.service`.

A live timed opt-in with automatic shutoff used a disposable account to test
signed Browser access, direct download, blocked domains and private targets.
The report verified seven signed events; after relay restart the independently
saved head matched. The audit was explicitly disabled, the shutoff timer was
stopped, and the test-only ledger and newly created test key were removed only
after checking the exact expected head, record count, domains, single deleted
test account, owners and file set. Current status reports audit disabled,
matching unit, no transition, no key and no ledger. A new enable creates a
fresh key and ledger; ordinary disable retains them. Later signed-account,
relay, blocked destination, file sync and fresh-login checks passed.

The live destination policy after the toggle is semantically identical to
the tracked default, though formatting changed its SHA-256 to
`31654ffd64073946ba9833a7594bf5fe4ef1f5bf575466e00984a6946f515433`.
The independent `codi-browser-policy` manager now validates against this
runtime using root-owned operator `policy-e36ed9571`, SHA-256
`e36ed957153e4390749c2192a8230f7ea52b24ae8fc44682233167f451e49b43`;
its previous wrapper is backed up at
`/var/backups/codi-browser-policy-before-audit-runtime`. See Browser
`LIVE_POLICY.md` for audit controls, key backup, checkpoint limits, and the
separate Linux guest egress boundary.
