# ksu.codes — existing viewer, Files and Text status

Verified 2026-11-16: **https://ksu.codes serves the original Desktop/Workspace
viewer** from platform/desktop/active-system/. Its CSS, reference data and
artwork remain unchanged. Account/date are at the top of the narrow dark right
rail and APPs at the bottom. Calculator, Files, Text, WordCraft and Help are
enabled. Other menu entries remain disabled.

The latest static update fixes **reopening an already-open Text account file**.
Files activates the existing Text window by signed-in account and full confirmed
path before transferring any bytes. Desktop restores minimized/rolled windows,
selects their existing workspace and delegates focus to CodeMirror. The live
buffer, selection, undo/redo and confirmed base revision stay intact. Save As
moves this identity to the new path, including paths whose usual association is
WordCraft; opening the old path can create its own editor. Different full paths
and untitled documents remain independent. A late synchronous lookup also
prevents two Files instances from racing to create duplicate Text windows.

An existing editor is not refreshed or repinned when another browser changes or
removes its server file; ordinary Save still checks its confirmed revision.
Closing then reopening creates a fresh document. Existing duplicate windows
from an older session are not merged or silently discarded. WordCraft's
internal multi-document activation remains separate work.

The preceding update fixes **Text Save/Save As identity and Desktop restoration**.
Text publishes its confirmed path/revision through a read-only file-binding
signal. Desktop updates the same window's caption, accessibility label and
saved layout without remounting its editor. First Save binds an untitled window;
ordinary Save advances its confirmed revision; Save As changes its path. Failed
or cancelled saves preserve the previous binding and live buffer.

Restored Text layouts are historical navigation information. Text reads current
server bytes and records their actual revision, rather than permanently pinning
an old layout SHA. Explicit Files-selected launches still check their exact
selected SHA, and recovery drafts still retain their captured base revision.
Missing/unavailable Text stays identified and read-only with Retry in the same
document/window; it is never silently replaced by an editable blank note.
The initial ready promise can reject; Retry and current inspection report later
attempts instead of waiting forever on that initial rejected promise.

An already-incorrect old layout cannot reveal a previously lost Save As path.
After loading this update, reopen that file once from Files. Its server bytes
remain intact; subsequent saves/restoration retain the correct identity.

The preceding update protects unsaved **Text/CodeMirror6** documents.
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

Known remaining fixes: browser refresh still requires sign-in. WordCraft
multi-document activation remains separate. A broad failure fixture also observed
that Files' initial load error requires closing/reopening that app; Text's new
Retry is scoped to Text. These remain separate work. The recovery test's old
clean-SaveAs close workaround is removed; the saved copy stays open across refresh.
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
| Reopening dirty Text preserves instance, buffer, selection and actual undo/redo without a gateway request | PASS, local and hosted |
| Actual Files double-click restores minimized/rolled Text and selects its existing workspace | PASS |
| Save As/first Save activation identity; different folders/untitled editors stay distinct | PASS |
| Concurrent initial opens from two Files instances create one editor with truthful results | PASS |
| Changed/deleted server file does not reload or repin an existing editor; closed file opens fresh | PASS |
| Foreign-account/noncanonical activation targets refused | PASS |
| First Save, ordinary Save and Save As update caption, accessibility label and persisted path/revision | PASS, local and hosted |
| Two saved documents restore independently after refresh/sign-in; fresh context verifies all server files | PASS |
| A clean restored file accepts a newer externally saved revision; explicit selected-file SHA remains exact | PASS (browser restore and domain boundary) |
| Deleted/unavailable Text retains identity and a read-only error; Retry reopens in the same window/document | PASS |
| Failed/cancelled Save As preserves binding and buffer; delayed Save As preserves newer edits and correct recovery target | PASS |
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

The latest qualification has **11 Text activation checks,9 binding/restoration
checks,11 recovery checks and15 viewer regression checks locally and over
hosted HTTPS**, plus45 unit/lifecycle checks. Activation uses actual Files
double-click and public authorized operations, real CodeMirror focus/selection/
undo and signed server files. It includes two Files controllers racing to open
one resource, second-context server changes/removal and exact account/full-path
identity. No unexpected console/page errors occurred in activation qualification.
The binding suite verifies real CodeMirror, Desktop DOM/
layout and signed files; it includes a fresh browser context and injected read-
discovery HTTP503 failures. Its deliberate missing file HTTP404, name collision
HTTP409 and counted injected HTTP503 responses are retained; extra errors fail.
The recovery suite uses
actual CodeMirror, IndexedDB, browser beforeunload dialogs and signed account
files. Its isolated storage-failure context retains and asserts exactly one
injected discovery error; unrelated errors fail. Journal tests cover immutable
captures, ordered writes/deletion, discard races, stale-source preservation and
invalidated writers. The preceding Files release passed8 selection/deletion/
navigation checks and8 upload checks; those focused suites were not repeated
for Text activation. Their controller tests remain in the45-test run,
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
| Packaged parent source | efdae4c8ff2b3ddb9fb0ac8fde8663d561e93a31 |
| Files | bfe45472cfa1613daab1504a00984bbc19241cf6 |
| Text | 11b43118df3ee38a171e6cdb8e48be9b7e4a7d1b |
| Desktop | 0ad80f5d5528f5487036e1b36daedf660b9a2512 |
| Runtime | 2c028dde78ac901151df4adf4b2a92853329e21b |
| Storage | fc937993f567cbaa9ac280ded1fa8f45ca922599 |
| Retained Accounts Python | c53a2f64b287b1f59bd90cdcd355766c5d713e63 |
| WordCraft bridge | a41d6f9286458a5b460b02fd2f65f2110b969d1c |
| Retained WordCraft engine source | 0d48f9a1bd5a2bb88d8431760a14b0ba55161563 |
| Public release ID | 8fb54bad9028f94d998191e2c4a14658dc6a65bf0d0651a951824f1e716bfd40 |
| Archive SHA-256 | ebde9ce16a5519730b2986b5bab0d0fe1fa06311553f27fc74f0dc1a0d80e279 |

The release contains 244 public files including its manifest, totaling
96,903,235 bytes. Its archive is 27,443,472 bytes. All source inputs and packaged
payloads were hash-verified; 96 JS packages have notices. Files, Text, Desktop activation,
Runtime JS focus forwarding and shared composition/bundles changed. The Runtime
Python protocol source is unchanged from the installed backend. Viewer artwork/
CSS and the
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
/srv/data/webos-viewer-releases/8fb54bad9028f94d998191e2c4a14658dc6a65bf0d0651a951824f1e716bfd40/public.
The backend retains loopback port 38141, its existing Python environment and
/home/dflanag3/webos-rebuild-test/private/account-state. Caddy reloads changed
only the ksu.codes static root; beta routing, services and data were not changed.
The original laptop workspace remains read-only. No external Git publication
or old host-release cleanup occurred.

The current static-only operator is deploy/viewer_static_operator.py. Its
matching root-only rollback plan is
/var/backups/webos-text-activation-20261116-01/ on box-webhost. Explicit rollback
with tag text-activation-20261116-01 and the current release ID restores the
preceding binding/restoration frontend, including its duplicate-open behavior,
without restarting the backend. The browser draft schema remains compatible;
the rollback does not erase those records or account files. The operator guards
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
/home/dflanag3/Projects/.webos-migration/text-activation-20261116-01/.
Current reports are hosted-activation/result.json, hosted-binding/result.json,
hosted-recovery-2/result.json and hosted-viewer/result.json; unit-final.log records
45 passing tests. Corresponding local reports qualify the same application
payload (local-recovery-2 uses the corrected readiness harness). The first hosted
recovery attempt timed out with a clean server-baseline view beside the edited
untitled view and no console/page errors. Its typing helper had waited only for
a window to exist; it now waits for loaded state and an editable
CodeMirror surface before typing, then asserts the actual text. No application
bytes or original recovery assertions changed. That failed run is retained and
is not counted as a PASS. The live baseline reproduced the duplicate-open
problem: Files returned
opened where activation was required. Its failure is retained and is not a PASS.
Child source and the packaged runtime parent are committed to verified local bare
origins only. Final docs follow the packaged parent; no application bytes changed
after qualification. Temporary profiles/candidate cleanup, fixture shutdown and
preserved unrelated WIP hashes are recorded in the checkpoint. The final public
archive and manifests remain outside Git. Prior binding/restoration evidence
remains in text-binding-20261116-01; recovery evidence in text-recovery-20261116-01.
Prior Files/navigation reports remain in files-navigation-20261116-01, and the
original Desktop/Text review evidence remains in desktop-files-text-review-20261116-01.
Earlier native-dialog evidence remains in files-upload-20261116-01. Temporary build/profile
cleanup and preserved unrelated WIP hashes are recorded in the new checkpoint.
The final archive and manifests remain outside Git. The [complete source matrix](../migration/APP-MATRIX.md)
remains the inventory of the broader, separately integrated app suite.
