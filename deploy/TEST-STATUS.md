# ksu.codes — current release pointer

The current 2026-11-17 UTC WordCraft release is documented in
[WORDCRAFT-DOCUMENTS.md](WORDCRAFT-DOCUMENTS.md): all 92 local and hosted browser
checks pass, with rich recovery, confirmed file identity and both Open routes.
Its provenance and matching rollback supersede the values below. Existing
Files/Text/Login behavior and limits remain.

The remainder is the historical 2026-11-16 release record. Its then-remaining
WordCraft activation gap has been addressed. Do not use its old current-root
or rollback values for the new release.

## Historical Files/Text/Login release

Verified 2026-11-16: **https://ksu.codes serves the original Desktop/Workspace
viewer** from platform/desktop/active-system/. Its CSS, reference data and
artwork remain unchanged. Account/date are at the top of the narrow dark right
rail and APPs at the bottom. Calculator, Files, Text, WordCraft and Help are
enabled. Other menu entries remain disabled.

The latest static update adds **server-validated browser sign-in persistence**.
After loading the update, sign in once. Refresh and reopening the same browser
profile then resume the existing registered session while its server deadline
remains valid. The existing deadline is eight hours; refreshing does not extend
it. A fresh browser profile/context still requires its own sign-in.

Accounts owns an opt-in IndexedDB store containing the bound session token,
public identity and a structured-cloned nonextractable Web Crypto key. It never
stores the password or exports that private key. Desktop receives only its
public session projection. Every restore proves possession to the existing
server, validates the new authority signature and exact identity/key binding,
and rechecks that another tab did not replace its retained record. Cached
certificate metadata cannot open the desktop on its own.

Sign-out forgets its exact browser record before server revocation. Other tabs
sharing that server session cannot restore it on refresh. An old tab cannot
delete a newer account's remembered sign-in. Invalid records/keys and expired or
revoked sessions return to the original login form. A renewal outage keeps
account views closed and retains the credential for the existing reconnect
flow. Unavailable browser storage allows a current-tab login with an explicit
warning that it cannot be remembered. Open tabs do not silently switch accounts.

Unsaved Text still warns on reload and offers account-scoped local recovery
after a successful automatic resume or explicit sign-in. No issuer/backend
code, account-state format, fixed session deadline, desktop appearance or file
transfer limit changes. Browser storage remains best effort and same-origin
trusted code shares its authority; this is not a new application sandbox.

The preceding update fixes **reopening an already-open Text account file**.
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

Known remaining fixes: WordCraft multi-document activation remains separate. A broad failure fixture also observed
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
| Refresh/browser-profile reopen resumes the same session/key after real server renewal, without password auth | PASS, local and hosted |
| Fresh context and another account have independent login, files and drafts | PASS |
| Unsaved reload recovery survives automatic login; cross-tab sign-out requires explicit reauthentication | PASS |
| Renewal outage admits no cached desktop identity and reconnects when the server returns | PASS |
| Expired retained server session; damaged metadata/private key; concurrent account replacement; uncertain logout | PASS, private Accounts fixture |
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

The latest qualification has **7 Desktop login-persistence,11 Text activation,
9 binding/restoration,11 recovery and15 viewer checks locally and over hosted
HTTPS**, plus45 unit/lifecycle checks. A private real Accounts/Login fixture
passes13 additional cases with actual IndexedDB/CryptoKey, signed HTTP and
synthetic retained SQLite expiry; its expiry operation is never run against a
hosted account. Independent Login's three-context and signed account-file's
five-context regression suites also pass, including backend restart, stale-save
refusal and owner isolation. These use the unchanged installed Python profile.

The Desktop persistence suite checks real Files/Text, native unload warning,
local recovery, a full Chromium profile restart, another account and a second
tab's normal End session. Its injected renewal HTTP503 responses are counted;
extra console errors fail. Text activation uses actual Files double-click, real
CodeMirror focus/selection/undo, signed files, concurrent Files opens and external
server changes/removal. No unexpected activation console/page errors occurred.
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
| Packaged parent source | 4efc73ff23b77f5f4a68869898169dfb32bd14f6 |
| Files | bfe45472cfa1613daab1504a00984bbc19241cf6 |
| Text | 11b43118df3ee38a171e6cdb8e48be9b7e4a7d1b |
| Desktop | dadd8602a7bda239f28b361da060f1fe56c869b4 |
| Runtime | 2c028dde78ac901151df4adf4b2a92853329e21b |
| Storage | fc937993f567cbaa9ac280ded1fa8f45ca922599 |
| Accounts browser | c8229d6cacd0af6a2837255334374108a30f1715 |
| Retained Accounts Python | c53a2f64b287b1f59bd90cdcd355766c5d713e63 |
| WordCraft bridge | a41d6f9286458a5b460b02fd2f65f2110b969d1c |
| Retained WordCraft engine source | 0d48f9a1bd5a2bb88d8431760a14b0ba55161563 |
| Public release ID | 7544838dbca89c9a2ddd4abcebc02006c98e5c44c008e4f004813020ba28e123 |
| Archive SHA-256 | e8cc7bacdf502cb0925329b72a8c13d9d8af3e9c938db835a4ebdf6f3c35c69c |

The release contains 244 public files including its manifest, totaling
96,911,356 bytes. Its archive is 27,445,407 bytes. All source inputs and packaged
payloads were hash-verified; 96 JS packages have notices. Accounts browser retention,
Desktop login composition and their bundles changed. The Accounts and Runtime
Python source remains unchanged from the installed backend. Viewer artwork/
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
/srv/data/webos-viewer-releases/7544838dbca89c9a2ddd4abcebc02006c98e5c44c008e4f004813020ba28e123/public.
The backend retains loopback port 38141, its existing Python environment and
/home/dflanag3/webos-rebuild-test/private/account-state. Caddy reloads changed
only the ksu.codes static root; beta routing, services and data were not changed.
The original laptop workspace remains read-only. No external Git publication
or old host-release cleanup occurred.

The current static-only operator is deploy/viewer_static_operator.py. Its
matching root-only rollback plan is
/var/backups/webos-login-persistence-20261116-01/ on box-webhost. Explicit rollback
with tag login-persistence-20261116-01 and the current release ID restores the
preceding Text-activation frontend, which requires sign-in on refresh,
without restarting the backend. The browser draft schema remains compatible;
the rollback does not erase those records or account files. The previous frontend
ignores the new Accounts browser store. Re-enabling this release revalidates any
retained credential with the server before opening the desktop. The operator guards
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
/home/dflanag3/Projects/.webos-migration/login-persistence-20261116-01/.
Current assembled reports: local-login-4 and hosted-login, local/hosted-binding,
local/hosted-recovery, local/hosted-activation and local/hosted-viewer result.json.
Additional reports: accounts-final-3, login-component and account-files; unit.log
records45 passing tests. One initial fixture wrongly expected file authority
construction without advertising a gateway; real file operations remain asserted
in the Desktop and account-file suites. A corrupt-key test exposed a repeatable
server400/retry path; local key-pair validation now removes that invalid record.
New Desktop tests were corrected to activate Text before Save and bring the
intended browser tab forward before UI input. Interrupted diagnostic runs and
all failures are retained and are not PASS results. Original assertions remain.

Binding/recovery login helpers now accept only the expected automatically
restored account; fresh contexts still exercise the actual login form. The
recovery account-isolation fixture forgets only its remembered login before
changing accounts, retaining every original draft/ownership assertion. No test
only backend route, credential inspector or fake storage enters the release.
Child and parent commits went only to verified local bare origins. Final docs
and the account-file inspection-shape assertion follow the packaged runtime
parent; no application bytes changed after qualification. Temporary output
cleanup and original unrelated WIP hashes are recorded in the checkpoint. One
final archive/manifests remain outside Git. Earlier Text activation, binding
and recovery evidence remain in their respective private20261116 run directories.
Prior Files/navigation reports remain in files-navigation-20261116-01, and the
original Desktop/Text review evidence remains in desktop-files-text-review-20261116-01.
Earlier native-dialog evidence remains in files-upload-20261116-01. Temporary build/profile
cleanup and preserved unrelated WIP hashes are recorded in the new checkpoint.
The final archive and manifests remain outside Git. The [complete source matrix](../migration/APP-MATRIX.md)
remains the inventory of the broader, separately integrated app suite.
