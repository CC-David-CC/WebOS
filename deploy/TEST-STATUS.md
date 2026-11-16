# ksu.codes — existing viewer and Files status

Verified 2026-11-16: **https://ksu.codes serves the original Desktop/Workspace
viewer** from platform/desktop/active-system/. Its CSS, reference data and
artwork remain unchanged. Account/date are at the top of the narrow dark right
rail and APPs at the bottom. Calculator, Files, Text, WordCraft and Help are
enabled. Other menu entries remain disabled.

The latest static update fixes external-file drops, native file-selection and
cancellation handling, explicit upload feedback and the invalid My files
breadcrumb. The root breadcrumb uses a nonempty UI sentinel, mapped explicitly
to the account API's empty root path. It no longer generates Chonky's missing
ID/name errors, and clicking it returns from Documents to My files.

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

The latest hosted qualification has **8 focused Files checks and 15 viewer
regression checks**. The focused test records all console errors; the deliberate
HTTP409 name-collision refusal is classified as expected and retained in the
report. Chonky validation errors and other unexpected console errors fail it.
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
| Packaged parent source | 14c27143 (full pin in viewer-release.json) |
| Files | 70aba65 (full pin in viewer-release.json) |
| Desktop | 95c7ae3ee265105758caad0ac441268a4304c3a5 |
| Runtime | c1ce8c592e0a2c33decbb4ec86af7d4ed9f28c66 |
| Storage | fc937993f567cbaa9ac280ded1fa8f45ca922599 |
| Retained Accounts Python | c53a2f64b287b1f59bd90cdcd355766c5d713e63 |
| WordCraft bridge | a41d6f9286458a5b460b02fd2f65f2110b969d1c |
| Retained WordCraft engine source | 0d48f9a1bd5a2bb88d8431760a14b0ba55161563 |
| Public release ID | 4c4ac4f60262ee76042efb27b8fe942e03cb0e0134e6375ed2488e0b1fbf814c |
| Archive SHA-256 | bb521bedbf9d18569676c13e925fb1c30a8953284de7dfa6be996224a6587395 |

The release contains 244 public files including its manifest, totaling
96,848,520 bytes. Its archive is 27,432,099 bytes. All source inputs and packaged
payloads were hash-verified; 96 JS packages have notices. Only Files bundles and
composition/build manifests changed from the original-viewer release; the
viewer artwork/CSS and WordCraft graph remain identical. The engine is a
verified existing input, not a newly compiled Rust engine from the newer bridge
revision. No compiler output or private account state is committed.

The backend remains the existing service/code from the first original-viewer
release. Its retained Accounts Python was verified against installed source;
the newer delegation-policy implementation was not deployed. No backend restart
or account-state migration was performed by the Files updates.

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
These Files changes do not alter the limits. Account files remain in the
existing private account-state/account-files area, separate from source and
public releases.

The current public root on box-webhost is
/srv/data/webos-viewer-releases/4c4ac4f60262ee76042efb27b8fe942e03cb0e0134e6375ed2488e0b1fbf814c/public.
The backend retains loopback port 38141, its existing Python environment and
/home/dflanag3/webos-rebuild-test/private/account-state. Caddy reloads changed
only the ksu.codes static root; beta routing, services and data were not changed.
The original laptop workspace remains read-only. No external Git publication
or old host-release cleanup occurred.

The current static-only operator is deploy/viewer_static_operator.py. Its
matching root-only rollback plan is
/var/backups/webos-files-breadcrumb-20261116-01/ on box-webhost. Explicit rollback
with tag files-breadcrumb-20261116-01 and the current release ID restores the
previous direct-picker frontend, without restarting the backend. It guards
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
/home/dflanag3/Projects/.webos-migration/files-upload-20261116-01/.
Current reports are hosted-breadcrumb/result.json and
hosted-breadcrumb-viewer/result.json. Earlier baseline/failure/native-dialog
experiments are retained with their actual outcomes. Temporary diagnostics and
synthetic test files are kept separate from user files; cleanup evidence belongs
in that checkpoint. The [complete source matrix](../migration/APP-MATRIX.md)
remains the inventory of the broader, separately integrated app suite.
