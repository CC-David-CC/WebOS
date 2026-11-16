# ksu.codes — existing viewer test release

Verified on 2026-11-16: **https://ksu.codes uses the original Desktop/Workspace
viewer** from `platform/desktop/active-system/`. Its CSS, reference data and
artwork are unchanged. The narrow dark right rail has account/date at the top
and APPs at the bottom. The rejected blue replacement is no longer served.

The separate, authorized integration enables Calculator, Files, Text,
WordCraft and Help. Other menu entries are disabled; Linux/v86, Terminal and
voice are not enabled. Use End session before switching accounts. Source
organization does not imply the rest of the app suite is integrated; see the
[complete source matrix](../migration/APP-MATRIX.md).

| Hosted check | Result |
|---|---|
| Original geometry, rail order, palette and account presentation | PASS |
| Original window move, resize, minimize and restore | PASS |
| Calculator mouse/keyboard use, independent instances and close isolation | PASS |
| Files signed account listing, new folder and upload | PASS |
| Text server save and unsaved-close Cancel/Discard | PASS |
| Actual WordCraft WASM startup and formatted heading/paragraph/list | PASS |
| WordCraft acknowledged save, close and Files reopen | PASS |
| End session honors unsaved WordCraft cancellation | PASS |
| Files reopens saved Text and WordCraft documents | PASS |
| Fresh browser context retrieves the same formatted account document | PASS |
| Reload, sign-in and original layout restoration preserve the document | PASS |
| End session returns to the original login gate | PASS |
| Pre-update disposable account retrieves its exact saved file after update | PASS |
| Account-state path, issuer and instance retained | PASS |
| Beta page bytes and checked service PIDs unchanged | PASS |

The browser report contains 15 assertions covering the grouped workflows
above, with no page errors. It records aborted requests during lifecycle
transitions. Tests use real HTTPS and disposable accounts/files. They do not
qualify every app, delegated agents, a physical second machine, or every file
operation; older replacement-viewer results are historical, not acceptance of
this viewer. The same 15 assertions also passed locally.

## Release provenance

| Item | Selected revision or identity |
|---|---|
| Packaged parent source | `26083315255497570a488048d0992494d7a9fd0f` |
| Desktop | `95c7ae3ee265105758caad0ac441268a4304c3a5` |
| Runtime | `c1ce8c592e0a2c33decbb4ec86af7d4ed9f28c66` |
| Storage | `fc937993f567cbaa9ac280ded1fa8f45ca922599` |
| WordCraft bridge | `a41d6f9286458a5b460b02fd2f65f2110b969d1c` |
| Retained WordCraft engine source | `0d48f9a1bd5a2bb88d8431760a14b0ba55161563` |
| Retained Accounts Python source | `c53a2f64b287b1f59bd90cdcd355766c5d713e63` |
| Public release ID | `15e9cca46ce877315cc89e4fc53069ab942050d0b36f34de53405cd5667b868a` |
| Frontend archive SHA-256 | `70be52db35f4384a4211a737f8bbdec2f8eb04a1ee8c10e165df5e57909434b2` |
| Backend archive SHA-256 | `584140a723b2b39060604da9e6c467f0a968691b3e7d8ccdd8d3875300da2e67` |

The frontend has 244 public payload files totaling 96,843,141 bytes, plus its
manifest. The compressed archive is 27,429,647 bytes. All packaged inputs and
served startup assets were hash-verified; 96 JS packages have bundled notices.
The engine is a verified existing build, not a newly compiled Rust engine from
the newer bridge revision. Detailed component pins are in the release
manifests. The frontend manifest's older descriptive backend sentence means
the existing service/account system is retained; the companion
`backend-release.json` records the actual code update and exact backend pins.

The retained Accounts Python matches the previously installed source exactly.
The newer Accounts delegation-policy implementation was not deployed. Storage
and the test launcher apply the approved concurrency increase. Existing Python
dependencies and the private account-state directory remain in use.

## File limits

| Limit | Live setting |
|---|---|
| Maximum individual file | 128 MiB |
| Stored space / entries per account | 1 GiB / 1,024 entries |
| Shared stored space | 10 GiB |
| Transfer allowance per account per UTC day | 50 GiB |
| Transfer allowance service-wide per UTC day | 200 GiB |
| Simultaneous transfers per account / service-wide | 8 / 16 |
| Payload pacing per account / service-wide | 4 MiB/s / 8 MiB/s |

Uploads and downloads share the daily transfer allowance; reservations include
failed/cancelled attempts and survive restarts. Static app/WASM downloads are
separate. The shared browser file client admits four requests at once with
bounded waiting. It does not replay dispatched writes. Only concurrency was
increased; the other limits remain unchanged.

## Operation and recovery

`webos-rebuild-test.service` now listens on `127.0.0.1:38141`. Its code and public
assets reside under
`/srv/data/webos-viewer-releases/15e9cca46ce877315cc89e4fc53069ab942050d0b36f34de53405cd5667b868a/`.
Its existing private state remains at
`/home/dflanag3/webos-rebuild-test/private/account-state`. Only the ksu.codes
route and test service were changed. Beta services, routing and data were not
changed. The original laptop workspace remains read-only.

The first activation failed because the old listener left port 38140 briefly
unavailable after shutdown. Configuration rolled back, but restarting the old
backend also failed initially; it was restored and HTTPS health verified before
proceeding. The successful transition uses fresh port 38141, with port 38142
reserved for rollback. No account files or issuer keys were replaced.

The current guarded operator is `deploy/viewer_test_operator.py` (fresh-port
change in `a139026d`). Root-only rollback evidence is in
`/var/backups/webos-viewer-20261116-02/` on box-webhost. It retains the old
frontend and backend configuration, plus validated candidate and rollback
configurations. The operator refuses unknown concurrent configuration edits.
To undo this specific test update, run its explicit `rollback` mode for the
release above through the verified box-webhost alias. That restores the prior
test code on fresh port 38142 and its matching route, retaining account state.
It does not restore beta or the original source. Do not replay init, stage or
prepare over existing destinations, or apply older rollback plans to the new
port configuration.

Private commands, exit codes, credentials, browser reports/screenshots and the
resumable checkpoint are in
`/home/dflanag3/Projects/.webos-migration/viewer-test-20261116-01/`.
Hosted acceptance is `hosted-final/result.json`; visual evidence is
`hosted-final/correct-viewer.png` and `hosted-final/viewer-apps.png`. No raw
credentials/account data or compiler output are committed. No external Git
publication occurred. Existing host release collections were not deleted.
