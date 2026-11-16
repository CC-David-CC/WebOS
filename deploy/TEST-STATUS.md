# ksu.codes — existing viewer, Files and Text status

Verified 2026-11-16: **https://ksu.codes serves the original Desktop/Workspace
viewer** from platform/desktop/active-system/. Its CSS, reference data and
artwork remain unchanged. Account/date are at the top of the narrow dark right
rail and APPs at the bottom. Calculator, Files, Text, WordCraft and Help are
enabled. Other menu entries remain disabled.

The latest static update protects unsaved **Text/CodeMirror6** documents.
Desktop reads Text's real dirty/pending lifecycle state and warns before browser
refresh/navigation while work is at risk. Clean Text does not trigger this warning.
Text checkpoints local recovery drafts after250ms of inactivity and reports a
local update only after IndexedDB commits. These are browser-local drafts, not
confirmed account saves or cross-machine backups. Recovery is scoped to the
same issuer/account, including untitled documents and drafts whose layout entry
is missing. No password, account token or signing key enters a recovery record.

After sign-in, Text offers Recover draft, Discard draft or Later. Recovered text
remains unsaved. A changed/unverifiable server revision requires Save As instead
of overwriting that file. Confirmed saves clear only their acknowledged snapshot;
newer edits remain dirty. Discard cleanup is ordered and committed only when a
view really closes, so cancelling session end preserves still-open drafts.
Storage failure is visible, while the native warning and actual account Save
continue to work. This does not guarantee recovery of edits newer than the last
committed checkpoint, after browser storage eviction, or after clearing site data.

Known remaining fixes: browser refresh still requires sign-in; clean Text
Save/Save As path/revision/title can remain stale in Desktop's saved layout;
same-file activation can create independent editors. These are separate work.
The recovery test explicitly closes a confirmed clean Save As copy before
continuing, rather than qualifying that separately recorded restoration bug.
No editor menus, Desktop colors/geometry, login policy or backend changed.

The preceding Files update removed the redundant Select multiple and Up header
buttons. Ctrl/Meta-click, Shift-click for a range, and Space retain standard
selection. The existing up arrow beside My files handles parent navigation.
Its derived OpenFiles notification is handled once; known breadcrumb ancestors
use the listing operation rather than a lookup in the current folder's entries.
The arrow is disabled at the account root. Refresh remains in the header.

Selecting and deleting several account items remains supported.
Delete in the toolbar/context menu or the Delete key
opens one confirmation listing the selected items. Cancel changes nothing.
Every resource is authorized before deletion starts; files retain exact selected
revision preconditions. A refusal stops the batch and reports the acknowledged
count. Unknown outcomes are never retried or counted as confirmed. Folders must
be empty; deletion is never recursive. Rename, Move and Download remain single-item.

The earlier external-file drop, native input/cancellation, upload-feedback and
My files breadcrumb fixes remain included. The UI root sentinel maps explicitly
to the account API's empty root path, without Chonky's missing-ID/name errors.

## Remaining native picker issue

The user reports that double-clicking an MP4 in Chromium's OS chooser returns
cancellation, while selecting it and clicking **Open** works. This also occurs
in temporary plain HTML file inputs with no Files handlers, for both single-
and multiple-file selection. Event inspection in the explicitly authorized
existing ksu.codes tab recorded a trusted cancellation with an empty file list;
no upload request was started by that cancellation. A controlled 4 MiB selection
using Open delivered trusted input/change events and the actual Files UI
acknowledged the account save. The user also confirms Open works for their file.

This isolates the double-click problem to the browser/native chooser path in
that session. The precise Chromium, Snap or GTK defect is **not identified**.
No browser restart, permission change, global configuration change or browser
upgrade was performed. Use **select the file, then Open**, or external drag/drop.
Do not label the double-click issue fixed based on the automated chooser tests.
The user explicitly deferred this separate investigation; its resume record is
[BROWSER-FILE-PICKER.md](BROWSER-FILE-PICKER.md).

## Verification

| Check | Result |
|---|---|
| Clean Text reload without warning; dirty Text cancelled reload retains both buffers | PASS, local and hosted |
| Accepted reload/sign-in restores named and untitled drafts without changing account bytes | PASS |
| Changed server revision requires Save As and preserves the server file | PASS |
| Typing during delayed Save retains newer dirty text and its updated recovery base | PASS |
| Explicit Discard and completed session end remove drafts; cancelled session end retains them | PASS |
| Orphan draft recovery with missing layout; same-browser account isolation | PASS |
| Injected recovery-storage failure remains visible; warning and verified account Save still work | PASS |
| Ctrl-click multi-selection, one confirmation listing each item, Cancel preserves all | PASS, local and hosted |
| Confirmed multi-delete preserves unselected files and reports acknowledged count | PASS |
| Ctrl-click toggles, Delete key and empty folder | PASS |
| Shift-click range selection | PASS |
| No redundant header buttons; existing up arrow navigates two levels and is disabled at root | PASS |
| Second-browser revision change stops batch after 1 of 3, preserving changed/remaining files | PASS |
| Nonempty-folder refusal preserves children and remaining selection | PASS |
| Reload/sign-in and fresh-context account listings agree after deletion | PASS |
| Native Upload button opens a chooser; 4 MiB binary saved and read with exact hash | PASS, local and hosted |
| Browser-protocol external file drop; 4 MiB binary saved/read with exact hash | PASS, local and hosted |
| Late cancellation cannot overwrite a completed import result | PASS |
| Duplicate-name refusal preserves the existing file's bytes | PASS |
| Picker cancellation permits another attempt | PASS |
| Navigation cannot redirect a pending picker import | PASS |
| Fresh browser context retrieves both account uploads | PASS |
| My files breadcrumb returns from Documents to root | PASS |
| Unexpected console errors in focused Files checks | None |
| Original desktop geometry, rail order, palette and window operations | PASS |
| Calculator independent instances and close isolation | PASS |
| Files → Text/WordCraft save, close, reopen and formatting | PASS |
| Fresh-context retrieval, reload/restoration and unsaved-work protections | PASS |
| Pre-update disposable account file after the first Files update | PASS |
| Existing-tab file selection with explicit Open | PASS, actual native chooser and UI acknowledgment |
| Existing-tab native double-click selection | KNOWN FAILURE, including plain HTML controls |
| Beta page, checked backend/beta/Caddy processes and account-instance/issuer continuity | PASS |

The latest qualification has **11 Text recovery checks and15 viewer regression
checks locally and over hosted HTTPS**, plus35 unit/lifecycle checks. The Text
package's normal test command also passes its10 tests. The recovery suite uses
actual CodeMirror, IndexedDB, browser beforeunload dialogs and signed account
files. Its isolated storage-failure context retains and asserts exactly one
injected discovery error; unrelated errors fail. Journal tests cover immutable
captures, ordered writes/deletion, discard races, stale-source preservation and
invalidated writers. The preceding Files release passed8 selection/deletion/
navigation checks and8 upload checks; those focused suites were not repeated
for Text recovery. Their unchanged controller tests remain in the35-test run,
and the viewer regression exercises actual Files uploads and document opening.
Focused browser tests retain
all console errors. The upload collision expects HTTP409; deletion tests allow
exactly one deliberate revision-conflict HTTP409 and one nonempty-folder
HTTP403 after verifying the corresponding behavior. Extra/unrelated refusals,
Chonky validation errors and other unexpected console errors fail qualification.
The original tiny upload test was expanded to use the actual toolbar chooser;
the focused test uses 4 MiB opaque binary fixtures with MP4 filenames. No media
decoding or physical OS drag is claimed. The plain-control experiments use
native OS dialogs; automated chooser acceptance alone does not qualify native
double-click behavior. Delegated agents, every app, every file operation and a
physical second machine remain outside these checks.

One earlier hosted viewer run lost its browser connection with Target closed
and no captured page errors. Low available laptop memory/full swap was observed,
but its cause was not established. The unchanged assertions passed in a fresh
browser, and both subsequent release regressions passed. Failure evidence is
retained; it is not counted as a successful run.

## Release provenance

| Item | Selected identity |
|---|---|
| Packaged parent source | e8ec1e444d3b659103a1e8d70da211b1070e98b0 |
| Files | 7a0dd487953b2ec639e691581684c3578787a395 |
| Text | 4548494f7a143e3905ddd4c5ff771fb225c155c7 |
| Desktop | 86f1b97080f9b660d9623e2237065b1810b39877 |
| Runtime | c1ce8c592e0a2c33decbb4ec86af7d4ed9f28c66 |
| Storage | fc937993f567cbaa9ac280ded1fa8f45ca922599 |
| Retained Accounts Python | c53a2f64b287b1f59bd90cdcd355766c5d713e63 |
| WordCraft bridge | a41d6f9286458a5b460b02fd2f65f2110b969d1c |
| Retained WordCraft engine source | 0d48f9a1bd5a2bb88d8431760a14b0ba55161563 |
| Public release ID | fdefcf8fd407066577426d097509d1973d0e5a02a5949308b6eb4f3d79c9f34d |
| Archive SHA-256 | ade1d6cf156d79bb7d667bd846a8a19f0d016463406392c61c110f1d63008f04 |

The release contains 244 public files including its manifest, totaling
96,893,852 bytes. Its archive is 27,441,169 bytes. All source inputs and packaged
payloads were hash-verified; 96 JS packages have notices. Text, Desktop lifecycle
wiring and shared composition/bundles changed. Viewer artwork/CSS and the
WordCraft engine payload remain identical. The engine is a
verified existing input, not a newly compiled Rust engine from the newer bridge
revision. No compiler output or private account state is committed.

The backend remains the existing service/code from the first original-viewer
release. Its retained Accounts Python was verified against installed source;
the newer delegation-policy implementation was not deployed. No backend restart
or account-state migration was performed by the Files/Text updates.

## Limits and operation

| Limit | Live setting |
|---|---|
| Individual file | 128 MiB |
| Stored space / entries per account | 1 GiB / 1,024 |
| Shared stored space | 10 GiB |
| Transfers per account / service per UTC day | 50 GiB / 200 GiB |
| Concurrent transfers per account / service | 8 / 16 |
| Payload pacing per account / service | 4 MiB/s / 8 MiB/s |

Uploads and downloads share the daily allowance, including failed/cancelled
reservations that survive restart. Static app/WASM downloads are separate.
These Files/Text changes do not alter the limits. Account files remain in the
existing private account-state/account-files area, separate from source and
public releases.

The current public root on box-webhost is
/srv/data/webos-viewer-releases/fdefcf8fd407066577426d097509d1973d0e5a02a5949308b6eb4f3d79c9f34d/public.
The backend retains loopback port 38141, its existing Python environment and
/home/dflanag3/webos-rebuild-test/private/account-state. Caddy reloads changed
only the ksu.codes static root; beta routing, services and data were not changed.
The original laptop workspace remains read-only. No external Git publication
or old host-release cleanup occurred.

The current static-only operator is deploy/viewer_static_operator.py. Its
matching root-only rollback plan is
/var/backups/webos-text-recovery-20261116-01/ on box-webhost. Explicit rollback
with tag text-recovery-20261116-01 and the current release ID restores the
preceding Files/navigation frontend, without restarting the backend. Browser
draft records are retained, but that older frontend cannot offer recovery; save
or recover open drafts before an intentional rollback. Restoring the new code
can discover retained orphan drafts again. The operator guards
configuration hashes, validates Caddy, preserves file ownership/mode and checks
process/account continuity. Do not replay init/stage/prepare over existing
paths. The preceding Files update plans use different tags and releases.

The first original-viewer backend transition had a port38140 reuse failure;
that service was recovered before successful activation on fresh port38141.
Its older backup /var/backups/webos-viewer-20261116-02/ covers a different
backend/frontend transition. Do not apply that older plan as a routine Files
rollback.

Private evidence, credentials, scripts, screenshots, commands and the resumable
checkpoint are under
/home/dflanag3/Projects/.webos-migration/text-recovery-20261116-01/.
Current reports are hosted-recovery/result.json and hosted-viewer/result.json;
unit-final.log records35 passing tests. The initial local recovery fixture
typed onto its default Save As filename, then a later fixture hit the known
clean Save As layout bug. Both failures remain with their actual outcomes;
the fixture was corrected without removing assertions or claiming fix#2.
Prior Files/navigation reports remain in files-navigation-20261116-01, and the
original Desktop/Text review evidence remains in desktop-files-text-review-20261116-01.
Earlier native-dialog evidence remains in files-upload-20261116-01. Temporary build/profile
cleanup and preserved unrelated WIP hashes are recorded in the new checkpoint.
The final archive and manifests remain outside Git. The [complete source matrix](../migration/APP-MATRIX.md)
remains the inventory of the broader, separately integrated app suite.
