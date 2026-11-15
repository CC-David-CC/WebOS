# Signed selected-profile numeric depth — bounded PASS

Eight actual signed desktop workflow rows pass with desktop
`19396b4bee0fb99dfc330ce2b465cfb1175c2913` and combined core
`15b9607a7880eeb7cf98f9de40a3563d19a3c5a6`.
The normal core app SHA-256 is
`01f3eee8e2e0d0ccee253a33af40d47b704f04015b7f992e20a04f44ab0e27e6`.
This lane changes only the new test/staging/notes directory, with no product,
service-policy, live-site, canonical Files/Text or solver edits.

| Actual signed acceptance | Result |
|---|---|
| Public empty plane, ordinary concentric Circle primitives r20/r10, region discovery, selected depth5 | PASS; independently expected native1500π volume and bounds[-20,-20,0]→[20,20,5]. |
| `edit-selected-profile-depth`5→7.5 | PASS; native2250π and bounds Z0→7.5, same body/feature/selection/runtime and unchanged source. Exact nine authored parameters retain all fields except depth. |
| No-op and stale/invalid requests | PASS; same depth returns changed:false; stale revision, zero/negative/over-limit/string depths and extra engine field refuse without document/source/history/stream publication. |
| Shared `travel-authored-edit` undo/redo | PASS; selected-profile-depth journal entry restores1500π then2250π with intended identity and source. |
| Normal My files Save, server sync, separate fresh account | PASS; local/server hashes equal; foreign account receives404. |
| Fresh signed login, normal Files/Open, edit8, undo7.5 | PASS; native2400π then2250π; exact source/history/region/runtime retained. |
| Genuine native depth9 result held through visible Close | PASS; real volume8482.300164692442, uncommitted cancellation, pending Worker terminated, late original reply inert and host commands unregistered. |
| Fresh Files recovery after Close | PASS; saved depth7.5,2250π, source/history/selection and server hash unchanged. |

The real signed command registry exposes the five selected-profile commands;
undo/redo uses the existing shared authored-history command. No direct private
core authoring call, native file seed, source writer, wizard, AI provider or fake
successful Worker result is used. Native data is only a read oracle.

The server file hash after first Save is
`972deecc9f3c2b46165327ede0d6c465ca5de9a0f05694482f43e58e7f8487e3`.
After fresh reopen, depth8 edit and undo to7.5, another normal Save produces
**the same hash**. Cancellation/Close and the final fresh reopen retain it.
The native document is the editable source; no derived profile/mesh/native
handle is added to the selected feature's exact nine-field request.

Actual authenticated network asset hashes are verified before authoring and
after both fresh reopens: normal app, sketch/project/semantic Workers and the
explicit selected-profile native Worker/JS/WASM. `runtime-pins.json`,
`fixture-catalog.json`, `signed-receipt.json`, `pins.json` and raw build/run logs
bind the result. A separate actual signed frame/app HEAD check also records the enforced CSP headers in `csp-receipt.json`. This uses the combined artifact, not the older depth-only app.

## Fresh fixture and code-only prerequisites

Owned loopback fixture: `http://127.0.0.1:20407/`.
R730 paths:

- Source: `/mnt/data10tb/codi-selected-depth-signed-desktop-20261106-r1`.
- Combined runtime: `/mnt/data10tb/codi-cad-selected-profile-combined-20261106-r1`.
- Catalog: `/mnt/data10tb/codi-selected-depth-signed-apps-20261106-r1`.
- Private temporary parent: `/mnt/data10tb/codi-selected-depth-signed-tmp-20261106-r1`.
- Evidence: `/mnt/data10tb/codi-selected-depth-signed-evidence-20261106-r1`.

The desktop source was freshly archived from the stated commit. `stage.py`
requires the explicit **combined-pins.json**, checks its source/app and all
runtime file hashes, copies only reviewed normal dist/code prerequisites, and
generates the staging asset inventory. No previous account, user-file data,
keys, issuer/gateway state or TMPDIR is read or copied. The fixture generates
fresh service state and the driver registers fresh synthetic accounts.

Builder dependencies and the retained Manifold receipt come from reviewed
code-only r4 source
`/mnt/data10tb/codi-selected-profile-signed-desktop-20261106-r4`.
The receipt is copied only after the corresponding locked raw JS/WASM match.
This does not newly qualify Manifold. Existing
`../selected-profile/finish-catalog.py` copies canonical Files/Text public code
from `/mnt/data10tb/codi-selected-profile-signed-apps-20261106-r4`.
An independent tree comparison confirms all71 Files files and the Text file
are byte-identical. Sorted path/SHA inventories hash to:

- Files: `6415d85962c510416042d6947f3f52e81062e06af087a8c3017535e1ba6fa1dd`.
- Text: `24e9fe96be8295e3688774d5b59ce090f4f1bd16f68dc006aa0fcc4c00d68e81`.

Generated catalog SHA-256:
`d2f1eee78febd41a3b7d704424daedf5adcc14bf0d643b3be76b64c85967e67a`.

## Reproduction

Use new unique directories/free loopback port for future reruns; retained20407
stays unchanged for review. Stage a fresh checkout with this directory's
`stage.py --source NEW_SOURCE --runtime EXACT_COMBINED_RUNTIME --pins
EXACT_COMBINED_RUNTIME/.build/combined-pins.json --prior-source CODE_ONLY_SOURCE
--prior-apps CODE_ONLY_APPS --output NEW_EVIDENCE`. Its explicit source/app pin
is intentionally tied to this qualification. Build only jsketcher with
`active-system/scripts/build-public-apps.py --apps jsketcher --node NODE --output
NEW_APPS`, then run the existing finish-catalog helper with reviewed prior apps
and the new output. Generated runtime inventory/manifest stays private.

Start the existing `tests/files-desktop-signed-fixture.py` from the new source:

```sh
TMPDIR=NEW_TMP CODI_DESKTOP_FIXTURE_PORT=20407 CODI_TEST_STRICT_CSP=1 \
CODI_GATEWAY_ROOT=/mnt/data10tb/codi-beta-batch-c0465afe \
CODI_SDK=/mnt/data10tb/codi-beta-client-44da-dd8cbea7/gateway_service/client.mjs \
CODI_CADDY=/mnt/data10tb/codi-enclosure-test-caddy CODI_APPS_BUNDLE=NEW_APPS \
/mnt/data10tb/codi-mirror-sync-venv/bin/python -u -B tests/files-desktop-signed-fixture.py
```

Use the matching loopback SSH forward, repository-locked Puppeteer test deps,
Node and `CODI_TEST_CDP=http://127.0.0.1:19329/`. Run `signed.test.mjs` with
`CODI_TEST_URL=http://127.0.0.1:20407/`, `CODI_TEST_PORT=20407`, full `CODI_SOURCE`,
`CODI_EXPECTED_{APP,SKETCH,PROJECT,SEMANTIC}_SHA` from runtime-pins.json and a new
`CODI_RECEIPT` path. `csp.test.mjs` independently checks actual authenticated frame/app response headers using a fresh synthetic account. Helpers explicitly reuse the prior public primitive,
selected-profile and numeric-expression test utilities. The driver closes only
its own browser contexts and disconnects shared Chromium.

The actual signed frame/app response carries two enforced CSP policies. The
fixture's `worker-src 'self'` policy intersects the base policy, so Workers are
same-origin only even though the base policy permits blob media and lists blob
Workers. Scripts allow WASM compilation without general unsafe-eval.
The initial header probe incorrectly rejected `blob:` anywhere in the header;
its failed log/receipt are preserved. The corrected probe verifies the Worker
directive specifically, preserving the requirement while allowing legitimate
media permissions. No product/header changes were made. No router, DNS or public ports are
changed. Test-account credentials/cookies remain ephemeral and are not committed.

## Limits

This is one bounded signed annulus/depth/history/files/lifetime workflow. It
adds no human depth UI, typed binding, profile types, generated-face semantics,
export, physics or general CAD gate promotion. Core post-commit caller-loss
controls are separate source-matched receipts; this signed test qualifies a
pending uncommitted visible Close. It does not claim journal entries persist
through native save: a reopened editable model receives a new current-window
journal when edited. Native geometry/intent persistence and account isolation
are tested independently. No performance or hardware-memory claim is made.
