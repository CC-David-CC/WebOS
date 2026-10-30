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
