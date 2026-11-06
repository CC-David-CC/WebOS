# Sketch DXF host controls

`host-stub-signed.test.mjs` is explicitly a test-only fake CAD DXF provider. On isolated fixture `20388`, desktop candidate `46a1f3322` and an existing CAD app, it exercised real host command registration and signed My files Blob writes. It verified direct `application/dxf` Blob write/sync, wrong MIME and >8 MiB rejection, new-path no-overwrite, and held fake-provider output after a changed revision failing without a server file. This does not validate CAD geometry, the real DXF Worker, the UI selected-face action or general Files behavior. Test-only app bundle `faf2651d56094ed4fcea3088f62936f2c6c74f399d8a65244e6ccd67333b44b0`. Test contexts are closed after each run; fixture is separate from live preview and other test accounts.

`signed.test.mjs` is the prepared end-to-end control for the actual CAD backend: public Point/Segment/Circle/Arc creation, independent DXF code/value parse and millimeter units, stale/missing target/no-overwrite and account denial, plus an offset XZ plane proving sketch-local coordinates, exact read-only source state, fresh-login durable reads and a close-before-delivery control. The latter holds an actual real-backend result after computation, closes the app through its visible Close control, then releases that exact result and checks no file appears. This is explicitly delivery fault injection, not a substituted geometry provider. It passed against matching real CAD r6 on signed fixture `20389`; see `signed-r6-receipt.json` for exact source/runtime pins and scoped observations. The menu route and full-sweep arcs are separate follow-ups, not part of that r6 claim.


## Real r6 signed run

The fixture uses desktop source `e289b7359` and the exact `1d2b19d5d` r6 app/Worker listed in the receipt. Its catalog contains only the newly bundled CAD app plus the retained hash-verified Files/Text bundles. The app builder was run normally against the host sources and the current runtime's static asset inventory; obsolete hashed static assets and source maps were excluded. The unchanged Manifold build receipt was retained from the preceding reviewed bundle. Packaging metadata is staged only in this isolated fixture, not silently installed in the source tree or public hosting.

Source stage, bundled apps, raw logs and temporary private fixture state are on R730 under `/mnt/data10tb/codi-real-dxf-signed-{desktop,apps,evidence,tmp}-20261105`. Preserve private account databases/keys outside Git. The raw log is `codi-real-dxf-signed-r6-20261105.log` in the evidence directory. These tests close all of their own browser contexts and disconnect from the shared CDP endpoint. They leave older fixtures `20383`–`20388` unchanged.

To reproduce, build the pinned CAD runtime, copy its reviewed runtime assets into `apps/system/jsketcher/node_modules/jsketcher-build`, refresh hashed runtime filenames in the isolated app manifest, and run `active-system/scripts/build-public-apps.py --apps jsketcher --node NODE --output OUTPUT`. Add the recorded Files/Text bundles to that test catalog. Run `tests/files-desktop-signed-fixture.py` with that `CODI_APPS_BUNDLE`, the established gateway/SDK paths and `CODI_TEST_STRICT_CSP=1` on a fresh loopback port. Run `signed.test.mjs` with `CODI_TEST_URL` and `CODI_TEST_CDP`. No accounts from any other fixture or hosting service are required.

`menu-signed.test.mjs` is prepared for the next runtime's actual visible File menu link. It uses the production marker service solely to select the known publicly authored face (does not claim pointer picking), then actual menu, prompt and confirmation controls. It will check cancellation, source-message forgery refusal, signed persistence and a concurrent file revision during the replacement dialog. It is not yet qualified.

## R7: visible menu passes; native full-Arc loader fails

`signed-r7-receipt.json` records the independent `b249b5afb` r7 fixture `20390`.
Every packaged current runtime asset was compared byte-for-byte with r7 dist.
The ordinary public-agent/Files/lifecycle control passed again. The actual
File menu → export face DXF → themed prompt → signed My files control passed,
including cancel, forged top-window source-message rejection and preserving a
competing file revision created while Replace confirmation was open. Known-face
selection was set through the production marker service, so this is not proof
of human pointer picking. An initial menu harness used the wrong prompt CSS
class; correcting the selector required no product change. That timeout log is
retained as `menu-before-selector-correction.log`.

The separate `full-arc-signed.test.mjs` control remains failing on r7: its
explicitly seeded native Arc with coincident endpoints is admitted by normal
project validation, then ordinary rebuild fails before export. Passive
`full-arc-restore-diagnostic.mjs` observes the genuine staged
`craft.pipelineFailure$`: `Cannot read properties of null (reading 'u0')`,
`retainedLastComplete:false`. No Worker, loader, geometry provider or input was
substituted to get that diagnosis. Root owns the consumer correction. The test
now stops promptly on the explicit open failure, rather than waiting for its
older 90-second success-only timeout.

The minimal 676-byte synthetic native fixture is tracked at
`fixtures/full-sweep-arc-native.json`; it has one public XY plane, empty boundary
and constraint lists, and one Arc with `a=b=(3,-3)`, `c=(3,7)`. This fixture
contains no account or key material. The original private signed file and raw
failed/diagnostic logs remain in the R730 r7 evidence directory. The pure DXF
Worker's full-sweep support does not establish that this ordinary native-loader
path works. Preserve that distinction when reporting progress.

R7 source/bundles/private temporary state use the new
`/mnt/data10tb/codi-real-dxf-signed-r7-{desktop,apps,evidence,tmp}-20261105`
paths. Fixtures `20383`–`20389` and public hosting remain unchanged. All test
contexts were closed. No whole CAD gate or app promotion is claimed.
