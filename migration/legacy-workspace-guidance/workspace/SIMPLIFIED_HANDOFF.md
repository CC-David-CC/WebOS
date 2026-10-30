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

The ingress table is not installed. A managed boot/startup dependency, actual
public proxy-chain test, issuer integration and rollback are still required
before the login IP restrictions can be considered live.
