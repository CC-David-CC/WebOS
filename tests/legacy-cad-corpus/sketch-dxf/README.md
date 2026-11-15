# Sketch DXF host controls

Current scoped qualification is **R9**, recorded in `signed-r9-receipt.json`: all eleven normal-loader native Arc cases, ordinary public export/lifecycle and visible File/menu controls pass. Earlier failure receipts remain historical evidence; no whole CAD gate or public deployment is claimed.

`host-stub-signed.test.mjs` is explicitly a test-only fake CAD DXF provider. On isolated fixture `20388`, desktop candidate `46a1f3322` and an existing CAD app, it exercised real host command registration and signed My files Blob writes. It verified direct `application/dxf` Blob write/sync, wrong MIME and >8 MiB rejection, new-path no-overwrite, and held fake-provider output after a changed revision failing without a server file. This does not validate CAD geometry, the real DXF Worker, the UI selected-face action or general Files behavior. Test-only app bundle `faf2651d56094ed4fcea3088f62936f2c6c74f399d8a65244e6ccd67333b44b0`. Test contexts are closed after each run; fixture is separate from live preview and other test accounts.

`signed.test.mjs` is the prepared end-to-end control for the actual CAD backend: public Point/Segment/Circle/Arc creation, independent DXF code/value parse and millimeter units, stale/missing target/no-overwrite and account denial, plus an offset XZ plane proving sketch-local coordinates, exact read-only source state, fresh-login durable reads and a close-before-delivery control. The latter holds an actual real-backend result after computation, closes the app through its visible Close control, then releases that exact result and checks no file appears. This is explicitly delivery fault injection, not a substituted geometry provider. It passed against matching real CAD r6 on signed fixture `20389`; see `signed-r6-receipt.json` for exact source/runtime pins and scoped observations. The menu route and full-sweep arcs are separate follow-ups, not part of that r6 claim.


## Real r6 signed run

The fixture uses desktop source `e289b7359` and the exact `1d2b19d5d` r6 app/Worker listed in the receipt. Its catalog contains only the newly bundled CAD app plus the retained hash-verified Files/Text bundles. The app builder was run normally against the host sources and the current runtime's static asset inventory; obsolete hashed static assets and source maps were excluded. The unchanged Manifold build receipt was retained from the preceding reviewed bundle. Packaging metadata is staged only in this isolated fixture, not silently installed in the source tree or public hosting.

Source stage, bundled apps, raw logs and temporary private fixture state are on R730 under `/mnt/data10tb/codi-real-dxf-signed-{desktop,apps,evidence,tmp}-20261105`. Preserve private account databases/keys outside Git. The raw log is `codi-real-dxf-signed-r6-20261105.log` in the evidence directory. These tests close all of their own browser contexts and disconnect from the shared CDP endpoint. They leave older fixtures `20383`–`20388` unchanged.

To reproduce, build the pinned CAD runtime, copy its reviewed runtime assets into `apps/system/jsketcher/node_modules/jsketcher-build`, refresh hashed runtime filenames in the isolated app manifest, and run `active-system/scripts/build-public-apps.py --apps jsketcher --node NODE --output OUTPUT`. Add the recorded Files/Text bundles to that test catalog. Run `tests/files-desktop-signed-fixture.py` with that `CODI_APPS_BUNDLE`, the established gateway/SDK paths and `CODI_TEST_STRICT_CSP=1` on a fresh loopback port. Run `signed.test.mjs` with `CODI_TEST_URL` and `CODI_TEST_CDP`. No accounts from any other fixture or hosting service are required.

`menu-signed.test.mjs` is prepared for the next runtime's actual visible File menu link. It uses the production marker service solely to select the known publicly authored face (does not claim pointer picking), then actual menu, prompt and confirmation controls. It will check cancellation, source-message forgery refusal, signed persistence and a concurrent file revision during the replacement dialog. It passed on r7 and was repeated successfully on r9; see the corresponding receipts.

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


## R8/R9 native Arc consumers and exact circular curves

The independent source review found that `ReadSketch` now applies the same strict
per-coordinate `1e-6` full-sweep predicate as native Arc/DXF. It derives a Circle
loop for full sweeps while retaining the authored Arc ID/type/data in native
storage. Construction circles remain in the construction collection, outside
profile extraction. Raw partial Arc vectors bypass the generic `1e-3` vertex
weld. The inspected contour joins compare coordinates, rather than requiring
shared Vector object identity; other primitives' legacy weld behavior is
unchanged. Mixed-entity near-contact cases remain separate qualification work.

The R9 short positive sweep correction constructs a degree-two rational circular
curve using endpoint and angular-bisector control points. The signed oracle reads
the actual loaded primitive's NURBS degree/weights, samples its actual curve and
tessellation, and checks its radius in the real face's world frame. It does not
substitute a reader, Viewer, curve engine, solver, Worker or project loader.

`arc-cases.mjs` declares eleven independent expectations: identical endpoints;
near-positive and near-negative full sweeps; just below the strict threshold;
at/above the threshold in both directions; diagonal full/partial classification;
and a construction full sweep. Each occupies its own publicly authored plane to
avoid unrelated overlaps. Native fixture seeding is explicit: public primitive
creation still rejects full/near-coincident Arc endpoints. The test then uses
normal signed My files load, public inspection/export and ordinary Files reopen.
Every native object remains an Arc, even when its derived topology and exported
DXF represent the full circle. DXF currently includes the construction geometry;
construction's exclusion from solid profiles is tested separately.

R8 completed first normal load, actual derived curves and all six full-only
exports, but its final fresh Files locator timed out at the default small browser
viewport. `signed-r8-receipt.json` records that partial result, not a full pass.
The R9 native control explicitly uses a 1920×1080 desktop viewport and completes
both normal opens, all eleven exports, exact native byte/hash preservation and
the second set of derived/native inspections. The original r7 native null-u0
failure and all earlier logs remain preserved.

Run `full-arc-signed.test.mjs` normally for all eleven cases; set
`CODI_ARC_CASES=full` only for the explicitly labeled six full-only cases. Set
`CODI_TEST_URL` to a fresh signed loopback fixture and `CODI_TEST_CDP` to Chromium.
The fixture still uses strict CSP and the established signed gateway/SDK. Both
ordinary `signed.test.mjs` and `menu-signed.test.mjs` were repeated against the
exact final r9 package. R9 source/bundles/evidence/private state use
`/mnt/data10tb/codi-real-dxf-signed-r9-{desktop,apps,evidence,tmp}-20261105`;
R8 uses the equivalent `r8` paths. Fixtures `20383`–`20391`, public hosting and
all private account/key custody remain unchanged. All test-owned browser
contexts close in `finally`.
