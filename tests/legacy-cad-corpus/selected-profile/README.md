# Signed selected-profile integration — scoped PASS

Eight actual signed desktop workflow rows pass against CAD
`a0b363bce15e8533be17c9332b46a7e51ddeea5d` (r4) and desktop
`478970d72f5af22ea8315b03ca20265e8303319f`.
This directory owns tests, staging helpers and receipts only. No product code
or public service was changed. Overall CAD1 remains open.

| Actual acceptance | Result |
|---|---|
| Public empty plane, ordinary Circle and ignored Point; returned IDs/revisions used for discovery | PASS |
| Invalid/stale requests preserve source, history, native document and stream versions | PASS |
| Genuine semantic success held through visible File/Open, Keep editing; cancellation and late inert reply | PASS |
| Public selected extrusion, exact nine-field intent, unchanged source, independent volume/bounds/runtime checks | PASS |
| Normal My files Save and server sync; another freshly registered account denied | PASS, 404 |
| Fresh login and normal Files/Open preserve source, history, region selection and native metrics | PASS |
| Genuine positive native result held through actual Close; cancellation and late inert reply | PASS |
| Fresh login/Files reopen after Close preserves saved intent and server hash | PASS |

Circle center `(0.0005, 0)` mm, radius10 mm, depth5 mm give independent expected
volume `500*pi` cubic millimeters and bounds `[-9.9995,-10,0]` to
`[10.0005,10,5]`. Native validity reports valid, one solid. The unrelated Point
is excluded from the region. No native-file seed, private geometry writer,
wizard, AI/provider or fake successful reply is used. Native access is an oracle.

Actual signed network assets are hashed before authoring and after both fresh
reopens: normal app, sketch/project/semantic Workers, selected native Worker,
portable JS and WASM. `signed-receipt.json`, `runtime-pins.json`,
`fixture-catalog.json`, `pins.json` and `evidence/r4-signed.log` bind the result.
There is no default-engine fallback.

## Preserved initial failure

R3/20405 remains unchanged. Its test held a real successful native result, then
timed out expecting Keep editing after File/Open. An inherited Axis expectation
was inappropriate here: `projectManagerBundle.ts` explicitly rejects
`snapshotCurrentProject()` while `craft.isProcessing`. The original run did not
record the rendered error, so it is not an asserted native-Open refusal proof.
Exact failed receipt/log remain in `evidence/r3-native-open-assumption-failure.*`.

The final test uses two appropriate phases: Open/Keep editing during held
successful **region discovery** (no active modeling replay), and Close during
held positive **native evaluation**. It never bypasses the processing guard,
forces a prompt or weakens preservation/measurement assertions. Successful
messages are retained original results, never manufactured.

Root separately corrected r4 to track sketch namespace revisions instead of
unrelated project-cache writes. This signed test uses that corrected runtime;
it does not itself qualify root's separate cache-write/source-ABA controls.

## Private reproduction

Final loopback fixture: `http://127.0.0.1:20406/`. R730 paths:

- Runtime: `/mnt/data10tb/codi-cad-selected-profile-public-20261106-r4`.
- Source: `/mnt/data10tb/codi-selected-profile-signed-desktop-20261106-r4`.
- Catalog: `/mnt/data10tb/codi-selected-profile-signed-apps-20261106-r4`.
- Private state: `/mnt/data10tb/codi-selected-profile-signed-tmp-20261106-r4`.
- Evidence: `/mnt/data10tb/codi-selected-profile-signed-evidence-20261106`.

Stage a NEW checkout of the desktop source above. Run `stage.py` on R730 with
new source/runtime/output paths and code-only prerequisites from
`/mnt/data10tb/codi-axis-alias-signed-desktop-20261106` and catalog
`/mnt/data10tb/codi-axis-alias-signed-apps-20261106`. It verifies all runtime
pins, copies normal dist excluding maps, retains tracked non-static inventory,
replaces static inventory, and copies builder dependencies. The retained
Manifold receipt is used only after raw JS/WASM hashes match the runtime's
unchanged locked inputs. This does not newly qualify Manifold/provenance.

Build jsketcher with `active-system/scripts/build-public-apps.py --apps
jsketcher --node NODE --output NEW_APPS`, then run `finish-catalog.py --prior
PRIOR_APPS --output NEW_APPS` to retain unchanged canonical Files/Text code.
Generated metadata stays private; Git product manifests are untouched. Never
copy prior TMPDIR, account/key material, user files, or service state.

Start `tests/files-desktop-signed-fixture.py` from the staged source using:

```sh
TMPDIR=NEW_TMP CODI_DESKTOP_FIXTURE_PORT=20406 CODI_TEST_STRICT_CSP=1 \
CODI_GATEWAY_ROOT=/mnt/data10tb/codi-beta-batch-c0465afe \
CODI_SDK=/mnt/data10tb/codi-beta-client-44da-dd8cbea7/gateway_service/client.mjs \
CODI_CADDY=/mnt/data10tb/codi-enclosure-test-caddy \
CODI_APPS_BUNDLE=NEW_APPS \
/mnt/data10tb/codi-mirror-sync-venv/bin/python -u -B tests/files-desktop-signed-fixture.py
```

Forward that loopback port. Use new free ports/directories for future runtimes;
retained20405/20406 stay unchanged. R730 Node is
`/mnt/data10tb/codi-3mf-qualification-SrUmue/node/bin/node`. Supply repository
locked `puppeteer-core` test dependencies through local node_modules resolution.
No original-workstation account state or assets are required.

Run `signed.test.mjs` with loopback `CODI_TEST_URL`, matching `CODI_TEST_PORT`,
CDP `CODI_TEST_CDP=http://127.0.0.1:19329/`, full `CODI_SOURCE`, and mandatory
`CODI_EXPECTED_{APP,SKETCH,PROJECT,SEMANTIC}_SHA` from `runtime-pins.json`.
`CODI_RECEIPT` names a new result file. Synthetic-account cookies stay in RAM.
Helpers reuse the existing numeric-expression/signed-distance lanes explicitly.
The driver closes only its own contexts and disconnects from shared Chromium.

## Limits

This proves one signed Circle-region workflow and host lifetime/persistence.
Nested/disjoint/XZ/display proofs are separate core receipts. It does not qualify
shared authored undo/redo, dependent source regeneration, generated-face edits,
nonempty global expressions, Boolean composition, new-representation 3MF export,
or selected-profile human authoring UI. This remains an experimental public
command surface, not a completed CAD1 baseline or production engine promotion.
