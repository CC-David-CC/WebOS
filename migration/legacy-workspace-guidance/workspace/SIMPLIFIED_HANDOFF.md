# Simplified branch handoff

## 2026-10-31 — Arduino serial output capture

Live static release `ee3363f4b850dbec9ea235e4b72ed61f4311142309cedfffb19e057775ba493b`; previous `f8e2eafafd0422f0383603e2c814b2021c647b61397c457ba76f51a2ed432423`. Arduino Simulator can save the visible decoded serial output as a `.txt` snapshot in My files. The monitor keeps only the most recent 32,768 UTF-16 code units, avoids splitting surrogate pairs and warns after trimming; restart clears it. The save requires confirmation before replacing a file, checks versions, and distinguishes later serial output from the saved snapshot. Local desktop and emulated-phone tests and a live emulated-phone test cover Unicode echo, cancelled replacement, output during save, account sync and reopening in Text. The live disposable account was removed. This is not raw or timestamped serial recording; physical hardware and touch remain unverified.

## 2026-10-31 — Electronics Design shared three-view layout

Live static release `f8e2eafafd0422f0383603e2c814b2021c647b61397c457ba76f51a2ed432423`; prior stable `4092716a15ee79d1e7bb1d08cdd130af5f23d1317155eec943cc4a86e1d570ab`. On a sufficiently wide and tall window, **Show three views** displays breadboard, schematic and PCB panes using one native document and simulation. Clicking a pane selects it for editing; narrowing or shortening the window returns to single view. The pinned upstream source is patched by `prepare_source.py` followed by `prepare_split_source.py` and rebuilt; the new JS/WASM hashes are pinned in `prepare.py`. Local 4K-sized browser tests exercised selecting each pane, schematic edits, a deletion reflected in all three views, undo, save and width/height fallback; local desktop and emulated-phone account regression tests passed. A live 4K-sized account test covered schematic edit, server sync, narrow resize and reopening on an emulated phone-sized session. Disposable live accounts were removed. Physical monitors/touch, every editor tool and full electrical or manufacturing correctness are not validated.

## 2026-10-31 — Spreadsheet aggregate accuracy

Live static release `4092716a15ee79d1e7bb1d08cdd130af5f23d1317155eec943cc4a86e1d570ab`; previous `eccde7cf460139dd2d983acfcd08a473e0bdf25259d3996d9b9b2da4ad1b2a16`. Supported SUM, AVERAGE, COUNT, MIN and MAX now ignore blank and nonnumeric text cells in referenced ranges or standalone cell arguments; decimal numeric text is included because grid values may be stored as text. AVERAGE of no numeric values reports an error, while MIN and MAX return zero. This changes earlier average/count results for blank ranges. Formula evaluation remains bounded and supports only the documented subset. Unit tests cover mixed cells, cycles and bounds; local desktop and emulated-phone account tests and a live emulated-phone account test checked displayed values and CSV output. The live disposable account was removed. Physical touch and broad Excel compatibility remain unverified.

## 2026-10-31 — Spreadsheet CSV export

Live static release `eccde7cf460139dd2d983acfcd08a473e0bdf25259d3996d9b9b2da4ad1b2a16`; previous `b58c9c8e2e94545d6f4cb9ebb5cd51c1135fc645d607e6bcf2b42454d9a674cc`. Spreadsheet exports the selected worksheet’s calculated values to a separate CSV in My files; formulas, formatting and other sheets are not included. Export runs in the conversion worker, rejects unsupported formulas, limits output to 8 MiB, confirms replacement and protects formula-like text. Local desktop and emulated-phone account tests and a live emulated-phone test cover import/edit/export, cancelled replacement, multi-sheet selection, formula values, invalid-formula rejection and Data Explorer opening. Unit tests cover quoting and CSV text protection. The live disposable account was removed. Physical touch and full spreadsheet compatibility remain unverified.

## 2026-10-31 — Spreadsheet CSV import

Live static release `b58c9c8e2e94545d6f4cb9ebb5cd51c1135fc645d607e6bcf2b42454d9a674cc`; previous `72e97c0bf8047e7cbbbca80cc9c735cdd129f516324abbbd2828bd765593733c`. Spreadsheet can open UTF-8 comma-separated CSV from My files as a new workbook. Fields stay text and leading `=` receives an apostrophe to prevent accidental formula evaluation; the original CSV remains unchanged. CSV is limited to 8 MiB and a 10,000-cell grid, including minimum grid dimensions. Local unit tests cover quoting, embedded newlines, malformed input and limits; local and live desktop/emulated-phone account tests cover opening, editing, saving, sync and fresh-session recovery. One live phone-sized run timed out waiting for sync; a later fresh run passed, and all disposable accounts were removed. Local XLSX and formula regression tests passed. Physical touch, other delimiters and non-UTF-8 encodings remain unverified or unsupported.

## 2026-10-31 — Document save and PDF snapshot safety

Live static release `72e97c0bf8047e7cbbbca80cc9c735cdd129f516324abbbd2828bd765593733c`; previous `7deebe2bfd81bee4eddab89c6444942433358ee55790e5048ddcfe6535b5dca5`. Saving a different existing report now asks before replacement, checks its version and preserves the draft on cancellation or stale saves. PDF export captures the destination and document snapshot at the start and reports later edits; PDF conflict checks and the saved-file watcher use metadata. Local and live desktop/emulated-phone tests cover these cases and account recovery. A local formatted multipage PDF, image, PDF Viewer, offline sync and conflict workflow also passed; its first run used an outdated local PDF Viewer bundle and was rerun with current source. Live disposable accounts were removed. Physical touch and broader document/PDF compatibility remain unverified.

## 2026-10-31 — Digital Logic truth-table export

Live static release `7deebe2bfd81bee4eddab89c6444942433358ee55790e5048ddcfe6535b5dca5`; previous `91a9a4b45c5a6b0a4a4dca28badaa96494c344173067216e513a5f94b604d191`. A calculated truth table can now be saved as CSV in My files. Editing the circuit invalidates the calculated table; a save checks that it still represents the current draft. Existing files require confirmation and a version check, and formula-like headings receive an apostrophe for spreadsheet safety. Local desktop and emulated-phone browser tests cover quoting, cancelled overwrite and edits during save. Local and live emulated-phone account workflows calculated a half-adder table, synced its CSV and opened it in Data Explorer; the live disposable account was removed. A CSV is an exported snapshot; simulation and table limits and physical-touch caveats remain.

## 2026-10-31 — G-code relative movement

Live static release `91a9a4b45c5a6b0a4a4dca28badaa96494c344173067216e513a5f94b604d191`; previous `93a06328aae04a0873cc7d9eb59d413aa15e0c3e4814ed8d0e8f3f1d93942a2f`. The parser normalizes G90/G91 XYZ movements before grouping layers. It treats M82/M83 extrusion mode separately; firmware dialects can differ. It rejects multiple commands on one line, positioning-mode lines with coordinates, arc-center mode changes, and invalid numeric moves, in addition to previous unsupported cases. Local worker tests compared equivalent absolute/relative coordinates, extrusion and layers; desktop and emulated-phone account tests compared pixels at the same canvas size and recovered the file in a fresh session. A live emulated-phone workflow also passed; the disposable account was removed. An initial pixel comparison failed because status text changed canvas height; controlling the test canvas size produced matching images. Large-worker cancellation passed locally. This is a visual aid, not machine or safety validation, and physical touch and other controller dialects remain unverified.

## 2026-10-31 — Digital Logic combined-circuit examples

Live static release `93a06328aae04a0873cc7d9eb59d413aa15e0c3e4814ed8d0e8f3f1d93942a2f`; previous `b737b94d940239632dd62110f8260775ee56ed4316e62b10ed4f730e74264c39`. The example selector now offers a half-adder and a 2-to-1 multiplexer alongside the single gates. Local desktop and emulated-phone tests checked each truth-table row, interactive input changes, replacement, and disposal; local registered-account desktop and phone-sized workflows and a live phone-sized workflow saved, synced, reopened and checked the half-adder truth table. The live disposable account was removed. These are logic models, not timing, electrical, or hardware validation; physical touch remains unverified.

## 2026-10-31 — Data Explorer save checks

Live static release `b737b94d940239632dd62110f8260775ee56ed4316e62b10ed4f730e74264c39`; previous `46ceeb7e966bc0ae3cd50dbdcc8262bb10d308a901a9eeb9337a61b8ce3988f2`. Analysis saves check source hashes and project versions with My files metadata instead of rereading potentially large source files. CSV export overwrite checks also use metadata. Local desktop and emulated-phone tests covered saved analysis reopening, stale project and changed source protection, invalid-project rollback, CSV results, cancelled overwrite and no full-file reads for these checks. A live emulated-phone analysis workflow passed; its disposable account was removed. This does not prove a 128 MiB dataset works on every device or qualify physical touch.

## 2026-10-31 — Audio Editor WAV precision

Live static release `46ceeb7e966bc0ae3cd50dbdcc8262bb10d308a901a9eeb9337a61b8ce3988f2`; previous `92583c0e95dd3bf778fb6b209b4891cd7c8aa6ed9423eff7b260de12295df53e`. Save options now offers 16-bit PCM, 24-bit PCM and 32-bit float WAV. PCM clips values outside −1 to 1; float retains finite out-of-range values, although playback may clip. Existing version checks and the 128 MiB output limit apply.

Local desktop, emulated phone and 4K tests plus live desktop and emulated phone tests checked sample values, output format, rate, synchronization, fresh-session reopen and stale-save protection. An earlier live phone-sized run hit the server request limit during consecutive rapid sync tests; a later run passed after the limit cleared. Worker tests cover 24-bit interleaving and odd padding, float headers, nonfinite rejection and the 128 MiB limit. Physical phones, all codecs and effects, and multitrack persistence remain unqualified.

## 2026-10-31 — Audio Editor WAV sample rates

Live release `92583c0e95dd3bf778fb6b209b4891cd7c8aa6ed9423eff7b260de12295df53e` decodes conventional RIFF/WAVE files at their source sample rate when the browser supports it. If the rate is unavailable or unsupported, decoding uses the browser rate and reports that the original may differ. WAV output remains 16-bit and does not preserve source bit depth or compressed formats. Existing-output checks now use mirror metadata instead of rereading audio bytes. Local and live desktop and phone-sized tests round-tripped a 32 kHz WAV through reverse, save and fresh-session reopen; local 4K-sized and forced-fallback tests also passed. Physical audio-device behavior, all codecs and multitrack saving remain unverified.

## 2026-10-31 — broad text search navigation

Live release `4aa4e77e8401e50c6d306c7a077bdb5b77ae96be11eba70e3e9923308d063e8d` keeps the 50,000 stored-match limit but adds directional searches and single replacements beyond it, including wraparound. Replace all remains disabled for truncated result sets. Local and live desktop and emulated-phone tests cover a match after the limit, reverse/forward wrap, a single replacement, literal symbols, case matching and a chunk boundary. Large-document searches may still take time on the UI thread; physical touch remains unverified.

## 2026-10-31 — larger text documents

Live release `245696116948979eba6935624562050d8dc5e923c4c4f5ce200eeb30fd00035a` raises Text’s opening limit to the shared 128 MiB file limit. CodeMirror indexed lookups avoid rebuilding the document for cursor position and line navigation; word counts are omitted above 2,097,152 UTF-16 code units. Broad searches stop after 50,000 matches and disable Replace all until narrowed. The mirror exposes metadata-only `stat` for change checks. Local and live desktop and emulated-phone tests opened, edited and synced an 8 MiB file and checked the search limit and line navigation; a local desktop test completed an approximately 127 MiB round trip but was slow and memory intensive. Single very long lines, low-memory devices, the exact maximum and physical touch remain unqualified.

## 2026-10-31 — notebook working-copy cleanup

Live release `f76d2c172d3691c0f048cfb84124181ff1772fb53abaf5b1b33fd9dd844f3f09` requests best-effort removal of each closing window’s generated JupyterLite file and checkpoint keys from that account’s browser database, including pending replaced copies; account My files are separate. Unknown database layouts are left untouched. Local desktop, phone-sized and 4K-sized and live desktop and phone-sized tests closed and reopened windows, verified a second kernel still executed, checked both saved server copies, and verified old working-copy keys were absent. An initial live candidate emitted a Jupyter disposed-session error; the explicit widget shutdown was removed and the revised live tests passed without page errors. Browser crashes, interrupted startup, older copies and future storage-layout changes may leave temporary data.

## 2026-10-31 — notebook first-save race

Live release `c82e925ee2f7098eaffb40abbe0555082678d7676a6747d31760d63ded250d04` schedules a follow-up automatic save when the notebook changes while its first save is in flight, and captures the requested destination before asynchronous work. A regression test first waits for the Python kernel metadata to settle, pauses the first account-file write, edits the cell, and checks the newer edit syncs and reappears in a fresh session. It failed against the previous version and passed locally and live at desktop and phone-sized viewports. JupyterLite temporary working copies and lifecycle cleanup remain unfinished; untrusted notebooks are not isolated.

## 2026-10-31 — Digital Logic truth tables

Live release `c70938b7f52efdae36f714ea6219eb58c37d8b52933074642d5f5e2584b43e38` adds a truth table from the current JSON draft using a separate DigitalJS simulation. It supports 1–6 one-bit buttons and 1–16 one-bit lamps, reports undefined signals as X, and cancels old results when the draft changes. Local desktop, phone-sized and 4K-sized tests cover seven gates, a half-adder, undefined signals and cancellation. Registered-account local desktop and phone-sized and live desktop tests reopened saved circuits and generated their tables. The live phone-sized workflow reached cleanup after those checks but hit the shared gateway limit; its test account was removed separately. Physical touch, sequential logic and hardware validation remain outside this test.

## 2026-10-31 — G-code extrusion interpretation

Live release `c36d3910b40e2d7100ca7b81678272766fe67bac2fc6a93fd1566e093a9dfdec` classifies tested M82/M83 extrusion changes using per-tool E values and G92 E resets, so decreasing absolute E is shown as non-extruding travel. Numbered commands, coordinate-only modal moves and full-circle arcs are rejected instead of being silently omitted. Local desktop and emulated-phone workflows, a 100,000-move worker test and cancellation passed. The deployed worker passed registered desktop and emulated-phone tests, and the complete live viewer workflow passed at phone size. Controller semantics vary; this is not a hardware or safety validation.

## 2026-10-31 — account-file retry and batching

Live release `8789f1b5077fe40f25e19c96fef717510c5df91aff4a3a54457a8194f7ca7237` keeps automatic sync attempts from restarting for each local change after a 429, and batches up to 16 existing-file version checks. Individual writes and deletes retain server-side hash checks. Local unit tests cover 20 edited files and conflict preservation; a local registered-account Files test covers cross-device conflict resolution. Live desktop and emulated-phone tests injected two 429 responses and verified queued files reached the server. The issuer authorization budget is still shared behind the reverse proxy; no 100-user capacity or safe change to that limit is established.

## 2026-10-31 — PDF search occurrences

Live release `c49f945e61f50d41de8e87381a3cad3234a3df819db15105e3cba5c2fbae844d` updates PDF Viewer search to visit individual occurrences, wrap across pages, and highlight text that spans PDF text runs. Local and live registered-account tests passed at desktop and phone-sized viewports for repeated matches, reverse navigation, wraparound, cancellation, literal `+`, selection, resize and invalid-file recovery. The disposable live accounts were removed. The viewer still cannot OCR scanned pages; physical touch is unverified.

## 2026-10-31 — Electronics Design account files

The Simplified desktop is deployed at `https://ksu.codes/`; older statements below that this branch is not deployed are historical. Electronics Design release `8acb38f7676d4105c5c450c99cac59380ecce18239eb237169569bb987ece051` captures current projects directly to My files, checks for unsaved work and stale versions, and keeps editor exports separately until saved. Native Save uses the shared account workflow. A new design created during a save retains its own identity. The upstream GitHub account and history controls are disabled; see `docs/DEFERRED_APP_FEATURES.md`. The integration and its limitations are described in `apps/system/electronics-design/README.md`. Local registered-account workflows passed at desktop, emulated-phone and 4K sizes; a 9 MiB project passed locally. The live registered-account workflow reached its final cleanup before the gateway returned a request-limit error; the disposable account was then removed separately. Standalone part import from My files passed local and live desktop and emulated-phone checks; a local test placed an imported part, saved the design, and reopened the embedded definition. Unused imported parts are temporary. Independent physical-touch tests, broad simulation coverage, and hardware validation remain open. Do not treat this as completing the overall app review.


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

## Browser memory-growth fix — local candidate

Real live desktop and phone-sized checks loaded example.com, Grainger, and
McMaster. Grainger returned its own access-restriction page in both tests;
this was not a local blacklist decision. McMaster rendered on the phone-sized
viewport, while the desktop window failed with `Engine buffer outside WASM
memory`. The live example.com page also displayed missing-glyph boxes for
Arabic and CJK text; the currently packaged fonts do not cover those scripts.

The desktop failure was reproduced twice in an isolated preview. In the two
failures the engine had grown shared WASM memory from 536,870,912 bytes to
644,284,416 bytes, while Emscripten's exported typed-array view remained at
the old length; newly allocated frame pointers were valid in the grown memory
but outside that stale view. The local Browser adapter now holds the imported
`WebAssembly.Memory` and reacquires its views whenever its buffer changes.
A real shared-memory growth unit test passes, as do 93 Browser unit tests.
Two concurrent local desktop Browser windows each reloaded McMaster five times
without the prior error. These are limited examples, not a guarantee that all
websites or physical phones work. Deployment and download regressions remain
in progress; this fix is not yet live.

## Browser memory-growth fix — live

Release `0389a65b0a5bf8da3d0c26e714f6a79e05a0ba37d134c07130e54964248c3042`
is now live from source `ee1704dcd`; only the Browser app bundle changed in
the 38-app catalog. Its matching public source archive is
`/browser-sources/codi-browser-source-ee1704dcd.tar.zst`, SHA-256
`0ef62be5518d9cbd01543efd9bacafc22238ac6b4ca7a00719898753cfbab60a`.
Two fresh public desktop sessions and one phone-sized session each navigated
to McMaster five times without the former memory error; screenshots showed
the rendered site. A live phone-sized clicked-download/save/server-copy test
and isolated desktop/phone cookie-protected download regressions passed.
One of three simultaneous test registrations timed out before creating an
account; the same test registered successfully when rerun separately. Its
cause was not established. All test accounts were removed. Phone tests were
emulated; actual Android input and general website compatibility are not proven.

Grainger returned its own access restriction in the earlier test, and the
current fallback fonts do not cover Arabic or CJK characters. Those issues
are not resolved by the memory fix. Server audit remains disabled. Previous
frontend release is `f3681cd5867e0f779049812f9fc178db90d4c2f8169699a1d66b1fba69d35919`;
hosting snapshots are `change-20261031T035715125933Z` and
`change-20261031T035715126409Z`. Current generator SHA-256 is
`3cf1dca82b180122de30fdf44f9751941423281fdfdc5566418826be22525d0e`,
manifest `23203a7bc06b2743978a130e2d9eddf9af1c4eec54c767366fe701602fbee041`,
and Caddy `c1bd4ec92c21f152bb725ccd9c37128710f594974fa6f4dacaeeab4cff14142a`.

## Browser language-font candidate — local only

The candidate Browser now stages unmodified Noto Arabic and CJK fonts before
Gecko initializes, with SHA-256 integrity checks and bundled SIL OFL notices.
`apps/system/browser/tools/prepare_fonts.py` reproduces the exact font assets
from verified Ubuntu packages or matching installed fonts; the font binaries
are generated inputs, excluded from Git. This adds about 19 MiB per initial
Browser load. The desktop and phone-sized isolated Browser rendered Arabic and
Chinese on example.com rather than missing-glyph boxes; the phone-sized site
compatibility run also visited Grainger and McMaster. Browser offline tests
passed with the project Python environment. This candidate is not yet live;
prepare its corresponding source archive, perform release/hosting activation
and public regression before announcing it. Physical phones and full language
coverage are not verified. The previously documented live release is unchanged.

## Voice and keyboard menu controls — live

Simplified frontend release `affe246ba843cc62a41a77557171e254db33379ea0a24414e381d9b6dbb130e4` serves desktop source `ef070123a`. The microphone overlay starts hidden on desktop and visible on compact/touch layouts. Applications → System Tools → Voice input toggles it; Keyboard lock toggles the on-screen keyboard hint, with status feedback. The overlay contains no keyboard button. Desktop keyboard mode initially permits typing; the previous voice-mode default remains on compact screens. Desktop and emulated phone-sized tests passed both locally and on the public site; two disposable public accounts were removed. No physical-phone test was performed. All 5,462 release files passed hash verification before activation. This release retains the previously live Browser bundle: the font candidate above remains local only.

Hosting generator remains `3cf1dca82b180122de30fdf44f9751941423281fdfdc5566418826be22525d0e`; manifest `d05ef60376f13a66485f96a6822ca35d19b9a1d4b08ccfca51a44a15548b08a8`; Caddy `44be733ea39f778de37eb32ecb5c03735b4607dea6e5ed843087c5f684353001`. Previous release is `0389a65b0a5bf8da3d0c26e714f6a79e05a0ba37d134c07130e54964248c3042`; hosting backups `change-20261031T040729846308Z` and `change-20261031T040729846712Z`.

## Browser Arabic and CJK fonts — live

Simplified release `d20562ff8056d481ae9e7aadc4c5738a961179d01c51855be2e2afa388472be0` now serves Browser bundle `72d5f07565f4b0118deb99e722089d3de58bc6e9c6acbc6cbbd981c74848adb6` with verified Noto Arabic and CJK fonts. The runtime fetches and validates them only when Browser starts; they add approximately 19 MiB to the first load. Desktop and isolated phone-sized live example.com checks displayed readable Arabic and Chinese; a live phone-sized clicked download saved to My files and its server copy. The website compatibility run also visited Grainger and McMaster, but individual website compatibility is not guaranteed. Four disposable registered test accounts were removed. Phone testing was emulated, not physical. All 5,466 release assets passed checksum verification before activation. No backend or Browser relay policy changed.

The exact Browser source snapshot is published and indexed as `/browser-sources/codi-browser-source-f70a64aa3.tar.zst`, SHA-256 `1772fa4cc0e5ec205a163b9e6467ba18ffabf782e6c3a38f62316e9ad84f520d`. The host source-allowlist transition passed rollback exercise and all ten site health checks. The new source index SHA-256 is `ec1a78e44a50090d1f1eb98f02a5d59985fa7541537793f044bb0b757721c888`, notice-manifest SHA-256 `9a32b0901ea603c82bba5da24e598d4bf14b3f2eb7f00432bb7b8c2a7e66500a`. Generator SHA-256 `fef25364c7c5c2796e105c5379401c5681e45d5792448f317973619bbc49da7a`, hosting manifest `18a32de48f45a2584c334d37188a0d1dbe8351a4385c3ce1195e12dbfbd4722b`, Caddy `637f68109e7324fb8aad44b2cbe2adfa0d56d27a73f4e0e2fad8a66a85255aca`. Previous frontend `affe246ba843cc62a41a77557171e254db33379ea0a24414e381d9b6dbb130e4`; hosting backups `change-20261031T041104276143Z` and `change-20261031T041104276554Z`. The linked-component license inventory remains qualified as documented in Browser source provision.

## Live report administrator interface check

A disposable registered account was temporarily added to the report administrator list by `tests/live-browser-report-admin-guard.py`, whose root-only journal stores the exact original administrator configuration and allows guarded restoration. A fresh live desktop Browser recorded example.com locally, used the real administrator UI to request a report, and displayed its signed domain total. The guard removed requests belonging only to that account, restored the exact original administrator list, restarted the relay, and left no pending journal; the test account was removed. The first attempt encountered a transient 502 because the service reported active before its Unix socket accepted connections; the test guard now waits for actual socket readiness. This test did not use the real administrator's credentials and did not establish physical-phone behavior. Server-side traffic audit remains separately disabled.

## Beta Help text — live

Help now states that this is a beta service and links to `dflanag3@students.kennesaw.edu`; it retains the explanation that Linux terminal files are temporary and separate from account files. The former Files/Text Editor guidance was removed. Release `c1acaebb41326ea77d0ea0e7beaae01213454d1ab72c5aa62d3bc840717fccc0` contains Help source `9bd6227cd`; desktop and phone-sized live Help checks passed, and their disposable accounts were removed. Previous release `d20562ff8056d481ae9e7aadc4c5738a961179d01c51855be2e2afa388472be0`; hosting backups `change-20261031T041836425960Z` and `change-20261031T041836426399Z`. Generator SHA-256 `fef25364c7c5c2796e105c5379401c5681e45d5792448f317973619bbc49da7a`, manifest `c4c6246aba67b0f44adedb6d556a4ba136c9acd1d079185ae0b978c159ebbb6a`, Caddy `7c373d279c7f5f35ab099ed7ec9bcae94b2fd793726c996b4a4b3968a73b9c28`.

## Browser relay recovery message — live

Simplified release `6f94f5df3bcd9ca43cbbdd65544080e357e40d4489ec7ecb2b2f35d081157086` includes Browser relay client source `808fac040`. HTTP 502, 503 and 504 now say the Browser network is temporarily unavailable and instruct users to select Reset engine; ordinary policy denials retain their own messages. Local simulated-outage and real live tests passed: the live relay was intentionally stopped, a registered Browser displayed the message, the relay was started, and Reset engine reconnected. The test account was removed and relay health was verified. The source archive `/browser-sources/codi-browser-source-808fac040.tar.zst`, SHA-256 `8a5d4ee98efd14272379a54665dce2c3a21fd92aff4871281ab2ff674b4a4249`, is publicly indexed; source-route rollback was exercised and ten sites were checked. Before activation all 5,466 release assets were verified. Generator SHA-256 `1e3ca517ece6a2c9617f8a4728d24bf7605dbc805de23a2e2912e833c7a189ef`, hosting manifest `e0a7c48bec1a5495742514d5120f5ebcb6432fef91265f9df8cea55f97329a4a`, Caddy `48f77ec2a65f828c0eaea9d23d46df0087816396e6bf094babf6c73c38d571a7`; source-index SHA-256 `9831f53993bab0c241f2bc55506dbc225c44ca2ed2e21c4fa73e820529d076b9`, notice manifest `da1d21e5942c15408e34e7ed00f79009681714c88dc49ab035c894128fb35000`. Prior frontend `c1acaebb41326ea77d0ea0e7beaae01213454d1ab72c5aa62d3bc840717fccc0`; hosting snapshots `change-20261031T042054042156Z` and `change-20261031T042054042570Z`.

## Browser svg_fmt notice evidence

The previously unavailable `svg_fmt 0.4.1` package VCS revision remains unavailable, but the vendored crate's three Rust files and README match upstream `nical/rust_debug` commit `492600cac47f64bcadaf9ad037ed64c5fecc8e63` byte for byte; the original Cargo manifest differs only in version 0.4.0 versus 0.4.1, with the same author, repository and MIT/Apache-2.0 declaration. `apps/system/browser/tools/audit_svg_fmt.py` verifies the pinned lock checksum, vendored hashes and source comparison. The historical tree's MIT LICENSE was appended to the public combined notices with an explicit source-match qualification. The matching upstream collection and preparation scripts were updated; all 84 JS and 33 Python Browser offline checks pass. Public notice SHA-256 is `c2717cef7dd3d8485cd4ddfa39101b4ae893353cd63240d0078085b47bc9b05c`, and notice-manifest SHA-256 is `6fc94a25b454dccff8eb9af32f03eb15f6a376d60f8bad486ae8462689ee03e7`. The remaining uncertain Rust and final-link license inventory is not claimed resolved. Frontend and relay releases were unchanged.

## Browser enum-map notices

The exact `enum-map 2.7.3` Codeberg revision contains MIT and Apache-2.0 texts under `LICENSES/`, which the earlier GitHub-only upstream scan did not collect. The live combined Browser notice now includes both exact hash-checked texts and the distinct SPDX copyright lines from the Firefox-vendored crate; the MIT text itself uses placeholder copyright fields. `collect_enum_map_notices.py` reproduces the input from the pinned Firefox checkout and upstream revision. `prepare_notices.py` now requires it and includes the two newer Browser source archives in its generated index. The full combined notice was rebuilt from pinned inputs and matched the public file byte for byte; the notice test and 84 JS/33 Python Browser offline checks passed. Public combined notice SHA-256 `fbca71d13f022e85945e762d7cb5a9d9939ac7b25cbf803b0b1a24759b5d8329`, notice-manifest `2bbc58cc430284b074c112c8cf758c20f18390981500b79857dcf8eb17274916`. Other license and final-link uncertainties remain.

## Browser HTML import size — live

The Browser's former 2 MiB HTML file cap conflicted with the desktop's 128 MiB file limit. Browser source `1573b1ffc` now accepts HTML up to 128 MiB, passes input as a transferable byte buffer instead of converting and copying a large JavaScript string, and bounds the temporary per-window imported-page history at 256 MiB. It preserves imported page files for back/forward navigation until that budget is reached or the engine is reset. The existing My files mirror returns independent bytes; a partial view is copied before transfer to avoid detaching unrelated data. Large HTML still requires substantial device memory.

Live frontend `3b1012207d7b545be3c90a7ea3c85962ebf51cff5f326621e155196ae8ce95be` serves Browser bundle `09a8794331c71e52b5fd483ee0bd6dcb3e19753f844161ae3a6ba7838d0ae29e`. Actual local and live Gecko tests rendered a 128 MiB uploaded document, rejected 128 MiB plus one byte, and opened a 3 MiB file through My files; the account copy was still readable afterward. Live test data/account were removed. The Browser suite passed 85 JavaScript and 33 Python tests. Physical mobile behavior at 128 MiB has not been tested. Source snapshot `/browser-sources/codi-browser-source-1573b1ffc.tar.zst`, SHA-256 `4f376d5619d916adf902c7818bc2f8a577c2849a830db27790aa045d00f3f4a5`, is published and indexed; source route rollback was exercised and ten sites checked. All 5,466 release files were hash-verified before activation. Prior frontend is `6f94f5df3bcd9ca43cbbdd65544080e357e40d4489ec7ecb2b2f35d081157086`; hosting backups `change-20261031T043007806754Z` and `change-20261031T043007807176Z`. Current generator `f01b3fb88a37f15e130ce18a4afeabf785a59c3d76512ea558e344442aeb4dc6`, manifest `dce410e29dcc54ba74c945fa31ea289f08cf4a7605ffc1e6d9e2c6b43a9da0db`, Caddy `622280712346df6e8935f8d7bb0279ff214fda8eba0cf05ade8aefe14675dd8c`; source-index `7a63f2c2eb18b6bca3509aaf7a13059a7346b6cc492a2edfb04a814cbb1db5f7`, notice-manifest `e38ef23ff040349dca5170d5b994c74d47d32ef6cc9be234b49e863a388bd020`.

## Browser URL download memory — live

Simplified frontend `7b5c760dc28cf7fb58fe4d735a45a80810d8bd765483c779c976d65c546fd68f` uses relay-client source `b6b5d43e2`. For the relay's normal Content-Length response the Browser allocates one bounded destination buffer and writes incoming chunks into it, avoiding the previous retained-chunks plus second full-size buffer. Missing Content-Length still uses a bounded chunk fallback. It rejects invalid, oversized, shorter or longer responses and cancels a stream on error. This is a client-side memory improvement; the server continues its existing chunked response and private temporary-file fetch. Unit tests covered chunk boundaries, bad and missing lengths, cancellation, and an exact 128 MiB generated stream. Actual live desktop and phone-sized UI tests fetched example.com through the authenticated relay, saved it to My files, verified the server copy and removed the test files/accounts. A live 128 MiB remote URL transfer and a physical phone were not tested. Existing direct signed relay, public destination, blacklist and private-address checks also passed with the candidate source.

The exact source archive `/browser-sources/codi-browser-source-b6b5d43e2.tar.zst`, SHA-256 `574d6652461794e99cb746e90da5c50b168283e5e12b6cf2ab27f5851a9cb999`, is indexed and publicly verified; the source-route rollback exercise passed all ten site checks. All 5,466 static release files were hash-verified. Current generator SHA-256 `54530be6de2bde410ddfd3fb7930c0fff25b4bd2b926150cf5ebc9cdc2db2f74`, manifest `793c2f272ed5e1c4a3cdc237cc0b82b60b6e25ede6103a29a7678da3bcffe878`, Caddy `8f5c681627db9c12ac9b8821c12d649df15c67b557567fc872cf7a396bca21c6`, source-index `fc0511bd255a3f41f6273398b0d6e3fc85e7492a50d8b41ce2bb6580661b8476`, notice-manifest `79ccef204c0ffee3515bc3a6c631ffe68616fdf0219877625bf831db30ec2e45`. Previous frontend `3b1012207d7b545be3c90a7ea3c85962ebf51cff5f326621e155196ae8ce95be`; hosting snapshots `change-20261031T043257793819Z` and `change-20261031T043257794241Z`.

## Live 128 MiB remote download and clear size error

A temporary sparse fixture served from i36's public Ethernet address through a temporary `104-180-210-36.nip.io` Caddy route exercised the real signed Browser relay and account file service. A file of exactly 128 MiB reached My files and synchronized; browser and server SHA-256 both matched `254bcc3fc4f27172636df4bf32de9f107f620d559b20d760197e452b97453917`. A 128 MiB + 1 byte file was rejected, but initially gave only a generic network-policy error. The new typed size exception returns HTTP 413 with the bounded message `Download is larger than 128 MiB.`; other denial details remain generic. Local audit HTTP tests, 85 Browser JS/33 Python tests and 32 authorization checks passed. After deployment the live end-to-end 128 MiB, checksum, deletion and explicit over-limit-message checks all passed again. Disposable accounts and fixtures were removed; i36's original Caddy configuration was restored and its IP-echo endpoint checked. i34 and i35 were unreachable during this test; i36 remained online.

Relay runtime `7a046ff7b5f37d64cd8c921a9e429c268a8b99c121df4417d0cde020764763eb` from `1f6f3c159` is active; the guarded upgrade was rollback-exercised, with prior unit at `/var/backups/codi-browser-relay-before-size-runtime.service`. Audit and policy operator pins were updated to audit operator `0c1195dca65652181c0a32d4e6932e95de8903a97d0999f09b71105a73b9f19b` and policy operator `policy-ccb023f08`; both commands passed live status/read checks and audit remains disabled. The registered relay, HTTPS download, blacklist, private addresses and file-gateway regression passed on the new runtime. Source archive `/browser-sources/codi-browser-source-1f6f3c159.tar.zst` SHA-256 `e9dd5610d383abc8619c989b69dd3e0b470c1f403bbc5f3455fd97b4608c8fb9` is published and indexed after a source-route rollback exercise. Current host generator `8423607ec727d587a2140ca9e0157c982f1b38837496ffa48bdfb6c314444a45`, manifest `793c2f272ed5e1c4a3cdc237cc0b82b60b6e25ede6103a29a7678da3bcffe878`, Caddy `c3de6b467defabc6530ce349023ceba4fd1194d5aee02840d5bc2f6139d38d1d`, source index `b82a6f1c5c5e104a2d873a0836d9d4b3e46a6f281e4fa8078611135f7161fffe`, notice manifest `d90b13a3239ca8da1dbd3450d14f02ff177a9b7e90949751db8947b14f238616`. The website frontend remained `7b5c760dc28cf7fb58fe4d735a45a80810d8bd765483c779c976d65c546fd68f`.

## Slow Browser URL transfers — live, Moonpie tested

A prior server total timeout of 60 seconds and client timeout of 65 seconds could terminate valid downloads on slow links. Relay source `9fe78a273` now allows up to 30 minutes for each upstream fetch, with a 10-second connection timeout, 60-second read-idle timeout, 128 MiB limit, renewed account lease checks, unchanged destination policy and existing per-user/global connection limits. The browser's full request timeout is 35 minutes. Closing the Browser or losing its relay authorization aborts in-flight URL download fetches; an actual local desktop test confirmed close-triggered cancellation. Browser local tests passed 85 JS/34 Python checks plus stream and relay tests.

A fresh headless Chromium session on Moonpie (`maint@100.105.243.29`, pinned SSH host key, separate public network) loaded the live Browser. An i36 temporary fixture streamed 71 KiB over 70.8 seconds, beyond both old cutoffs. The UI saved it to My files; browser and server hashes matched, then the file and disposable account were deleted. i36's temporary Caddy route/service and Moonpie's isolated browser processes were stopped; i36's original Caddy route was restored and its endpoint verified. The Moonpie machine has roughly 2 GiB RAM; the Browser process peaked around 1.5 GiB during startup, so very low-memory devices remain a real limitation. This was one slow URL test, not a 30-minute or physical-phone qualification.

Live frontend `c53ab4c92df70ccba190b66dcaeb79472ab091e8a285df5dfb585291c1b5d118`; relay runtime `edfd7db342c856c66bf8a19fa50593aa3c08a7498be584d8fca34b86421b71ca`. The relay runtime upgrade and rollback were exercised; old unit backup `/var/backups/codi-browser-relay-before-slow-runtime.service`. Audit operator `d6d78b9eaf47258358511b562d70750936b82e2ff7d14145123f5a6e3c6ec49d` and policy operator `policy-a80a78e35` were repointed and live status/read checks passed. Server audit remains off. Signed relay, blacklist, private address denial and account-file regression passed on the live runtime. Browser source archive `/browser-sources/codi-browser-source-9fe78a273.tar.zst`, SHA-256 `eb1405b13bc172920170259ee87e59594b977ea2498fa3daa08ec705b2fa627f`, was indexed after the source-route rollback exercise; ten sites were checked and 5,466 release files were hash-verified. Previous frontend `7b5c760dc28cf7fb58fe4d735a45a80810d8bd765483c779c976d65c546fd68f`; hosting snapshots `change-20261031T044505798587Z` and `change-20261031T044505798999Z`. Generator `22e8ceb89f38aecb62f153311e31be13bc62f07bebdf4d0d420e5add661b8cfd`, manifest `9bf90f3a73822963631ae6257f70bc84474257d6304392dfb552111d156bad7e`, Caddy `efcbe83711309a91bc26381b500d8f411bf67ecc72c85d3069bff95fec5592a8`, source-index `d5ccdfbda943a016b40aa9603c41d0b3f69213468ab06a8969d4d634a52520c3`, notice-manifest `e08a14c3d19486f5335fd4f404c4927173d844a496617425dc67c9d53f205e55`.

## Moonpie Browser memory experiment

On Moonpie (about 2 GiB RAM), the live Gecko glue prestarts 20 pthread workers and imports a WebAssembly memory whose binary minimum is 8,192 pages (512 MiB). A temporary isolated candidate changed only the generated glue's prestarted worker count from 20 to 8; Emscripten's non-strict pool can grow on demand. With fresh headless Chromium runs on the same machine, the largest Chrome process at Browser readiness was approximately 1,463 MiB RSS for the live 20-worker build versus 1,472 MiB for the 8-worker candidate; after loading example.com the respective largest-process samples were approximately 1,081 and 1,100 MiB. These are individual RSS snapshots, not peaks or unique-process/PSS totals, and the live and isolated candidates used different origins and cache state; this does not establish a statistically meaningful difference. The smaller pool did not show a useful memory improvement and was not deployed. Chromium emitted D-Bus service-enumeration warnings in both headless runs; both Browser windows reached ready and navigated. Disposable accounts and candidate files/processes were removed. The minimum 512 MiB imported memory is encoded in the existing WASM module; lowering it would require a different engine build and qualification, not merely changing a runtime option.

## Lower Gecko initial-memory experiment

A separate r730 build linked the existing Gecko engine with 256 MiB instead of 512 MiB initial WebAssembly memory and passed local real-worker 128 MiB HTML, over-limit, My files, signed relay/download and five-navigation McMaster checks. Moonpie started it and loaded a page. The candidate grew to about 455 MiB WebAssembly memory by the first native sample; both the 256 and 512 MiB engines grew to about 2 GiB of WebAssembly address space in the artificial 128 MiB HTML test. These buffer sizes are not RSS. One Moonpie largest-process RSS snapshot was lower at startup for the candidate but similar after loading a page; differing origins/cache and single samples make that inconclusive. No engine was deployed. The first build attempt failed due to Node missing from PATH; the isolated retry succeeded. Reproduction details, hashes, and limitations are in `apps/system/browser/docs/MEMORY_EXPERIMENT.md`. Temporary candidate builds were removed; the original engine source and live release were not changed.
### Browser relay IPv6 transition-address protection — 2026-10-31 UTC

Relay runtime `d022d596bb2ab2d0fca8c4633b552f75b03b7483f72703886162c582ff646353`
from source `3a82d4665221beeb2745f16674479f82b1602d84` is active. Its
address validator rejects IPv4-mapped IPv6, well-known and local-use NAT64,
6to4 and Teredo ranges to prevent encoded destinations evading IPv4 rules.
Ordinary public IPv6 remains accepted. A network-specific NAT64 prefix cannot
be identified automatically and requires a separate network rule. Unit tests
and a real local Wisp session covered denial; the installed policy was checked
directly on box-webhost. The live registered-account test passed signed relay,
public download, blacklist, private-address denials, Wisp, file write/read/
delete and fresh-context sign-in; the disposable account was removed. This
does not claim a live end-to-end DNS translation test.

The guarded upgrade and rollback were exercised; old unit backup is
`/var/backups/codi-browser-relay-before-transition-runtime.service`. The
active unit SHA-256 is `4b1efe74f85f08cc97e3e50033bcc6cbb6dfa1ba49ac8ac125c9a88279ae10f6`.
Audit operator `7849f5502227f8a62b93d486ee8ba9cc1ef99fa934c878b42329604813ded935`
and policy operator `policy-17d95b771` now point to the new runtime. Audit
status confirms disabled, matching service, no key or ledger; both access
lists remain empty. The previous public Browser source archive predates this
relay-only patch; update the source index before treating distribution
provisions for the new source as fully reviewed.

The update is now published: `/browser-sources/codi-browser-source-3a82d4665.tar.zst`
has SHA-256 `e908debde58ac8280f4768593c73ba7099bf6bde3ca9365017a4b83aa2e1db39`.
An HTTPS download was hash-checked, and the archived relay policy matches the
deployed source commit. The managed hosting route rollback exercise passed;
the ten site checks were unchanged. Current generator SHA-256 is
`028554374cda0aebfb0c399ab9c473e88b45f69670dc03d06aeb8e081be3431c`,
manifest `9bf90f3a73822963631ae6257f70bc84474257d6304392dfb552111d156bad7e`,
Caddy `329297a7963bca9e9b8ed3d6635c1a915c959a01881aeef88175f8a5d67453c3`,
source index `64e06a7aed14a64f0a56d4e4f2e8dfc4eb98932c0aaf03204d5a9f4490227edd`,
and notice manifest `6285a85f3f8213064f38bb85c859f357e1586b17fdab634f281a859cd5ba15f4`.
The prior index is backed up at `/var/lib/codi-ingress/browser-source-index-3a82-backup.json`.
The previously documented uncertainty about the exact final-link license
inventory remains; publication of this source snapshot does not resolve it.

### Signed-in Browser source access — 2026-10-31 UTC

The public `/browser-sources` path and its files now return 401 with a sign-in
instruction. Signed-in users open Browser and choose **Licenses & source**;
the link uses the Browser relay's short-lived, registered-account lease and
path-scoped HttpOnly cookie. Closing Browser or losing that lease can end source
access; reopen Browser to obtain a new link. Public source paths are no longer
usable for unauthenticated automation or as permanent distribution links.
The protected source index and range download passed with a real disposable
account; missing cookies, unlisted files, and an anonymous lease are rejected.
The live UI test opened the link and verified the index. The test account was
removed. Source recipients still have access to notices and source; the wider
licensing inventory remains under review.

Frontend `c538220f32e70e55616f423e10d8e51af9bbf95b82d3bd510d64a29706feef03`,
Browser bundle `27c53dde04fd16189bcea2e8e56fa38881a1cd0cde2e6e09945dac8febf1f49a`,
and relay `953a58dc68dde9f1c988fa18857ea344347508f7e07e6c508eb256245e20764a`
are active. The relay rollback was exercised; the previous unit is at
`/var/backups/codi-browser-relay-before-source-auth-runtime.service`. Audit is
disabled, and audit operator `d4919a4b70b077b93037e1a4a4020d5a9c2056f653410ff2d8ab7fea54cb3aa6`
and policy operator `policy-8874c0118` point to the new relay. Hosting generator
SHA-256 `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `6945436b3856931831a757768c6a02d5222eb8d111136a95e4ce7556826ce65e`,
and Caddy `b28129f67e7a0c2ee50719bd1f87df300ce00248c856627f33a951348fa76731`.
Hosting rollback inputs are `/var/backups/webhost-sites/change-20261031T051342536271Z`
and `/var/backups/webhost-sites/change-20261031T051342536750Z`.

The first frontend staging run left the new app bundle directory mode 0700,
causing a 403 until corrected to public-readable modes. The staging script now
normalizes the copied bundle's permissions. A fresh public test after correction
passed; the exact reported module URL with `?retry=14` returned 200. Old tabs
that cached the failure may need a page refresh. Source-only scripts and tests
are backed up separately; unrelated guest SSH work remains untouched.

The authenticated index now includes `codi-browser-source-ed78ff4b3.tar.zst`,
SHA-256 `0b6f94ae5573bb80d430085cdad66bb3720fdb63d8e5883166412f5219b34139`,
covering the deployed protected-source implementation. The Firefox notice's
old absolute public link now points back to the protected index. A fresh real
registered-session test verified the UI, index, notice link, both source range
downloads and refusal without the session. Current source index SHA-256 is
`81955daf2abf8e4ce82743b5278d40862afd75bea462b251a9b5f720d5f1e614`,
Firefox notice `863ab7630592181f9c16be9f509cbc0b859c56124af4711d8a519c6b4c79fa0e`,
and notice manifest `b149d4c620611e8284a0920c5cc85ea69ce28a61bb3ac0e5ea0a2233c7c391dd`.
The prior files are backed up at `/var/lib/codi-ingress/browser-source-index-ed78-backup.json`.

The link input list and generated unified source identify Firefox's bundled
Content Analysis SDK. Its exact pinned license was added to the authenticated
combined notice; the registered live test reads it. Combined notice SHA-256
`ee553fd12a0e8ef825cae8661f19c86c6f15e83dbf0592caf8b5c249eeab7c01`,
notice manifest `1230180107f7157ba7b2be53d883c5a334d5057506d5e75019eaacb671c8e3a3`.
The previous files are at `/var/lib/codi-ingress/browser-content-sdk-notice-backup.json`.
The wider final-link license inventory remains incomplete.

A fresh live desktop site check rendered the example.com reference page and
the McMaster-Carr catalog. Grainger displayed its own “Access is temporarily
restricted” page; the reason for that site's response is not established.
The script checks engine failure status and saves screenshots for inspection;
it does not automatically establish that arbitrary sites are usable. The
disposable account was removed. `apps/system/browser/docs/TEST_STATUS.md`
now distinguishes current live evidence from its original source-only report.

The Browser's persistent “Navigation requested” message confirms only that
the engine accepted the command. The native control interface exposes the URL
and history state but no verified load-completion or HTTP-status signal. Avoid
turning this into a “loaded successfully” claim based solely on a changed URL
or painted frame; improving it requires an engine progress interface and
qualification of the resulting engine build.

An isolated native candidate compiled and linked with
`nsIWebProgress::GetIsLoadingDocument` exposed in the status JSON. In a real
local Gecko/Wisp fixture, the HTTP server confirmed receiving a request and
held its response for eight seconds; one-second status samples remained
`loading: false`. This candidate did not meet the intended loading-state test
and was not deployed. Its experimental WASM SHA-256 was
`3c3328968f0408977666e39f9f11fb3d46975c871ed400ce2dcd530a95e9665c`;
the live engine remains unchanged. Investigate a progress listener or another
authoritative signal before presenting a completion status. The first fixture
attempt also used a directory URL that the test server refused; it was rerun
against `/demo/index.html` before making the observation above.

A follow-up debug progress-listener candidate observed a stop event associated
with a delayed successful request after the response, and a nonzero result for
a blocked request. An HTTP 404 returned a zero Gecko network result, confirming
that network completion is not HTTP success. Rapid start/stop events also
occurred between status polls. It remains unshipped; source patch, test scope,
privacy caveat and remaining work are in `apps/system/browser/experiments/`.

The subsequent unshipped HTTP-channel candidate distinguished local 200,
404 and a redirect to 404; a zero Gecko network result alone still does not
mean HTTP success. A ten-second delayed-response fixture also demonstrated that
the **shipping** engine's Stop button remained queued after four seconds. Its
native `xul_load` spins until an interactive document while the worker serializes
commands, so cancellation needs a coordinated worker/native solution. The
prototype and remaining security, lifecycle and navigation tests are documented
in `apps/system/browser/experiments/`. Live source and engine are unchanged.

An isolated Stop prototype adds a matched worker/mailbox atomic signal and a
native event-loop check. Three delayed-response runs completed Stop in 68–85 ms;
immediate Stop and later navigation passed, and a two-window fixture showed
the other window remained usable. The three source patches and reproducible
local-only tests are retained, but the prototype is not deployed: ABI pairing,
build/source integration, idle-event-loop, overlapping-command, lifecycle,
phone and failure tests remain. The live Stop limitation still applies.

The pinned live WASM's name subsection has 367,777 named functions; a
reproducible scan found references to `svg_fmt::`, `seahash::`, `app_units::`
and `content_analysis::sdk::`. These may be type references, not a complete
component inventory. Exact Firefox-vendored SeaHash 4.1.0 package metadata,
which declares MIT and lists its authors, was added to the authenticated
combined notice; its exact upstream release has no separate license file.
The live registered-account test read the addition. Combined notice SHA-256
`3f2781508e089b26b8c9af60f0820bd8085aaa9bb9d77d4c21aef852266c519a`,
notice manifest `6a30ebc4b64a65acb01ca5345f677567d2da5769954110cca73ff237fb27f6e6`;
prior files are at `/var/lib/codi-ingress/browser-seahash-metadata-notice-backup.json`.

### Browser rule changes during connection setup — 2026-10-31 UTC

Relay `af8d81daf6fdda84d9b563ce6885f862a4d68c0a55bea194d0c9360c47b1092e`
from source `933db11eaef2b2d1a75630ee13af3f81888b4738` is live. It rechecks
current domain and network rules after DNS, immediately before Wisp connection
attempts, and after a connection completes; if blocked after connecting it
closes the socket before forwarding Wisp payload. Explicit downloads recheck
after DNS and before processing a response. Requests or TCP attempts already
sent cannot be retracted. Deterministic local tests cover rules changing while
DNS or a Wisp connect waits. The live registered-account suite passed, including
source access, outbound policy changes stopping an existing stream, denial of a
new stream, and access after restoration. Its first policy test attempt could
not start because the temporary guard had been cleaned up; the guard was
restored for the successful rerun, the test rule restored, its scheduled
timer stopped, and the guard removed. Audit remains disabled. The protected
source index still needs the new `933db11ea` source snapshot.

That snapshot is now listed on the authenticated source page as
`codi-browser-source-933db11ea.tar.zst`, SHA-256
`86a7231825d85de9199d5117ffe12d4f18f941161f75ad7351f4df00d0169836`.
A registered live session downloaded the complete file and verified its hash;
the test account was removed. The source index and manifest were regenerated
from the pinned notice inputs and now match the generator byte for byte.
Index SHA-256 `5aece1521b25cc96606d7805b0fd9836f37e55f043f1459aae7386c0b279d939`;
manifest `1cd10b58626614a584ebdc74e539ac7653fac56e1953c00a36a424bdd822a500`.
The prior files are at `/var/lib/codi-ingress/browser-source-reproducible-index-backup.json`.

Relay rollback was exercised; previous unit is
`/var/backups/codi-browser-relay-before-rule-race-runtime.service`. Current
audit operator is `c98a0663a48f646a6c4e88b78939b0021ac53e05674547d966e734be9f36bf2c`;
policy operator is `policy-9915463c7`. No unrelated guest SSH work was touched.

The live Browser **Download URL** workflow was rechecked after the relay
update in desktop and emulated phone-sized Chrome layouts. Each test saved an
HTML file to My files, synchronized it to the server, then signed in as the
same disposable user in a fresh browser context and recovered identical
contents. Both test files and accounts were removed. The second context is
separate browser storage on the same computer; this is not a physical-phone or
separate-network result. `tests/browser-live-url-download.test.mjs` now covers
this recovery and attempts scoped file cleanup even if its later checks fail.


### Integrated Browser Stop candidate — 2026-10-31 UTC

The responsive Stop prototype is now integrated into the pinned engine patch
and paired with the worker using `browser-gecko-mailbox-v2`; its source is
backed up at `6bd03a679`. A separate, locally staged engine build from the
pinned sources has WASM SHA-256
`23b02f87791ad87208faf3680c5269ce0a7dc77c7bf33c7f88986e52d2ea5e2b`.
Tests against that actual engine stopped a delayed load in 68 ms, navigated
again, handled immediate Stop, and preserved a second Browser window. A
phone-sized emulated viewport also passed Stop and close/reopen during a slow
load. Nine patch tests and 62 mailbox/policy tests passed. A completely stalled
Gecko event loop and a physical phone have not been verified. The candidate is
not live: the corresponding source provision and further release checks remain.
The live Browser remains on ABI v1; do not mix its engine with the v2 worker.

The integrated Stop candidate is now live at release
`8d5fe713698d4bb94781b10ef22c4815e48b1d046237730e23259945d2332f05`,
Browser bundle `a84f7a0611eb8cdec8406738a8b1afabe493ff9b20c94b6455642d6f9ba5a4eb`.
Its corresponding v2 source archive is listed on the authenticated source
page, SHA-256 `736e7a6694e50ab66d8fe77da9a666685a6753b7613a5b9cbac4e72ff90ca171`.
A registered live test downloaded and verified it; unauthenticated source
access returned 401. A separately packaged bundle stopped a 10-second fixture
response in 67 ms and accepted subsequent navigation. Live registered desktop
and emulated phone-sized sessions rendered example.com; the phone-sized
session's Stop control returned, and both tests exercised signed relay,
blocklist, private-address denial and signed file-gateway operations. The
screenshots were visually inspected. Test accounts were removed. Physical
phone behavior and a live slow-response Stop test were not checked. The status
still says “Navigation requested.” after successful rendering; accurate page
completion/error reporting remains unfinished, as does the complete engine
license and final-link inventory review. Hosting generator SHA-256
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `15384f69c1f69e4deacbb7b959fce2fda2ff2fbe245ff16004b937e0b59de90f`,
Caddy `75d50e4c780724f95d425350db300c6c171866a5e2f41cdc738a72b4740c4ba1`.
Hosting backups are `/var/backups/webhost-sites/change-20261031T060217965059Z`
and `/var/backups/webhost-sites/change-20261031T060217965535Z`; prior release
is `c538220f32e70e55616f423e10d8e51af9bbf95b82d3bd510d64a29706feef03`.

After activation, the Browser Download URL workflow also passed in separate
live desktop and emulated phone-sized sessions: each saved to My files,
synchronized the server copy and recovered it after signing into a fresh
browser context. Both test files and accounts were removed. Temporary build
copies on the workstation, r730 and box-webhost were removed; live assets,
source archives, rollback backups, screenshots and unrelated work remain.

### Browser navigation-status investigation — 2026-10-31 UTC

An isolated diagnostic engine tested page completion, HTTP errors, redirects,
Stop, a blocked host and a deliberately closed TLS connection. The network
result alone cannot distinguish 404 from 200, or the tested block from TLS
failure. A script redirect also produced an intermediate cancellation result,
and successful start and stop events used different request identifiers.
The findings and reproducible loopback-only fixture are in
`apps/system/browser/experiments/README.md`; no diagnostic code is live.
Accurate, race-safe navigation status remains outstanding. The first TLS test
fixture hung on a TLS handshake; the corrected fixture explicitly closes it,
and the full asserted test passed. Unrelated guest SSH work remains untouched.

### Browser navigation feedback — 2026-10-31 UTC

Release `1ce5edb5bb8312f9cf3ab6a793f809549b38628a28b7440b42058359e4e68117`
is live with Browser bundle
`88b0f26a45dffa7c2c6fe385059aad3fe6450eb52894de7ded40184bbc45d3e4`
and engine ABI v3. Gecko's top-level network events now report completed
loads, HTTP 4xx/5xx and generic connection failures; policy-block notices are
preserved separately. Redirect cancellation is not treated as an error, and
older Wisp stream notices are tagged to avoid replacing a newer navigation's
status. The native wait also exits after a verified non-cancellation network
failure, allowing later requests instead of waiting indefinitely for an
internal error page. These are not guarantees for every website or race.

Local real-engine tests covered HTTP 200/404, HTTP and scripted redirects,
stalled-load Stop, a blocked destination, TLS failure, later recovery,
overlapping navigation/Stop, a second independent window, and an emulated
phone-sized viewport. An initial test found the listener attached too early;
that ordering was fixed. A subsequent test found blocked loads could keep the
native command waiting; the failure exit fixed the tested case. The packaged
bundle passed the same navigation suite. Ten patch and 89 JS tests passed.
Live registered desktop and emulated phone-sized sessions rendered example.com;
the phone-sized session reported a real 404 and Stop. Both live layouts saved
a Browser download to My files, synchronized it and recovered it in a fresh
browser context. Test accounts and files were removed. Physical phone behavior
has not been checked. Source snapshot
`codi-browser-source-ac6ea5798-v3.tar.zst`, SHA-256
`318ef4997e96e9f862ecf53bfa9c61e8c7dac2fb507fc71004bf36dd23c86d92`,
is available on the authenticated source page and was downloaded and checked
by the live registered test. Direct unauthenticated access returns 401.

Previous release `8d5fe713698d4bb94781b10ef22c4815e48b1d046237730e23259945d2332f05`;
hosting rollback inputs `/var/backups/webhost-sites/change-20261031T061922276453Z`
and `/var/backups/webhost-sites/change-20261031T061922276862Z`. Current hosting
generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `4765ea3e77b329afb91aa9f03ea569aa2430e3ad4f8c4088c898aead325a8f7f`,
Caddy `8b8602566e96063bd0e22c623333153d75e62e853ab9cdb41e155c522e856cc0`.
The complete engine final-link/license inventory remains unresolved.

Temporary local, r730 and webhost build inputs for this release were removed;
live assets, source archives, rollback backups and unrelated work remain.

### Browser Rust metadata and live WASM review — 2026-10-31 UTC

The authenticated combined notice now includes exact package metadata from
Firefox's pinned sources for app_units, core_maths, debug_tree and void, whose
releases lack separate project license files. Metadata identifies declared
licenses and listed authors without inventing copyright statements. The live
registered-session test checked the added entries and the complete notice hash
`04dd62fdc18dc6b94bfa439f55b4103de6bb34394b53e8e6167264dd8d2b8ada`;
manifest `8f35548e9754f63a3fa201ef9698c5c55c93a39085dd2ef41fbcb8aed140240f`.
Prior files are in `/var/lib/codi-ingress/browser-rust-package-metadata-backup.json`.
A hash-pinned scan of the actual live ABI v3 WASM confirmed 367,819 function
names and the named crate/type references documented in SOURCE_PROVISION.md.
Name counts are not a complete final-link audit; remaining licensing questions
are not declared resolved. Unrelated guest SSH work remains untouched.

The updated notice generator and associated Browser source snapshot is
`codi-browser-source-9f99310f6.tar.zst`, SHA-256
`14f39b6438216f4ab3a99524255389594ec73682b392e30fe555780a04edd88b`.
The signed-in source page and complete archive download were verified with a
fresh disposable account; the account was removed. Current index SHA-256
`0750f7e555476aa7ed0389cbd9ecfc30bad573e80141bd1f4abb7886d9d186f2`,
notice manifest `b63a5c359fcd48774bf528ad652fae2d301d89756f214321cea6e38f49a00953`;
the index rollback backup is
`/var/lib/codi-ingress/browser-source-index-rust-metadata-backup.json`.

### Gecko Rust archive input inventory — 2026-10-31 UTC

A reproducible scan of the pinned Gecko `libgkrust.a` archive found 5,713
members, 470 crate/build pairs and 454 package names. The hash-checked live
combined notice includes the exact Rust input and headings for all 318 vendored
package/version manifests identified in that archive. The other names map to
tracked workspace manifests or nine Rust toolchain crates. Three additional
native archive members were traced to cubeb-core, mozglue and SWGL build
directories. The archive and report hashes, caveats, verification tools and
workspace/toolchain distinctions are in `apps/system/browser/docs/SOURCE_PROVISION.md`.
These are link inputs and heading coverage, not proof of final retained
objects or complete license compliance. No live runtime or notice changed.

### Live rule-manager and documentation check — 2026-10-31 UTC

Read-only live operator checks reported empty incoming-login and outgoing
IP/country block lists, the configured Browser domain blacklist, a populated
but disabled whitelist, and the independent server audit disabled with no
key or ledger present. The Browser and network-policy READMEs now correctly
identify the running relay and distinguish the historical trusted-proxy
finding from the active guard. The new IP/country outgoing list covers the
Browser relay, not the separate Linux guest or every server egress path;
login blocks do not revoke existing sessions. The focused policy and operator
tests passed (11 and 2 tests) with a scoped maxminddb 2.8.2 environment. The
first attempt used the shared auth venv, which lacked maxminddb, and failed
its local-country-database test; the isolated dependency environment fixed the
test setup. No live policy was changed for these read-only checks.

The corrected documentation and current Browser source are published for
signed-in users as `codi-browser-source-f15af44a6.tar.zst`, SHA-256
`27e670c3bdae08bfe550ca6d732fc483e22d5ca50704f3d18b26ec7f02b01d27`.
A registered live test downloaded and verified the complete archive alongside
the runtime source, exercised relay and file-gateway checks, and removed its
disposable account. Current source-index SHA-256
`784e0ca9614166e56a99d8487d6c7ef8046bc76907b07caf66c72d64e7c2fd6c`,
notice manifest `df4e896c4d37024e38e805b037f6402a90e7427c5a362f55fe950e83ac529252`;
prior index files are in
`/var/lib/codi-ingress/browser-source-index-doc-update-backup.json`.

### Live Browser relay recovery — 2026-10-31 UTC

With a disposable registered account, the current live Browser displayed an
unavailable message when its relay was stopped before launch. After the relay
started, Reset engine reconnected and loaded example.com. A second stop while
the Browser was open produced its connection-ended message; restarting and
resetting again loaded a page. The test account was removed. This is manual
recovery and does not restore the temporary Gecko profile. The test made no
administrator report request, avoiding uploads from other browsers. Relay,
issuer and file services were active afterward; the public site returned 200,
unauthenticated source access returned 401, access block lists remained empty,
and server audit remained disabled with no key or ledger. The socket readiness
probe initially saw a missing socket during startup before the later retry
succeeded; this did not cause a test failure.

The current live release was tested with `CODI_TEST_REPORT=local`: a
disposable registered account recorded example.com in its browser storage,
then remained open for 32 seconds without submitting a report or acquiring a
server report row while no administrator request was active. The test made
no report request affecting other browsers and removed the test account.
The explicit-request and report-persistence tests remain documented in
`apps/system/browser/docs/DOMAIN_REPORTS.md`; those earlier tests used the
then-current release. Server audit remains independently disabled.

### Live Browser files and Linux boundary — 2026-10-31 UTC

Two disposable registered accounts wrote different HTML contents under the
same My files path and synchronized their server copies. The second account
could not find the first account's file before writing its own, and each
account subsequently read its own version from the server. A fresh signed-in,
phone-sized browser context opened the first account's HTML via Browser →
Open from My files; its rendered pixels matched, and the browser and server
copies remained identical. Both test files and accounts were removed. This
is an account-isolation workflow check, not an exhaustive security audit.

A separate disposable live account confirmed that Files browses temporary
Linux home, Linux-only files do not appear in My files automatically, account
files do not appear in Linux's former Account mount, and explicit Copy to
account works. After refreshing and signing in again, the temporary Linux
file was gone and the account file remained. Test account files were removed
and synchronized before the disposable account was removed. This used browser
automation on one computer, not a physical phone or an independent network.

### Browser subresource and relay policy regression — 2026-10-31 UTC

A disposable registered account saved an HTML document in My files that
referenced a blacklisted embedded resource. The current live Browser opened
the document and displayed the network-policy block message for that resource;
the file and account were removed. This was one embedded-resource case, not a
claim about every website.

The local relay's current `wisp.py`, `download.py`, destination policy, and
shared network policy hashes matched the installed live runtime. Their focused
tests passed: 14 Wisp tests, five downloader tests, and six destination-policy
tests. These included controlled DNS answer changes, mixed/public-private and
IPv6 transition addresses, redirect target checks, changes during DNS/connect,
and closing existing traffic after a new rule. The DNS and redirect tests used
local fixtures; they did not change public DNS or demonstrate every external
resolver/network configuration. The separately documented network-specific
NAT64-prefix limitation remains.

### Reproduced Gecko intermediate link map — 2026-10-31 UTC

An isolated reproduction used the pinned upstream relocatable relink recipe
and a linker map, without replacing the retained libxul. The result matched
all retained library sections except the generated module name and build ID;
name subsections other than module name also matched. The map identified
5,269 distinct Rust archive members across 326 package names in the
intermediate link. Pinned comparisons, counts, scripts and limitations are in
`apps/system/browser/docs/SOURCE_PROVISION.md`. This is not the final Browser
WASM link and does not by itself resolve all licensing obligations. The first
attempt used the upstream ordinary `-shared` recipe and hit its documented
linker crash; the relocatable recipe succeeded. No live service was changed.

### Browser final-link symbol comparison — 2026-10-31 UTC

A mapped final Browser relink produced WASM byte-for-byte identical to the
live engine. Its final map and a regenerated, hash-matching intermediate map
were joined by symbol name using `tools/join_gecko_final_maps.py`. The join
found unambiguous direct matches to 315 Rust package names, while 637 matched
symbol names had multiple possible input categories and 2,955 final libxul
symbol names had no match. Hashes, reproducible parser, counts and caveats are
in `apps/system/browser/docs/SOURCE_PROVISION.md`. Inlining and symbol naming
mean this is not proof of package absence or complete license compliance.
No live runtime or notice changed. The compact summary is retained locally;
temporary engine and linker-map copies were removed.

### Browser embedded graphics notices — 2026-10-31 UTC

The signed-in Browser source page now includes the original embedded notices
from the pinned aa-stroke `bezierflattener.rs` and `tri_rasterize.rs`, as well
as the MIT license from the matching .NET WPF graphics implementation at
revision `3993645a2957293053ec8090eff1fd472a07cd65`. The exact WPF revision used
to produce the Rust port is not established. The collector pins the complete
Firefox source-file hashes and WPF license before extracting notices. The
component notice SHA-256 is
`02a2923ad8fc48e68cde3756ff4323b81e8bcff56101fb9bee4803061a5b942f`;
notice manifest SHA-256 is
`40736943c79faaecd3a0c2ead8247b78e388dc0eda1c9a252abfbe43f3a53a8c`.
Previous files are backed up on box-webhost under
`/var/lib/codi-ingress/browser-wpf-notice-backup.json`. Local generation and a
fresh registered live source/relay/files test passed; its test account was
removed. The broader linked-component license review remains open.

### Browser notice source snapshot — 2026-10-31 UTC

The authenticated source page now indexes
`codi-browser-source-8a7a3c43d.tar.zst`, SHA-256
`ecf9e1526400f863291849c8ddbb4594c6534fcc1ec070ba629d2e63a1dbd8de`,
including the updated aa-stroke notice collector and WPF license. A live
registered session downloaded the entire snapshot and verified the hash;
relay, file and access checks also passed and the test account was removed.
Index SHA-256 is `49167a41e6024920cbf20b8de2860c0c143ed4bc817cf6db733e77d453fa3541`;
notice manifest SHA-256 is `2ea88b61c485792dd6f156bca4b2f2e147ef4aa7c254f6ad412d7d4f95553525`.
Prior index files are saved at
`/var/lib/codi-ingress/browser-source-index-wpf-update-backup.json`.

### Rust source comment notices — 2026-10-31 UTC

A reproducible source scan of 195 Rust package candidates identified by
unambiguous final-link symbol matches collected 85 distinct copyright-bearing
comment blocks across 482 file references, including libm's Sun notices. It
only scans the first 100 lines of tracked source files and omits test/example
directories; attribution at package level does not prove a given file was in
the binary, and other files and dependencies still need review. The signed-in
component notice SHA-256 is
`953caeb7f1f698f875d5ef4675d81b31e6cb4c26b3665cebf4a3419d497c1ba0`;
the manifest SHA-256 is
`b9b05b549abac8c2abd5dbf91875f0951ff810acdeaa838c98f303817b7f560f`.
The old notices are backed up at
`/var/lib/codi-ingress/browser-linked-headers-backup.json`. Local notice
validation and registered live source/relay/files checks passed, and the
live disposable test account was removed. The new collector source is backed
up in Git; update the downloadable source snapshot before declaring the source
provision work complete.

### Linked notice collector source snapshot — 2026-10-31 UTC

The authenticated source page now includes
`codi-browser-source-7bc6719ed.tar.zst`, SHA-256
`4fe52eaa8a8c2450fae3683845eaa4480ab045e2f5f28faf4a2a40a69a049c80`.
It contains the new linked-Rust header collector and the two pinned compact
link-audit records needed to reproduce the candidate list. A registered live
session downloaded and hash-verified the complete archive; relay and file
checks passed, and the test account was removed. Index SHA-256 is
`f3ef45a667ea5973111110a177697704e6dc82f60a1380399aab02a34e534b30`;
manifest SHA-256 is
`e3c26d091d1dd303bedef382498b0961417575df826c5eed9ded54f1430fb470`.
Previous index files are backed up at
`/var/lib/codi-ingress/browser-source-index-linked-headers-backup.json`.

The link summary also lists three vendored package names only in ambiguous
matches (`ffi-support`, `mime`, and `rustc-demangle`), which were outside the
195-package direct-match source-header scan. A quick source search found
Mozilla copyright headers in `ffi-support`; the other two produced no matches
in their `src` trees with that search. This is a lead for further review, not a
claim that those packages are absent or that their notices are complete.

### Linked Rust notice coverage audit — 2026-10-31 UTC

A reproducible comparison of the pinned final-symbol and archive inventories
against the exact live notice text found headings for all 198 vendored
package/version candidates, including the three ambiguous-only candidates.
Twenty-six lack separate vendored license files; all have supplemental markers.
Three (`aa-stroke`, `debug_tree`, `seahash`) have package-level metadata rather
than a verified standalone upstream license, and `svg_fmt` uses a source-matched
historical license. A marker alone is not a legal determination or evidence of
exact per-file linkage. Report SHA-256:
`646833aaa6f9db6ff500f7f24929978c1bd2d384760dfc5de83866b02f7242ec`.
The live combined notice hash matched the audit input; the audit test passed.
No live files were modified by this review. Other license categories remain
under review.

### Current Browser supplier-site recheck — 2026-10-31 UTC

The live Browser release `1ce5edb5bb8312f9cf3ab6a793f809549b38628a28b7440b42058359e4e68117`
was exercised in fresh registered desktop and emulated phone-sized Chrome
contexts. In both, example.com reported loaded; Grainger returned HTTP 403 and
its own “Access is temporarily restricted” page; McMaster reported loaded
and displayed its catalog. The phone-sized McMaster canvas showed a desktop
layout wider than the viewport and a large supplier survey overlay; usability
of that page on a physical phone is not established. These checks do not test
login, purchasing, full site interactions or general site compatibility. Two
disposable test accounts were removed. The first test-runner attempt had no
Node executable and exited before registration; the rerun used a temporary Node
22.16.0 archive checked against the distribution's SHA-256 list. No live site
code or policy was changed.

### Browser horizontal phone touch check — 2026-10-31 UTC

A fresh registered live session in emulated 412px Chrome opened a controlled
1,600px-wide local HTML page in the actual Browser engine. A horizontal touch
drag caused the page's own `scrollX` observer to report a nonzero offset (53px),
so sideways panning works in this fixture. This does not establish pinch zoom,
inertial scrolling, precise drag distance, physical-phone behavior, or that a
specific third-party site permits horizontal scrolling. The test created no
user file and its disposable account was removed. The test source is
`tests/browser-live-phone-horizontal-scroll.test.mjs`.

### Phone horizontal drag measurement — 2026-10-31 UTC

The controlled horizontal-scroll test now waits for Browser controls rather
than matching a transient status message, and measures after queued updates
settle. Two fresh live runs with six 35px touch moves spaced 40ms apart reported
final page offsets of 92px and 91px. A listener in the latter run confirmed
that the outer canvas received all six move coordinates. This suggests that
more investigation is needed between input dispatch and the embedded engine's
scroll behavior; it does not establish the cause or prove physical-device
behavior. An intermediate diagnostic run's original test waited indefinitely
for a transient status; after verifying its controls were enabled, the test's
status text was changed locally to let that run finish. That run is not used
as an independent readiness result. All disposable accounts were removed; no
live product code changed.

### Browser scroll fix live — 2026-10-31 UTC

Simplified release `628cceb37a2bb3541390a87df258453ac0fc4a4b03fafac0a899f0784709c108`
serves Browser bundle `d4779962241ed074236cbbe00c29eeeb258f9859e736c8fa21b1ed76e7b5f5ee`
with engine WASM SHA-256 `4efd895c3ec20729ee738ab942e6fbc2fc798ced2f28b7d37b116668540758be`.
The software wheel fallback uses immediate scrolling so successive touch events
accumulate instead of restarting a smooth animation. A live registered
phone-sized Chrome test moved 210px for both a six-step and a single 210px
gesture; a registered desktop Browser rendered example.com. Signed-in source,
relay admission, deny policy, file gateway, and account re-login checks passed.
Test accounts were removed. Local real-engine tests also covered vertical touch;
physical-phone input and custom page scroll widgets still need testing.

Corresponding source is `codi-browser-source-7092c2e0d-scroll.tar.zst`, SHA-256
`bb21975085ee8552ac16c428a59c83aa014be955b18742e0336f37f0b5703cae`,
on the authenticated source page. Its combined patch passed a reverse dry run
against the experiment checkout. Previous frontend is
`1ce5edb5bb8312f9cf3ab6a793f809549b38628a28b7440b42058359e4e68117`;
hosting backups are `change-20261031T071928382832Z` and
`change-20261031T071928383307Z`. Generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest is `02aefbcde5ecc43c9da2988e3ad8d10b7d5860f49c586ab9b0401a7ab07ba90b`,
and Caddy is `84647a587008adb146180c260a038c0310a011d2f317189ceb474a677faa16ab`.
The generic HTTP smoke script failed because it expects 200 on port 80 but
Caddy redirects to HTTPS; a separate local HTTPS status probe returned 200 for
nine sites and the configured Basic-auth 401 for hardware.ksu.codes. This
status probe does not replace full functional checks of the other sites.

### Maximized apps and Files touch menu live — 2026-10-31 UTC

Simplified release `00490a673b162911ef55b86c0e536ac555249957da212fd1bfbe4ca5c1aedf71`
uses Files bundle `96c5adddcef0b1710e63af9bde696ea25a3984fc6f25693850acb336d9d5d16d`.
New app windows open maximized within the desktop and maximized windows follow
viewport changes; the maximize control restores a smaller window. Layout
persistence records the maximized state. On touch/narrow screens, Files has a
New / Upload menu for its existing create-folder, create-file, and upload
actions. Desktop right-click remains available. A real live registered test
created and uploaded files via the phone-sized UI, waited for server sync,
recovered both in a fresh browser context, and removed its files and account.
Two open windows followed phone, 1080p and 4K emulated viewports; a restored
window stayed independent and both states survived reload. A fine-pointer
desktop launch was also checked. Local tests covered menu toggling, the file
chooser and disposal. Physical F11, real phone touch and all other applications'
individual responsive layouts remain to be tested. App-by-app work is tracked
in `docs/APP_UNIFICATION_PROGRESS.md`.

Previous frontend was `628cceb37a2bb3541390a87df258453ac0fc4a4b03fafac0a899f0784709c108`.
Hosting backups: `change-20261031T072742460126Z` and
`change-20261031T072742460532Z`. Generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest is `4df245dbc575d0ee1b24b2f6dca368564f3ee635ed2494aae1f45da6f85778a3`,
and Caddy is `ed555313f1afe1e6cef074615ec1acdf85bc8a506a7419b94620648ef3c496a0`.

### Files Open action and Files → Text workflow — 2026-10-31 UTC

Simplified release `e4cec0d0b929cb5f6bdc41e146d433d2d8e99eb5314b5ce5a833ea2c0d280a2f`
serves Files bundle `070b263b69e8cc8c29954e111c24a7fef925db883365827913276fc34187eb1d`.
A selected file or folder now has an explicit Open action, so touch users need
not perform a mouse double-click. Linux guest files still require copying to My
files before opening in a desktop app. Live registered desktop and phone-sized
tests created a text file in Files, opened it in Text, edited and synchronized
it, closed and reopened it, then read the server-backed copy in a fresh browser
context. Both disposable accounts and their files were removed. The initial
local test revealed that a single phone tap only selected the file; an initial
reopen test tapped an already-selected file and deselected it. The corrected
test uses the visible Open action. Real-phone behavior and broader Files/Text
edge cases remain open.

Previous release: `00490a673b162911ef55b86c0e536ac555249957da212fd1bfbe4ca5c1aedf71`.
Hosting backups: `change-20261031T073255411340Z` and
`change-20261031T073255411743Z`; generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `273b361d38f7d7f48df27ad7d0b72dd5144b48e5922d6417049c8932a303fbb3`,
and Caddy `c455ebbc5d581d0180ec771a683c25756b7ade23fa29a15c4c349d472d71f5ac`.

### Text first-save naming — 2026-10-31 UTC

Simplified release `d5e3b44eb6e6f3d5038d0adbda6ea090455508f2dbb9e7fe236f3bef00849898`
serves Text bundle `0bfe806569aa98921bfef3274c8f9cee44ce9879bfc1f252f3395ecedc892f66`.
The first Save for an unsaved Text document asks for a path in My files. It
uses the existing version-checked create behavior, so an existing file is not
overwritten and the draft is preserved. Live registered desktop and phone-sized
tests checked naming, collision refusal, sync and fresh-context recovery;
test accounts were removed. Local desktop and phone-sized editor regressions
also passed for existing-file edits, conflicts, Save As and reload. The old
phone regression test was updated to use the current Keyboard lock menu.
The dialog still uses a path field rather than a visual destination picker;
physical phone keyboard behavior and broader app integration remain open.

Previous frontend:
`e4cec0d0b929cb5f6bdc41e146d433d2d8e99eb5314b5ce5a833ea2c0d280a2f`.
Hosting backups: `change-20261031T073619549120Z` and
`change-20261031T073619549552Z`. Generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest is `0afb0763ef2f80c6ed583945eeb2f43d6dd249409809110fcce296e2a6bb4071`,
and Caddy is `25c0553f189c179dc00d8e83aa9612af3fb76de42635aaff840aaa7fcb1d79b8`.

### Text My files folder picker — 2026-10-31 UTC

Simplified release `099f46ea3c88af6866333d24508f6af6a7d07e1f403506529a704f35fd00d7a7`
serves Text bundle `0c8e1a9420c867d4c50ea4f06ed0dc3d0e271d13ed3ac89372174eebaa0590f3`.
Text's first-save and Save As dialog can now browse account folders using the
shared `host.storage.pickFolder` service. A typed path remains available;
existing destinations are not overwritten. The picker returns only My files
folders, checks the active account, and closes on app disposal. Its list and
buttons have 44px minimum targets. Registered live desktop and phone-sized
tests verified folder selection, cancel, collision refusal, sync, recovery in a
fresh browser context and cleanup; disposable accounts were removed. Local
existing-file, conflict, reload and shared open-picker regression tests passed.
Physical phone keyboard and accessibility testing remain outstanding.

Previous frontend:
`d5e3b44eb6e6f3d5038d0adbda6ea090455508f2dbb9e7fe236f3bef00849898`.
Hosting backups: `change-20261031T074116644050Z` and
`change-20261031T074116644458Z`; generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `ff9309da3ac2bcda972f88b34e7bc70b296ccbf92d0f2027aaf7e8822ba07703`,
and Caddy `d6f62938039e9718e8158994d8f35b9a6078f60eff925ac1d85b8a581a2a0081`.

### Document Editor account-file workflow (2026-10-31)

Live release `3da419b1cd6f33642b73ca9bfa64d5d3de338c698c508b65855f1a721a029787` adds Open from My files, Choose save folder, and preserves the current editable draft if a chosen document cannot be opened. Local desktop and phone-sized browser tests passed, including save, sync and fresh-session recovery; the broader desktop report/PDF and touch tests also passed. On the live site, the desktop test passed. The phone-sized run completed the same save/recovery checks but encountered a server request limit during fixture cleanup; its test account was then cleaned directly with path and content checks. Investigate request limits when reviewing sync behavior. This is not yet a complete Document Editor review.

Hosting generator SHA256 `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `68865ff3e73a2d3becc89d0b1de2cc46de7a50f56e5f92466e199770fd63ee42`; prior active release `099f46ea3c88af6866333d24508f6af6a7d07e1f403506529a704f35fd00d7a7`. The staging check found changes only in the Document Editor bundle and app catalog.

### Document image selection and storage capacity target

Live release `16a4f64d12e26500417df61f49edb6597869c3c2bf391b707bd3cece42163e12` makes Document Editor's Image button use the shared My files picker for PNG, JPEG and WebP. Local desktop report/PDF and touch insertion tests passed; the touch-sized image workflow also passed against the live site and its disposable account was removed. Hosting generator remains `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest is `455c5fd89539938acd51157a326a166a1fb877664d527af8e7aa5365bb43abdd`. Prior release is `3da419b1cd6f33642b73ca9bfa64d5d3de338c698c508b65855f1a721a029787`.

The user set a planning target of 100 simultaneous users, most not transferring at once. See `docs/ACCOUNT_STORAGE_CAPACITY.md` for current per-file polling and authorization bottlenecks, design direction and mixed-load test requirements. This target is not verified capacity, and the existing scan/retry design is not yet suitable to claim it.

### PDF Viewer review (2026-10-31)

Live release `74e9a439382583139cb01b212676bf6665b5a2cb507efc004ef92c357c3443a9` switches the viewer to Open from My files, adds larger controls and automatic width re-rendering, and retains the previously displayed PDF if opening a new file fails. The local desktop report/PDF/upload suite passed on rerun; the first attempt encountered a connection-interrupted timeout after its offline phase. Focused desktop and phone-sized open/navigation/resize/invalid-file tests passed locally and on the live site; isolated live accounts were removed. The viewer remains canvas-only, without text search, selection, editing or annotations. Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `e0f3550f91599bda4ecc872c49ae623d132d794ef4a5207c1d468413accac7d1`, prior release `16a4f64d12e26500417df61f49edb6597869c3c2bf391b707bd3cece42163e12`.

### Spreadsheet workflow review (2026-10-31)

Live release `7f0798683edc5e41e4515d62505d120fa883fadc90d1dc68aa26d848a14fd72c` adds Open from My files and Choose save folder, larger toolbar targets, and retains the current workbook after a failed open. Local tests passed formulas, XLSX import/export, upload, saving, fresh-session recovery and failed-open preservation; a phone-sized test used touch to enter a cell. The corresponding live desktop workflow passed. Phone-sized checks reached fresh-session recovery but cleanup hit the existing file-authorization request limit; both disposable accounts were then removed using guarded cleanup. This does not validate full spreadsheet touch accessibility or Excel parity. Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `eacb42f1f1efb8367a0edad75415226aa19ae06da62aa9a465c4030b6947e889`, previous release `74e9a439382583139cb01b212676bf6665b5a2cb507efc004ef92c357c3443a9`.

### Interrupted mirror scans (2026-10-31)

Live release `158720539a14493dbee33ee37d15045e1df3d19f88610c8701e6dc09555bbb3b` carries source `e0db6cd22` mirror SHA256 `3eefc87ae89c7be21a0c1a18b339c52c889bd855773d91e38237f7ac5fc193d1`. A scan remembers completed file checks across interrupted attempts within that mirror instance, invalidates an entry on local version change, and clears progress after a complete scan so later external changes remain discoverable. A deterministic 12-file fixture with a three-version limit per window proved eventual completion, later same-size external changes, and a local edit during interrupted scanning; existing mirror conflict/offline/rename tests passed. Baseline failed the 429 handling test. Local browser Document and Spreadsheet desktop/phone-sized save/reopen workflows passed; a live registered desktop Spreadsheet check passed and its disposable account was removed. The public module SHA matched the pinned source. This does not resume interrupted folder inventory, reduce idle scans, or validate 100 users; the batch/index and capacity work remains open in `docs/ACCOUNT_STORAGE_CAPACITY.md`.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `f635000df16a8cb46eab42a3f4a3b46e25cbebd68c9c41ac63c4d54aa168935e`, previous release `7f0798683edc5e41e4515d62505d120fa883fadc90d1dc68aa26d848a14fd72c`. Staging verified the mirror was the only changed asset before cache metadata regeneration.

### Local candidate: batched file versions (2026-10-31)

Source-only candidate adds optional gateway version-batch capability, at most 16 unique paths and 32 MiB hashed per request. It enforces registered account read permissions and private descriptor checks; oversized or missing files are deferred to individual version checks. Browser mirror falls back when capability is absent and retains partial-scan recovery on 429. Local signed browser/gateway check verified 20 files in two batch operations instead of 20 individual version operations, including same-size external disk modification and fallback to the old protocol. Python tests cover account isolation, disabled read access, malformed paths, symlinks, and restrictive modes; real signed issuer/gateway checks cover anonymous and cross-account access. Existing mirror/codec/version tests passed. Nothing in this candidate is deployed: verify guarded worker packaging, rollout/rollback, real concurrent behavior, and resource usage before treating it as production-ready. See `docs/ACCOUNT_STORAGE_CAPACITY.md`; batching alone does not establish 100-user capacity.

### Batched version checks live (2026-10-31)

Gateway worker `541d74f9042d34c3514a2b27cfee708104f0879194232720e864e9b3af329040` was built from verified live `be4a9ef3a613c2e90517fae427d4d2256b97b74ee2134c10cafe263fc2440eac`; only gateway client, HTTP dispatcher and user store changed, and the live dependency lock was preserved. Existing protected code-upgrade helper activated it, reporting preserved permission bindings and no account/file data restoration; the issuer and file service restarted. Live static release `12e690c7afda47f279a45642b6bc21f73cd2d2034170978ba4cda3179ca2c265` selects the batch-capable mirror. Public capability and a real registered browser scan of 20 files using exactly two signed batch calls passed. The disposable account and its exact fixture files were removed. Local mixed test used eight accounts, two simultaneous batch requests and a 2 MiB upload, passing in 0.825s total after setup (maximum batch 0.065s); this is one small fixture run, not a 100-user benchmark. See `docs/ACCOUNT_STORAGE_CAPACITY.md` for remaining load and efficiency work.

Native release pin `0aaf61849fa03e41376d63a36496c83e83adbc97c14aeafe366100ff9e530af2`; native config SHA256 after gateway upgrade `e7a36e37271b0ada77c05ad501f387d9fc4d532f73a068341d9e4f7c7cbf3bc3`, file config `16bac2187e18910cb704e94f8c603f550e523134afde07cbbef3bc98a6417a0d`. Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `7503a25ac29bf7e5c7cd626b877f7a9491c7893840c156da4b5c8a8ef008ce53`, prior static release `158720539a14493dbee33ee37d15045e1df3d19f88610c8701e6dc09555bbb3b`. Old gateway worker is retained for code rollback through the protected helper. No 100-user capacity claim.

### Data Explorer result saving (2026-10-31)

Live release `477888700cdd6204b669860bab43213a0e6f03780cb29b290fc44cb44335bf04` adds the shared My files opener and folder chooser, a CSV output path and Save results CSV. Export writes the current SQL result to the browser mirror with overwrite confirmation and server synchronization; it does not serialize Perspective chart settings, filters or pivots. The input CSV remains unchanged. Local desktop, phone-sized and 4K-sized browser tests covered PC upload, SQL aggregation, chart rendering, chosen folder, saved CSV contents, cancelled overwrite, fresh-session recovery, window close and reopening the result. Desktop and phone-sized tests passed against the live site, and their two isolated accounts were removed. Tests emulate viewport/inputs; physical phone touch and broader data/chart workflows remain unverified. SQL/query and chart settings are still temporary, and large queries may exceed device resources.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `85dd9b55238be1d1deb81547269bf0ec5f16c480e997f18490c8d00c21538325`, previous static release `12e690c7afda47f279a45642b6bc21f73cd2d2034170978ba4cda3179ca2c265`. Staged asset comparison found only Data Explorer bundle and catalog changes.

### Python Notebook file workflow (2026-10-31)

Live static release `a0eec8a0a284820b467244970f05eeb980949b656263fa923d088fb3d8cfbc06` adds Open from My files and a save-folder chooser. It prepares an opened notebook under a new temporary JupyterLite path and only replaces the active notebook after it loads; invalid notebook content leaves the existing path and draft intact. Local tests passed Python/NumPy execution, notebook upload/open, automatic save, two-account same-browser isolation, rejected-file recovery, and fresh-session recovery; desktop, phone-sized and 4K-sized viewports were emulated. Live desktop and phone-sized save/recovery checks passed; test accounts and their server fixtures were removed. Physical phone touch, all notebook formats and untrusted-code isolation are not established. The JupyterLite working copy may remain in browser storage after close; My files is the persistent account copy.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `0396531f11b500b905cf6f6f745b9502e4fe6f533c7ca3357a1f15b3b6f14819`, previous static release `477888700cdd6204b669860bab43213a0e6f03780cb29b290fc44cb44335bf04`; only the notebook bundle and catalog changed in staging.

### Image Editor failed-open protection (2026-10-31)

Live static release `a917daea9c878b4fd284be0a699b72a58e4a1e7fe329a5c167217f6d75193743` validates a chosen PNG/JPEG/WebP before replacing the current editor and preserves its edits when decoding fails. The My files action has clearer wording and a larger touch target. Local Files upload/resize/save/server PNG test and desktop/phone-sized failed-open/fresh-session tests passed; focused desktop and phone-sized checks passed live, and the disposable accounts and exact fixtures were removed. Physical touch, full image tooling and all formats remain unverified. Save currently updates the opened file; Save As and animated GIF editing remain unimplemented.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `5d5916be12033a02ef922254d136cc470813796b5108e3137ea7621970237e30`, previous static release `a0eec8a0a284820b467244970f05eeb980949b656263fa923d088fb3d8cfbc06`; staging changed only the Image Editor bundle and catalog.

### Desktop window sizing and shared tools (2026-10-31)

Live static release `34bf76afe9033469c4cb482a5eaeb79f5b91f63c7c200edc8d0946c4fcbb1ece` makes new desktop windows open in alternating half-width, full-height left/right tiles; phone windows still open full screen. Explicit maximize follows viewport changes, restores to its tile, and manually moving/resizing a tile clears its automatic placement. The tile side is saved per window. Local and live browser tests emulated phone, 1080p and 4K viewports, resizing, maximizing, manually moving and switching between phone/desktop widths. Existing manually restored windows retain their saved geometry. Physical F11 and hardware touch were not tested.

Trystero 0.26.0, TanStack Virtual core 3.19.9, ONNX Runtime Web 1.31.1 CPU/WASM, WebTorrent 3.0.21 and Yjs 13.6.33 are lazy shared bundles with disabled System Tools entries. No app consumes them yet. A real local and live browser test confirmed disabled menu items, lazy loads, Yjs state exchange in memory, WebTorrent creation/destruction with trackers disabled, and ONNX WASM inference on a tiny local model with no external requests. No actual peer, tracker, TURN allocation or multi-device collaboration test was made. ONNX's separate shared copy has CPU/WASM only; Transformers.js still retains its independent ONNX dependency. TURN service, proxy and shared ingress were active, DNS for turn.ksu.codes resolved and TLS verified; those checks do not prove relay allocation or NAT traversal.

Image Editor Save As was deployed in preceding release `1f1887d6b2a610ae42fa9ca8b39ebaf5bc7517168cba8fc40c3f872533fc964d`. One live phone-sized run saved the first copy but timed out after an immediate subsequent resize/save with the older size still present. This release exposes Unsaved changes on editor modifications; later local desktop, phone and 4K-sized checks and one live phone-sized check passed when waiting for that change signal. The earlier failure remains a limitation to investigate if it recurs; this is not physical touch validation.

User expanded scope to all listed non-game, non-XR/AR webOS applications and shared tools, while developing games and XR/AR separately. `docs/NON_GAME_EXPANSION.md` records current inventory, proposed categories and unfinished integration. The full app review and 100-user storage capacity objective remain active.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `a98f610bebc6c5fbe32af7feb205f1697eba8aadabd795ed5db1807f3ee0dfd9`, previous static release `1f1887d6b2a610ae42fa9ca8b39ebaf5bc7517168cba8fc40c3f872533fc964d`. Staging changed only the shell, app catalog, Image Editor and five new tool bundles. Disposable live test accounts/fixtures were removed.


## 2026-10-31 — Audio Editor open safety and game scope

Audio Editor validates browser decoding before replacing the current track, keeps the edited track and destination name when an invalid file is chosen, and avoids the upstream open-or-append modal for My files. Desktop, emulated phone and 4K local tests exercised upload through Files, reverse, invalid open, WAV save, server sync and reopen. A fresh registered live-site desktop test passed the same workflow, plus local Tone and WaveSurfer checks; its disposable account and test files were removed. Physical-phone behavior, large-file memory pressure, multitrack saves and full audio workflows are not qualified.

Live static release: `8de776337097c89fb9ae825db7e9e3bd9999522f518a4292716db5bf5bccde44`; previous release: `34bf76afe9033469c4cb482a5eaeb79f5b91f63c7c200edc8d0946c4fcbb1ece`. Hosting generator SHA: `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA: `c0db2952fa9972d366e559cb41b9075615bcf3d44535717a294090b490ed024f`.

The user authorized games and identified `../served_apps_public/game_tree` as the design starting point. It contains pseudocode and specifications, not playable games. Its own AGENTS.md requires independent apps, real Rive integration, and one finished vertical slice before expansion. XR/AR remains outside the newly authorized scope.


## 2026-10-31 — Falling Blocks live preview

Applications → Games → Falling Blocks (preview) is available at ksu.codes. It
contains the independent Phaser game and locally served Rive coach. Local
desktop tests cover multiple windows, account saves, stale versions, simulated
separate-browser gateway failure, minimize/restore and isolation. A disposable
live account passed menu launch, coach rendering, account save and recovery in
a fresh phone-sized browser session; that account and its one test file were
removed. This does not establish physical-phone operation or complete game
acceptance, and the app is labeled preview.

Live static release `d652a17c3d8144db943eeddd48b5bd11e8a66e7364797ab7e70003c9bd758e0c`;
previous release `8de776337097c89fb9ae825db7e9e3bd9999522f518a4292716db5bf5bccde44`.
Generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`;
manifest SHA `8fd3e6bc30d456bf31c28af2ed59314e45c2451b95b8e481f45b699aff5e2242`.
The reviewed release differs only in app.js, catalog and Falling Blocks assets.
The full build now includes Falling Blocks: run its pinned `prepare.py` with
Rive CLI 1.8.0 and install its npm dependencies before building.


## 2026-10-31 — diagrams.net file workflow

Live static release `1ba25a429096862853834d5eb47b83a13c5aece4b46917e0f5605684a0934c28`;
previous `d652a17c3d8144db943eeddd48b5bd11e8a66e7364797ab7e70003c9bd758e0c`.
Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`;
manifest SHA `8bb32e7d5e3f2e229a3aceb56b6ee1faf5823479173910d75f8d6a5a4c117af9`.
Only diagrams.net assets and app catalog changed. Open validates XML before
replacing the current diagram; save supports choosing a folder and confirms
replacement. Local and live desktop and emulated-phone tests opened a diagram,
edited its label, rejected malformed XML without losing that edit, saved and
synced it, recovered in a fresh browser session, and uploaded via Files. The
two disposable live test accounts and their files were removed. This does not
prove arbitrary compressed payloads, full touch UX or physical-phone behavior.


## 2026-10-31 — Excalidraw file workflow

Live static release `641af409e1602e8278c95ee22a06c8c7a01e06642d53e238ff40bdc70d336f41`;
previous `1ba25a429096862853834d5eb47b83a13c5aece4b46917e0f5605684a0934c28`.
Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`;
manifest SHA `74f77dda811ebacf8d24760ab3ca121e0e935b31a6b6924c55f825bc076e4310`.
Only Excalidraw assets and the app catalog changed. Open validates basic
document structure before replacing the drawing; Save location chooses a folder
and replacing an existing file requires confirmation. Local and live desktop
and emulated-phone tests drew a shape, rejected an invalid file without losing
the edit, synced it, recovered and resaved it from a fresh browser session, and
uploaded through Files. Disposable live accounts and test files were removed.
Physical touch, arbitrary embedded images and full upstream compatibility are
not established.


## 2026-10-31 — SVG-edit file workflow

Live static release `477085a902f1ec63021de1a0b8359985083f6891c82c1d0855a32f31f0cda896`;
previous `641af409e1602e8278c95ee22a06c8c7a01e06642d53e238ff40bdc70d336f41`.
Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`;
manifest SHA `51cb1071dc7bba7b0d0a6b8d91ccaaf574fc7a33e951b0e4bde4237c6a1b9b78`.
Only SVG-edit assets and app catalog changed. The editor checks XML and SVG
root before opening, attempts to restore the prior drawing if the editor rejects
a valid-looking file, offers a folder picker, and confirms replacements. Local
and live desktop and phone-sized viewport tests used the rectangle tool with
pointer input, rejected malformed SVG without losing it, synced to account disk,
reopened in a fresh browser session and uploaded through Files. Two disposable
live accounts and their files were removed. Physical touch and complex SVG
compatibility are not established.

## 2026-10-31 — Replicad primitive projects

Live static release `b2a0809a06bd3c316eb12c52ce8f6434a65ef31247c06074f3fa4b5e915229e7`; previous `477085a902f1ec63021de1a0b8359985083f6891c82c1d0855a32f31f0cda896`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `05e198f56bb0a6da1f7e3b4993d10d12c24b0fc14cd7e9fe08610377605afe32`. Changes are Replicad assets, the app catalog, and the desktop routing/close/layout changes needed for project files.

Replicad is a box/cylinder generator, not a complete visual or programmable CAD app. It now saves and opens editable `.replicad.json` projects in My files, validates dimensions and input, guards unsaved work and changed files, creates STL/STEP in a cancellable local worker, and opens its projects from Files. The local desktop and emulated-phone test verifies uploading through Files, invalid-file recovery, account/server sync, opening from a fresh browser session, STL dimensions, and a STEP file header. The same live desktop and emulated-phone tests passed before the upload case was added; a later live upload run was interrupted by HTTP 429 from the file gateway after rapid tests, so live upload was not verified. Disposable live test accounts were removed. Actual phone touch, geometry beyond the tested models, 3D preview, CAD source editing, and manufacturing validation remain outstanding.

## 2026-10-31 — G-code viewer workflow

Live static release `d216536a208de11e1cc72dea56978385d628724a8646493001e6d335340bcefe`; previous `b2a0809a06bd3c316eb12c52ce8f6434a65ef31247c06074f3fa4b5e915229e7`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `ecd6468317bef1113620a90cd53a7272bf00cb4ba047cce8fc63a018c2da6f78`. Only the G-code app assets and catalog changed.

The viewer now offers an example and a switch for non-extruding moves, makes My files the primary open action, and retains the existing view when an input cannot be previewed. Local and live desktop and phone-sized tests exercise the example, upload through Files, account/server sync, invalid-input recovery, a visible change when toggling travel, close/reopen and a fresh browser session. Disposable live accounts were removed. The library is intended primarily for 3D-printer G-code; it is not a full CNC or safety simulation. Large files currently parse on the UI thread, and physical touch and broad controller compatibility remain unverified.

## 2026-10-31 — Grid.Space export workflow

Live static release `79f13c13f38a130370f6484defb080f31a1549f4d11bca7472de24b1c85f3870`; previous `d216536a208de11e1cc72dea56978385d628724a8646493001e6d335340bcefe`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `a46a516266fe3f14533f4f4885e6aea5d93807ac1026f39ce12e7557cea3d17d`. Changes are Grid.Space app assets, the catalog and a desktop close guard.

Mesh:Tool and Kiri:Moto now offer an explicit save-to-My-files panel for exports, with folder choice, collision checks, cancellation and a close warning for pending exports. Local and live desktop and phone-sized automated tests upload a model, perform a mesh union, slice it in Kiri:Moto, save both exports, check account-server hashes and test a second account in a separate browser context. This separate-context test does not establish same-browser account-switch isolation. Upstream controls remain desktop-oriented and were driven partly through their APIs in automation; physical touch, broad format/profile coverage and hardware use remain unverified. Workspaces are browser-local until exported; exported files sync to the account. Disposable live accounts were removed.

## 2026-10-31 — Digital Logic file workflow

Live static release `b1f8fcb55abf011e081d984f5df11441ce96b940b9eddd1ae495aa289bfd0bfb`; previous `79f13c13f38a130370f6484defb080f31a1549f4d11bca7472de24b1c85f3870`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `3c0daf5a17b19b5972edac2f0f3bd020af3293705ec45b76451e3d2590e8fee2`. Changes cover Digital Logic assets, app catalog, desktop document routing, layout and close guard.

The JSON editor now saves `.logic.json` documents, opens them from Files, selects a save folder, warns about unsaved edits, checks file conflicts and preserves the current editor/simulation when a replacement fails. Local desktop and phone-sized tests checked the AND truth table; local and live tests checked upload, sync, bad-file recovery, close warning, direct Files open and fresh-session recovery. An initial live test failed due to a menu-element timing race; the adjusted test passed on desktop and phone-sized viewports. Disposable live accounts were removed. The app is still a bounded feed-forward JSON simulator, not a full schematic editor or hardware validation. Saving currently requires valid supported JSON, and physical touch remains unverified.

## 2026-10-31 — CircuitJS file workflow

Live static release `fc51848fd9c9786e802dc85610a5a7e4b36ed08fa0d136f08641990c28038dd1`; previous `b1f8fcb55abf011e081d984f5df11441ce96b940b9eddd1ae495aa289bfd0bfb`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `da7b14421c5cc85294e8d7d8b2ddd7fbbe494e1f269cc27010ca0f58f44e54a7`. Changes cover CircuitJS assets and its corresponding-source archive, app catalog, desktop file routing, layout and close guard.

The circuit simulator now opens `.circuit` files directly from Files, uses a folder picker and conflict-aware saves, warns on unsaved changes, and preserves the current simulation when an unrecognized file is rejected. Local and live desktop and phone-sized tests verify a 5 V divider, change a resistor to obtain about 6.67 V, save and sync, upload through Files, reject a bad input, cancel the close warning, reopen from a fresh phone-sized session, and dispose the iframe. The source archive includes matching desktop-integration source and the live test fetched it. An initial local reopen test exposed CircuitJS's `<cir>` XML root; import was corrected and retested. Disposable live accounts were removed. This is CircuitJS rather than ngspice, not a hardware validation; physical touch and broad circuit-format compatibility remain unverified.

## 2026-10-31 — Electronics Design output workflow

Live static release `b131c53090ecd3e905dae2009c4510438c84780ade18278ca93abaa45795f1e5`; previous `fc51848fd9c9786e802dc85610a5a7e4b36ed08fa0d136f08641990c28038dd1`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `d74a5882a31d11ac6ec85db30cbf8af9f843f95b82cff7dad003022fd0b4e90d`. Changes cover Electronics Design assets, app catalog, desktop file routing, layout and close guard.

Captured editor outputs are retained separately, can be saved or discarded individually, and prompt before closing while pending. Saves offer folder selection, replacement confirmation and version checks; `.dez` projects can open directly from Files after the editor starts. Local desktop and phone-sized tests and a live desktop test cover upload, two actual captures, selective discard through the bridge, close warning, account sync and fresh-session Files reopen. The live phone-sized run reached fresh-session local recovery but hit HTTP 429 on its final server sync; it is not a complete live phone pass. Disposable live accounts were removed. The host cannot detect uncaptured editor edits, which is stated in the UI. Phone tests used keyboard simulation; physical touch, broader design workflows and fabrication validation remain outstanding.

## 2026-10-31 — Storage rate-limit recovery

Live static release `7d482122147e5e72ecdcf22931945a6f7b3756b4461ebd39dfa9d7775d56c0e8`; previous `b131c53090ecd3e905dae2009c4510438c84780ade18278ca93abaa45795f1e5`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `419b34b85b2e4c55a967020a9c18a7a01bd91e2893199c81c54e21a037ce8c09`. The only changed application asset is `storage/browser/mirror.mjs`, SHA `4614ca9854364fdd6dbfedd761b87a2f8dbf88c10ead7e07ca1d8266c5eb58dc`.

The current live Caddy route forwards file-authorization requests directly to the loopback issuer; its file authority buckets `REMOTE_ADDR`, so visitors share that proxy-observed limit. The mirror now spreads automatic retries with jitter and bounded exponential backoff after 429; explicit sync and new local writes still attempt immediately. Node tests checked pending-write retention, eventual retry and timer cleanup, alongside existing offline/conflict tests. Local and live account-backed browser tests injected two 429 responses, accelerated timer durations for the fixture, and confirmed the signed write eventually reached the server; the disposable live account was removed. No issuer or gateway limits were changed. This reduces retry pressure only: idle polling, shared proxy buckets, server concurrency and the 100-user capacity target remain unresolved. See `docs/ACCOUNT_STORAGE_CAPACITY.md`.

## 2026-10-31 — Arduino firmware workflow

Live static release `2227cc5560f89e90ed0d80f52554ca0a508e402df3fc3e78067f06eb18543ba6`; previous `7d482122147e5e72ecdcf22931945a6f7b3756b4461ebd39dfa9d7775d56c0e8`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `a1b0ba49296069541be607b9c9d0978da3ada8ceeeb492a90ea45d9cbdc67577`. Changes cover Arduino assets, catalog, desktop document routing and layout.

The simulator now saves the loaded firmware to My files with a folder picker and conflict checks, and opens `.hex` files directly from Files. Invalid HEX leaves the prior simulation running. Local and live desktop and phone-sized tests cover real Blink LED transitions, upload, bad HEX, independent windows, save/sync and fresh-session Files reopening. Disposable live accounts were removed. This is a limited ATmega328P simulation; sketch compilation, other peripheral models, physical touch and validation on hardware remain outstanding.

## 2026-10-31 — Pico project workflow

Live static release `c2d66514aa5973267c544aa36d469f22ce2f1c28db169c9f3e4090542b152fb2`; previous `2227cc5560f89e90ed0d80f52554ca0a508e402df3fc3e78067f06eb18543ba6`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `c86b5675efff5e0b8a00d9ad2517fac88889bd830a12f3a6b9436a9683e78a3d`. Changes cover Pico assets, catalog, desktop routing, layout and close guard.

Pico projects open directly from Files; saves offer a folder picker, replacement confirmation and stale-version protection. Closing or replacing an active firmware board conservatively warns that flash may have changed; a board-generation check avoids applying an old save result to a replacement board. A local isolated-account test using private ROM and MicroPython firmware checked flash persistence, invalid-project recovery, a declined close, competing saves, reset isolation, fresh phone-sized Files reopening and worker disposal. Local and live desktop/phone-sized Blink tests passed without uploading the private ROM to the live site. Disposable live accounts were removed. SSI emulation, arbitrary firmware and physical touch remain incomplete or unverified.

## 2026-10-31 — Stitch Converter artwork workflow

Live static release `387d5a53a94fadb22d98fe196ead582767011f51802e0d293729e1a5f6f5b876`; previous `c2d66514aa5973267c544aa36d469f22ce2f1c28db169c9f3e4090542b152fb2`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `bba05b8cc7e55d50e75875a92e93c92ca6c5dad065cc6721ea7a6e4117f0f48b`. Changes cover Stitch Converter assets, catalog, desktop file routing, layout and close guard.

The converter separately saves editable `.stitch.svg` artwork and machine output, warns about unsaved artwork, checks versions, opens supported artwork and machine files from Files, and clears a stale preview when artwork or size changes. Local and live desktop and phone-sized tests cover editing SVG, PES export and reopen, bad-file recovery, upload, sync and fresh-session Files opening. Disposable live accounts were removed. This checks one example and one machine format, not full machine compatibility, physical sewing, or physical-phone touch.

## 2026-10-31 — Embroidery Studio project workflow

Live static release `a882cd06001539f180da5d557eaec47d4a3b30d5e3d6c5cb19885fb13c66fc1b`; previous `387d5a53a94fadb22d98fe196ead582767011f51802e0d293729e1a5f6f5b876`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `cfc36a6e69c3187b3de2a56e57f4e178f76bd38e9f417270c11aa91749f77431`. Changes cover Embroidery Studio assets, catalog, desktop document routing, layout and close guard.

The host now invokes the embedded editor's project Save As command directly and saves its captured project to My files in one step. It offers folder selection, version/overwrite checks, direct `.stitchfoundry` opening, basic project validation and warnings for known unsaved edits. Machine exports and separately captured files remain distinct. Local and live desktop and phone-sized tests create a design through the editor API, check project save/sync, overwrite cancellation, invalid-project recovery, machine export, upload and fresh-session Files reopen. A separate local test checked the editor Save As capture bridge and stitch export. Disposable live accounts were removed. The underlying editor is pre-release; full dirty-state detection, native UI/touch usability, machine-format compatibility and physical sewing remain unverified.

## 2026-10-31 — Audio Editor file workflow

Live static release `6e1d3e53140abf1d4047d920b827d5f17529254169baa7fa346c7109b5e8888f`; previous `a882cd06001539f180da5d557eaec47d4a3b30d5e3d6c5cb19885fb13c66fc1b`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `18462561c9a77cf0fb4f9875d26e677ff9af684e3fb5a79b16a26dd4a1d8eccf`. Changes cover Audio Editor assets, app catalog and desktop layout restoration.

The single-track editor now provides a folder picker and usable default WAV name, avoids saving while loading, checks the current file version before replacement, and remembers its opened or saved file for layout restoration. Local desktop, phone-sized and 4K-sized tests and live desktop/phone-sized tests cover upload, an actual sample-checked reverse, invalid-file recovery, close warning, stale-save refusal, sync and fresh-session Files reopen. Disposable live accounts were removed. Its existing 32 MiB input/output limit remains below the requested 128 MiB file-service limit; large-audio memory handling, multitrack project persistence, broader effect/codec coverage and physical touch remain unfinished.


## 2026-10-31 — Larger audio files

Live static release `4b5f72175898b56247e7dc2201a063fe37e00afdbded42ec5ad056d453ca6bf6`; previous `6e1d3e53140abf1d4047d920b827d5f17529254169baa7fa346c7109b5e8888f`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `e40bfce95dbed6337b70bea34108d746f4f94376a29894bb8299984afaf6c080`. Changes cover the Audio Editor and its asset catalog plus the shared browser file mirror.

Audio files and encoded WAV output now allow up to 128 MiB. Audio is decoded once at the editor's audio-context sample rate, and bounded sample chunks are encoded in a per-window worker. A save can be cancelled while encoding; closing the window terminates its worker. The file mirror accepts immutable Blobs without an additional eager byte-array copy. Local desktop and phone-sized and live desktop and phone-sized checks exercised the existing edit/save/reopen and conflict workflow. An isolated local account opened and saved a >32 MiB file, checked its samples, and synchronized its result with the server. A separate local worker test created a 128 MiB WAV and checked rejection above the cap. A full 128 MiB application-to-server workflow and physical phones have not been tested; decoded audio and effects can use much more memory than the source. Disposable live test accounts were removed.


## 2026-10-31 — Scientific calculator

Live static release `3e100710ab782e804a58c20988f823735d1d36786e98d5f515ecdf70362799d0`; previous `4b5f72175898b56247e7dc2201a063fe37e00afdbded42ec5ad056d453ca6bf6`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `8bd1586485915a2b0fc4fc6d907647a81c245411899323af2073db2dc1166ab1`. Only Calculator and catalog assets changed.

Calculator now has a touch keypad, powers, common scientific functions, scientific notation, angle-unit selection, and per-window Ans. Expressions are parsed with a bounded arithmetic grammar rather than executed as JavaScript. Calculations remain temporary, and results use floating-point arithmetic. Unit tests cover precedence, inputs and errors; local desktop, phone-sized and 4K-sized and live desktop and phone-sized tests check keypad and keyboard interaction, angles, error messages and independent windows. Physical-phone behavior and broader numerical requirements remain unverified. Disposable live accounts were removed.


## 2026-10-31 — Terminal filesystem guide

Live static release `5bc73539fbab22b64f9b6d776e060d7b339970601dc08bc76fd08602ea0ab657`; previous `3e100710ab782e804a58c20988f823735d1d36786e98d5f515ecdf70362799d0`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `04e2412bffe35c00387221ff0591452e225459d6c672a58ae439aecba1c5c0f2`. Changes cover the Terminal app, its catalog and `terminal.js`.

The terminal command bar opens an in-window guide explaining separate shells, the temporary shared Linux filesystem, copying a Linux file to My files, and basic nano commands. Startup-banner handling also recognizes an interleaved help echo; unit checks cover split and interleaved chunks. Real browser-hosted Linux tests on local desktop, phone-sized and 4K-sized viewports and live desktop and phone-sized viewports exercised separate environment variables, nano save/exit, a file shared between shells, and closing one shell while another continues. A separate local Files test checked explicit copying to account storage and the temporary Linux filesystem reset on reload. Physical-phone touch, arbitrary Linux programs and all startup timing cases remain unverified. Disposable live accounts were removed.


## 2026-10-31 — Selectable and searchable PDF text

Live static release `b51352baed6c388d17f7d1992db7235b8af6e4753a547db7307cb37c30c157fc`; previous `33b8c5196d79043f10e9aeffc517b7066854c181a8bdbc81a2929dfd44627246`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `327079eb233224758348e54df96e8e85f44b08a16cb3bf55115e44a7974c6aae`. Changes cover the PDF Viewer and its catalog.

The viewer uses PDF.js to place selectable embedded text over the rendered page and searches locally for matching pages, highlighting their first literal case-insensitive match. A changed query cancels the previous search; closing or replacing the document invalidates pending work. A visible message explains that scanned image-only pages cannot be searched. Local and live desktop and phone-sized tests cover selection, find, cancellation, navigation, resize, malformed-file recovery and close; desktop tests also use a mouse drag to select text. Disposable live accounts were removed. This is page-by-page search, not navigation between every occurrence; OCR, annotations, forms, physical-touch selection and broad complex-PDF compatibility remain unverified or unsupported.


## 2026-10-31 — G-code parsing and unsupported modes

Live static release `cf7adfc67c26b8ad32c24632a423e398ca9c5e373a380190a41119b457355696`; previous `b51352baed6c388d17f7d1992db7235b8af6e4753a547db7307cb37c30c157fc`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `b36860757f7b6e98906df125d5b083b3f3d0e6948f9865e7c16e8953595a3e1a`. Changes cover G-code Preview and its catalog.

The existing library parser runs in a cancellable worker; a hash-pinned build patch exports it without changing parsing behavior. A local visual parity test compared the example pixel-for-pixel with the prior live renderer. Local desktop, phone-sized and 4K-sized and live desktop and phone-sized tests cover example, upload, sync, unsupported files, travel toggle and fresh-session reopen. A separate local worker test checked 100,000 parsed moves and responsive cancellation of 500,000 moves while retaining the previous view. Relative positioning (G91), inch units (G20), numbered move commands and G92 XYZ resets are rejected rather than knowingly visualized incorrectly. These checks do not identify every unsupported controller command. Rendering and transferring parsed commands still use main-thread work and memory; the 128 MiB file-service limit is not a demonstrated device capacity. Physical touch and hardware/controller validation remain unverified. Disposable live accounts were removed.


## 2026-10-31 — Files conflict recovery and upload destination

Live static release `6b98de55cfe3d093a61e5cd228d079c1f2a7d3201495f79edab2e6077b270b1e`; previous `cf7adfc67c26b8ad32c24632a423e398ca9c5e373a380190a41119b457355696`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `0050dd558f5dba526793d4aee2257f4b508b8242f439fdd3b2176bd989ee58d3`. Changes cover Files and its catalog.

New / Upload is visible on desktop as well as touch. Upload binds to the chosen drive and folder; a location change before accepting a chooser requires choosing again, and navigation after upload begins cannot redirect it. Account uploads pass immutable browser Files to the mirror without an extra eager byte-array copy; temporary Linux uploads keep their existing byte path. For conflicting edits, users can save the device version under another name before resolving; replacing either side requires confirmation. Deletion conflicts explicitly offer restoring the server file or confirming deletion. Local desktop, phone-sized and 4K-sized and live desktop/phone-sized tests checked conflict preservation, cancelled replacement, deletion recovery and destination binding; the full two-winner conflict test also passed locally and live on desktop. Existing local Files → Text and context-menu workflows passed. One repeated live phone upload test hit the shared 429 request limit; a later retry reached the server. The 100-user capacity target remains unverified. Disposable live accounts were removed.


## 2026-10-31 — Reduced idle file polling

Live static release `c079370703f3f8b8251641019c26e6069263ea65605b498a7822940583fc1d0f`; previous `6b98de55cfe3d093a61e5cd228d079c1f2a7d3201495f79edab2e6077b270b1e`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `d37cc248b551539f65d6424bf5258c5570155aa49c47f9955bea28280ea6476d`. Changes cover the Files app, its catalog and the browser mirror.

Successful idle mirrors now poll at approximately 60 seconds in visible tabs or four minutes hidden, with jitter; pending or failed work retains the shorter retry schedule. A stale tab refreshes on becoming visible and writes still initiate sync immediately. Files provides Sync now (Refresh for temporary Linux) to explicitly discover server changes. Unit and real local/live browser checks cover scheduling, stale-tab refresh, manual server-change retrieval, pending retries and cleanup; local desktop, phone-sized and 4K-sized plus live desktop and phone-sized manual-sync checks passed. The live 429 retry fixture also passed. Disposable live accounts were removed. The shared issuer bucket and full directory scans remain; 100 visible idle users could still exceed the issuer limit before active work, so this is not a 100-user capacity result.


## 2026-10-31 — Data Explorer analysis projects

Live static release `481ce1de8fac535c0f632b6003c2ba08d51c9fd8e413a9be1bd03d15f6a0a8c6`; prior staged release `d03aeb5e4d6ba80a2259e36e333a915175edd839776939e14894861590e43f1e`; previous feature release `c079370703f3f8b8251641019c26e6069263ea65605b498a7822940583fc1d0f`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `f648c0a24f8b4c11431c3a88e8ead8ea5921a4d93b5476f1ce01578c03f3a2b8`. Changes cover Data Explorer, the shared picker/route, the desktop close guard and app catalog.

Analysis projects save SQL, Perspective settings and a source CSV path/hash in My files; they do not embed the CSV. Reopening confirms changed source content, checks versions before replacement and rolls back failed SQL/project loads while keeping the prior analysis. Unsaved query/chart changes warn on close or replacement. Save locations and CSV export are collapsed for screen space. Compound project extensions now work in the shared file picker. Local desktop, phone-sized and 4K-sized and live desktop/phone-sized tests cover project save/sync, fresh-session reopen, close cancellation, stale writes, changed-source confirmation and invalid-project recovery; the existing CSV export workflow passed locally. A local >32 MiB CSV with 140,000 rows opened and queried; 128 MiB is allowed but not proven in this app, and device memory may be limiting. One live phone run hit the known shared 429 limit; a later retry passed. Disposable live accounts were removed. Physical touch and large-file device coverage remain unverified.


## 2026-10-31 — Bounded account inventory

Gateway worker `8ed6e9ab142e00b58c5902bb0be8e8b608b43a4cd630dc86ee15477f9c0dc576` replaces `541d74f9042d34c3514a2b27cfee708104f0879194232720e864e9b3af329040`; the protected code-upgrade helper preserved permission bindings and file state while restarting the file service and issuer. The dependency lock was preserved from the existing worker. Live static release `5797493e5496138f2f513da997ffe616e6cf851c96ef7dbe44da2aeaf9250675` replaces `481ce1de8fac535c0f632b6003c2ba08d51c9fd8e413a9be1bd03d15f6a0a8c6`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `7fe22c03b7a6559c4ada7205cf6e87dfe0032257b7bbcfb`.

The signed account inventory returns a complete bounded directory tree or an empty incomplete result, which makes the browser fall back to ordinary per-directory listing. It retains the existing list permission and account isolation; the mirror rejects malformed or incomplete data rather than interpreting it as deletions. Local signed authorization tests cover separate accounts, revoked permission, anonymous denial, bounds and fallback. Local and live browser tests observed one inventory request instead of seven listings for six folders; both detected same-size changes, including a direct live disk edit. A local eight-account mixed test with an overlapping 2 MiB upload completed in 0.831 seconds after setup (max inventory 0.066 seconds); this is not a 100-user capacity result. Existing local file-conflict recovery and live manual sync passed. Disposable live accounts were removed. The shared 60-per-minute issuer bucket remains and can still limit 100 users even for empty accounts; fair admission and reduced authorization overhead require further work.

## 2026-10-31 — Replicad model preview

Live static release `e0545e2edfa82c963c07db4410e53bf685d69b4efb0822bf3a875f8a7813e204` replaces `5797493e5496138f2f513da997ffe616e6cf851c96ef7dbe44da2aeaf9250675`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `0002b30b8e6e5d21d9c792e531cccf93d4aec72ec89ff5e404009d6ee67f9a4f`. A rejected activation attempt had a mistyped manifest hash and made no hosting changes.

Replicad builds a rotatable and zoomable 3D preview from the actual worker-generated STL, with an explicit stale-preview notice after parameter or project changes. Each app window owns and releases its preview renderer, controls and worker. Local desktop, phone-sized and 4K-sized tests and live desktop and phone-sized tests verify rendered rotation, project upload/open/save, server sync, export geometry/STEP header and closing/reopening. Live disposable accounts and their files were removed. Tests use emulated screen sizes and mouse input; physical phone gestures and physical manufacturing validation are not proven. WebGL is required for preview; the app remains a box/cylinder generator with no general CAD scripting or assemblies.

## 2026-10-31 — Digital Logic gate examples and upload snapshot

Live static release `61be28a2d115b78ee0bbe9f94f846fc11f556a51d71459a15d9ca2e6254f8b0d` replaces `e0545e2edfa82c963c07db4410e53bf685d69b4efb0822bf3a875f8a7813e204`; the intervening release `14d7f1c2584334fb38c99f6e2f191ee5e33ed065158802a46fe0cdfae85994f2` introduced the gate examples before the storage fix. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `1387891dd66ab827853b89dea3bcd93e320d6fa18bd7a7e01362d1a1334735da`.

Digital Logic offers AND, OR, XOR, NAND, NOR, XNOR and NOT examples with descriptions. Loading an example creates a new unsaved circuit and does not overwrite the previously opened file. Local desktop, phone-sized and 4K-sized tests check every truth-table row, cancellation and disposal; local and live desktop and phone-sized account tests check upload, save, server sync, fresh-session reopening and preservation of the original. A live phone-sized test reached saving the XOR example but hit the shared 429 gateway limit during sync; a later retry passed. Physical touch and hardware behavior remain unverified.

The live test exposed an existing shared storage bug: saving an uploaded browser `File` directly to IndexedDB could leave it backed by the original computer file. If that source disappeared, the browser copy became unreadable. The mirror now snapshots the bytes used for hashing into a browser-owned Blob before saving. A controlled live negative test reproduced `NotFoundError` on the old code; the new code passed the same offline source-deletion/read/online-sync test locally and live. Local 32 MiB and 128 MiB source-deletion tests passed with hash-checked bytes and server sync, and mirror regression tests passed. This fix does not recover already-unreadable older copies. Snapshotting requires temporary memory proportional to file size; physical-phone memory behavior has not been measured. Eight disposable live accounts were removed.

## 2026-10-31 — Arduino serial monitor and desktop fonts

Live static release `f56968169f054fedb49bc0beae37cfb5a0056cee17297383ecf6fd68e0ac69f5` replaces `61be28a2d115b78ee0bbe9f94f846fc11f556a51d71459a15d9ca2e6254f8b0d`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `1b8828f181341a4d14bdaae9c7db79442a71a3425503a497cfc5025854bcbc03`.

Arduino Simulator has a two-way UTF-8 serial monitor and a bundled, compiled ATmega328P serial echo example with C source and rebuild instructions. A bounded 1,024-byte input queue waits for the emulated receive register and firmware to consume each byte; a full queue leaves unsent text in place, and stop/restart clears the queue. Queuing is not proof of delivery to firmware. Local desktop, phone-sized and 4K-sized and live desktop and phone-sized tests cover Blink, a 200-character echo, UTF-8, queue overflow, restart, independent window serial output, upload and existing account-file workflows. The echo example was saved, synced and reopened in a fresh session locally and live at phone size. Three disposable live accounts were removed. Tests do not prove physical touch, timing accuracy, every UART configuration, physical hardware or unmodeled peripherals.

The desktop CSS referenced three absent fonts, producing 404s and already falling back to browser system fonts. The stale declarations and names were removed, retaining the existing system-font fallback without adding bundled font dependencies. The browser tests check that those missing font requests no longer occur. A phone test initially clicked a covered first simulator window while a second fullscreen window was active; the test now focuses the intended window before interaction and passed. Two earlier checks raced the local server startup and failed with connection refused; reruns after readiness passed.

## 2026-10-31 — Pico firmware loading and serial console

Live static release `0fecbf06b9dbb3713c58bdb0316ab79204d9f2e93544f707c37701204c66fc4b` replaces `f56968169f054fedb49bc0beae37cfb5a0056cee17297383ecf6fd68e0ac69f5`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `273f0eee89974f3e5016ced9430fc31113ea911405f06c165e6ee5c506dad273`.

Pico now starts when ROM and UF2 are selected in either order. Serial commands are admitted atomically only when the USB device is ready and its 512-byte FIFO has room; too-long or rejected commands stay in the input. The console has Ctrl+C and Ctrl+D and streaming UTF-8 output decoding. Input is encoded as UTF-8, but the tested MicroPython 1.20 interactive REPL dropped non-ASCII input; Python escapes worked. A unit test fills the actual USBCDC FIFO and proves a rejected message does not alter it. Local real-firmware desktop account testing covers both loading orders, a 200-character command, Unicode output, interrupt and soft reset, flash save/sync, competing saves, invalid-project recovery and cleanup; a fresh phone-sized session reopens saved flash. Local phone-sized and 4K-sized Blink and live desktop/phone-sized Blink tests passed, including preservation of input when no serial firmware is running. Two disposable live accounts were removed. Private ROM and firmware were used only in the local test. This does not establish general firmware compatibility, physical touch, full SSI behavior or hardware timing.

Test development exposed that Puppeteer keyboard typing did not faithfully enter non-ASCII text and that MicroPython's tested interactive REPL dropped raw non-ASCII input. Tests now use explicit input values and Python escapes to check UTF-8 output; they do not claim that raw Unicode works in this REPL. A project-loading test also initially waited on an old prompt or a window title that was not refreshed; it now waits for the selected project path and the new prompt. One local test raced other registration tests and timed out at login; the isolated rerun passed.

## 2026-10-31 — Circuit Simulator examples and change detection

Live static release `41004df7cb57468467c03b54c29eecc44373ca21d90967a30d1d2cab9a35270f` replaces `0fecbf06b9dbb3713c58bdb0316ab79204d9f2e93544f707c37701204c66fc4b`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `b83e225b33bd9ada9fffab8bbfc398f988ab6723b938968762e1a45c45bce74d`.

The simulator now offers a voltage divider, RC low-pass filter and half-wave rectifier with short explanations. Loading one starts a new unsaved circuit; an asynchronous load refuses to overwrite a circuit edited while the example was loading. CircuitJS's full export includes changing capacitor/inductor state; an integration API now exposes its upstream design-only export for comparison, while full exports remain the saved files. Scope-only changes are protected by a conservative full comparison after iframe interaction. Consequently a non-editing interaction with a running circuit can sometimes cause a save warning; the design-only serializer omits scopes and is not a standalone scope-change detector.

Local desktop, phone-sized and 4K-sized example tests and live desktop/phone-sized tests cover component presence, changing RC output, cancellation, scope-change warnings, save/sync and fresh-session reopen. A local and live phone-sized delayed-example test preserves a concurrent resistor edit; the live test reached cleanup and then hit the shared gateway 429 limit, after its functional checks. Existing local account tests passed for 5 V and 6.67 V divider output, upload, failed-open preservation, Ctrl+S, close warning, independent windows and iframe cleanup. Corresponding source and GPL notices remain packaged; the served source archive was fetched in an authenticated live test and its integration source and manifest were checked against the build. Four exact disposable live accounts and their files were removed. Physical touch, broad circuit fidelity and hardware validation are not proven.


## Kiri:Moto workspace snapshots — 2026-10-31

Release `b1d263b34c9db8c4842f3119a814f3e2c2c8b5cadec0716db6daf24aab058a9e` adds explicit `.kiri` workspace snapshots to My files, including model geometry and slicing settings. Opening validates in an isolated temporary workspace before confirmation and replacement; stale file versions are checked. Later edits require another save. Local and live account tests passed save/sync, malformed-file rejection, fresh phone-sized session recovery, restored slicing, and closing while validation runs. A local phone-sized mesh/slicing regression also passed. Tests use upstream APIs for some operations and do not establish physical-touch usability, exhaustive file validation, printer profile correctness or physical fabrication safety. Mesh:Tool project state remains browser-local.


## Mesh:Tool workspace snapshots — 2026-10-31

Release `08c4eb2fdbd9ddfc950941007590c029845c135a1940c615bfe3e3b2813391c5` adds explicit `.meshproj` account-drive snapshots of the editable Mesh:Tool document. The format stores mesh geometry, groups, sketches and document metadata, but not revision history; changes after saving require another snapshot. Open validates in an isolated temporary editor before asking to replace the current work; stale saves are rejected. Local desktop, emulated-phone and 4K-sized tests and a live desktop-to-emulated-phone account test cover upload, a moved model and circle sketch, save/sync, corrupt-project recovery, stale saves, reopen and temporary validation cleanup. The shared Kiri snapshot regression passed locally. The exact disposable live account was removed. Tests use upstream APIs for some edits, so physical touch, broad sketch/model coverage and fabrication safety remain unverified.


## Audio Editor recording lifecycle — 2026-10-31

Release `afbc323e8af9fb294f002ce2c38f72bdad79479eb1574effd3a73b688cf696a3` warns before closing an Audio Editor window while its microphone is active or permission is pending, in addition to unsaved edits. Opening or saving is blocked while a microphone is active to avoid saving an incomplete recording. Window-owned media streams are stopped on disposal, including delayed permission results; the recorder is cancelled and waveform resources are destroyed. A local desktop and emulated-phone and live emulated-phone simulated-microphone test covers independent windows, the New Recording modal, declined and accepted close, and delayed permission. Local and live account tests cover upload, edit, WAV save, sync and fresh-session recovery. These tests do not establish physical microphone or phone touch behavior. Three exact disposable live accounts and their checked test files were removed.


## G-code units and coordinate resets — 2026-10-31

Release `b0721278def821abf6eb215d83dcf009cd48c2bdf0bcc1700f9377c1e475d4bd` converts G20/G21 units and G92 XYZ coordinate resets to millimeter paths, including switches between absolute/relative motion and extrusion; G92.1–G92.3, unsupported work offsets and non-XY arc planes are rejected. It starts at zero without stored machine offsets and does not simulate initial homing; homing after movement is rejected. Local desktop, phone-sized and 4K-sized account workflows compared equivalent rendered paths; worker tests compared mixed units, XYZ reset, extrusion and XY arc parameters, and large-file cancellation passed. On the live phone-sized test, two screenshot comparisons were obscured by the floating voice notification; the corrected large fixture then hit the existing gateway request limit. A reduced live account-file test without that overlay passed rendered metric/inch and reset/no-reset comparisons, and live worker parameter comparisons passed. Five exact disposable live accounts and checked fixtures were removed. Physical touch, controller compatibility and hardware safety remain unverified.


## Files sync status — 2026-10-31

Release `87f37964f1b08edec68d71acaffe2e0a6fe3358f81581c2f894b4cd4203cf113` distinguishes the initial server check, local changes waiting for sync, server-check failures and a completed check. A manual Sync now error no longer remains on screen after an automatic retry succeeds. Local desktop, phone-sized and 4K-sized tests and a live phone-sized test held the initial check, injected a 429, verified the message and automatic recovery, and verified a pending local edit arrived on the account server. Local Files → Text save/reopen and manual server-change sync regressions passed. Tests accelerated retry timers and injected the limits; physical touch and the 100-user capacity target are not proven. The existing shared proxy-observed issuer bucket and gateway concurrency limits remain unchanged. The exact disposable live account and checked fixture were removed.


## Local file admission candidate — 2026-10-31

An undeployed candidate separates file-issuer request budgets by live registered account while retaining a server-wide ceiling and a bounded legacy bucket. A token is used for admission only; signed one-use operation proof and account policy still decide access. A local browser test verified two independent accounts and credential-bearing challenge requests, and 35 issuer security tests plus the full HTTP gateway suite passed. In a bounded local 100-account, one-file-each fixture at concurrency three, all inventories passed (2.479 s total; p95 86 ms), but only 27 subsequent version checks passed before the gateway shared budget limited 73. The fixture used permissive account setup and is not a 100-user capacity claim. Source and tests need guarded packaging and live validation; login bursts, fairness under abuse, large transfers and the gateway budget remain outstanding.


## Account-scoped file admission live — 2026-10-31

Issuer `/srv/codi-connected/releases/file-admission-r1` manifest `037c6d174937f7f5df2f144e25d305b429a2b628b6b5eb62418ab06b6f111804` and file worker `/srv/codi-gateway/releases/file-admission-r1` manifest `6d5d37380cce9c40c259b55c8ad87f6c11836c55c76640dc93fd7ef9f43a6160` are active. Worker upgrade first retained permission bindings; a live two-account browser check verified compatibility with the previous issuer. The guarded issuer upgrade preserved state and restarted the previously active issuer, steward and guest roles. Afterward, a public browser test performed 62 signed inventories across two registered accounts and checked account-file isolation; four exact disposable test accounts and checked fixtures were removed. Managed config SHA256 values: native `4fa0934edfd6b2794ac9e516440c02efa959f833ae4da4630f72f8c89f62b8fb`, file `3556db9d9ec2777811f28801cb73f880185439bd0203a54ef81962ec0349215e`. Live client and issuer use per-account admission, bounded legacy and server-wide buckets; authorization still requires the existing one-use proofs, current session and permission checks. Local security, browser and bounded 100-account fixture results are recorded in `docs/ACCOUNT_STORAGE_CAPACITY.md`. The gateway shared 256-request/minute limit, four active requests, login bursts and 100-user end-to-end capacity remain unresolved.


## Local combined file inventory candidate — 2026-10-31

An undeployed candidate combines bounded account inventory and file hashes into one signed request, with a 64-file/32 MiB hashing budget and fallback for the rest. Local security and browser tests cover permission revocation, separate accounts, symlinks/hard links, direct same-size disk edits, invalid metadata, both older-protocol fallbacks and file-conflict preservation. A local 100-account fixture with one 4-byte file each and three concurrent requests completed all combined checks in 2.647 seconds after account setup, p95 91.08 ms, using 200 gateway requests; this is not a 100-user capacity claim. Live deployment and broader transfer/load checks remain.


## Combined file inventory live — 2026-10-31

File worker `/srv/codi-gateway/releases/combined-inventory-r1` manifest `2bd92f334f1a29407d33872396cddd51d12d938caa473d33471a5836a0d29084` and static release `fdee484702df0b88b6d032674b337bc937ec8850ec46d07f46269ae1021f320e` are active. Worker upgrade retained account/permission bindings and issuer state. The old mirror passed a two-account file workflow with the new worker before the static switch. The new mirror passed a live phone-sized six-folder combined-inventory test, both legacy-protocol fallbacks, a direct same-size disk edit and a simulated-429 local-edit recovery test. Four exact disposable live accounts and verified fixtures were removed. Native managed config SHA256 `38c688ddc832c04a9fc4861977aa3edbae8cd80dca586b8d72b6a6f25222024b`, file managed config `7a0d8170b5d9c64be5acc010a3ca5e4fe8137e8ccf069318aa8d971ff53b0587`. Local security and bounded 100-account fixture evidence is in `docs/ACCOUNT_STORAGE_CAPACITY.md`. The gateway 256-request/minute and four-active-request limits remain; the one-file fixture and live tests do not establish 100-user capacity.


## Local file gateway burst queue — 2026-10-31

An undeployed candidate keeps the gateway’s four active operations and 256-request/minute budget, but adds up to 128 bounded waiters with a five-second timeout. Local queue tests cover overflow, timeouts, cancellation, disconnect before admission, and releasing slots after a cleanup failure; 18 existing gateway HTTP regressions passed. A local unsmoothed 100-account, one-file-per-account workload with eight edits and one 8 MiB upload completed in 3.405 seconds after setup, inventory p95 2.534 seconds and 218 gateway requests. An issuer/gateway-only 100-check burst improved from 4 successes and 96 immediate limits to 100 successes in 2.241 seconds. The tests do not cover 100 browsers, large transfers, sustained load, or fairness when four slow transfers occupy all slots; see `docs/ACCOUNT_STORAGE_CAPACITY.md` for the memory observation. Candidate requires guarded packaging and live validation.


## File gateway burst queue live — 2026-10-31

File worker `/srv/codi-gateway/releases/file-queue-r1` manifest `3f2017b1bd608c38a13dc9a2d4d1d7e55846425d7611c6df90f2c8b6f17e3528` is active. The protected upgrade retained account and permission state and restarted the issuer and file worker; steward and guest were not restarted. Managed config SHA256 values: native `b395ba4dbb2f0ba6efdc53bae9fa2d6c4d1bacdfee607147c3756e047e5b4d7c`, file `b2ddae756286951b5d609de0aeb1fd5cc307cc0791245b96e26db8c0eb8e94d5`. Live browser checks passed eight parallel signed inventories across four accounts and phone-sized local-edit recovery after injected 429; five exact disposable live accounts and verified fixtures were removed. Local queue tests include disconnected-waiter proof preservation and cleanup-failure slot release; the bounded local 100-account mixed test is detailed in `docs/ACCOUNT_STORAGE_CAPACITY.md`. Four active slots, 128 waiters, a five-second queue timeout and the shared 256-request/minute budget remain. Four slow transfers can still occupy every slot; 100-user sustained capacity, login bursts, physical devices and large-transfer contention remain unqualified.


## 2026-10-31 — Replicad through-hole and volume

Live static release `4b83bfc39bd7ea81b19a890eed09aa465f81f699f880efefd561af9aedc9ce8a` replaces `fdee484702df0b88b6d032674b337bc937ec8850ec46d07f46269ae1021f320e`. Managed hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `180a4e55b59077cbb0b82094164da91061e2619635c648f5bd70eb073e075841`. Backups `/var/backups/webhost-sites/change-20261031T152659173940Z` and `/var/backups/webhost-sites/change-20261031T152659179862Z`.

Replicad now supports one optional centered vertical through-hole in box/cylinder models and reports the CAD solid volume. Older project files default to no hole. Shared model validation rejects invalid dimensions and holes. Local desktop, emulated phone and 4K, plus live desktop and emulated phone, passed upload/open/save, account sync, fresh-session reopening, preview, STL dimensions and measured mesh volume, STEP export, and close/reopen. A unit test covers validation and old project files. The test upload fixture must be in a visible home directory because snap Chromium cannot read its host's private `/tmp` or hidden home directories. Live test accounts and verified fixture files were removed. Physical touch and manufacturing remain unverified; this is still a limited primitive generator, not general CAD.


## 2026-10-31 — Calculator scientific keypad

Live static release `b6cbd988a87307b846e5b0dd6a53cd98317ad9169dac30f883dbf132f2ce8c4b`; prior release `5a66937dec8e3335609c0a0787a4d006ffda61f127cdb66bee2eeb4dd872489b`. Generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; hosting manifest SHA `9dcc02206b31bc618f6d2f5299b2c07e8adcc4d9acb19b5c6eaab4dd312b4852`. Managed rollback inputs `/var/backups/webhost-sites/change-20261031T152939977882Z` and `/var/backups/webhost-sites/change-20261031T152939978357Z`.

Calculator adds inverse sine, cosine and tangent (honoring angle units), exponential function and scientific notation keypad entry, with an EE explanation in the app. Unit tests cover inverse and domain behavior. Local desktop, emulated phone and 4K, plus live desktop and emulated phone, exercised keypad input, units, errors and independent windows; the final explanatory text was checked live at phone size. Disposable live accounts and empty homes were removed. Floating-point and physical-touch limitations remain.


## 2026-10-31 — Files Move to action

Live static release `a148b7bf4fbf77cc86f1b9cb677871d2ce589402402303aadde796bd723b788c` replaces `b6cbd988a87307b846e5b0dd6a53cd98317ad9169dac30f883dbf132f2ce8c4b`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; hosting manifest SHA `ed485f536701384dac056ff9fed4ff6d3fbfda137bcdf2034ea13c78c11568d8`. Managed rollback inputs `/var/backups/webhost-sites/change-20261031T153237950509Z` and `/var/backups/webhost-sites/change-20261031T153237950914Z`.

Files offers a Move to… action for a single file in My files, using the shared folder chooser and existing version-checked, server-journaled move. Cancel, same-folder choice, destination collision, source change during selection, successful sync and fresh-session reopening passed local desktop, emulated phone and 4K, and live desktop and emulated phone. Test fixtures/accounts were removed. Files and destination folders must finish syncing; folder moves and physical-device touch remain unverified or unavailable.


## 2026-10-31 — Digital Logic full-adder example

Live static release `28a74ac3d051cff4b30c48f9785c7ae092bfbe4544082adb8af2877d1e8024b3` replaces `a148b7bf4fbf77cc86f1b9cb677871d2ce589402402303aadde796bd723b788c`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `d5671ed2c4102a7dcbb5f3b094c011b3a7bf296b5d84dd56c1aa293497a04df1`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T153541536243Z` and `/var/backups/webhost-sites/change-20261031T153541542174Z`.

Digital Logic includes a full-adder example using XOR, AND and OR gates. Local desktop and phone-sized tests compare generated truth tables and interactive outputs for all eight combinations. Local desktop, phone-sized and 4K and live desktop and phone-sized account tests cover project/CSV save, sync and fresh-session recovery. Disposable live accounts and verified fixtures were removed. Simulation is combinational logic only; it is not timing, electrical or hardware validation. Physical touch remains unverified.


## 2026-10-31 — Files copy and accessible rename

Live static release `20a32d10892ea4a5ac60a4680f0d5bd608729ab0a11a56f214aebaf9822f9339` replaces `28a74ac3d051cff4b30c48f9785c7ae092bfbe4544082adb8af2877d1e8024b3`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `76e0f64ed841a4f296d371e19a02a388f7c247cd5b26758a563f7cd8b3faff81`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T153755719392Z` and `/var/backups/webhost-sites/change-20261031T153755719818Z`.

Files now exposes Rename on the toolbar and Copy to… for a single My files file. The chooser asks for a destination and name, rejects existing targets or stale/conflicting sources, and creates a separate browser-first copy for synchronization. Local desktop, phone-sized and 4K, plus live desktop and phone-sized checks cover cancellation, collision, stale source, same-folder and other-folder copies, rename, sync and fresh-session recovery. A phone-sized move regression also passed locally. Disposable live accounts and verified fixtures were removed. Copying and moving folders remain unsupported; physical touch is not yet tested.


## 2026-10-31 — Spreadsheet intermediate arithmetic errors

Live static release `4ccf87ee51d4f2fb0b579339abcc3a0ddd8d97452296fef75a903ac03bfadbef` replaces `20a32d10892ea4a5ac60a4680f0d5bd608729ab0a11a56f214aebaf9822f9339`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `88a89ee1a75700517d63f5088946c529cffb73a116cf0070878872dbe9333634`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T154000455673Z` and `/var/backups/webhost-sites/change-20261031T154000456075Z`.

Spreadsheet now propagates intermediate nonfinite arithmetic results as errors; previously expressions such as `=1/(1/0)` could misleadingly display zero. Formula unit tests cover division by zero, non-real powers and overflow. Local desktop, phone-sized and 4K and live desktop/phone-sized account checks cover displayed error, preventing CSV overwrite, correction, sync and fresh-session reopening. Disposable live accounts and verified fixtures were removed. This remains a bounded formula subset, not full Excel compatibility.


## 2026-10-31 — Image Editor metadata checks

Live static release `44fc3629dc7512f85fb7d14f46f7c653429a36acc983127df2aeaf971bf1b5d7` replaces `4ccf87ee51d4f2fb0b579339abcc3a0ddd8d97452296fef75a903ac03bfadbef`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `aa7e3b74de16c69ea498549e6eefb7b847b24f443fd327c82e829e76e742414b`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T154253781357Z` and `/var/backups/webhost-sites/change-20261031T154253781757Z`.

Image Editor watches versions and checks Save As destinations via metadata instead of reading the full image, and checks the original account before and after an ordinary save. Local desktop, phone-sized and 4K and live desktop/phone-sized tests instrumented reads, exercised collision cancellation and verified stale saves cannot replace a changed image. The existing Save As resize/sync/fresh-session regression passed locally and live at phone size. Disposable live accounts and verified fixtures were removed. Account switching during an in-flight save was guarded in code but not separately simulated; physical touch remains unverified.


## 2026-10-31 — Image Editor account-switch check

No production code or hosting change. Local desktop, emulated-phone and 4K and live desktop and emulated-phone tests registered two accounts in one browser, saved different same-named images, delayed the first account’s image encoding during an actual account change, resumed it, and confirmed neither stored image was changed. Both tabs retained their account-specific image; a return to the first account recovered its original. Four verified disposable live accounts and their fixtures were removed. This closes the specific account-switch test gap noted above, not a general multi-account security audit.
