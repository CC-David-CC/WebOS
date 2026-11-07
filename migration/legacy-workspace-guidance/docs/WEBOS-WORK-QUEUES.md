# WebOS work queues and progress ledger
## User-confirmed scope revision —2026-11-06

Gate1 now covers21 exercises: E01–E16 and E18–E22. E17 hinged assembly and
assembly-specific competency C10 move to Gate2; preserve original identifiers.
Multibody parts/material regions/core3MF and linked part drawings E22 stay in
Gate1. All other qualification, beta, handoff, backup and pause conditions remain.
This supersedes earlier22-exercise/12-competency scope statements below.


Visitor networking policy, 2026-11-06: **all server outbound relaying is disabled**. Main frontend runs in explicit offline mode; preserve it and the stopped relay units. [Installed policy, proofs and changed unit pin](../research/user-egress-off-20261106/README.md) supersede prior relay enablement notes. CAD work continues; Files remains accepted.

Current mechanical integration: [signed mechanical path, remaining integration and new P0 numerical gaps](evidence/CAD-MECHANICAL-INTEGRATION-20261106.md). This checkpoint supersedes older pending-export/integration statements below; full Gate1 remains open. Filesystem-race testing is cancelled.

## Active priority — strict mechanical Join

User-approved author decision: a normal Join must produce one verified manifold
connected solid, or reject without changing the accepted model. Separate bodies
are explicit. Save the chosen result intent in feature history; do not silently
repair geometry, weld vertices, switch backends or reinterpret failure as success.
This applies to human and agent operations through the same model API. One part
may still contain deliberate material regions; this is not a one-material rule.

The common kernel-union corpus passes representation/persistence controls only.
Strict Join postconditions are integrated as CAD abb52d229, with box/Boolean
creation added to the shared bounded authored journal at 928dde9b2 and explicit
Join source-ancestry preservation at 0d815e141. Component/protocol controls and
TypeScript pass. Signed positive/refusal/UndoRedo/native-file qualification is
**pending**. The first CAD0d815e141/desktopcf97976d9 run found the startup defect
recorded below; corrected CAD224f3302d is being built for a fresh replay. In particular NoError or raw mesh-component counts
cannot certify a cavity or contact case by themselves. See Boolean contact and
persisted Join acceptance in CAD-ENGINE-GATE-1.md. A bounded implementation/proof
proposal is underway alongside region-reselection qualification; this decision
must be qualified before claiming the corresponding Gate1 feature complete.

## Corrected Join candidate: actual R2 readback

CAD224f3302d/desktopcf97976d9 closes the first-box startup reproducer in the
actual signed strict-CSP app. First-box creation, Undo to truly empty, Redo with
the original ID, and mixed box/Join/dimension chronology pass. All8 OCCT setups
pass, including face/overlap Join, edge/point/disjoint refusal, cavity retention,
operand reversal and native Save/sync/fresh Open. Four initial SMLib setups pass.

The run then stops at an over-specific SMLib point-contact error assertion:
actual JOIN_MULTIPLE_SOLIDS versus expected JOIN_NONMANIFOLD. The requested Join
was refused. Its post-refusal preservation check and the remaining four setups
were not reached, so the17-case corpus is not yet qualified. [Unchanged failure
and exact scope](../test/agent-cad-corpus/strict-join/FAILURE-R2.md).
Only this expected point-contact classification is authorized to change, with
an additional raw-native classification control; geometry/history requirements
remain unchanged for the next frozen-runtime retry. No product relaxation.

## Current candidate qualification: first-box startup defect

Strict-Join signed R1 fetched the exact CAD0d815e141/desktopcf97976d9 build,
then found a real regression in the new generic creation journal: the first box
from an empty project rejected before any Join. Startup had project generation1
but an empty Craft journal generation0 and null full-tip metadata. All17 planned
Join setups remain unqualified on that build. [Preserved failure and read-only
startup evidence](../test/agent-cad-corpus/strict-join/FAILURE-R1.md).

Candidate CAD224f3302d proposes the first journal entry only for a genuinely
empty unbound baseline, preserves the captured journal during startup, and
publishes the current-generation journal atomically with the evaluated model.
Stale/nonempty history checks are unchanged. Component/transport checks and
TypeScript pass; fresh signed replay is still required. Do not mark this fixed
from source review alone. No public deployment changed.

The optional native revolve Worker adapter and its real new/retained-kernel
component evidence are integrated. Public source-axis commands, saved revolve
feature, shared history and E13 qualification remain missing. The experiment
also exposed retained build-time bootstrap pins; those were aligned to the same
reviewed Worker source with unchanged native artifacts. This is not a default
engine promotion.

Manifold investigation retains23 actual native observations, including proper
cavities versus point/edge contacts that current public diagnostics cannot
separate. A separate native diagnostic fork is under evaluation; the active app
runtime remains unchanged and strict mesh Join remains explicitly unqualified.

## Same-feature region reselection: signed result

Frozen CADb8712790e/desktop5c5eeba80 passes six actual signed strict-CSP setups
and 30 rows: disconnected profiles, nested circle regions, compatible unchanged
Boolean child replay, incompatible fillet-child atomic refusal, an explicitly
unsupported real polygon descriptor, and closing during a genuine held native
candidate with late-reply rejection. Same feature/output IDs, mixed depth/region
UndoRedo and normal Save/sync/fresh Open/reedit are covered. Four saved-file
source/intent/analytic checks pass independently, including 2700, 625π, 750 and
998.926990817 mm³. Evidence is integrated at desktop5b9c23cdb.
[Exact scope and evidence](../test/agent-cad-corpus/region-reselection/README.md).

Typed reselection, combined source-edit/region repair, circle winding and broader
human selection remain open. This does not close E04/E05 or full Gate1. Fixture
20926 has been stopped after all readbacks; its port is closed, owned targets are
gone and shared Chrome remains available. Gate1 remains 21 exercises, 17 partial,
4 missing shared operations and 0 complete row sign-offs; E17 stays Gate2.

## Latest signed integration results

Exact CAD3cc1eede5/desktop4748c13cb passes both new bounded workflows on the
real signed strict-CSP desktop. E04/E05: explicit disjoint/nested selection,
atomic independent-loop edits, source regeneration/refusals, UndoRedo and four
normal native Save/server sync/fresh Open/reedit files. The cross-frame array
bug is fixed and passes the unchanged signed runner; root checked16 recorded
native bodies and all4 saved files (maximum volume error1.82e-12mm³).
[Region evidence](../test/agent-cad-corpus/region-descriptors/RESULTS-R2.md).

Existing driving dimensions: actual SegmentLength/DiameterLength edit/removal,
redundancy reactivation, unrelated free-loop preservation, typed length names,
refusals, UndoRedo and three native Save/Open files pass34 recorded steps.
Root independently checked3 native solid snapshots and the3 saved documents.
[Dimension evidence](../test/agent-cad-corpus/driving-dimensions/README.md).
These steps include cleanup/file rows, not34 separate CAD feature qualifications.

Fixture20925 remains root-owned for the separate engine-capability test lane;
all completed region/dimension test contexts have closed. No new beta release
or broad Gate1 signoff. E17/C10 assembly stays Gate2;21 active rows remain open.
Existing-feature region reselection is the next bounded shared workflow.

## Latest bounded result — signed document units

Frozen CADf770a52a5/desktopf4c4d63e5 passes15 signed rows: actual menu/public
unit changes, exact canonical model/mesh invariance, no new Worker dispatch,
authored Undo, window isolation/New and normal Save/server sync/fresh Open.
Root checked6 native snapshots and saved envelopes identical except presentation.
Opaque journal inspection tokens can change; targets/cursor/authored state do not.
[Evidence and remaining paint/UI limits](../test/agent-cad-corpus/display-units/RESULT.md).
Fixture20922 is fully stopped and private state/processes/port/targets cleaned.

Shared pattern commands/history/bridge are integrated. The exact combined
CAD183bd3a4d/desktop0fdc2a7f8 package (183 files,73 core assets) passed signed
full-part qualification at disposable strict-CSP fixture20923; no deployment.
The pattern test covers source/seed/count/spacing edits, creation/edit UndoRedo,
refusals and native Save/server sync/two fresh Open cycles. Root independently
checked12 native snapshots and both6627-byte native files.
[Scope, retained first-run failure and portable evidence](../test/agent-cad-corpus/source-bound-pattern/README.md).
A separate actual-browser run accepted all17 exported recipe commands and native
Save/sync. Fixture20923 is now stopped; private state, Python/Caddy, port and
owned browser targets are gone. Shared Chrome remains alive.
Atomic edits and region descriptors are merged. Region descriptors passed44
pure controls plus9 real semantic Worker cases and genuine client cancellation
checks; signed E04/E05 replay/save/reopen remains pending. Existing driving-
dimension edit/removal is a separate active P0 lane.
No new deployment or exercise signoff; Gate1 remains21 rows, E17/C10 is Gate2.

## Native format decision

[Our own `.cad` ZIP container](CAD-NATIVE-FORMAT.md) is the planned editable
format; implementation and streaming/delta-memory acceptance remain open.
Only our native project needs editable import. Other formats are exports or
optional views. Existing JSON qualification is not archive qualification.

## Current integration defects and follow-up

The signed E04 descriptor run on CAD74eb58278/desktop0fdc2a7f8 passed explicit
geographic second-region selection and native500/1000mm³ extrusions, then
refused the first valid atomic point batch. Root confirmed a realm-local
Array.prototype check at the desktop→CAD iframe boundary. Root fix3cc1eede5
retains Array.isArray, dense own data, bounds and duplicate guards. Twelve
cross-realm coordinator admission controls pass on that exact source, including
old-fail/new-admit and retained malformed-data refusals. The fresh complete app
build and unchanged signed R2 now pass this workflow (see latest result).

Driving-dimension edit/remove core99a plus REQUIRED verifier correction215f is
integrated (rootcf882/93cf), with normal desktop adapters and Craft declarations.
The old verifier accepted an unrelated free-loop displacement; two actual
negative cases reproduce that defect. Corrected verification independently
recomputes the complete transition and passes20 groups/231 terminated Workers,
including legitimate dependent motion and typed Arc travel. Root merged type
check and14 host/retained adapter controls pass. Signed downstream/native-file
qualification now passes separately on3cc1/4748; component receipts remain
identified by their own source/build scope.

## Active next slices — 2026-11-06

Pattern component/native proof and root ledger/authored operation are integrated;
shared creation/edit/journal/public Save/Open wiring is underway. Count1 remains
unsupported. Document display units core and host/menu/dirty-state integration
are implemented;33 core controls,9 host controls and type checks pass. Frozen
CADf770a52a5/desktopf4c4d63e5 built and all183 package/73 core assets match;
signed fixture20922 is now the unit-presentation acceptance path, not deployment.

Atomic multi-point edits are merged (CAD6fa489538/desktop2fac13a1b):16 new real
Worker cases,61 retained single-point cases and15 host controls pass. These are
component proofs; signed disjoint-profile replay/Undo/native reopen remain open.
Selected-region descriptors are merged (CAD06c4f85e1); callers now receive
source-bound outer/hole memberships without parsing opaque region IDs. The
component evidence and independent integration review live in the CAD repo
at test/selected-region-descriptors/. Signed public E04/E05 remains pending.
Current merged type check and24 relevant host controls pass. Files stays accepted,
filesystem-race tests remain cancelled, egress remains disabled. E17/C10 is Gate2.

## Current combined qualification — 2026-11-06

Source69a476bfa/desktop1ef1390a4, appfb9565365, passes11 actual signed
strict-CSP combined checks plus a separate trusted-touch focus control. Includes
normal single-stage diagnostics without document changes, real source-bound
plate/holes/treatments, creation and mixed edit travel, natural viewport-focused
Ctrl+Z/Ctrl+Shift+Z, rejected/accepted replacements, undone-prefix Save/server
sync/fresh Open and three stable resource cycles. Root independently checks
five native metric snapshots and the touch event/focus receipt. See
[combined result and exact scope](../test/agent-cad-corpus/creation-history/NATURAL-FOCUS-RESULT.md)
and its natural-root-checks directory. Fixture20921 is stopped; root verified
Python/Caddy, private state, port and owned targets cleaned, shared Chrome kept.

All three source lanes are integrated: creation history, exact Worker mesh
integral, and normal per-stage diagnostics. Exact-volume components pass all
five OCI paths/20 genuine meshes/Fraction oracles and retained native corpora.
Normal diagnostic components pass32 groups/58 real Workers with explicit context
doubles; signed app qualification is single-stage compatibility, not a new
multi-stage authoring claim. Source/data/rank estimates stay distinguished.

Gate1 remains21 exercises:17 partial/four missing/zero fully qualified. E17/C10
is Gate2. Next active lanes: source-relative hole-pattern Worker integration,
document display units/persistence, and focused disjoint/nested-region missing
cases. Root owns host integration and combined proof. No new beta deployment,
engine change, Files reaudit or filesystem-race testing; visitor relaying stays
disabled. Older checkpoint pending statements below retain their original scopes.

## User-confirmed stopping point — 2026-11-06

The user revised **Full Gate1 to21 exercises**; E17 assembly/C10 moves to Gate2.
Manufacturing drawings E22 remain required. First finish the beta update and tested
hardcoded agent path; then qualify the full [Gate 1 contract](CAD-ENGINE-GATE-1.md):
in-scope competency rows,21 exercises and integrated original-rectangle change
workflow. Fix failures. Missing/unsupported required functionality is unfinished,
not a pass. Test both engines against explicit capabilities without forcing
parity or silently switching kernels.

Once the exact integrated build passes, update the full matrix/checklist and
handoff, commit/back up source and required notes/prerequisites to box-git and
R730, then **pause at the user's request**. Do not pause before these conditions,
mark the larger program complete, or continue into later gates after this
stopping point. Files stays accepted unless a concrete defect emerges. Preserve
CAD2–6 plans for resumption.

## Current actual beta state — 2026-11-06

**https://beta.ksu.codes/** now selects R4
`337b69de24aa84f726a5d3cedb8f16f7ade026baa206b4faa31281ff380d827e`.
The actual protected installer completed, followed by real actor plan/apply
and two successful Caddy validations. Independent post-activation readback
matches common1868/guard36df/sitesb025/Caddyb1f1; no pending transition or
installer journal remains. Mainf2, both accepted Files floors and byte-identical
`/desktop/` are preserved. All ten configured site GETs plus beta/prototype
return their expected reachable200/protected401 statuses. This health readback
is not an app-workflow qualification.

Visible **Agent tools** now sits immediately after File. The app says
**CAD Modeler (JSketcher inspired)** and no longer exposes Donate/GitHub actions.
Panel and reusable [JavaScript examples](../apps/system/jsketcher/examples/README.md)
use the same public command helper, without an AI provider. Guarded New/Open
and committed-outcome handling are included. R4 outer bundle isd90e75bb;
inner CAD appd78d5333 and registry43a7b8cf. Eleven numerical Worker/native
asset pins remain unchanged from the qualified core.

Private functional and responsive proofs retain their exact runtime scopes:
18 Agent tools workflow rows, six independent New/Open/publication/Close
controls, exact circle-DXF and material-enclosure3MF recipes with normal
Save/sync/fresh Files reopen, and12 responsive cases. Independent reviews
qualify the R4 source/artifact closure and managed routing/operator inputs.
Actual public R4 qualification now passes18 Agent tools rows and the exact
README circle/enclosure recipes, normal Save/server sync/fresh Files Open and
independent NEW native/3MF checks. The3MF has two objects, three regions and84
triangles with expected dimensions, volumes and920mm² paired interface. See
[public prerequisite receipts](../research/beta-cad-agent-public-acceptance-20261106/README.md).
The first launcher-only test failure is retained; the test now selects the
actual menu's accessible labels, with original CAD assertions unchanged.
This clears the beta-and-agent prerequisite, not the complete Gate1. Earlier
BBC public results remain historical evidence.

Full Gate1 remains unfinished. The [current21-exercise Gate1 baseline](evidence/CAD-GATE1-BASELINE-20261106.md) records the actual public scoped passes and remaining gaps. The [Gate1 execution plan](../research/cad-gate1-qualification-plan-20261106/README.md)
separates required primitives/solver/units/regions, dependent features,
ordinary solids, linked drawings and export/native replay. E17/C10 assembly is Gate2. Missing shared
commands are implementation gaps, not passes. Execute/fix the complete required matrix and original
rectangle workflow on a coherent build. No new Files defect, main-site promotion,
kernel-default change or CAD1/2 completion is claimed.

## Private foundation integration checkpoint — 2026-11-06

The explicit polygon V3 source/preparation, native shared-vertex ancestry,
mount/factory and whole-part history/save routing are integrated in CAD
`186972b7d`; emitted WASM colocation is corrected in `86cae0378`. Both LAN CAD
repositories contain the integrated source. Native source `b66472f8` is also
read-verified on both LAN repositories. Its exact R2 build passes retained V2
rectangle/circle/annulus controls and the polygon native checks. Independent
Chrome R2 component evidence covers eight shapes,29 point classifications,
authored ancestry, refusals, cancellation and Worker cleanup. Combined routing/
journal controls29 and TypeScript pass. The private genuine polygon app now
passes14 public-command workflow rows and four independent saved-native oracles,
including depth edits/travel, source refusal/replay, normal Save/sync/fresh Open
and dependent box/Boolean replay. A clean rebuild matches all40 served assets.
CAD source3103ad78f, appea2914df, and its exact scope are retained in
`JSKetcher.git:test/polygon-profile-app-history/README.md`; root integrates its
source/evidence at63973bcb2/842ebdc2a. V2 fresh reopen and human polygon selection
remain unqualified in that slice. No public beta polygon promotion is claimed.

Typed rectangle read-only inspection is integrated `417740e35`, with a separately
pinned private signed nine-row proof. General typed mutations remain refused.
E18 is still partial. Worker-only authored edge-key reads now pass actual
Chrome: nine inputs,32 classifications, real native edge renumbering with
identical semantic IDs,14 Workers terminated. Native fillet/chamfer helper
source08b19002 passes14 bounded cases; main export6d8395a6 compiles, with direct
export qualification pending. These are component results; E11 remains missing
until shared app/history, references and geometry qualify. The current plate's
specialized ledger must genuinely share the selected-owned part/runtime before
that chain can use the new features. Beta still uses R4; main and the prototype
are unchanged. Full Gate1 remains open.

The user explicitly cancelled filesystem-race testing. Do not run or resume
those tests or try to override their review. Ordinary CAD functional checks
continue. Source packaging remains deferred until functional qualification.
Actual activation commands, retained failures and readback are recorded in
[the R4 operator notes](../research/beta-cad-agent-operator-inputs-20261106/ACTIVATION.md).

Continue the full bounded release/CAD1–6 queues. Source packaging stays deferred
until functional qualification. Older checkpoints below retain original pins
and are historical where this section supersedes their installation state.

## Active integration checkpoint — 2026-11-06

Files remains accepted within its recorded scope. No public site, default
kernel, account state or source package changed during this checkpoint.

| Bounded workflow | Status and evidence |
|---|---|
| Public selected-region authoring | Six actual cases pass on matched builds: rectangle, disk, annulus, three nested circles, disjoint regions and XZ placement. Native saves reopen in fresh contexts. CAD `test/selected-profile-public/`, integrated `95782f1bf`. |
| Source regeneration | On source `a0b363bce`, annulus outer diameter40→50 regenerates volume1500π→2625π. Unrelated Point/new-plane/Circle operations work. Invalid nesting refuses `STALE_REGION`, preserving accepted state. Fresh native replay retains both sources. |
| Currentness and cancellation | Identical project snapshot writes permit inspection success. Source edit plus undo changes versions and cancels stale work even when bytes match. Genuine late results stay inert after source change or host Close. |
| Signed My files | Eight rows pass on CAD `a0b363bce`, desktop `478970d72`, app `8ae3ddc83`, private fixture20406: public creation, exact nine-field intent, Save/sync, other-account404, two fresh Files reopens and genuine Open/Close controls. Proof `91fb9856e`, `test/agent-cad-corpus/selected-profile/`. |
| Existing mechanical workflows | Five-hole bracket, typed bracket/real Parameters UI and enclosure/material/configuration/rebind/native persistence pass on that same signed build. Both core3MF exports independently pass two objects, three regions, 84 triangles, mm units, expected bounds/volumes and 920mm² paired interface. Proof `19b97e8be`, under the signed directory's `composition/`. |
| Rejection diagnostics | Actual public tests pass eight workflows/twelve fault controls with 99 terminated Workers on source `aca23b2b3` and later `15ed6c577`. Causes describe the failed check, not proof of global infeasibility. CAD `test/admission-causes/public/` and integration-review evidence. |
| Full adversarial controls | Source `a0b363bce` passes ten getter probes, two currentness controls and 35 request/forgery/lifetime/control rows, with all 270 observed Workers terminated. Proof `186113c7a`, CAD `test/selected-profile-public-adversarial/`. The separate after-commit outcome issue is not hidden by this pass. |
| Profile edge cases | Twelve public cases pass explicit behavior/preservation checks. Independent checks verify nested volume, bounds, validity, runtime pins and disposal. Unsupported regions remain distinct from drawable entities. CAD `edca939f8`, `test/selected-profile-public-edge-cases/`. General polygons/arrangements remain open. |
| Public Boolean composition | Registered operand runtime selection is integrated. Source-matched combined `b322e02c2`/app `99d007ac` passes union/subtraction/intersection, independent lens volumes/bounds/validity and fresh native replay; exact pins in CAD `test/selected-profile-combined/capacity/`. |
| Selected-profile depth history | Integrated `99f143a2c` and independent review `3df1a4fdc` pass numeric depth/Boolean dependency, real authored travel, no-op/rejection and postcommit controls. Signed desktop `8698ffdfa` proves depth/Save/sync/foreign404/fresh Files reopen/Close on combined `15b9607a7`, private20407. Final6f01/app85d signed composition passes at private20408, integrated054a6aae4; exact current proof is test/agent-cad-corpus/selected-profile-capacity-combined/. |
| After-commit outcome | Selected/default-box/depth corrections report AbortError committed:true after publication when the caller is lost, preserving accepted geometry. Independent actual combined `15b9607a7` tests pass, separate from prepublication cancellation. |
| Generic source dependencies | Exact registered BOX/SELECTED/BOOLEAN ancestry is integrated `2e90f0d6a`. Combined `b322e02c2` passes source diameter edits through Boolean, empty-to-solid with stable ID, unrelated sketch work, rejection/journal preservation and native reopen. |
| Capacity and remaining integration | Selected worker/controller32-name and100000 cumulative-triangle component boundaries pass, including real refusals/release/readback/legacy8. First public32 run found an additional application publication-check cap8. Root `6f01a09fe` aligns that metadata cap with bounded256-entry history;33 owner/detachment/ledger tests pass, full public32 now passes with three33rd zero-Worker/zero-ID refusals, readonly-full, depth/travel and native reopen, CAD46805f9b8. Same6f01/app85d signed depth/bracket/typed/enclosure/material/3MF composition passes desktop054a6aae4. This is not a hard used-memory guarantee. |
| Box continuation | Actual combined `b322e02c2` exposed an old-default build stamped onto a new box after selected extrusion. `6e9f8bafe` continues the existing registered part build, exposes boxEngineBindings and preserves the initial default.17 pure controls pass; independent5-row public composition/empty continuation/defaultOCC/Manifold/refusal/native-reopen proof passes, CAD80297e30d. No implicit conversion or default promotion. |
| Managed beta delivery | Full beta-derived75-app artifact `bbc429…` passes actual CAD menu/title/native-file routing, editing/travel/Save/sync/foreign404/fresh Files reopen/Close while preserving the old74 descriptors and shared host/storage code. Independent artifact review `e938771ce` verifies318 files and6288 catalog assets. Exact generator/guard source `18732341b` and independent real-Caddy/guard proof `8934ad605` pass313 routes and journal/floor refusal controls. Sealed release admission now requires pinned baseline830 metadata/retained serving-root coverage and type preservation (22 tests). Corrected publisher `92f35b09f` passes18 independent real root namespace controls, including crashes/retries and exact closure; peakRSS19,440KiB. Root staged BBC on box-webhost (319files/167dirs/223,839,635B), independently checked all hashes/custody and actual idempotence. Common/guard/sites/Caddy/floors and public main/beta/prototype remain unchanged. Fixed actor `809575cf8` independently reproduces inventory79be/18files. Literal installer `609aac2c8` passes8 namespace crashes. Own-sudo correction `66013e7fc` passes actual UID1000 sudo plan/install/recover and independent-controller refusals; root reproduces sealed5de. Reviewed fixed updater atomically replaced only knownc47 code inputs and retainedc47; actual server literal sudo plan now PASS, protected5-file closure and all6 hosting/floor hashes remain exact. Whole-actor transition/recovery proof remains open. Actor/newguard remain uninstalled. Public acceptance drivers refuse before accounts until candidate activation. Only immutable code is staged, not selected. |

Reply-field fix `61a5ecdbc`, dependency classification `15ed6c577` and
sketch-namespace currentness `a0b363bce` are integrated. Each proof retains its
exact source/app/Worker pins. Later description changes or candidates are not
implicitly covered by older signed receipts. Original product and harness
failures remain in the issue/evidence logs.

Full CAD1/Gate1 and CAD2 remain open. New-profile typed bindings, generated-face
references, manufacturing export from generic outputs, broader topology,
atomic feature-history coverage and qualified managed beta delivery remain
queued. Existing material-aware3MF evidence does not qualify generic outputs.
Source packaging stays deferred until functional gates qualify.

Work continues on CAD `integration/cad-mechanical-candidate-20261105` and
desktop `integration/desktop-mechanical-candidate-20261105`; source, tests and
notes are backed on box-git and R730. Preserve the complete CAD1–6 checklist.


## Latest bounded checkpoint — signed alias composition, 2026-11-06

Files remains accepted. CAD source282c0f5ec/appc8b5e10f passes actual Axis core
150Workers/17controls and new signed host20404's16 workflow rows, including
normal Save/sync/account denial/fresh Files reopen and genuine cancellation.
See test/agent-cad-corpus/axis-symmetry/combined-alias for exact pins. This
includes the nonlinear alias correction, exact reader and Viewer disposal.
The earlier36bf signed pass remains separately pinned historical evidence.

Private selected-profile preparation/native/ledger/static-CSP components now
pass their bounded tests. Root is connecting a distinct history operation,
retaining the original source plane and unselected regions, with explicit
runtime selection and no fabricated rectangular face provenance. Public
Craft/history/parameter/signed persistence qualification remains open. ARC28
numerical/domain rejection-cause preservation is a separate active lane.
No public deployment or default native/runtime promotion; source packaging is
still deferred. Consult CAD-FUNCTIONAL-GATES.md for the current serial queue.

## Current checkpoint — combined Axis and core correctness, 2026-11-06

Files remains accepted. Combined CAD source36bf090f4/app6545abcb passes actual
AxisSymmetry core authoring, live-axis edits, refusals, exact travel and native
reopen:150 tracked Workers terminate and17 fault/lifetime controls pass. The
normal app build includes exact-coordinate reading and Viewer disposal; default
native assets are unchanged and no private webosTest helper is packaged. The
desktop adapter is integrated at708deffa5 and its eight boundary controls pass.
Fresh signed host20403 is in progress; no signed Axis success or deployment is
claimed yet. Independent offline normalization/harness composition passes228/228
mechanical tests,9/9 normalization,5/5 AST guards and TypeScript. An inherited
power-substitution algebra defect has its own correction/qualification lane;
original equation residuals remain mandatory.

The selected-profile OCC kernel component passes its native/browser corpus,
including nested and disjoint region requests, mixed holes, transformed frames,
strict data dispatch and cleanup. Public Craft/history/discovery, preservation
of unselected source regions, parametric regeneration and signed persistence
are the next serial integration work. See CAD test/combined-axis,
test/selected-profile-kernel and [current functional gates](CAD-FUNCTIONAL-GATES.md).
Full CAD1/Gate1, later gates and final managed beta remain open; source packaging
remains deferred. Native NVIDIA issue fixes are separate LAN-only branches.

## Earlier checkpoint — shared Worker dimensions and R11 integration, 2026-11-05

**Files remains accepted within its recorded scope; full CAD1/Gate1 and CAD2 remain open.** The [qualification ledger](evidence/CAD1-GATE-LEDGER-2026-11-05.md) separates the full gate from bounded drawing, parametric and native-file passes. Root combined runtime607b1ea42 (private direct20614) integrates Worker signed X/Y/projected dimensions and exact planar display preparation. Root production-browser controls pass signed dimensions, live datum edits, refusal/cancellation, exact travel/native reopen (74 main-phase Workers terminated) and13 plane/corner cases with extension fallbacks and selection. CAD test/combined-r11 holds these matching receipts. App88d65535, sketch Worker9fa5dd2f, project validator134e945d. No public deployment or default change.

Signed host20394 independently passes the public signed-distance route through Save/server sync, another-account denial, fresh Files reopen, real Open/Close cancellation and late-reply recovery; [receipt](../test/agent-cad-corpus/signed-distance/signed-r2-receipt.json). Its signed-distance-only appd79b runtime has the same numerical Worker, but predates the new plane rendering optimization. Root combined signed host20395 now also passes those controls using the exact R11 app88d65535 and matching Workers; [combined signed receipt](../test/agent-cad-corpus/signed-distance/signed-r11-receipt.json) includes authenticated served-byte pins. No public deployment. Prior R10 numeric-source/Script and native Arc/DXF scopes retain their exact pins and proofs; they do not qualify every command. Initial numeric formula bindings in that lane remain labeled native seeds.

The plane display optimization retains all2,000 models/history/views while avoiding2,000 temporary display NURBS allocations. Its separately pinned full-restore comparison measures sibling gaps311/291ms→267/261ms, not a hard general latency guarantee. ARC25 remains partial, including first full rendering cost. New signed-distance validation recomputes a bounded private candidate in a separate disposable Worker before replay; this binds native bytes/intent but adds measured Worker wall time. No claim of all active-editor processing being off the main thread.

Collinear now passes the actual Worker core and signed host20396 with app91c921bb: consumed construction geometry, signed X/Y/projected dimensions, duplicate no-op, contradiction/refusal, exact travel, genuine Open/Close cancellation and late-reply recovery, Save/server sync, account denial and fresh Files reopen. See [scoped Collinear evidence](../test/agent-cad-corpus/line-relations/README.md). Independent-axis symmetry is next in its own bounded core lane; this public adapter still refuses it. Existing UI mathematics is reused, while legacy active-editor processing remains outside these Worker proofs. General regions, broader primitives/constraints, typed/reference dimensions, persistent references, the full original-rectangle chain and remaining Gate1 exercises stay queued. Final delivery/beta follows functional qualification; source packaging remains deferred.

NVIDIA findings/fixes remain separate LAN-only issue branches, with no application kernel rollout or GitHub push: transform tolerances, mirror analytic types, sampled coincidence tuples, UV-metric validation and sphere pole/seam tessellation. CAD docs/AGENT-CAD-ISSUES.md records their separate evidence and limitations. The latter investigations are not substitutes for CAD1 qualification. Earlier checkpoint scopes below remain historical evidence.

## Current checkpoint — Worker sketch view, 2026-11-05

Files remains accepted. Private CAD runtime1c3f5dc3f / desktop1076ec10a passes actual Worker drawing/selection, shared Concentric, exact travel/refusal/close and signed Save/sync/account denial/fresh Files reopen. The new view owns no numerical PM/cache and explicitly reports omitted content and geometry-only selection. See [signed workflow evidence](../test/agent-cad-corpus/worker-view/README.md) and CAD test/worker-sketch-view plus adjacent transport/render/adversarial/performance/scheduling receipts. Signed bracket/material composition and independent two-object/three-region3MF checks also pass on the same runtime; see [composition evidence](../tests/worker-view-composition/README.md). Legacy tools, broader rendering/mechanical/reference coverage, large3D display, raw-input ownership, final release and beta remain open. No full CAD1/CAD2, public deployment or source-packaging claim. Earlier entries retain their original pins/scopes.


## Current checkpoint — 2026-11-05, replay responsiveness and cancellation

Files stays accepted within its recorded scope. Current qualified private CAD runtime427a5cda2 (R730 codi-replay-contour-20261105-r5, direct20491/signed20383) preserves signed primitive authoring, bracket variants, material rebind, normal My files Save/sync/fresh reopen/account isolation and independently checked2-object/3-region core3MF. Root actual five-hole regression and14-case exact contour comparisons also pass. Desktop test/agent-cad-corpus/primitive/SIGNED-427-20261105.md and CAD test/replay-contour/README.md hold pins and limits. No public deployment or source packaging; OCC remains default.

- [x] Removed all-line contour-pair scans and regular-grid hash collision chains without changing the14 tested contour/region/error outcomes. Dense contour preparation observed76ms→3–5ms; this is a component observation, not a hard whole-app latency bound.
- [x] Standard independent PLANE replay uses one strict staged index flush rather than rebuilding the accumulated index after every feature. Consumers/final evaluation still flush; implementation identity and legacy parameter admission remain checked. Same-face failed initialization now retries its source correctly.
- [x] Fixed an actual delayed publication bug:991 could return AbortError then later publish10,000 models. Final427 closes the exact failed temporary document after synchronous receipt rollback, binds caller cancellation to the rebuild, snapshots ownership options and preserves newer document/service ownership. The10,000-feature cancellation remains at0 models/history12s later, source preserved, all tracked Workers/engine owners/mounts released, sibling CAD live. This is not successful10,000-feature publication.
- [~] Host-invalid receipts may retain staged RAM bytes in the disposed private workspace; the documented host contract discards that hidden iframe. Separate caller-signal cancellation while host-current verifies rollback. Saved account files are not these staging bytes. Independent actual API/storage/options/cleanup controls pass with scope recorded under CAD test/review-restore-cancellation/.
- [ ] Active2D editor/cache migration, wider shared Worker commands, dense scene/view preparation, raw-input ownership, full CAD1/CAD2 acceptance and final combined release/beta remain. A2,000-independent-plane model still stalled its sibling about2s during display work, despite one index flush; do not claim large-model responsiveness finished.

Backed component candidates for the next Worker integration are Concentric70038daed and projection3deae76c7 with corrected intrinsic-hook aliasing fixd75f16676/evidencef726498a0. They are not production-dispatched in427; installed Worker3211 has no optional hook. Keep exact source/runtime scopes and the original release objective. Earlier checkpoints below retain their historical evidence.


## Current checkpoint — 2026-11-05, public primitive authoring

Files remains accepted within its documented scope. Private CAD1b2 + desktopccaec89b9 now passes actual public empty-plane/Point/Segment/Circle/Arc authoring, immutable ID discovery, invalid/stale refusal, four-step undo/redo, normal signed Save/sync, separate-account denial and fresh-login Files reopen. Signed closed-relation, bracket-family/configuration and material/core3MF regressions also pass; independent exports retain2 objects/3 regions/84 triangles. Root five-hole, multi-plane and plate/enclosure composition regressions pass. This is a real command-only basic-authoring slice, not all CAD1 or CAD2.

- [x] Primitive mutations use the existing private full-history replay, source-frame checks and atomic workspace/model/sketch-byte journal. IDs are coordinator-owned; public callers provide bounded detached data, not native source or publication callbacks. Empty creation publishes real PLANE+strict native bytes together.
- [x] Point is visible with a disposable projection and stable ID, without an invented edge/collider. All supported construction curves stay out of solid profiles. The narrow rectangle planner retains reference Point/construction geometry and refuses an extra ordinary curve rather than silently changing region intent. Candidate-module WebGL/curve comparisons and independent exact997 full-app projections, all three plane transforms, native reopen, queued capture, atomic refusal and real host-close controls pass.
- [~] Reviewer found misleading readiness after unsupported box ancestry: creation succeeded but append could not discover the sketch. Final candidate997df3dbb reuses the existing strict ancestry classifier and reserves history/sketch capacity before creation; no unknown-consumer widening. Matching app997 passes the final signed primitive workflow on20382 (server SHA6301cde9acd338c74e7b1d2942d07a9357cf6d9c4b4aedc61a3034d698ccd3ce); independent full-app readiness/projection controls also pass (CAD test/primitive-full-app-review/README.md). Synthetic controls and TSC pass.
- [ ] General entity editing/deletion and profile selection, active2D hydration/legacy processing, dense responsiveness, full original-rectangle acceptance and broader references remain. Final combined release qualification and managed beta follow. No public deployment, source packaging or kernel-default change.

CAD `test/public-primitive/README.md` records exact source/app/Worker pins, commands and limits. Initial direct20487 uses1b2; final direct20488 uses997. Desktop primitive corpus receipts record signed bundle/server/export hashes. Both source branches are backed on box-git and R730; no beta account state or keys go to main. Earlier checkpoint scopes below remain historical evidence.


The agent-authoring versus human-viewing minimums are tracked in [AGENT-CAD-USABILITY-GATES.md](AGENT-CAD-USABILITY-GATES.md); bounded factory/constraint tests do not imply general primitive authoring or all profiles.

## Current checkpoint — 2026-11-05, immutable feature history

Files remains accepted within its documented scope. Private CAD runtime `5f8d745d9dcce2f60d16e6cbee837cdf6b3ab6c8` passes the registered closed-sketch2:1 relation, dependent100x50x20→120x60x20 resize, incompatible/stale refusal, undo/redo, signed Save/account denial/fresh Files reopen and held-Worker close controls. Signed bracket-family/configuration and material-review/core3MF regressions pass; both exports independently retain2 objects/3 regions/84 triangles and expected bounds/volume/interface. See `test/agent-cad-corpus/transition/SIGNED-5F8.md`. No public deployment or source packaging; OCC remains default.

- [x] Shared evaluator computes and publishes the same privately owned, deeply frozen feature history. Privately branded immutable histories can be reused without another metadata copy. New requests and editor drafts remain separate mutable candidates. Timeline pointer is captured before awaits; failed snapshot bookkeeping releases when handled.
- [x] Independent real-Worker comparisons retain old prepared/new-feature/timeline geometry-versus-save mismatches and prove frozen5f8 consistency. A strict attempted raw record write is blocked; native requests, geometry, saved definition and fresh native replay agree. Empty first creation and repeated rewound insertions also pass. This is an application ownership fix, not an OCC/NVIDIA/Files defect.
- [x] Root five-hole edit/rejection/cancellation/Save/reopen, multi-plane source-frame/exact-travel and plate/enclosure composition regressions pass; the latter two release53/53 and13/13 Workers. The old five-hole mutation oracle now checks blocked write+unchanged depth, independently measured edited bounds and exact undo; mutable-parameter cancellation remains separate.
- [~] Broad cooperative capture preserves native10000-history/1-million-node/depth128 bounds, without whole-history serialization/hash. Single-container key enumeration can still pause; comparison alone is not atomic for arbitrary unversioned mutable/Proxy inputs. Incoming raw internal data needs trusted ownership and authoritative version/lifetime evidence. Keep ARC23 partial for this admission audit, not a blanket safety/performance claim.
- [~] Pure Point/Segment/Circle/Arc append is implemented and independently actual-Worker tested, including native constraint/generator preservation and identity/domain refusal. It is not wired to a public command/empty-plane publication/Save workflow yet.
- [ ] Active2D hydration/legacy editing, the dense514-segment responsiveness gate, public basic authoring/general region selection, full acceptance part and broader dependencies remain open. Finish functional composition, delivery and managed beta before the original release milestone can complete. Full CAD1–6 and experimental native limitations remain queued.

Current private build: R730 `/mnt/data10tb/codi-closed-sketch-transition-20261105-r6`, direct20486/signed20380. Root CAD `test/closed-sketch/README.md`, `test/closed-sketch-publication-review/PIPELINE-OWNERSHIP.md`, `test/headless-primitive/README.md` and the primitive/helper independent reviews contain exact pins, commands and limits. Main and `/desktop/` remain preserved. Previous runtime scopes below remain evidence, not current blockers to restart.

Earlier Worker foundation runtime516 is documented in CAD `test/transition-combined-516/README.md` and desktop `tests/jsketcher-transition-notify-signed-20261105.md`. Its installed-Worker Save, strict CSP, material/3MF and performance observations keep their original scope.

## Current bounded release work — 2026-11-05

The [row audit](../research/release-audit/current-reconciliation-20261105.md) and [completion table](ACTIVE-FILES-CAD-RELEASE.md#completion-audit) resolve the old bfc existing-edit, combined signed M05 and Concentric blockers within their recorded domains. Desktop 81aa proves the normal pending-export sign-out barrier, app-close cancellation and subsequent account isolation; it does not force an account switch past that barrier.

The concrete functional blocker is CAD ed87's actual 139,364-byte constrained sketch: invoke 515 ms, undo 676.3 ms, redo 766.8 ms. Follow [ARC18–22](CAD-CORE-SEPARATION.md#current-bounded-worker-first-follow-up--2026-11-05) for Worker transitions/replay, current owned publication, hydration without repeating heavy solve, shared callers and combined qualification. JSON capture alone at 10–14 ms does not fix this. New source work is a candidate until matching runtime proof. Finish the finite accepted-operation currentness review and final affected-scope audit; delivery and managed beta follow functional qualification. CAD1–6 and experimental native limitations remain separate scope.

## Previous wrapper work — retain recorded checkpoint scope (2026-11-05)

The user explicitly rejected treating the third-party SMLib wrapper restriction as the WebOS CAD limit. Keep one authored graph, sketch solver and history; retain a whole native result for an evaluation. Empty results, one solid and multiple solids/regions are distinct outcomes. No automatic engine fallback, no invented component identity and no fake native volume. OCC remains default pending the full comparison; the experimental SMLib catalog now selects our direct NVIDIA-source provider.

- [x] Direct NVIDIA provider corpus: edge/point/face/disjoint unions, cavity, genuine empty reuse, repeated through-cuts and bounded operand evidence/mesh preservation. Owner and independent root tests pass. Native source `e854d6c`, provider `ab8f97135`, corpus `9477806b8`, integrated on CAD candidate. Nonmanifold native volume is null by contract.
- [x] OCC/Manifold worker adapters:14 actual Chrome cases preserve empty and multiple-solid results; empty outputs can feed a later union. Native solid counts and mesh connected components remain different facts. Source `9d7a399ba`; no shared-app claim from this provider test.
- [x] Modern worker display projection: Float32 precision loss reports unavailable while native geometry remains valid. Main-thread publication uses transferred buffers and bounded metadata; shared-model integration is being reviewed.
- [x] Common model/ledger/commands integrated and source controls pass: canonical outputs including empties, stable IDs, typed inspection, atomic publication and shared history.
- [x] Matched0bd/1fddd app: all-three-engine empty replay/reuse, empty↔nonempty edits, rejection and shared travel. Signed public-host Save/sync/account/fresh Files reopen passes for raw SMLib0bd and OCC/Manifold1fddd. See `tests/jsketcher-solid-output-signed-20261105.md`, `tests/jsketcher-solid-census-signed-20261105.md` and CAD `test/solid-output-history/RESULT-1FDDD.md`.
- [x] OCC census42b626445 verifies true empty versus null/edge/vertex/wire/mixed topology. Matched1fddd signed bracket-family and manufacturing regressions pass; independent3MF oracles retain2 objects/3 regions/84 triangles. See `tests/jsketcher-census-agent-regression-20261105.md`.
- [~] Native NVIDIA cavity-fill issue: direct C++185ce1e reproduces wrong material/void status and volume by operand order. Scoped native fix lane active; production multi-material+void guard remains. Failed operation preserves published geometry/history and remains savable, with one intentionally skipped feature ID; strict byte-equality failure retained.
- [x] Earlier matched807 metrics test passes on all three prior backends for500→700 mm³ edit, inspection, shared travel and fresh native replay. This does not qualify the newer raw provider or arbitrary geometry.
- [ ] Multi-material plus void support, arbitrary STEP/export, full CAD1 corpus, mechanical acceptance and final managed beta qualification remain open. The original bounded release objective and full later backlog remain unchanged. No new deployment or default promotion.


## Earlier browser-agent/three-engine checkpoint — historical (2026-11-05)

Latest user direction: agent-driven browser CAD is the immediate target; human UI work is deferred. Keep the existing history, transactions, file authorization and native project model as the shared path. Evaluate OpenCascade, Native Mesh/Manifold and SMLib side by side. SMLib should become the default only after the shared agent/history/save/refusal/lifecycle acceptance passes; no default change is qualified yet.

- [x] Located RandoTechNerd/smlib-wasm and pinned its source plus NVIDIA SMLib source. A private strict-CSP worker-only build is being qualified on R730. This does not establish integrated CAD support.
- [x] CAD candidate `9e9dadf84` adds generic owned-solid display reads/binding checks for existing OCC and Manifold mounts. Real strict-CSP Chromium workers pass box6000/common3000/union9000/subtract3000 mm³, matching bounds, stale/disposed/foreign handles, public response/buffer mutation isolation and2/2 worker termination. Test: `test/webos/owned-solid-mesh-browser.test.cjs`. Display mesh is derived and never saved as design intent.
- [~] Third-engine mount, registered data-only operations and shared-history commands are being integrated in separate lanes. Initial generic box/Boolean support is not arbitrary sketch, plate, enclosure, fillet or STEP qualification.
- [ ] Real three-engine agent create/edit/reject/undo/redo/native Save/fresh replay through the same document pipeline. Record source/runtime pins, tolerances and unequal results, not a blanket parity claim.
- [ ] Broaden meaningful operations and parameters, then retest the bracket/enclosure workflows on each engine where supported. Unsupported capabilities must be discoverable and reject explicitly without fallback.
- [ ] Promote SMLib to the default only after the agreed common acceptance; persist engine/version provenance per operation and never silently reroute existing documents.
- [ ] Build our own source-pinned WASM and dependable STEP exchange. NVIDIA's public source currently establishes USD/SMLib I/O and OCCT-BRep converters, not a STEP document translator. Keep OCC available for STEP and qualify precise cross-engine conversion separately. A triangulated approximation must not be advertised as equivalent editable CAD.

The earlier9418 Save reentry/race browser gate now passes in `test/review-save-compat/ACTUAL-REENTRY-9418-20261105.md`; a later postcommit-notification correction and Circle Mirror correction have focused tests but still need final combined runtime qualification. CAD candidate9e9 includes those source changes. Current desktop candidate is not deployed; main and `/desktop/` remain unchanged. Files foundation remains accepted. The full bounded release objective and broader CAD1–6 backlog remain active; packaging stays deferred until functional gates qualify.

Ownership: root shared registry/build/controller/integration; server lane SMLib source fork/mount; browser lane existing craft-history operation integration; review lane independent numeric/agent acceptance. Heavy processing remains in workers, builds on R730. Workstation has approximately11GiB free after the user's cleanup; do not confuse this with a durable storage guarantee.

## Qualified combined slices — 2026-11-05

- [x] Files foundation remains accepted/deployed within its signed 128MiB persistence, isolation, changed-chunk, conflict and recovery scope. No new Files-service defect is established.
- [x] Combined runtime CAD `b2a66ca86` / desktop `82bef8323`: existing dimension edits reject conflicts atomically; actual stale dialogs refuse to overwrite a later edit. Valid edits, rollback/retry, undo/redo and native restore pass. The earlier bfc counterexample is fixed in this bounded path.
- [x] Explicit centered-hole parent repair passes signed Delete, inspected begin/repair, refusal, unresolved undo with stale-display provenance/Save refusal, redo, unrelated enclosure materials/review, normal Save, account isolation/positive control, fresh Files Open and close cancellation. General ambiguous/split-reference repair is not claimed.
- [x] Configurations and held v2 Worker close pass again on the exact combined signed fixture. Independent checks of both configured 3MF exports preserve two print objects and three regions.
- [x] Actual tool-cleanup faults release history, editor context/streams, listeners and pick ownership; replacement entry is refused during exit; clean reopen/resize work and saved bytes stay unchanged. The injected b285 failure and exact b2 positive are separately recorded.
- [x] Near-1MiB real history workflow passes five edits, undo/redo, complete native reopen and history release. Entry charge 8,306,560bytes/2 snapshots; this is not a heap bound. Undo still produced 403ms/heartbeat461ms, so full worker-first/performance work remains open. No 128MiB CAD-document claim.
- [x] Desktop 64 command-boundary tests and core/independent history controls pass. Exact evidence/commands: `tests/jsketcher-combined-core-b2a-20261105.md` and `tests/jsketcher-parent-repair-signed-20261105.md`.
- [x] All 13 affected carried browser/engine controls pass on b2. The missing test-only helper was rebuilt from exact source on R730; its hash and commands are in tests/jsketcher-b2-carried-regressions-20261105.md. Thin-intersection results still differ between engines; no equivalence or physical-phone claim.
- [ ] Mutation audit identified a concentric exception: a rejected relationship is deliberately retained by the old path. Unify it with the common atomic transaction/revision boundary. Diameter's separate transaction/guard path needs bounded review before broader claims.
- [~] Truthful local solver diagnostics remain research. Rank/equation count is not a general logical-redundancy, global satisfiability or physical-DOF certificate. Finish revision-bound plain-data Worker integration and explicit unavailable/degenerate/numerical-failure reporting.
- [ ] Complete mutation/currentness and worker-first capture/performance gates, final functional review, then source/runtime delivery and managed beta. Packaging remains deferred. Main and `/desktop/` are unchanged.

Lead integration includes these qualified b2 slices. CAD3b8886e59 is runtime-equivalent to b2; desktop source after82 changes tests/docs only. Source/tests/notes are backed on box-git and R730; verify latest branch refs before resuming. Root owns shared integration/deployment, server lane owns readonly diagnostics, browser lane owns carried regressions, review lane owns current mutation inventory and scoped concentric unification.

Signed20350 was stopped gracefully and its private ephemeral account/data tree removed after all checks. The exact bundle/dist remain on R730. Direct20441/CDP19329 were live during qualification; verify processes and hashes before reuse. Earlier fixture handles below are historical. Full bounded objective and later CAD1–6 backlog remain active.

## Active next candidate and blockers (not deployed)

Current cbb148326 browser qualification: actual client/installed Worker40 registered-case successes+2 typed cases+8 refusals,51 Workers all terminated with real cancellation and no CSP/unhandled-rejection violations. Root13 carried runs (11 UI/lifecycle plus2 engine controls), six primitive tool shapes → validated Save/native restore, and async no-op/held-close all pass. Actual OCC washer face also passes changed Save/native replay and point coincidence to a real circular-boundary center (`research/diameter-regeneration/cbb-curved-face.md`). CAD receipts: `test/mechanical/CARRIED-CBB1-20261105.md`, `test/review-save-compat/BROWSER-WORKER-CBB1-20261105.md`.

New concrete blocker: actual direct editor.save succeeds, then another actual edit in the same editor causes Save-and-Exit retry to falsely refuse because its private entry capability still binds the pre-save baseline. Draft and prior saved bytes remain safe; reviewer is fixing capability rearming only after its own verified atomic commit, with foreign/ABA guards retained. Staged segment-Mirror prototype is under root review; complete child ownership must reject future-stage Bezier/spline references before admission. No staged/Mirror full app/native proof or release claim yet. Full original objective stays active.

Newer preliminary runtime `6f3c28790` passes signed E-name multisource propagation and ordinary/no-op Save (`research/diameter-regeneration/6f3c-signed.md`). Root independently passes actual served-Worker E/Math16→18; desktop and390px emulated-phone spline creation/edit/history/awaited Save/native restore; and corrected valid near-1MiB large-label Save/reopen. Complete authored text survives; Canvas sees≤512 units. Sampled longest task51ms/heartbeat57ms, not a hard bound. The old tiny-line fixture had snapped to zero-length segments; the new Worker correctly refused it. The corrected test asserts100/200mm initial lines, and the primitive-tool degeneracy gap remains open. CAD receipt: `test/mechanical/COMBINED-6F3C-20261105.md`.

Combined source `cbb148326` additionally integrates all registered-schema/ellipse/Bezier Save validation, shared unsigned-distance domain correction, and analytic curved boundaries/Circle-generator ID fix. A matching private app+all-Workers build is running; actual native washer-face Save and broad Worker/browser checks are next. These source-level changes do not yet close the compatibility release gate. Multi-stage/Mirror provenance work remains active. No beta deployment or source packaging.

- Lead b2 remains qualified within its recorded scope. Preliminary combined runtime CAD `ae579c93a` / desktop `55d3662b4` now passes actual async Save and signed ordinary/multisource parameter regressions. D12→14 updates the stored circle6→7 without reload; wrong units/zero/negative values preserve accepted source, sketches, journal, model and server bytes. An unrelated public five-hole plate and second D2 sketch remain unchanged. Undo/redo, normal Save, fresh Files/editor reopen and account controls pass. See `research/diameter-regeneration/ae579-signed.md`.
- Root independently proves actual no-op Save exact bytes/key version/no Worker, duplicate Save and active-tool refusal, real driving-length Worker validation, and close-during-held-Save termination/history release. Signed fresh Files Open → no-edit Save-and-Exit keeps native/source/server bytes equal and host dirty=false. See `tests/jsketcher-async-save-ae579-20261105.md`. Retained b4 D0/D14 and0b9 false-dirty failures are historical negative controls, not active failures in ae579's qualified domain.
- Integrated transaction bounds remain64 records,1MiB/sketch,4MiB aggregate inventory and8MiB conservative journal, distinct from My files limits. Supported affected sources/frames are validated before one parameters+workspace+models+journal publication. Unknown/implicit references refuse. Public parameter/travel arguments remain unchanged. Await migration covers120 calls/53 files; syntax/Babel/await audit passes, only recorded runtime subsets qualify.
- RELEASE BLOCKER: universal changed Save exposes missing carried geometry/schema coverage. Bounded B-spline candidate `db82b0d91` passes real Worker controls, but full app Save/native reopen is pending. Remaining registered constraints, ellipse/Bezier, curved boundaries, stages and generators are under implementation/review. Do not hide routine save regressions as completed compatibility.
- Separate ae579 failure: physical name E is accepted but Worker Save rejects it. Root's external-binding fix preserves E/Math engineering names and legacy constants/name rules; both real Worker and signed6f3c proofs now pass. Root also retains complete large-label text while bounding Canvas preview to512 units and aligns the Worker string ceiling with the1MiB sketch cap. Actual corrected huge-label Save/reopen/paint assertions now pass on6f3c. Prior0b9 Canvas profile remains retained on R730.
- Independent retained0b9 configured3MF selected/reopened oracle passes: two objects, three regions,84 triangles, expected dimensions/volume and paired interface. This does not imply arbitrary geometry, printing, physics or full CAD1 acceptance.
- Three agents own spline/curved-boundary core, other curve/schema compatibility, and signed browser fixtures. Root owns shared integration/review, large-label/name fixes and independent tests. Source/tests/notes go to box-git and R730. No new deployment or packaging; full original release objective and later CAD1–6 queues remain active.

## Historical b3 checkpoint — accepted only within its receipt scope

- [x] CAD runtime `b3ccb284b` / desktop `680f79d88` is independently qualified and promoted to the lead integration branches with later test/receipt commits. CAD source checkpoint `38468797e` includes the independent composition review. Source is backed to both LAN repositories; no new CAD deployment.
- [x] Typed original-sketch entry and invalid-Angle-save counterexamples are fixed. Lead actual annotation edit/undo/native restore and invalid width/NaN/Infinity/1e309 rejection pass; Save preserves the prior valid angle.
- [x] Six strict-CSP signed regressions plus public rigid create/pose/refuse/dissolve/recreate/Save/fresh Files reopen pass. Independent oracles pass three material-aware 3MF files. 58 desktop command-boundary tests pass. Full scope, exact bundle/hashes and reproduction: `tests/jsketcher-b3-combined-signed-20261105.md`.
- [x] Exact-build carried splines/DXF/history/selection/touch and bounded OCC/Native Mesh tests pass (`8205bff37`). Rigid bounds/whole-entity controls (`adf3f7a02`) and typed/common/material/placement composition review (`eb320d5e3`) pass. Do not infer engine equivalence, physical phone or generic profile support.
- [~] Configurations at `e3c65523c` have isolated Worker/core/native UI/bracket+enclosure/3MF research evidence. Root owns desktop adapter/signed tests; storage_review owns combination and selected-v2 typed-dependent evaluation; storage_browser owns independent configuration review; storage_server prepares signed acceptance tests. Configurations are not integrated or released.
- [ ] Complete mutation inventory, worker-first capture/performance, final functional/release audit and managed beta remain. No full M02/M03/M04 or CAD1 completion. Packaging stays deferred until functional gates qualify. Main and /desktop unchanged.
- [x] Removed 605.1 MiB of identified obsolete compiler dist/.build outputs from inactive clean test worktrees after tracked-file/process checks, preserving source/dependencies/evidence. Workstation still has limited space; large builds use R730.

Current runtime fixture: signed20263 (root session58092/tunnel13490), direct20260/CDP20261; signed CDP19329. Verify processes before reuse. Exact b3 dist is R730 `/mnt/data10tb/codi-7102-qualification-20261105/dist` despite its historical directory name. Older status below is superseded only within this accepted bounded scope.

## Current focus — supersedes historical checkpoint status

The bounded Files foundation is accepted and deployed; CAD is the active work. No new Files-service defect is established. CAD replay/Save reliability and the remaining mechanical, parameter, shared-command and final combined-app gates remain open. The signed three-region enclosure/core-3MF workflow passes within its stated domain. Source packaging is deferred until functional gates qualify. See [CAD-FUNCTIONAL-GATES.md](CAD-FUNCTIONAL-GATES.md); the full original objective remains unchanged.

This is the operational queue for the complete WebOS program. **Use and update this file whenever work is started, tested, integrated, deployed, blocked, or handed off.** Preserve the full scope below. Add discovered work to the appropriate queue; do not remove an unfinished item merely because a prototype exists.

For separate app/domain assignments and their ordered finish lines, use
`docs/WEBOS-SILOED-WORK.md`. That decomposition separates browser storage,
server storage, synchronization, desktop/app ownership, JSketcher upgrades,
geometry engines, manufacturing metadata, 3MF, physics and operations. The
planning documents do not themselves resume development.
Estimated effort, risk and working/partial/missing fields are in
`docs/planning/SILO-MATRIX.html` (also Markdown/CSV/JSON). Estimates do not
check off acceptance gates; use their stated assumptions and dependency notes.
The J01 estimate was corrected after verifying existing fork history: upstream
main/surfacing integration and many adaptations are already present. Remaining
J01 work is consolidation/regression qualification; see the corrected checkpoint
in `docs/JSKETCHER_UPSTREAM_WORK.md`. New mechanical CAD features remain J02.

## Historical candidate hold — 2026-11-05 (resolved within b3 scope)

- [x] Lead independently repeated clean CAD `185e1b9d3` / desktop `40d06d10d`: collinear/axis UI and real drags, role conversion, failed-rollback recovery, typed bracket propagation, six signed workflows and independent enclosure 3MF oracles pass. Exact scope and fixture identity: `tests/jsketcher-185-release-hold-20261105.md`.
- [ ] **Release blocker:** ordinary sketch entry with typed parameters fails on 185 (`361c90a91`). Interim bridge restores entry/editing, but independent review `b200e20fa` proves an invalid Angle annotation edit can mutate and Save despite the error. Fix rejection-before-mutation, finite values, typed dependent empty/unchanged-boundary replay and currentness; then run final combined signed/browser qualification. Passing command tests do not waive ordinary UI failure.
- [~] Whole-entity fix candidate `2f153907b` / desktop `402841a4c` and rigid groups `8645e7777` require combined review/qualification. Common bracket/enclosure/material/3MF candidate `c686fdbf3` has owner signed UI/agent passes (desktop receipt `d75be49fe`); independent root review remains. Configurations and worker-first capture/performance remain open.
- [x] Identified unused Cypress 4.12.1 binary download cache removed after checking no Cypress process; 603.8 MiB recovered, source and installed dependencies preserved. Fully integrated clean disposal checkout retired with Git worktree removal. Workstation is still tight; use R730 for large builds.
- [ ] Accepted lead stays CAD `36ac6cff3` / desktop `b27d3bed1` until the release hold is fixed. No new CAD deployment; preserve main and /desktop. The older combined acceptance below retains its original runtime scope.

## Historical 288/f3 integration — 2026-11-05

- [x] Combined CAD runtime `28870335` and desktop runtime `f3b50ad9c` independently pass signed bracket, native Undo/Redo menu, typed extrusion UI/command, length relation and signed X/Y/projected commands through Save/sync/fresh Files reopen. Actual frame disposal, closed-CV identity, affected real Workers and desktop/390px parameter panels pass. The combined material/enclosure 3MF regression and independent mesh/XML oracle pass. See `tests/jsketcher-mechanical-combined-20261105.md` and its digest JSON. No deployment or full CAD1/M02/M03/M04 completion is claimed.
- [~] M02: qualified signed X/Y/projected UI, public desktop commands and matching Worker paths. Collinear/independent-axis symmetry are in a separate active lane; whole-entity fixing and rigid groups remain. Tested ABA/hidden-parameter invalidation passes, but the complete mutation inventory and worker-first snapshot performance remain open; exact bounded UI-thread serialization is retained.
- [~] M03: qualified simultaneous physical length equality/ratio/difference, EqualLength Worker compatibility and reference-only measurement. Explicit promotion/demotion and rollback-failure recovery are under separate qualification. Other measurement domains and rank diagnostics remain open.
- [~] M04: qualified typed definitions, formula/unit errors, named extrusion depth, atomic publication, authored undo/redo, public UI/agent and signed reopen. Shared rectangle/hole/enclosure bindings and configurations remain active work. Shared definition edits must update every supported dependent sketch and feature atomically, including when invoked through the existing depth API.
- [x] Parent-owned settlement fixes destroyed-iframe promises: actual Save token release and exactly-once Open snapshot release pass. Unknown write outcomes are not retried or labeled uncommitted. Files core was unchanged. Identified npm download-cache cleanup recovered 1,484 MiB; source/installed dependencies were preserved and large builds use R730.

The immediately following entries describe preceding research checkpoints; their pending states are superseded only within the combined acceptance scope above.

- [x] Native authored Undo/Redo menu and keyboard actions are integrated through CAD `24d52ae8`. Root independently repeated actual menu/key/input/editor/busy/failure controls, strict-CSP signed bracket menu undo/redo with fresh Files reopen/account denial, and synchronous reset recovery. Desktop signed receipt is `77f864683`; no deployment. Feature-cursor navigation remains separate.
- [~] M03 research `61fb21b1` introduces the common simultaneous physical length relation and corrects EqualLength to use physical magnitudes rather than signed polar parameters. Nine lead solver/native controls and TypeScript pass; independent review and actual UI/ID/Worker qualification continue. This is not a completed M03 gate.
- [~] M04 research includes worker-evaluated unit-aware quantities and actual typed-source native restore with named extrusion depth; atomic apply/edit/journal and shared interfaces remain under test. A source codec or evaluator alone is not usable parametric editing.
- [~] M02 `0009f5f3` / receipt `56234654` has owner real selected UI, editors, undo/reopen, contradiction preservation and strict-CSP sketch Worker passes. Revision guarding still performs a bounded exact snapshot on the UI thread; measured cost grows with document size. Preserve broad shape correctness rather than narrowing availability. The shared transitional guard does not detect all ABA/hidden-parameter changes; authoritative mutation versions and worker/performance qualification remain open.
- [~] M04 internal core `a1460db9` has owner actual centered-hole plate parameter binding/formula edit, undo to prior numeric/empty source, redo, invalid-unit refusal, held-worker/dependent-cut cancellation, coherent expression/model observations and native reopen. Public UI/agent and final signed qualification remain outstanding; this does not qualify all parameter domains or fields.

- [x] CAD `d6253ea9` is now promoted to the lead integration branch. Owner and independent lead runs of the exact-source signed command-only bracket gate both passed: discovery/create, rectangle/depth/hole edits, true authored undo/redo, rejection, Save/sync, second-account denial and fresh Files reopen preserving IDs, dimensions and measured geometry. Test/receipt integrated through desktop `28d2ccb6a`; see tests/jsketcher-agent-bracket-signed-20261105.md. No private authoring helpers were used.
- [x] Rectangle journal cancellation/no-op corrections `ce55c687` passed actual five-hole worker fault controls. Autosave token fix `70aebd73` passed real open-dialog submission after two scheduled cache saves; authored rewrite/ABA still refuse stale submit (`c6036aac`). Lead also passed 17 journal/revision/capture controls and TypeScript.
- [x] The native 3D authored Undo/Redo gap from this checkpoint is closed within the bounded worker-plate domain by the later `24d52ae8` acceptance above.
- [~] Next independent mechanical lanes: signed X/Y/projected driving dimensions with explicit live-direction domains (M02), and worker-evaluated typed quantities/parameters with atomic candidate publication and persistence (M04). Both are isolated research until their actual shared operations qualify. M03 and broader mechanical coverage remain open.

Earlier integration snapshots below retain their original source scopes; the signed pass above supersedes their pending combined-acceptance status.

- [x] CAD lead `70aebd73` includes original rectangle dimension discovery/editing, full-tip extrusion-depth undo/redo, early initialization-failure reporting, and cache-independent authored namespace revisions. Desktop `defb370bc` includes the actual desktop/emulated-phone rectangle dialog and startup-failure receipts. These are scoped component passes, not the final command-only signed gate.
- [x] Desktop `bbb377ebd` adds bounded published geometry inspection, authored undo/redo and centered/corner-hole editing adapters. Lead ran 13 command boundary controls successfully.
- [~] CAD candidate `4215009d` combines rectangle sketch travel, depth/hole journals and the shared hole wizard, with bounded retained strings/capture. Lead ran 15 pure journal/revision/capture controls and TypeScript successfully. Owner Chromium/OCC hole/depth receipt `3f7373c9` qualifies source `ef676d45`; it does not qualify the newer combined candidate automatically.
- [~] Actual combined rectangle controls passed resize, exact-byte undo/redo, descendant geometry and Save between edits. Cancellation preserved state but returned the wrong error class; its correction is under test. Same-dimension no-op and held-dialog autosave controls are pending. Do not promote this candidate merely from the partial run.
- [ ] Run the full signed command-only bracket acceptance on the final matching CAD/desktop build, then affected combined regressions and managed beta qualification. Broader mechanical/parameter gates remain open. No new CAD deployment is claimed.

## Earlier bounded acceptance — 2026-11-04

- [x] Grouped Equal Length/Radius/Coincident undo boundary and atomic conflicting-group refusal integrated through CAD `6d34d820`; five lead focused controls pass, owner real-browser scope is recorded separately.
- [x] Bounded actual-window close/in-flight worker cancellation and other-window isolation tests integrated as CAD `bfb0fe56`; intermittent second-window startup remains unresolved.
- [x] Supported Save source `ae356553b` plus full-document revision `08e43c19` pass the rebuilt signed save/sync/fresh Files reopen gate, stale material/surface and changed-file-version controls; integrated receipt `baf2dd33c`. CAD `1ec4468d` fixes the default validator build and root actual strict-CSP Worker controls pass.
- [ ] True authored edit undo and original-sketch dimension APIs remain open. Separate worker prototypes have initial passes; UI/agent wiring, fault checks and combined signed qualification remain. See CAD-SHARED-OPERATIONS.md.

- [x] Scoped ordinary signed bracket integrated at `5988dbd8e`: edited five-hole model, rejection, undo/redo, actual Save and fresh Files reopen/account denial pass without diagnostic pre-Save preparation. Original blanket-interception stalls remain unproven.
- [ ] Full supported agent bracket remains: private helper sketch/history edits are insufficient. Three current lanes cover mechanical action history, shared UI/agent edits and independent-instance worker disposal.

- [x] Signed combined V2 export receipts/tests integrated as desktop `bd74ed906`
  and CAD `df27a17d`. Root independently reran the committed XML oracle on both
  actual signed files; hashes match the receipt. Both revisions have two print
  objects, three material regions, 84 closed triangles, expected bounds/volumes
  and lid/insert alignment. Final serialized run also proves fresh-session exact
  reads and second-account 404. The acceptance matrix now records bounded
  enclosure/material/3MF passes with those scopes; no release completion claim.
- [ ] Combined bracket regression creates the five-hole plate, edits dimensions
  and depth, rejects a touching-hole edit, and undoes/redoes. Its final Save did
  not advance file bytes; storage_review is capturing actual refusal/status
  before diagnosis. Prior held-message and input-selection test-harness failures
  remain distinguished from product failures. No packaging while this gate is open.
- [ ] storage_server is exercising existing beginner block/washer functionality
  (A00), not adding a new engine or feature catalogue. Source packaging stays
  deferred until the functional gates qualify.

- [x] Root actual combined `15a7e2a5` V2 core workflow produced a 6,941-byte
  3MF at `/tmp/codi-root-v2-functional.3mf`. Independent ZIP/XML checks pass:
  millimeters, two build objects, three material/appearance regions, 84 oriented
  closed triangles, expected body/lid/label bounds and volumes, identity component
  transforms, and BODY separate from grouped LID/LABEL. This is native/core
  export proof; signed desktop V2 export/recovery is still being tested.

- [x] V2 signed native material persistence integrated as `3c6ab428d` from
  `8ff159d92`: UI/shared-command assignment, matching local/server Save, fresh
  Files reopen, width edit, stale-save refusal, rebind retaining IDs, second
  Save/reopen and other-account denial. The passing fixture rebuilt its matching
  validator; the copied old validator's failed open is not a product diagnosis.
- [x] Root independent exact-combined `15a7e2a5` runtime controls pass V2
  create/edit/undo/redo/native replay/rejected edit/cancellation and real-pointer
  Push/Pull commit/Escape. Index SHA c35bce15493022ef28d0aa8b8d503f3bea4deeb980f4b1a3a8013e14515758bf.
  Signed three-region export and bracket regression are running on that build;
  source packaging remains deferred until functional gates are qualified.

- User priority correction: finish functional gates before source packaging.
  Root discarded the pending prepare.py packaging edit. Source archives,
  packaging/provenance expansion and new command-catalogue work are deferred.
  Combined CAD `15a7e2a5` contains V2 authoring/materials, paired-interface
  consumer and native check, autosave fix and Push/Pull Escape fix. TSC passes.
  storage_browser is rebuilding every runtime worker from this exact candidate
  and testing create/edit/save/fresh reopen/three-region export end to end.

- [x] Signed V1 manufacturing receipt integrated as desktop `84f6299b0`; CAD
  tests integrated through `27264b6c`. Both actual signed files match recorded
  hashes and pass root's strengthened independent component-graph/identity
  placement checks. Duplicate mesh references, translation and cycles refuse.
  Raw outputs are backed on R730; this remains two objects/two regions, not V2.
- [x] Surfacing capture invalidation source integrated as CAD `17cc1596` /
  `23fa4b38`, with no-op/reentrant browser receipt through `3b38261b`. Root
  reviewed mutation fences and TSC passes; source guards both sides of mutation.
  Agent now tests actual Push/Pull pointer/cancel. That test found Escape could
  commit typed distance on blur; a fix is being qualified. Surfacing's lack of
  a dedicated undo stack is explicit, not a claimed mechanical-history feature.
- [x] Root separated print-grouping checks from native contact proof and ran
  ten grouping/lifecycle controls. Wrong label placement, separated label,
  cross-feature pairing and merged body/lid refuse. No contact inference from
  matching transforms is permitted.

- [x] V2 authored history source integrated as CAD `0731e605` from `cc499ab8`.
  Root reviewed atomic role publication/versioned identity and passed five
  display controls (documented webpack harness), six material controls and TSC.
  Agent's real-history browser receipt covers edit/undo/redo/native reopen,
  invalid-edit preservation and held-worker host cancellation. Signed V2
  material/history persistence remains to qualify.
- [ ] Root V2 exporter consumer `a6bbca25` requires same-feature LID/LABEL in
  one object, equal placement, and the exact mount-bound interface proof.
  Six lifecycle controls pass; missing or mere zero-volume proof refuses.
  Actual native contact proof and complete three-region output remain pending.
- [ ] Immediate V1 export retest after `6ff03e0f` passes in the agent's actual
  strict-CSP fixture, including cancellation/stale refusal and edited/rebound
  re-export. Agent's independent Python ZIP/XML oracle checks two objects,
  materials, mesh closure, dimensions and volume. Await committed receipt and
  signed desktop export; do not count this as V2 manufacturing acceptance.

- [x] Root identified the initial export invalidation as a queued history autosave
  rewriting the workspace after an explicit snapshot. CAD `6ff03e0f` consumes
  that pending timer in explicit `projectService.save`; later edits still get
  their own timer/revision. TypeScript passes; immediate-export/cancellation and
  real-edit negative controls are being rerun by storage_browser, without delay.
- [x] Versioned inset worker research integrated through CAD `19de82fd` from
  `f9c56e58`. Root reviewed capture/triple ownership/common-volume semantics and
  ran 20 integrated controls; both historical V1 3MF writer checks also pass
  with available jszip. This does not qualify V2 manufacturing export/contact.
  storage_server owns the explicit V2 history/UI operation and contact proof;
  root owns material grouping/export integration. No deployment.

- [x] CAD `88462732` adds V2 assignment/schema/discovery/UI groundwork: LABEL
  remains a distinct region within the LID printable object, with body separate.
  Six assignment controls and TypeScript pass; actual V2 history/material UI is
  not qualified yet. Desktop `0eff85164` accepts the optional label through the
  same shared command (five command tests pass). Geometry/history remains agent-owned.
- [ ] Independent review found a save-currentness risk during surfacing drag:
  vertices mutate before the existing surface revision advances on drag end.
  storage_review owns reproduction and surfacing mutation invalidation. Do not
  extend existing save qualification to in-progress surfacing gestures.
- [ ] Initial real-app V1 export test refused with an unexpected stale/cancel
  error before bytes were produced. storage_browser is tracing the capture
  invalidation; no qualified native manufacturing export is claimed yet.
- [x] Additional signed held-save/history-travel refusal integrated as
  `fcb5330f4`; the programmatic race produces no file and restores the valid tip.
  Agent execution is recorded in the signed receipt; root reviewed/syntax-checked.

- [x] Signed save/close receipt integrated as `49c5fc218`: exact desktop
  `d8a60a427` and CAD `672aa235` pass normal Save, fresh Files reopen and
  other-account denial; busy sign-out refuses, confirmed window closure
  terminates the held hash worker and creates no file. This tests cooperative
  session admission/window cancellation, not a forced external account switch.
- [x] Expiry-recovery test integrated as `a0a320cb9`; root reviewed the fixture
  and assertions. Agent's exact f2/adc/dd8/44da run uses 40/90-second test-only
  lifetimes, observes actual timer renewal, preserves pre-expiry pending bytes,
  rejects the expired session locally and at issuer, and reconciles on same-account
  sign-in; B gets 404. Receipt: `tests/files-session-expiry-20261104.md`.
- [ ] CAD `f1ee0bb1` wires v1 OCC enclosure export to fresh native manufacturing
  reads and the core 3MF writer. TypeScript and existing lifecycle/hash controls
  pass; real app and signed export tests are assigned to storage_browser.
  This is not a qualified 3MF workflow yet. Label v2, native contact/paired
  surface proof, material UI/grouping and three-region export remain outstanding.
  Desktop `090f189c7` forwards export cancellation/window guards.

- [ ] Root export groundwork now includes disposable v1 manufacturing reconstruction
  with four passing lifecycle controls. It is not wired to desktop export yet;
  v2 inset label and a same-reconstruction contact proof are required before
  grouped LID/LABEL can pass the existing overlap check. The geometry agent's
  first real-engine v2 run produces a recessed lid and a distinct label, while
  edit/fault/regression qualification remains in progress.

- [x] CAD worker-save sequence integrated through `6e7e615f`; root reran three
  focused tests, TypeScript, and actual Chromium `worker-save-browser.test.cjs`
  against the isolated `672aa235` build. Material/native replay, cancellation,
  stale history edits and explicit material rebind pass. This is not a new
  combined-build or signed desktop proof; see CAD's worker-save integration note.
- [x] Desktop `d8a60a427` uses captured revision guards during Save rather than
  repeated full snapshot comparisons. Serialized capture is the saved baseline;
  dispatched earlier-version writes remain truthful. Signed caller/fault checks
  are in progress. Workspace capture/host serialization still use the main thread.
- [x] Enclosure manufacturing candidate integrated as `6833729d`; root geometric
  review and sixteen Node controls pass on R730 and workstation. Export adapter,
  inset-label region and signed end-to-end 3MF output remain incomplete.
- [x] Stage 1 requirement/evidence matrix integrated as `16b589b5d`:
  `docs/evidence/files-stage1-objective-audit-20261104.md`. The expiry-recovery
  test has a first passing run; stronger final refusal control/receipt is pending.

- [x] Source-gateway deployment research integrated through `c00f0c2d1` from
  candidate `9799a8cb2` and prerequisites. Root reviewed transition ordering and
  reran actor/transition tests: exact pins, unchanged routes/floors, three killed
  child phases, failed-health recovery, foreign-unit refusal and locks pass.
  Service actions in that transition test are modeled. No live deployment;
  protected staging/plan and new-CAD packaging remain pending.
- [ ] Files audit separates failed native steward/stopped timer from account
  sessions. Read-only status confirms native state, not a Files data-loss bug.
  Check account expiry/refresh evidence before restarting obsolete services.

- [x] Combined signed material test/receipt integrated through desktop
  `4b8fa41e9`; CAD identity/color/stale-token browser receipt integrated as
  `383e75ef`. Root reviewed and syntax-checked scripts; agent's combined signed
  execution is the existing evidence, not a claimed new root rerun.
- [ ] Worker CAD save preparation: `storage_browser` owns new isolated branch
  `research/manufacturing-save-worker-20261104`; root owns desktop integration.
  Normal Save already awaits `snapshotForHostSave`; repeated main-thread JSON
  work remains around/inside that path. Preserve one validated save operation.
- [ ] `storage_review` is mapping full Stage1 Files requirements to receipts,
  separating actual storage gaps from CAD serializer and deferred app/capacity work.

- Current successor entry point: `HANDOFF-FILES-CAD-2026-11-04-CURRENT.md`.
  The exact active user objective is copied into `FILES-CAD-RELEASE-OBJECTIVE.txt`.
  Handoff requested; goal not paused. Combined material signed receipt is on
  candidate desktop `c70998a69`; manufacturing WIP `37512e23` remains agent-owned.

- [x] CAD `34bbabea` integrates cleanup-aware rectangle/feature discovery from
  `23d5b29b`: unavailable reason and inspection revision reflect cleanup failure.
  Root reviewed changes and TypeScript passes; agent's no-blob browser control
  asserts both readiness reason and revision. Backed up to both LAN repositories.
- [ ] Beta source gateway remains uninstalled: mapped launcher qualification
  exposed recovery-receipt and admin-owned-hosting-checkout assumptions.
  A root concern about repeated health-callback wrapping did not reproduce
  because the loader creates fresh modules; agent is replacing that temporary
  global override with a bound proxy and adding repeat-call coverage anyway.
  Finish exact host-boundary qualification before deployment.

- [x] Material controls source integrated into CAD `7c2fb6e0` (agent candidates
  `f45514d5`, `dc75dee2`, `b3b505f7`) on top of worker cleanup. Separate BODY/LID
  identities, appearance controls, preserved custom placement/names, material
  revision fencing and canonical wizard string-ID discovery are included.
  Root reran 10 assignment/hash/envelope tests plus TypeScript successfully.
- [ ] Combined signed fixture qualification for that integration: agent's
  standalone b3 candidate passed actual wizard/UI/desktop commands, stale-token
  refusal, normal Save/fresh Files Open and second-account denial; await the
  committed receipt and exact combined build. Its earlier alternating 404/login
  failure was traced to two owned Caddy fixtures sharing a port, not product
  data loss. Require exclusive fixture-port ownership on subsequent runs.
- [ ] Clean release builder must include/pin the new manufacturing hash worker
  and updated geometry runtime/source notices; existing 67d package is older.
  New assignments hash incrementally in a worker, but the existing 8 MiB
  manufacturing save/restore preparation still uses main-thread serialization.
  Do not describe this as complete 128 MiB worker-based CAD persistence.

- [x] CAD worker cleanup integrated as `51cea5c1` (reviewed `eed0a9af`):
  separate enclosure mount, two mounts per candidate/three total, accepted
  resource detachment before queued replay, separate visible cleanup failure.
  Root reran 34 resource/ledger tests and TypeScript noEmit successfully.
  Root independently reran all three actual Chromium composition/cancellation/
  cleanup controls against the pinned no-blob fixture; all pass, browser closed.
  Signed parent and combined material candidate still require
  qualification. Both LAN backups contain the integration commit.

- [x] CAD `6f05e4fb`: independent Python ZIP/XML verification of noncommuting
  placements and three synthetic box regions in two build objects; 20 focused
  writer/adapter/envelope tests pass. Worker enclosure/inset export not proven.
- [x] Desktop material-command bridge implemented through the shared CAD
  operation with detached inputs and account/window/cancellation guards;
  12 focused command tests pass using controlled managers, not real geometry.
- [ ] Integrate material candidate and test actual signed command/Save/reopen.
  Review of `dc75dee2` found assignment overwrites names/placement and inspection
  omits material-only revisions. Agent is fixing both plus wizard string IDs.
- [ ] Combine cleanup/material work under signed-parent CSP. Composition's
  blob-permitting fixture does not prove the production no-blob policy.

- [x] Four-hole CAD signed-fixture persistence: normal Save, automatic sync,
  Files Open after fresh login, native history/geometry reconstruction, exact
  server bytes and second-account denial. Desktop `e2ade56a9`, CAD `67d34329`;
  `tests/jsketcher-four-corner-signed-20261104.md`.
- [x] Cancellation during semantic side discovery preserves accepted geometry
  and history and terminates candidate worker (controlled dispatch stall).
- [ ] Public CAD release with authenticated source/provenance packaging.
- [x] Driving diameter component: shared sketch UI/revision-bound action,
  conflict rollback, undo/removal and native replay tested in CAD `02afdd70`.
  Desktop command bridge `6598e4cb0` passes its scoped action-fixture tests.
- [ ] Combined signed-desktop diameter workflow and deployment.
- [ ] Authored enclosure, material regions and core 3MF remain incomplete.
- [x] Bounded OCC enclosure signed Files workflow: real wizard, normal Save,
  automatic sync, fresh-session Files Open, BODY/LID identity and other-account
  denial. CAD `7fde2965`, desktop evidence `757fa2f14`, receipt
  `tests/jsketcher-enclosure-signed-20261104.md`. Regenerated roles also passed
  the exact material resolver via a test-only import; no material UI claim.
- [ ] Enclosure material UI, label, manufacturing mesh and core3MF handoff.
- [ ] Composed plate/enclosure history with measured worker cleanup.

Accepted-engine detachment is integrated in CAD `6d692867`; root reran 34
resource/detachment/ledger tests. The capability distinguishes released native
resources from a closed document, but craft has not enabled it yet. The next
qualification must prove actual composed edits and cleanup in Chromium.

Enclosure integration source now includes bounded OCC and Manifold worker
construction/preview (`fd88e9fd`), distinct engine metadata (`57e41ddb`), and
explicit BODY/LID material binding (`7709fddc`). Root independently reran seven
plan/mesh/capability tests and the pinned static Manifold builder test. These
do not establish authored full-app acceptance or manufacturing tessellation.
The authored OCC operation is in the browser agent's qualification lane;
multi-feature composition and actual worker memory measurements remain open.
Resource pool `63f946c8` supports an explicit two-mount candidate within the
existing three-mount total ceiling; the app default remains one mount.

Source-access candidate `4a22f864e` prepared exact CAD67d/clean8c runtime and
verified public exclusion of all source artifacts, but final-registry signed
access and managed gateway configuration are still outstanding. It is not
deployed and does not contain the newer diameter/enclosure changes.

The source-access candidate is integrated through desktop `5d72e4cba`.
Root independently passed static public-exclusion, private exporter,
root-owned registry tamper/path checks, and the mocked preparer suite.
The archive-input test was initially invoked without its two required paths
and did not run; it is not counted as fresh independent evidence. Actual
archived-input/full-build evidence remains the agent's R730 receipt.
Review identified a source-dialog disposal gap; its fix and the managed
operator successor remain in the source-access lane before deployment.

Dialog fix integrated as `e7ac87443`. Root independently ran the real Chromium
dialog control with an owned loopback server/browser: close abort, late-result
refusal, URL revocation, invalid links and no index-triggered subresource load
passed; the owned browser/server closed afterward. Actual mount-dispose
independent-of-host-signal evidence remains the agent's separate browser test.
Beta uses its own gateway unit and c543 recovery actor, not main's managed.json
operator; beta-specific pin/recovery changes are still required before release.

## Current integrated checkpoint — 2026-11-04

- [x] Bounded main Files promotion: normal UI save, fresh-login reopen, exact
  server bytes and second-account denial; `tests/main-opfs-public-normal-20261104.md`.
- [~] Four-corner CAD history integrated at `c9e76b84`, backed up to both LANs.
  Nine root controls and TypeScript pass; full-app feature tests cover edits,
  replay and cancellation. Signed desktop storage qualification remains open.
- [ ] Authenticated source/license delivery and current runtime provenance.
- [ ] Authored enclosure body/lid after independent dual-engine geometry tests.
  Geometry experiments alone do not satisfy this gate.

## Queue notation and operating rule

- `[x]` means the exact stated outcome is complete and supported by evidence.
- `[~]` means partial, scoped, or research-only; it remains in the queue.
- `[ ]` means not complete or not yet verified.
- `LIVE`, `RESEARCH`, and `NOT STARTED` describe where a result stands; tests must name their actual boundary.
- Pop an item only when every part of its acceptance criteria is verified. Split a broad item before checking off a smaller result. Push newly discovered issues into the relevant section. Record date, commit/release, evidence, tests and remaining limitations in the ledger below. Do not use checked-box counts as a percentage of the overall vision.
- At each handoff reconcile this ledger against actual source, tests and live state. Maintain parallel work in isolated worktrees, integrate reviewed results, preserve user changes and back up source and notes.

## Scheduling: bounded work, parallel lanes and serial gates

Keep the complete program below as the backlog, not one enormous active task.
The lead selects a small active set based on current evidence and resources.
Each package names one observable result, exact base, owned paths, acceptance
tests, boundaries and a stopping point. Record status as ready, active, review,
blocked or done; add newly discovered work to the backlog rather than silently
expanding an agent's assignment. A failed test returns the package to active or
blocked with evidence; it does not become done merely because time expired.

**Can run independently:** app-specific UX/lifecycle fixes in separate
worktrees; documentation and inventory; independent security, accessibility,
and test reviews; CAD solver, geometry and manufacturing-model research behind
agreed interfaces. These lanes must not edit the same shared files. Tests that
need the same browser, port, CPU, disk or server use a scheduled resource slot.

**Must be ordered:** agree on a shared storage or host contract before dependent
implementations; implement server and browser sides in parallel after that;
integrate and test the actual combined workflow; independently review it; then
one designated operator stages, validates and deploys with rollback. Account,
file-format and service-worker migrations require compatibility and recovery
proof before a cutover. The CAD/3MF enclosure follows its necessary geometry,
material identity and export contracts; physical studies depend on qualified
models and a forward solver. App work can continue while these gates are open.

**Shared ownership:** one integration owner serializes edits to shared desktop,
storage contracts, hosting configuration and release pointers. Workers propose
changes and return exact commit, tests and limitations; the owner integrates and
tests them without overwriting other work. A release does not wait for unrelated
backlog items, but must meet the safety and compatibility gates for its scope.

**Current planning order on resume: storage first.** Make dependable account
storage the first major integration gate before broad app integration or CAD
delivery. The gate is met only when actual browser/server workflows preserve
saved data and account isolation, safely handle versions/conflicts, interruption
and recovery, keep heavy work off the UI thread, and demonstrate bounded
resources and responsive behavior at stated limits. Include the notebook's
committed-working-file protection, efficient transfer and compatible rollout;
do not claim a complete changed-chunk system merely because capture works.

After storage, integrate shared session/lifecycle safety and test cross-app
failures, then qualify apps one workflow at a time, classroom load, and the
parametric enclosure and material-aware 3MF slice. App investigation, design,
isolated fixes and independent tests may proceed in parallel when they do not
depend on unsettled storage contracts; do not release a dependent workflow or
create an app-specific competing storage system to bypass the storage gate.
Refine the ordering when actual evidence shows a dependency is different.

## Active release milestone — 2026-11-03

**Expanded CAD gate definitions — 2026-11-04:**
`docs/CAD-ENGINE-GATE-1.md` is the explicit foundational engine qualification:
12 competency areas, P0/P1/P2 acceptance priorities, 22 exercises, five separate
validation responsibilities and Change the original rectangle. Current work is
Files plus that foundation, not routine patch accumulation. The next gate is
`docs/CAD-ENGINE-GATE-2.md`, intermediate mechanical CAD with 12 groups, ten
projects and four additional areas. Gate 3 is now recorded in
`docs/CAD-ENGINE-GATE-3.md`: advanced modeling/engineering, with ten groups. The
user intentionally moved the original groups 11–16 to a following Gate 4, whose
description is now recorded in `docs/CAD-ENGINE-GATE-4.md`, including specialist
projects, automation and representation boundaries. See
`docs/CAD-ENGINE-GATES.md`: later gates inform earlier design contracts, while
implementation stays focused on Files/Gate 1. Gate 5 now records requirements,
functional intent, experiments, evidence and system synthesis in
`docs/CAD-ENGINE-GATE-5.md`; future research remains distinct from demonstrated
engineering. Gates 2–5 remain queued; none is declared complete by planning.
`docs/CAD-ENGINE-END-TO-END.md` defines the actual handoffs, failure paths,
acceptance workflows and bounded agent packages across this program.

The user explicitly resumed Files, JSketcher consolidation, mechanical features
and the material-aware enclosure/core-3MF handoff. See
`docs/ACTIVE-FILES-CAD-RELEASE.md` for ownership and the completion audit, and
`docs/goals/FILES-JSKETCHER-RELEASE-20261103.txt` for the full original goal.
Three isolated implementation lanes are active; the lead owns shared contracts,
review, integration and deployment. Preserve main, beta data and guarded assets.

### Active progress — 2026-11-04

**Latest user direction supersedes the earlier production-upgrade gates:** both
main and beta are no-user test deployments. Replace the test release and require
a reload; stop qualifying old windows, cached versions and extra historical
recovery families solely for compatibility. Keep saved-file correctness,
account isolation, worker cleanup and actual current-release workflows. Reuse
the already-reviewed healthy deployment path, preserve other sites/prototype,
and perform fresh public acceptance. Historical compatibility evidence remains
recorded but is no longer a prerequisite that expands this milestone.

**Current deployment:** beta **830ca4f1** and main **0366e10a** are selected.
The reviewed actual-host install/plan/apply passed; the main selector change used
the existing controller. Original/asset storage floors and beta routes were
preserved, journals cleared, ten hosted-service health checks passed, and
`/desktop/` bytes are unchanged. The known renewal timer was restored; its prior
failed service state is not fixed by this release. See
`evidence/files-830-and-main-0366-activation-20261104.json`.

Main retains Files, Text, Terminal, Calculator, Help and CodeMirror. Its ZIP
actions are now omitted; ZIP stays beta until separately qualified. Main still
uses the older storage graph. Broader apps and games remain beta. Essential
System tools remain integration targets, not blanket validated capabilities.

**Files latest:** F01–F10/R01 have bounded source evidence in
`tests/files-foundation-exit-20261104.md`: signed account-flight/conflicts,
128 MiB interruption and changed-data transfer, worker/resource behavior, quota,
exact dd8 disk/restart faults, actual guest separation and offline reproduction.
Fresh public 830 Text save/reopen/account-denial acceptance passed. Separate
ordinary fresh-login → Files → Text checks on beta and main passed without
manual storage calls. Main desktop/phone-emulated menus omit ZIP actions.
Receipt: `tests/files-public-830-continuity-20261104.md`. Its initial harness
sync/scroll/hidden-button corrections are preserved; normal UI behavior has its
own later check. R02 and the bounded beta Files foundation are accepted. Main
storage promotion, per-app qualification, automatic GC and classroom/100-user
capacity remain open. No new historical window/cache campaign is required.

**Current parallel CAD work:** Current CAD runtime source: 2bef632f includes the clean worker runtime, centered-hole
history, analytic projection, cylinder display fixes and type fixes. Normal
exact-source build, full typecheck and 17 focused tests pass. Scoped actual-app
edit/reject/recover/undo/native reopen and signed My files evidence are recorded
in the handoff. Metadata guards and nonplanar display defects are fixed.
However, the first clean-runtime signed test reproduced the saved-prism reopen
timeout previously seen once with the incremental runtime. Cause is under
investigation; no timeout was increased. Actual prepared package2bef passes
signed desktop command discovery/rectangle/edit/extrude/centered-hole/save/fresh-session
reopen and account denial (evidence/cad-shared-feature-signed-20261104.json).
Owned restore timeout now cancels workers and rolls back staged writes, with
actual held-reply/late-delivery evidence; original latency cause remains open.
File-menu source discovery works, but server-side source authentication and
precise notice gaps remain. Four-corner dependent-hole planning is next. No public CAD deployment, full plate, Gate1, bracket/enclosure
or material-aware 3MF completion is claimed.

**Discovered old-client defect:** unexposed e359 replaced the global catalog,
letting an old loaded host request new Files without document operations. Root
candidate `830ca4f…` keeps the old global catalog and the new immutable catalog
separate. Two builds, packaging controls and actual old/new-tab proof pass.
Only global catalog/cache/service-worker bytes differ from e359; no
storage, SDK, app-bundle, immutable-host or shell-loader bytes changed. Preserve
historical e359 test scope, never expose that rejected package.

**Main/beta priorities reaffirmed:** reduce main to the useful core integration
targets Files, Text, Terminal, Calculator and Help; CodeMirror remains a shared
dependency. These have bounded workflow evidence, **not full app validation**.
The user permits important tools being integrated first on main. A System tools
menu entry is not evidence that its library or all consumers are qualified.
Programming is first priority, build/design and 3D printing second; games and
other apps stay lower priority on beta. Preserve their source and beta access.
The order remains Files foundation, then programming/design/3D-printing workflows.
The reviewed e7e8 main candidate is now deployed. Its exact inventory,
launch/open/restore restrictions and existing 68-ID refusal tests are recorded in
`tests/main-core-independent-review-20261104.md`. Root reran successor-family,
reproducible recovery-bundle, launcher-pin, legacy-journal-fence and forward-fault
tests after integration; those were scoped fixtures. The later literal launcher,
protected installation/recovery and bounded public checks are now recorded in
the current activation receipt above.

**Historical Files candidate evidence, superseded above:** `09ef362f1` integrates signed e359/dd8
Files/Text desktop/phone-emulated actions and actual 8 MiB worker-close tests.
Saved data survives the tested 3ad→e359 transition; conflict/attempt metadata in
that retention control was synthetic. Real old controlled tabs and managed
transition remain open. Complete gateway inventories establish that c046+the
explicit 44da SDK used in prior tests has the same server/client bytes as dd8;
issuer/routing/fault substitutions retain their original limits. Near-limit
interruption/resources and portable R730 reproduction are active bounded tasks.

**Files-first gate reaffirmed:** finish and deploy the Files foundation before
broad dependent-app migration. The newly proposed Spreadsheet migration stopped
after read-only inspection, with no implementation changes. Independent CAD
engine/solver work may continue; dependent save/reopen release acceptance waits.
`4880ebbeb` adds signed commit/lost-reply/newer-edit/browser-process-death recovery:
exact later local UUID/bytes and attempted metadata survive; reconciliation has
two requests/two commits for two revisions, no duplicate replay. This is a
client-side successful-response hold with c046, not TCP/power-loss proof.
The exact 171-file beta asset candidate is
`e359a081ee09027ce0247daaeabadea3d3d2c766e7b176d6bb422f7b85003a0f`;
two builds and packaging refusal controls pass. See
`research/beta-files-forward/README.md`. Exact deployed-dd8 compatibility,
retained v2 data/client transition and managed installation remain open.
`tests/files-foundation-exit-20261104.md` is the reconciled F01–F10/R01–R02
finish line. It distinguishes deployed 3ad evidence, current source tests and
the unqualified e359 package. The public e359 candidate/input archive is now
on R730 with matching local/remote SHA-256; its README records the path and
remaining clean-source prerequisites. Independent exact-dd8 and retained-data
qualification is active. Broad app migration remains deferred.

**Latest integrated checkpoint; older entries below retain their original scope:**

- [~] Shared document operations now cover Text/Calculator, Files
  (`521e3582f`/`dae5c8efb`), Circuit/Digital Logic (`e8e6338b5`), the native
  Circuit picker (`21df8bc62`) and CAD parent (`cb57c744d`). Subtree/advisory
  controller checks total 16. Lead actual-app/engine reruns pass, with in-memory
  storage; exact results and the strict-CSP harness correction are `89236be4d`.
  Other apps and public promotion remain open.
- [x] Bounded signed Files close-during-copy: `d62ccc3e5` uses real OPFS Worker
  progress on an 8 MiB + 7 byte file, closes Files, observes one termination,
  released generation locks and no late download URL, then reopens and downloads
  exact bytes matching the signed server hash. Desktop and phone emulation pass.
  This does not promise immediate OS memory return or cover a browser download
  already in progress. The ordinary signed UI action chain also passes;
  `5af7c1bc7` strengthens fresh-session proof to readBlob plus independent hash.
  Chromium accepted/completed handoff also passes; completion was observed before
  the close command returned, so in-progress handoff survival remains unproved.
- [~] CAD worker CSP repair `715628d1` passes lead fresh build, three integrity
  tests and actual worker heap-growth/prism plus parent lifecycle checks under
  self-only script policy. Owner signed fixture passes width edit, worker
  extrusion and save/reopen. Test packaging is not runtime promotion. The next
  centered-hole implementation is at CAD `8a9f79d8`; scoped history and signed
  tests pass, but startup qualification, packaging and the full plate remain open.
- [x] Main catalog restriction is deployed as `0366e10a`, alongside beta Files
  `830ca4f1`, with fresh public Files/Text save/reopen and account isolation
  acceptance. Main keeps its older storage graph; promotion of the beta storage
  graph remains separate. See the current deployment receipt above. Earlier
  Caddy/operator fixture failures are historical evidence, not active blockers.

- [~] DOCUMENT SUBTREES: `63271e457` adds active folder/descendant coordination
  to the shared mount controller, including source/destination reservations,
  root scope, separate My files/Linux namespaces and release on disposal.
  15 primitive tests pass; actual Text/Calculator tests pass again at 1366/390
  after `06e696262` prevents editing during a blocked initial load and preserves
  file association if editor replacement fails. Circuit/Digital Logic source
  and owner real-engine tests are integrated in `e8e6338b5`. Files migration and
  Circuit native-picker admission are active; no all-app or deployment claim.
- [~] MAIN RESTRICTION QUALIFICATION: e7e8 now passes signed isolated Files→Text
  save/fresh-session reopen, other-account denial, Calculator and real v86
  Terminal/nano workflows. `53928d31d`, `2855183a9`, `3da83123d` add actual pinned
  controller simulation, exact auxiliary inventory and a proposed pending-main
  journal guard; lead tests pass. Protected launcher/real-Caddy recovery and
  installed entrypoint coordination remain open. Main is unchanged.
- [~] SIGNED CAD WORKER FAILURE: the signed parent correctly blocks the OCI
  worker's verified-blob `importScripts` under its existing script policy.
  Earlier isolated tests explicitly allowed blob scripts and did not prove
  this deployment policy. A statically bundled pinned worker is being tested
  without widening global CSP. Owner prototype passes real prism, tampered
  WASM refusal and live heap growth; combined signed save/reopen is still open.

- [~] MOUNT-OWNED DOCUMENT OPERATIONS: `9fa27ad72` supplies session-local active
  file claims, synchronous admission and observable state. Text/Calculator
  migrate in `3f6d745d0`; actual mounted-app Chromium tests pass desktop/phone
  sizes with stub storage/accounts. Parent-backed CAD and Files migrations are
  in progress; Circuit Lab and Digital Logic are integrated as noted above. Remaining apps are recorded in
  `docs/research/save-busy/AUDIT-20261104.md`; no all-app/deployed claim.
- [~] VERSIONED CAD WORKER HISTORY: `d64c506c` is tree-equivalent to owner
  `4ed4a5ec`. V1 rectangle wizard/craft, bounds/topology, width/depth edits,
  rejected changes, undo/redo/native reopen pass under strict CSP with actual
  OCC workers and a test-owned host binder. Parent binding is desktop
  `ed86194bd`; signed parent/Files/close qualification remains open. Full plate,
  dependent holes/cuts/fillets/patterns and all of Gate 1 remain incomplete.

- [~] MAIN/BETA BOUNDARY: main ksu.codes must offer only finished features with
  end-to-end evidence; all games and unfinished integrations belong on beta.
  Catalog, file associations, restored windows and direct launch are being
  audited; menu hiding alone is insufficient. Managed removal is not deployed.
  Preserve source, beta access, account data and /desktop. Lead owns deployment.
- [~] SAVE CONTROLS: disable Save during an app's load/local save and reject
  duplicate keyboard/agent actions. Keep newer edits dirty. User accepts this
  restriction; no automatic queued save requested. Background server sync alone
  does not keep Save disabled. All-app audit is active. Signed rapid-save proof
  `20b672f6b` preserves pending B during delayed A/B acknowledgments; simultaneous
  stale local writes give one winner and one conflict.
- [~] FILE COPY CLEANUP: `214fde710` proves twelve Chromium copy/use/close cycles
  and test-only wrapper-reachability controls; no native RAM guarantee.
  `a7ac40d65`/`e171752ec` cancel an actual OPFS copy via caller signal; Files
  forwards its host signal. Bundle build/helper tests pass; real window-close
  UI qualification and deployment remain open.
- [x] CAD COMBINED GUARDS: `4cae31eb` qualifies tree-equivalent `9bb3eae0` with
  app build/typecheck, core guards and ten real Chromium checks. Ordinary
  worker-solid history, signed persistence and Gate 1 remain open.

- [x] SOURCE-TRUST DIRECTION RECORDED: all JSketcher features are suspect and
  reference/inspiration. Contracts and independent evidence determine reuse;
  inherited behavior, compatibility and menus do not establish correctness.
  Future-layer contracts inform the core; stubs/physics plans remain deferred.
  Gate 1 and the successor goal now state this explicitly. Documentation only.
- [~] CAD CONSUMER BRIDGE: integration `e4a21e7c` guards legacy/native operands,
  default Boolean targets and failed OCC registration. Focused spy/type checks
  pass; real pinned-runtime positive and injected failure controls are integrated
  as `5e54c5a5`. Reference/sketch package `7090a161` and real worker-prism adapter
  `29c89c67` are integrated with their owner evidence. Registry guards `9bb3eae0`
  reject worker ID collisions/limits and unsupported stored face sketches.
  Combined browser/runtime validation, exact worker-history publication
  and edit/reject/undo/My files reopen remain open. No CAD runtime promotion.
- [x] FILES UI, BOUNDED BETA PROOF: `4613eebae`/`7a119bc4f` cover chooser upload,
  folder/rename/move/copy, exact-byte download, delete and other-account denial
  at desktop and phone-sized emulation. Fresh-session stat proves SHA metadata
  recovery, not a content read. Earlier harness failures/leftovers are recorded.
- [~] FILES REPRODUCIBILITY/RESOURCES: `37af97707` proves repeated identical Files
  builds and focused signed tests from clean R730 checkout using existing inputs;
  sealing prerequisites remains. `12b634976` adds isolated 128 MiB phase PSS/private
  observations with guest/speech excluded, exact hashes and cleanup. It still
  includes browser/test costs, not pure transfer allocations. Network efficiency
  is sufficient; focus remaining resource work on proven copies/verification
  passes and a reviewed stream-to-staged-OPFS boundary. Source `0801ea2d7`,
  integrated as `72c7fdbc6`, reduces redundant detached-copy verification scans
  after independent Chromium corruption, local-edit race and account-invalidation
  checks. It still creates a full detached Blob and has not been deployed or
  measured as a physical RAM improvement. Streaming contract `0480d3f52` is
  documented; `5974d91dd` reproduces the exact deployed SDK twice from LAN Git.
  Latest user direction accepts full detached copies with clean ownership and
  release. Repeated read/use/drop/close resource tests and actual consumer
  cleanup now take priority; streaming implementation remains optional follow-up
  based on measured need. Do not infer immediate GC/RSS return from release.

- [x] CAD RESOURCE OWNERSHIP, BOUNDED SLICE: fork `efb96770` qualifies source
  `531cc24d` with nine focused pool tests and six actual-browser regressions.
  Real OCC mounts injected into PLANE replay preserve accepted/full-tip resources
  on rejection, close superseded candidates, and terminate on document reset.
  Setup failures and cleanup-failure poisoning are covered. Existing rectangle
  undo/native reopen and OCC/Native Mesh registry checks still pass. This is an
  internal ownership API, not worker-prism history publication or an origin-wide
  memory budget. See fork `test/webos/craft-engine-resources-evidence-20261104.json`.
- [~] NEXT CAD SUBSTEP EXIT: integrate the bounded model projection; explicitly
  gate unsupported legacy consumers and transient references; bind the exact
  worker result to current document/engine ownership; publish model, history and
  registry atomically; then prove dimension edit, rejection, undo/redo and native
  save/reopen on that combined path. Only then expand this path to dependent
  holes/cuts/fillets/patterns. Projection `6cbee3a7`, integrated privately as `d6f7dfb0`, now has
  owner, independent and lead real Worker/registry proof in `91c8d95c`.
  The consumer audit identifies ignored failed legacy pushes, silently omitted
  Boolean targets, transient references and native restore ID bounds to gate. Full Gate 1 and the plate workflow remain open;
  engine parity is not required.
- [~] FILES PUBLIC ACCEPTANCE REVIEWED: small-file Files→Text save, independent
  account denial, fresh-context recovery and two-process conflict controls are
  integrated. Lead reran strengthened positive transfer assertions: 69,283
  request-body bytes for a one-byte edit of 1 MiB. The separately serialized
  public 128 MiB run passes initial/fresh-profile/changed-file independent hashes
  and verified deletion: 71,530 changed-operation request-body bytes, including
  a 65,951-byte delta upload. Review preserves the earlier failed test and exact
  retained test accounts. See `tests/files-public-beta-*-20261104.*`.
  Sampled profile-process RSS (~3.49 GB) is not physical memory or a total bound;
  the test retained Blobs and two desktops, with unmeasured guest/speech state.
  Memory, wider interruption/crash and shared-capacity qualification remain open.
  Two isolated 16 MiB phase/PSS runs pass hashes/deltas with real and stubbed
  guests: ~1.38 GB versus ~0.53 GB PSS at the second guest wait (different
  durations). Both actual guests reached ready. This suggests guest startup
  contributes, without proving production/128 MiB budgets or exact causal cost.
  See `tests/files-isolated-16m-memory-20261104.md`; no new public128 run.
- [~] FILES V2 ACTIVE ON BETA: protected preparation, supported-CLI guard,
  dedicated private probe, full public-artifact staging and the actual managed
  plan/apply completed. Candidate `3ad04c48`, issuer `853c12e5`, unchanged
  gateway `dd8cbea7`; beta reports OPFS/database version 2. The durable floor is
  present and transient journals are cleared. Signed known-file health passed;
  independent read-only inventory/unit/public checks also pass. See
  `evidence/files-beta-activation-20261104.json` and protected-install/probe
  receipts. Main and `/desktop/` remain on their existing releases. The browser
  owner verified a Ready-gated Files→Text edit/save, second-account denial,
  fresh-session reopen, 1 MiB one-byte changed transfer and independent-profile
  conflict pass; lead review is complete as recorded above. A controlled held-read
  follow-up found Text intentionally noneditable until ready; the initial
  empty-file test typed too early. Retain that failed test and readiness control;
  no lost accepted edit was reproduced. Activation does not complete Files
  acceptance. Public speech vendor JS returns 404, separately queued.
- [~] CAD WORKER RESULT BRIDGE: integrated checkpoint `4b6528e9` includes the
  strict headless analytic reader, deferred Verb initialization, exact live
  mount/topology binding and structured authored rectangle face/perimeter-edge
  roles. Independent review and lead real-worker tests pass width changes and
  reversed/reordered solver output; changed shared-controller paths also pass
  existing OCC and Manifold suites. Fork receipts are under
  `test/portable-prism-reader`, `test/portable-mount-bridge` and
  `test/prism-semantic`. Four connector edges/all vertices still lack qualified
  durable authored identity. Resource ownership now has the bounded proof above;
  model projection integration, atomic worker-prism history publication and
  edit/undo/reopen remain.
  No public CAD repin or full-plate qualification. Earlier checkpoint wording
  below is historical; these results supersede its missing reader/mount status.
- Foundation priority: the user explicitly accepts that usable workflows may
  lag component qualification. Continue correctness work and preserve failing
  cases; do not weaken a gate to meet a visible-progress deadline. Integrated
  workflows test the connections, alongside the isolated competency checks.
- [~] FILES INSTALLER INTEGRATED: `1dc60b460` contains the reviewed input
  bootstrap, fixed-path installer and cooperative legacy-CLI procedure. All six
  lead tests pass on the integrated tree: preparation, interrupted installation,
  floor/metadata refusal, and both the old-process negative control and its
  supervised quiescence correction. Receipt:
  `evidence/files-install-lead-20261104.json`. Those disposable tests remain
  separately scoped from the subsequent actual protected install and beta
  activation above; they do not alone establish account-storage acceptance.
- [~] CAD PROFILE WORKER: integrated checkpoint `c672d0d1`, tested worker code
  `25050c16`. Actual authored rectangle-to-OCC prism, unsnapped v2 profile,
  polygon-area volume check and dense result validation pass. The optional
  worker-local topology descriptor is limited to 16 KiB and is not sent to
  ordinary controller callers. Lead seventeen data/math checks and actual
  strict-CSP topology/profile/lifecycle tests pass; earlier box/Boolean
  compatibility also passes. See fork `test/engine-extrude` and
  `test/engine-topology` evidence JSON. ARC14 still needs the strict BREP reader,
  worker ownership, durable references and accepted history publication. Mesh
  closure/volume evidence is not BRepCheck/manufacturing certification. No repin
  or deployment; public UI extrusion still uses the earlier in-page kernel.
- [~] CAD MODEL VERTEX ID: `228cde72` fixes the object-as-ID defect. Lead fresh
  build/typecheck and real OCC/Native Mesh registry, replay, authored extrusion
  and publication tests pass. Producer labels remain unqualified and ordinal
  fallback unstable; vertex picking and saved vertex-dependent features remain
  queued under ARC15. See fork `test/webos/brep-vertex-ids-evidence-20261104.json`.
- [~] FILES REAL-SERVICE FIXTURE: source through `ba65151d2` is integrated at
  `de71f56b8`. The implementation owner passed interrupted unit-write, reload,
  restart and timer-stop recovery using real sealed processes and distinct
  DynamicUsers; independent review reproduced unit-write and old/bad unit
  controls. The marker is removed: exact operator-written unit bytes determine
  the fixture executable. Lead checked exact subtree identity, changed Python
  syntax and runner entrypoint. Production paths/policy/TLS/main readiness still
  have fixture substitutions; timer firing, install and live beta acceptance
  remain open. No live changes.
- [~] FILES INSTALL READINESS: packet `ad25aaded` records live pins and missing
  protected bundle, floor-aware guard and dedicated probe. Source preparation
  helper/bootstrap/quiescence work through agent branch `0f9d46d87` passes
  independent disposable review and is integrated/tested at `1dc60b460`.
  Actual protected preparation and supported-process inventory/freeze remain
  open. No server install. Read
  `research/beta-isolated-hosting/FILES-INSTALL-READINESS-2026-11-04.md`.
- [~] CAD HOST AND SIGNED FILES: desktop `64becedd8`, CAD code `9bde6b29`
  (boundary plan `cc2d46dd`). Lead rebuilt exact revision and passed command,
  menu, atomic creation, typed domain/precision refusal and notification tests.
  Real signed create/save/fresh-session reopen/editor width edit/second save,
  server hashes, account denial and closed-window refusal pass. The current UI
  extrusion produces measured bounds, but no worker-backed shared extrusion
  command exists. ARC13/14 now explicitly cover authored profile, worker
  operation and model/topology/history/lifetime bridge. Normal runtime pin
  remains `d3d36bc5`; no deployment. See both new rectangle evidence JSON files.
- [~] FILES CAPACITY: verified archive of twelve inactive public staging
  directories freed about 1.72 GB on webhost root; free space is now
  7,297,232,896 bytes. The unchanged 5 GiB reserve and account data are preserved.
  Main/beta/prototype return 200. This removes the immediate one-file arithmetic
  shortage, not concurrency or production qualification. Receipt:
  `evidence/webhost-staging-archive-20261104.json`.
- [~] FILES OPERATOR SOURCE INTEGRATION: imported only the independently reviewed
  `research/beta-isolated-hosting` subtree at `f6deb3251`, including the
  `a1e9e215c` gate-recovery correction. Seven targeted lead tests pass after
  integration. Independent exact-launcher fault qualification uses real
  loopback Caddy and disposable systemd, with explicit policy/main/timer/unit
  substitutions. Actual service/timer qualification continues separately;
  production installation and beta acceptance remain open. See
  `evidence/files-operator-source-integration-20261104.md`. No live changes.
- [~] ATOMIC RECTANGLE CREATION: fork `ec2e0156` records `07316f8f`.
  Lead build/typecheck, seven pure workspace tests, stream coordinator and nine
  current-build Chromium scripts pass. Real plane/worker rectangle bytes and
  history/geometry/registry publish together. Two sketches survive native reopen;
  cancellation, stale services/revisions, pre-install failure, post-commit reset,
  malformed worker output and parent-frame calls pass. Later host discovery,
  human action and signed My files results are above (ARC12). Full Gate 1 and broader
  document transactions remain open. No new package or deployment.
- [~] PARALLEL QUALIFICATION: engine `0431dff0` records scoped compiler/behavior
  evidence, not runtime promotion. Files `fa228b79c` recorded earlier capacity
  limits; later cleanup is above. The independent review findings in
  `c204b753b` were fixed at `a1e9e215c` and integrated as noted above.
  Existing disposable Caddy/systemd evidence retains
  explicit production substitutions. The 5 GiB account reserve is unchanged.
- [~] PRIVATE CAD WORKSPACE: fork `3e42030f` records implementation `67b8888f`.
  Lead seven pure core tests, stream coordinator, six legacy adapter checks,
  build/typecheck and eight actual Chromium scripts pass. Prepared bytes stay
  private until current-owner commit; per-key guarded delivery refreshes both
  modified faces and removes stale loop/object IDs. Cancellation, service
  replacement, reentrant callbacks and bounded candidate/delivery controls pass.
  Receipt `test/webos/workspace-preparation-evidence-20261104.json` retains the
  failing throttle control and corrected reset-test oracle. The bounded plane/worker-sketch composition is now above;
  common UI/agent wiring remains.
  The new bounds do not qualify all legacy memory use or durable My files.
  Desktop package stays `d3d36bc5`; nothing deployed.
- [~] PARALLEL RESEARCH RETURNS: rectangle parity/provenance `e6db73ea` keeps
  numeric worker versus named-parameter editor limits explicit. Engine `239c64b4`
  records a clean source build and agent-run session tests, but unexplained
  compiled-code differences prevent runtime promotion. Files `6fdc8d5a0` supplies
  the reproducible isolated protected-launcher runner; production systemd/Caddy
  boundaries remain simulated. These are backed research results, not a new
  assembled release. See the latest successor handoff for exact paths and gaps.
- [~] CONSISTENT CAD REVISION: fork `5b77f71d` records implementation
  `ccb66be7`. Lead build/typecheck, actual stream tests and 12 Chromium scripts
  pass. Successful/failed replay and reset publish matching geometry/history/
  registry/status; rejected commands preserve the accepted valid revision.
  Equal-value write revisions, nested notification/subscription cases and
  caller exceptions are covered. See the fork's `CRAFT-PUBLICATION-20261104.md`
  and `craft-publication-evidence-20261104.json`. Atomic sketch storage plus
  prepared plane publication remains next (ARC11); full Gate 1 stays open.
  No new package or deployment.
- [~] COMBINED CAD CHECKPOINT: fork `bdc4ff2b` integrates verified OCI/Manifold
  workers, guarded associative circular-cut patterns and the discoverable seed
  picker. The lead independently passed both engine suites/four contract checks,
  combined build/typecheck/eight CAD browser scripts, a fresh picker build/three
  targeted scripts, and the later Boolean preprocessing control. See the fork's
  `test/webos/combined-pattern-mount-evidence-20261104.json`. The pattern is
  limited to an immediate circular through-cut on an axis-aligned rectangular
  OCC plate. Engine mounts are still disconnected from CAD. Desktop package
  remains `d3d36bc5`; no deployment and Gate 1 remains open.
- [~] ENGINE OWNERSHIP REPAIR: original OCC name/pointer lifetime defects have
  real negative controls. New LAN source repo `occt-interpreter-codi.git` on
  box-git and R730 holds `5c353d62` full build and `eac17723` incremental relink,
  with agent-run real Chromium name/dispatch/curve/history/Boolean controls.
  No production runtime change; native interrogation cleanup remains open.
  Engine lane now owns a versioned worker-only session prototype preserving
  legacy callers. Global resource limits, broad bindings and composition remain.
- [~] AGENT ENTRY GAP: signed registry test confirms inspect/circular listing/
  concentricity exist, but sketch-start is unavailable and leaves the model
  unchanged. Desktop branch `research/cad-agent-plate-desktop-20261104` records
  this and the data-only transaction proposal (`942f5edaf`). Fork `508d54e4`
  has agent-tested empty-sketch and dimensioned XY rectangle factories, not
  integrated atomic document creation.
  Next agree and test plane/sketch publication without a required editor view.
- [~] FILES MANAGED TRANSITION: lead passed four `c2d6f696` inventory/controller/
  Caddy/recovery scripts. The separate hosting branch
  `research/beta-files-operator-20261104` is assembling exact v2 routes,
  retained issuer journals and gate-only forward recovery. Local process-death,
  Caddy and systemd controls exist; protected launcher, combined signed health,
  capacity and actual beta qualification remain. The lead owns deployment.

The entries below retain prior checkpoints; the later entries above supersede
their not-yet-integrated status without closing the broader work.

- [~] NEXT BOUNDED LANES ASSIGNED: from verified desktop `2384b3f3d` and fork
  `0259d3fc`, the lead continues with three isolated agents. Mechanical work
  owns replay-local seed/tool provenance and a narrowly declared associative
  OCC through-cut pattern (`research/feature-pattern-cut-20261104`), including
  identity, dimensions, count/spacing, undo/reopen and failure checks. Engine
  work owns verified worker loading and multi-operation OCI handles
  (`research/oci-multisolid-mount-20261104`), with real geometry, lifecycle and
  integrity tests. It remains unconnected research; a scoped Blob-script test
  policy does not authorize widening production CSP. Files work owns the
  damaged/forbidden inner-journal recovery gap in the existing managed binding,
  using the same controller and outer lock, without live mutation. The lead
  owns contract review, combined checks and integration. Initial agent results
  are not integrated passes; each lane must return a reviewed commit/evidence.
- [x] HANDOFF PLAN WRITTEN: `HANDOFF-FILES-CAD-2026-11-04.md` and
  `goals/FILES-CAD-NEXT-AGENT.txt` give the successor verified refs, independent
  lanes, reproduction commands, known failures and bounded acceptance. Source
  and candidates are checkpointed; the full release remains active/incomplete.
- [~] ENGINE MOUNTS: user prefers OCC, with Native Mesh/Manifold secondary,
  and requires proper broad library support beyond current used calls.
  `CAD-CORE-SEPARATION.md` ENG01–ENG08 records versioned mounts, discovery,
  explicit conversion/composition, lifecycle and qualification. R730 compute/
  storage, llm-60 compute/testing and LAN repo creation/cloning are authorized;
  llm-60 trusted SSH identity remains unverified. Fork `7d08c159` retains an
  unconnected prototype: actual Manifold box and strict-CSP OCI box in a real
  worker pass lead checks. Legacy SPI exports are absent in the selected
  runtime. OCI uses a separately derived JS wrapper and whole-worker cleanup;
  production loading, broad capabilities and resource qualification remain.
- [~] CURRENT CAD CHECKPOINT: JSketcher `2b3f2c0f` integrates headless solve,
  axis/admission, normalized private replay and monotonic document lifetime.
  Lead rebuilt app `aff1befe`: typecheck/build, 11 Chromium scripts and 9 unit
  checks pass. Five-hole resize/reopen, impossible-edit last-valid/correction,
  held results, occupied-open refusal, surface reset/reload and feature-ID
  history controls pass. `docs/DOCUMENT-LIFETIME-REPLAY-20261104.md` in the fork
  records evidence. Packaged `d3d36bc5` additionally passes OCC fillet/chamfer
  resize/reopen and explicit invalid-size/Native refusal controls. Desktop
  `73c1e8b13` qualifies both packaged workers and signed small-model plus
  dependent-plate workflows at phone/1080p/4K. See
  `evidence/cad-packaged-workers-20261104.md`. True feature patterns, units,
  bracket/enclosure, agent workflow and full Gate 1 remain; no deployment.
- [~] FILES RELEASE READINESS: root `2e312b797` integrates beta-only sealed
  candidate `3ad04c48…`, actual controlled-tab migration and signed Files/Text/
  session tests, plus separate real issuer/guest opt-in config checks. Lead
  verified the 87-file sealed inventory. Old `feaa1c6f…` candidate is superseded.
  `b391e259b` adds actual signed continuity across the exact issuer restart and
  a real filesystem/process floor journal. Lead fault tests pass; the managed
  binding remains separate research `e4a6c2ec6`, with damaged-journal, service,
  custody and host qualification open. Account volume was only 208.8 MiB above
  reserve at the recorded check. Headroom, full-app qualification and public
  rollout remain open. No deployment.

- [x] GOAL/ARCHITECTURE DOCUMENTED: user authorizes replacing coupled JSketcher
  internals and favors computational silos without canvas or fake browser UI.
  `CAD-CORE-SEPARATION.md` adds ARC01–ARC10, ownership, boundaries and explicit
  worker/regeneration acceptance. The saved goal, active audit and gate/execution
  indexes link it. Extend requirements with tests when needed. Documentation
  completion does not qualify the implementation.
- [~] ACTIVE CORE SPLIT: the production headless solver candidate has actual
  worker evidence for center/corner positions, independent residual/geometry
  checks and editor-ID isolation. The separate caller owner has a first actual
  five-hole solid resize and v2 reopen pass. The core/caller and replay/lifetime fixes now pass the combined local build;
  the full coupled Gate 1 chain and UI/agent equivalence remain open. Opening/cancelling
  the in-place sketch no longer rewrites saved boundary snapshots in its scoped
  candidate; the separate legacy 2D view still needs review.
- [~] CONFLICT UI: `2cec3e7e2`, integrated as `c955f1e50`, uses two independent
  signed Chromium processes/profiles and actual Files/Text controls. Offline
  conflict, cancellation, a newer server edit during resolution, preserving
  both copies and fresh signed reopen pass. No deployment.
- [~] FILE RESOURCE/SEPARATION: `7064310e1` passes signed 128 MiB changed-data
  sync and second-tab queued cancellation with the worker budget. `9f753a95c`
  passes actual v86 home/My files/signed-server separation and reboot reset.
  Scope and limits are in their tests/docs; final combined rollout remains.
- [~] COMBINED HOST TESTED: canonical CAD version 2 and leased My files Blob
  worker opening pass actual signed desktop runs at simulated phone, 1080p and
  4K. Native Mesh intersection/history and OCC rotation/scale save/reopen,
  independent windows, closed command refusal, old-format rejection and a
  second account's denial are covered. No deployment; see
  `evidence/cad-files-combined-20261104.md`. The full bracket/agent gate remains.
- [~] FILES UI TESTED: source `99bc3ba06` covers actual create/rename/move/copy/
  delete/upload/download, sync/reopen, cancellation, stale/colliding copies,
  signed account denial and explicit worker teardown. Phone is simulated and
  Linux disabled. See `tests/files-desktop-signed-fixture.md`.
- [~] DOWNLOAD RECOVERY TESTED: `218536add` verifies real signed TCP cuts,
  complete OPFS generations, retained prior bytes/version and recovery after
  Chromium SIGKILL/restart. Cuts happen during transfer; kills follow the
  reported failure. No power-loss or total-memory claim. See
  `research/opfs-storage/DOWNLOAD-TCP-CUT-20261104.md`.
- [~] INTEGRATED WORKER BUDGET: `544480232` limits cooperating heavy content
  workers across tabs. Lead independent two-tab capture/read, cancellation,
  FIFO/deadline, failure and renderer-crash tests pass (max 1 worker; 1.789 s
  observed capture/read run; 20 ms heartbeat max 28 ms). SDK/app allocations are
  outside this cap. Fork `e974cb76` integrates DistancePL boolean handling,
  normalized accepted requests and reserved feature IDs; combined rebuilt
  qualification remains. These do not by themselves prove a complete part.

- [x] DOCUMENTED SCOPE ONLY: Gates 1–5 and the six conceptual CAD eras are
  recorded with an end-to-end execution checklist. This checks off the requested
  planning artifact, not the capabilities; Files and Gate 1 remain incomplete.

- [ ] ACTIVE FOUNDATION GATE: user requests every basic CAD shape, feature and
  assumption be tested before further expansion. Use
  `docs/JSKETCHER-FOUNDATION-MATRIX.md`; preserve separate engine support states,
  real failing controls, UI/agent equivalence and beginner whole-part checks.
  Original nested circular-profile behavior was wrong; an explicit-region OCC
  candidate now has scoped browser evidence. Angle-unit/branch corrections and
  a narrow locked-length redundancy fix are in review. General arrangements,
  truthful DOF and the coupled edit chain remain open. No XR/physics work tonight.

- [~] INTEGRATED SOURCE: opt-in OPFS content adapter/migration and guarded beta
  mirror through `b81ea020e`, lead merge `c4ec9b527`; reentrant cancellation and
  corrected signed-test provenance in `0ec753c33`. No deployment.
- [~] TESTED: owner reports signed account isolation, injected lost reply and
  independent-profile conflicting offline edits preserving both versions.
  Earlier overlapping-fixture signed runs are provisional; corrected runs pin
  the served mirror hash. Full real-interruption and product UI gates remain.
- [~] TESTED: lead's public asset allowlist and account-scoped desktop backend
  wiring pass six packaging tests plus actual-stage hardlink refusal and real
  Chromium staged-worker save/reopen
  under strict CSP. Explicit preview-only origin-wide selection; OPFS remains
  off by default. See `docs/evidence/storage-product-integration-20261104.md`.
- [~] RESEARCH: CAD consolidation `a05a7433` builds the candidate OCC runtime
  from source, preserves Native Mesh and passes bounded strict-CSP feature tests.
  This is not final solver integration or general CAD/3MF qualification.
- [~] INTEGRATED SOURCE: snapshot lease candidate `242e9e951` protects cooperating
  readers; no published-generation collector is enabled. Independent staged
  account-scope/old-backend refusal tests are `eebc1f082`.
- [~] INTEGRATED SOURCE: `78addd57d` bounds generation-lock acquisition and
  backing-file size checks, and avoids the compatibility-copy path for byte
  reads. Staged strict-CSP capture/reopen passed again after integration.
- [~] TESTED CANDIDATE: lead combined CAD consolidation `a05a7433` and solver
  checkpoint `81a214e5` in a separate integration worktree. Actual solver,
  cross-stage/annotation rollback and admission IO suites pass there; rendered
  and account-backed project round trips remain. One agent now develops the
  Concentric feature while another completes solver correctness; lead reviews.
- [ ] EXPLICIT AGENT GATE: C05 in `docs/ACTIVE-FILES-CAD-RELEASE.md` requires a
  discoverable browser command workflow using stable IDs and the same validated
  UI operations: build/edit bracket, recover from rejected changes, undo/redo,
  save/sync and reopen under the correct account/window. No AI provider needed.
- [ ] ACTIVE: reader-aware OPFS reclamation, integrated 128 MiB/resource/fault
  tests, Files UI and origin-wide beta rollout; solver cross-stage rollback
  controls, then the remaining mechanical/material-aware acceptance models.

## Historical progress ledger — 2026-11-02 pause

- [x] LIVE: File-service non-JSON HTTP error status classification deployed and scoped two-account smoke passed. It does not fix server contention or guarantee exactly-once writes. See `evidence/file-http-status-errors-20261102.md`.
- [x] LIVE: G-code Preview rejects a stale file-session result; isolated race and live sync/isolation smokes passed. See `evidence/gcode-session-live-candidate-20261102.md`.
- [x] LIVE: Calculator cannot close while its file operation is pending; scoped live smoke passed. This does not fix logout/account-switch races. See `research/calculator-close/live-activation-20261102.md`.
- [x] LIVE: Excalidraw rejects stale file-chooser results; scoped live sync/isolation smoke passed. See `research/excalidraw-chooser/live-activation-20261102.md`.
- [~] RESEARCH: changed-data transfer and 128 MiB worker capture/upload demonstrated. Not live; large snapshots still consume substantial memory, and managed mixed-version rollout, crash recovery and full bidirectional incremental sync remain open.
- [~] RESEARCH: RAM-only Jupyter models, widgets and Jupytext formats have prototypes. Not live; an isolated copy of the live notebook reproduced a browser-local working-file stale-handle overwrite. Avoid opening the same Python working file in two notebook windows; back up with File → Save working file to My files. User accepts losing unsaved edits, not overwriting saved data.
- [~] RESEARCH: shared session-lifecycle work protects selected apps in isolated tests. The live logout/account-switch data-loss risks and multi-app qualification remain open.
- [~] RESEARCH: CAD/3MF and physical-system work is partial; no general material-aware 3MF or qualified physics workflow is claimed.
- [~] LIVE: separate /desktop/ sizing prototype remains reserved; do not overwrite it as incidental work.
- [ ] Queue next: safe notebook saved-data protection and RAM model; worker-based bounded file capture/sync; versioned asset/service-worker migration and rollback; session recovery; app-by-app My files and lifecycle qualification; classroom load and failure tests.

The following is the complete underlying checklist. Its unchecked boxes are acceptance gates, including items with partial progress above.

## Current bounded storage milestone

**Resumed 2026-11-03 by the user's active release goal.** The prior handoff is
`docs/HANDOFF-STORAGE-BETA-2026-11-02.md`; preserve its research and beta data.

User priority: saved data, account isolation, conflicts, interruption and
recovery, with heavy processing in workers. Work on these as one real
browser-to-server flow, including existing-file updates and fresh-session
reopening; other app and platform work waits unless needed for this flow.

Latest direction: establish `beta.ksu.codes` as the test environment for
iteration; after beta is established, qualify an upgrade path to the main
`ksu.codes` site separately. DNS currently resolves both names to the same
address, but HTTPS routing and any beta services/state must be verified and
kept separate before beta is considered ready. The current site has no real
users, so preserving an old-user upgrade path is not a prerequisite for
replacing its test services. Preserve existing on-disk data and configuration
unless specifically authorized otherwise.

Beta status, 2026-11-02: `https://beta.ksu.codes/` is live with trusted
HTTPS and separate issuer keys, accounts, file data and three dedicated service
identities. The services are enabled at boot, but an actual reboot has not
been tested. Guest Internet is disabled. They share the host loopback network,
so do not claim compromised-process network isolation. Main remains separate.

The beta gateway worker `dd8cbea7…`, SDK `44da83bd…` and guarded mirror
`cbfafe53…` are active. Public Chromium test `5fc0d26ad` passed Files/Text
save/reopen, account denial, Linux readiness, injected lost-reply recovery,
conflict handling and simulated cancellation. A 1 MiB random one-byte edit
across two mirror scopes sharing one signed account/session measured 66,233 B
upload request bodies and 146,230 B download response bodies plus 584 B
request bodies; authentication, TLS and other overhead are excluded. Test files
were deleted; disposable accounts remain because account deletion is unproven.

Beta activation evidence: `research/beta-isolated-hosting/ACTIVATION-2026-11-02.md`
on `research/beta-hosting-isolation` (initial `8ce4f843a`, later guarded
activation receipts `7ded4aec3` and `d5b4810fd`). Worker rollout/recovery and
SDK switch receipts are `c50a91875` and `e1c52fe96` on
`research/quota-owner-liveness-20261102`. The initial TLS activation and first
worker switch failed safely and were recovered before successful retries.
Refreshed read-only hosting verifier receipt `cf04068aa` binds the current
route and worker. Future route changes need a separately reviewed mutating
controller. Main promotion assessment `49d83e3b9` preserves main identity,
accounts and committed files; main has not received these storage changes.

The current guarded mirror is the minimum rollback floor. An old mirror can
misinterpret an uncertain-write marker and leave an unintended old server file
when a locally edited file is moved; this was reproduced with signed services.
Do not route fresh clients back to the unguarded mirror. Existing old tabs can
still execute old code; the user states this is a test site without real users.
The SDK forward-floor marker is respected only by cooperating operators.

An isolated signed 128 MiB two-session test passed with matching hashes. A
one-byte change sent about 66 KiB of upload bodies and received about 489 KiB
of download bodies, excluding full wire overhead. Sampled browser RSS peaked
around 2.04 GiB, then around 1.87 GiB in a metadata-oriented rerun; RSS may
count shared pages, the runs were not controlled, and bounded memory remains
unproven. A streamed cold read passed but did not establish a meaningful memory
reduction. A full cold download via individual chunk operations hit the issuer's
60/minute per-account challenge limit; that experimental route remains disabled.
The active candidate uses bounded batches and read-only retry/pacing, not blind
retry of uncertain writes. Its signed two-tab 64-read pacing test took about
64 seconds, reflecting the account limit. Physical WAN and power-loss behavior,
large-file concurrent-user capacity and further multi-device conflicts remain
open. A local TCP cut after a committed write passed without duplicate upload
(`c6ab94396`). Browser account invalidation, close and cancellation regressions
passed under simulated stalls (`0c95bc9f` and public test `5fc0d26ad`).

The 5 GiB disk admission floor is per participating gateway process; unrelated
processes, metadata writes and privileged mount changes can consume space. The
host currently has little headroom. Strict browser memory bounds may require an
account-scoped temporary OPFS design with verified publication, quota handling
and crash cleanup; Blob backing alone does not establish a bound. Isolated
prototype `3db7f4a99` uses worker chunks and CAS-published verified generations.
It reopened a 128 MiB file with the right hash and preserved a previous
generation after a dedicated Chrome process was killed during replacement.
The 1.26 GiB sampled Chrome RSS is not comparable with the earlier network
test or proof of a hard bound. Orphan cleanup, server sync, production account
isolation, cross-store atomicity and host power-loss behavior remain open.
Research cleanup `f489097e` journals candidates and only collects explicitly
staged, never-published generations under an exclusive account lock. Tests
retain unknown and published files, protect live writers, and cover browser
SIGKILL before and after pointer publication. Account-scoped scans and late
IndexedDB-upgrade rejection were added after review. Independent review and
server integration remain; this is not a host power-loss guarantee.
Follow-up `3aec0e59` adds indexed bounded cleanup and experimental signed
OPFS-to-beta-protocol upload sync. Tests cover over 4,096 published generations,
batched staging cleanup, referenced staging retention, concurrent local edits,
lost replies, malformed receipts, conflict preservation and account denial.
Independent review passed; the later download prototype is described below.
Desktop integration, strict RAM bounds and power-loss durability remain open.
Follow-up `796a10f6` implements experimental verified OPFS remote downloads;
signed corruption, local/remote race and invalidation tests passed, as did
Chrome process kills before and after local publication. Independent signed
Chromium review passed. The server can change after its last version check;
later sync must detect it. This is not integrated with the desktop or proven
power-loss durable.

Earlier 2026-11-02 research progress (deployment status superseded by the beta
status above): ordinary writes refuse to replace a local
version in an unresolved conflict; an isolated signed-account browser test
verified both versions and explicit resolution. A separate candidate reports
uncertainty if account validity changes after a local transaction commits;
an isolated signed-account Chromium test confirmed the local commit and
isolation, with simulated invalidation. Server sync required an explicit retry;
desktop-switch qualification and durable receipts remain. Neither change is
live. An isolated server test confirmed an external
host writer can still race publication; pre-publication revalidation reduces
the window but cannot guarantee atomicity against uncoordinated writers.
Signed gateway process-kill tests preserved old bytes before publication and
new bytes after rename plus directory fsync; they do not prove power-loss
durability. A real test-proxy TCP abort after server commit, combined with a
new local edit, preserved both versions and surfaced a conflict. Separately,
an injected directory-fsync failure after rename exposed a gateway bug: it
reported refusal despite the new file being visible. Phase-aware file and
folder mutation handling, plus cancellation-resistant bounded quota-cleanup
retries, are integrated in research and passed focused signed/fault tests;
they are not live. Persistent quota cleanup failures can still hold a slot
until expiry, and power-loss and arbitrary direct host writes remain unproven.

- [ ] Preserve previously committed bytes through saves, errors, concurrent
  writers, account changes, process interruption and lost acknowledgements.
- [ ] Enforce and test account isolation at browser, transport and server.
- [ ] Detect stale writes and preserve both versions or refuse without loss;
  report the actual state to the user.
- [ ] Recover interrupted work safely on restart, including uncertain commits;
  don't claim recovery where it hasn't been proven.
- [ ] Run heavy hashing and data processing in bounded, cancellable workers;
  measure actual memory and responsiveness rather than claiming a hard bound.
- [ ] Test the integrated path using real signed accounts, independent sessions,
  conflicting writes, fault injection and representative file sizes. Qualify
  rollout and rollback before changing live storage.

The previously paused broader program remains the backlog; this milestone does
not mark its other acceptance gates complete.

---

# Browser WebOS: complete program and handoff checklist

This is the user's long-term program, not a claim that all items are implemented. It is deliberately broad; new work discovered through use belongs on the list. Work in dependency order but combine tightly related implementation and tests into end-to-end slices. Parallelize independent apps/engines in isolated worktrees and integrate early. A milestone is complete only when its own tests and real workflow pass; a button, a package, a mock or a design document alone is not completion.

## Current starting point (2026-11-02)

- The current live system is the Simplified browser desktop at `https://ksu.codes/`. It is a test site and the user has authorized testing and updating it; do not assume that an authorization to delete unrelated data follows. `https://ksu.codes/desktop/` is a separate sizing prototype and should not be overwritten as incidental work.
- The current Simplified source/notes are in `/home/dflanag3/CodiServer/desktop-preview/SIMPLIFIED`; box-git backup is `box-git:/srv/data/git/CodiServer-distro.git`. The jSketcher fork is backed up at `box-git:/srv/data/git/JSKetcher.git`. Its GitHub remote was removed at the user's request: **use box-git only until the user changes that instruction**.
- The main Simplified worktree contains unrelated in-progress changes. Inspect `git status`, instructions and actual live state before every change; use a separate worktree/branch and never overwrite, stash, revert or delete someone else's work to make a test pass. Runtime state, credentials and real user files never belong in a source release. Generated intermediate builds and dependencies are disposable; final required public source/runtime assets and notes must be reproducible and backed up.
- Many apps have basic workflow evidence, not universal qualification; consult `docs/APP_STATUS.md`, `APP_UNIFICATION_PROGRESS.md`, app READMEs and live evidence, checking dates before relying on them. **Microduck is live**, and a real two-account public test covered running, server save/hash, denial to the second account and fresh-session reopen. It does not prove hardware fidelity, physical touch or complete simulation-state recovery.
- My files currently uses browser/account mirroring and a signed server gateway. A research candidate now exercises signed changed-chunk upload and download, including a 128 MiB browser test; see desktop branch `research/webos-cad-combined-20261102` and `docs/COMBINED-RESEARCH-CHECKPOINT.md` there. It is not deployed or a completed bidirectional incremental system: browser memory, incremental computation, external writers, recovery, packaging and concurrent-user limits remain open. An independent SQLite chunk model is also research only.
- jSketcher is a research candidate, not a deployed integrated CAD workflow. A browser host/export prototype has produced valid core 3MF for two disjoint assigned boxes using a stand-in file store. The enclosure's touching inset is deliberately refused pending qualified interference checks. This is not yet a qualified general manufacturing exporter. Solver midpoint/conflict fixes remain research-only; do not rely on them until the whole conflict/recovery path is qualified.
- User authorization covers necessary installs, downloads, live tests and changes; use scoped test accounts, remove only fixtures you created, and retain accounts/data if safe cleanup cannot be proved. Do not ask the user to approve routine reversible work or repeat permission already given. Communicate before disruptive changes, use established managed rollout/recovery, and never restore old account databases or files merely to roll back code.

## 0. Shared rules for every milestone

- [ ] Start from real current source, running configuration, related docs and app behavior; classify each statement as verified, partial, planned or unknown. Reproduce a reported bug before claiming a fix, unless the direct defect is already conclusive.
- [ ] Ship a complete vertical task: open/create -> change/use -> save -> close -> reopen -> inspect result; preserve two independent windows and account isolation. Use My files for account work, and label upload from the computer separately. Temporary v86 Linux files stay temporary and separate; Files may expose its Linux home for exploration.
- [ ] Make interface and workflows clear to a novice without removing expert controls. Test touch and accessibility, keyboard/mouse, phone, 1080p and 4K; genuine physical-device results must be distinguished from viewport emulation. Use sane default window sizes by viewport and resize responsive layouts after fullscreen/viewport changes.
- [ ] Preserve edits on failed open, save, cancellation, failed computation, stale version or account switch. Close dialogs should be app-themed, honest and cancelable. Repeated open/close must not accumulate listeners, workers, timers, audio, guest sessions or object URLs.
- [ ] Share desktop services, permission checks and documented commands; keep third-party UI frameworks and dependencies inside their app bundle where appropriate. Do not introduce a new global framework or an unnecessary wrapper when a native menu/file action suffices.
- [ ] Remove or suppress third-party account/provider prompts and telemetry where requested; maintain `DEFERRED_APP_FEATURES.md` with product and feature names that were disabled. Do not imply an AI/provider replacement exists. Preserve license/source notices and check distribution obligations for real dependencies.
- [ ] Check app/service boundaries with real registered accounts, malformed inputs, conflicts and resource limits; distinguish unit, browser-emulation, physical device, public network and real hardware evidence. Never claim a simulator, export, manufacturing file or optimization result proves real-world safety or accuracy.
- [ ] Keep app status, a plain student guide and a reproducible test recipe current. If a feature is incomplete, label it accurately instead of shipping a misleading success. Back up source/notes to box-git; clean only identified temporary fixtures and obsolete builds, monitoring local and server disk/RAM.

## 1. Accounts, storage and file-service baseline

- [ ] Verify login/register, session expiry, account switches, credential recovery and error handling on live and isolated services; enforce the user's current username/password rules. Visitors must authenticate to enter the desktop. Do not log passwords, private keys or file contents in diagnostics.
- [ ] Exercise account IDs -> permission records -> isolated server directories. Test two simultaneous accounts and an attacker using changed IDs, paths, symlinks, traversal, replayed proofs or another account's file; no foreign file, chunk-existence information or directory listing may leak.
- [ ] Verify My files browser-first save, pending/synced/conflict status, durable server write, fresh-session recovery and user-visible errors for quota, missing files, permissions, disk full, browser storage eviction, lost network and server restart. Ask for persistent browser storage where supported; explain that browser clearing can remove its copy.
- [ ] Retain normal account files as server disk files and a browser copy, while keeping temporary Linux guest data separate and resettable. File moves, copies, deletes and folder operations must be atomic or explicitly recoverable; sync deletion only with correct account/version checks.
- [ ] Test ordinary and interrupted uploads/downloads near the intended 128 MiB file limit without asserting every editor can open a 128 MiB file. Measure browser heap, server RSS, temporary disk, file descriptors and responsiveness; enforce documented, meaningful bounded resource limits.
- [ ] Capacity-test 10–30 simultaneous classroom sign-ins and prepare for roughly 100 parallel users, including a subset transferring large files, slow clients and unrelated small reads. Measure cold and warm disks and service recovery before claiming a capacity number.

## 2. Bidirectional changed-chunk synchronization

- [ ] Write a versioned protocol specification and executable test vectors. Define account/path/version binding, chunk size/content-defined boundary rules, chunk order and length, cryptographic hash domains, canonical manifest, version/CAS tokens, file rename/delete semantics, limits and error codes. A Merkle or manifest root is a **new version type**; it is not the existing flat SHA-256 and cannot be obtained by concatenating independent SHA-256 hashes.
- [ ] Preserve the existing normal signed challenge/proof and account authorization for manifest, chunk and commit operations. Scope chunk existence, staging, storage and caches per account. Test that an unrelated account cannot infer the existence or contents of a chunk from timing, error shape or an API response.
- [ ] On first sync transfer the required content; on later sync compare verified manifests and transfer only missing/changed chunks in **both** directions. Incremental hashing must reuse verified unchanged data when the storage layer provides trustworthy dirty ranges/versions. For inserts and deletes, measure resynchronization rather than assuming fixed boundaries preserve all following chunks.
- [ ] Support optional, versioned format-aware adapters where they save meaningful work: for example, document edits or CAD object/parameter changes. Define the adapter's supported versions, canonical representation, deterministic reconstruction and final integrity checks. Preserve the exact intended file and its metadata, account authorization, conflict recovery and rollback; use verified byte-based sync for unsupported, damaged or ambiguous formats. Test compressed containers and binary assets rather than assuming semantic edits always produce small byte changes. Do not make format-specific parsing a requirement for ordinary file access.
- [ ] Provide a safe transition from current full-file SHA and flat server files: build verified manifests on demand; maintain explicit legacy-client behavior and avoid changing the meaning of old version tokens. Full transfer may be necessary for first sync, a missing cache, a legacy peer or untrusted/corrupt metadata; document and test that exceptional path rather than treating it as normal changed-file sync.
- [ ] Stream bounded chunks with backpressure and bounded parallelism. Keep browser UI responsive; check cancellation/account identity after asynchronous work. Bound weak-hash/strong-hash candidate work (the old rolling prototype had a repeat-data collision flood) and prevent unbounded RAM, disk, timers, worker or file-descriptor growth.
- [ ] Run heavy file processing, hashing, simulation and similar computation in Web Workers or appropriately isolated worker processes, not on the UI thread. Verify responsiveness, bounded concurrency, cancellation, disposal and account/session changes, including multiple simultaneous app windows. Lightweight UI coordination may remain on the main thread.
- [ ] Stage private uploads, verify each chunk, order, size, full logical file and expected prior version, then atomically publish a complete file/manifest. Recover interruption before/after every journal, rename and fsync boundary; reconcile a lost reply that may already have committed. Never replace a newer version or publish a partial file.
- [ ] Persist browser chunk cache/manifest with transactionally bound generations and user/account isolation. Coordinate same-account tabs and devices; on conflicts preserve both edits until the user chooses. Download into a temporary verified snapshot and publish only after every required chunk is valid. A fresh device may need all chunks; a device with a valid prior copy should fetch only changes.
- [ ] Handle account logout, switch, deletion, file delete/rename, interrupted retry, missing chunk, cache eviction, quota and server restart. Garbage collection must not remove chunks referenced by committed files, in-flight transfers or recoverable journals. Existing host-disk edits must invalidate or rebuild stale metadata safely.
- [ ] Test first sync, no-op, one-byte changes in multiple chunks, insert/delete, rename, high-entropy and repeating/adversarial inputs, duplicate/out-of-order/corrupt/truncated chunks, forged manifests, account leakage, overlapping writes, lost reply, both-side crashes and expired sessions. Capture transferred application bytes both ways; for a 104 MiB file with a one-byte edit and a valid prior copy, demonstrate small changed-data transfer rather than a full file, and document measured overhead.
- [ ] Run real signed browser/server tests, 128 MiB boundaries, slow/cold disk, concurrent classroom load, two browsers/devices and a physical phone where available. Measure CPU, UI latency, memory and total peak disk; validate manifests and final bytes against independent full-file hashes. Only then stage a pinned release with exact operator inventories, crash-tested journal recovery and code-only rollback. Never wipe accounts/files to simplify the test.

## 3. Desktop, lifecycle and operations

- [ ] Keep the desktop as a unified application host: window/workspace state, focus, taskbar, launcher grouping, settings, themed errors, menus and keyboard/touch controls must remain consistent. Restore only intentionally saved state, not stale processes or another account's windows.
- [ ] Require per-window ownership and disposal for DOM listeners, workers, graphics contexts, audio, guest terminals and network requests. Test repeated open/close/reopen, multiple same-app windows, account changes during asynchronous work, minimizing, viewport rotation and stale completions.
- [ ] Support My files import/export in desktop dialogs without duplicate app-specific sign-ins. Integrate file actions into each application's own menu; remove redundant wrapper bars and transient 'opened' overlays. Upload remains explicit; use the requested Files right-click/download and drag-upload behaviors where supported.
- [ ] Make offline/connection status and maintenance honest: no claim of saved work without proof. Test reconnect, server restart, dropped Wi-Fi, interrupted save and explicit last-saved recovery. Users retain normal browser control; do not tell them that reloading necessarily accelerates peering.
- [ ] Maintain secure origin/CSP, cross-origin isolation and private runner policies only where needed. Verify executable dependencies, source/licensing, authentication for source/license pages and prevention of third-party credential/telemetry calls. Public network relay/browser is experimental and low priority; never imply arbitrary sites are rendered correctly or originate from the visitor's connection.
- [ ] Provide discoverable, typed, validated per-app operations for people and agents through the **same** model, authorization, file and lifecycle rules. A browser API is not automatically a remote-agent service. Require a separately authorized transport, per-user/instance permissions, revision checks, cancellation, limits and auditability before external invocation.

## 4. App-by-app delivery: core, office and programming

Apply all section 0 tests to each app; maintain a real status row and guide for each. Group related work but finish each app's primary user task.

- [ ] **Files:** discoverable create/rename/move/copy/delete/upload/download, sync/conflict feedback, safe folder behavior, browser/account storage and separate temporary Linux home. Test host disk changes, multi-tab, large files, interrupted moves and recovery; never pretend folder moves are done if not implemented.
- [ ] **Text/CodeMirror:** open/create/edit/save/reopen code and text with revision/conflict handling, large-file limits, encoding and touch selection; validate real desktop and phone. Shared editor library remains isolated/packaged correctly and resources release on close.
- [ ] **Terminal/v86:** independent shell sessions/windows, xterm scroll/touch controls and honest temporary-filesystem boundaries. Test supported BusyBox/nano/interactive behavior, guest reboot/reset, authenticated network/SSH policy and per-user destination-only logs. Do not claim guest files are the persistent account drive.
- [ ] **Calculator and Help:** complete the basic calculation/history and explanation flow; ensure help is truthful, concise and reflects the beta service.
- [ ] **Documents:** usable report-writing, proper My files open/save and PDF export, layout/print correctness and Unicode coverage; no DOCX/XLSX requirement unless the user requests one later. Distinguish document edits from flattened export.
- [ ] **Spreadsheets:** correct supported CSV/TSV round-trips, formulas, large-cell behavior and bounded large-file work; replace the existing 8 MiB restriction only after measuring a safe implementation. No requirement to support XLSX.
- [ ] **PDF Viewer:** safe opening, navigation, text/search where supported, password handling, large documents and explicit scan/OCR limitations; use My files and release workers/resources.
- [ ] **Data Explorer:** import, inspect, query/visualize and export using DuckDB/Perspective; test precision/large integers, malformed data, memory and reproducible results. Never silently round exact identifiers.
- [ ] **Browser Python Notebook:** isolate per-account notebooks, use stable non-enumerable IDs, test kernel startup/recovery, packages, autosave/conflicts, real account isolation and worker cleanup. Explain browser Pyodide limitations and treat untrusted notebook execution appropriately.
- [ ] **Notebook scripts and widgets:** default to metadata-free Jupytext `py:light`; offer `py:percent` and explicit `.ipynb` when notebook metadata or saved outputs are wanted. Running cells, changed execution counts or transient outputs alone must not trigger sync of the source file. Preserve authored code and Markdown, detect unsupported or lossy conversions, and test round-trip, conflicts and fresh-session reload. Bundle and test real `ipywidgets` Python and frontend support locally, including actual callbacks, phone touch, independent kernels and cleanup; do not claim support merely because a package imports.
- [ ] **Linux Notebook and terminal tools:** clearly label the separate v86-backed path; demonstrate supported subprocesses, executable tools and package behavior before claiming them. Preserve temporary Linux state semantics and avoid treating it as persistent My files.

## 5. Creative, media, diagrams and shared tools

- [ ] **Image Editor:** open/save from My files, Blob/object URL cleanup and conflict-safe saves; qualify animated/metadata/format limitations, low-memory devices and changes during long operations. The lower-copy candidate is research-only until exact live integration and account tests pass.
- [ ] **Audio Editor, waveform and Tone tools:** coherent open/edit/preview/export, independent audio windows and cleanup; disclose unsupported channels/codecs, measure latency on physical devices and prevent autoplay surprises.
- [ ] **diagrams.net, Excalidraw, SVG Editor:** use each program's own file menu with shared storage, no vendor account prompt, safe import/export, unsaved-change recovery and touch/4K layouts. Test complex SVG and unsupported provider integrations honestly.
- [ ] **Embroidery Studio and Stitch Converter:** local file workflow, material/thread settings, preview, explicit unsupported SVG and machine-format limits; remove provider routes while recording deferred AI features. Do not claim machine compatibility without independent validation.
- [ ] **Photos/video/music/books/news/maps and other requested apps:** inventory actual source and licenses; integrate only real working runtimes with shared storage, responsive layout and cleanup. For planned items—PhotoSwipe, Shaka/Video.js/hls.js/Mediabunny, Howler, foliate/PDF.js, Readability/RSS, MapLibre/OpenLayers/Leaflet—distinguish an included library from a usable app.
- [ ] **Shared system tools:** inventory CodeMirror, ffmpeg.wasm, zip.js, Mermaid, Plotly/ECharts, OpenCascade, ONNX Runtime, Transformers, MapLibre, WaveSurfer/Tone, TanStack Virtual, Trystero, WebTorrent and Yjs by actual bundled capability. Lazy-load with versioned resources, tests and disposal. A gray menu entry is a library reference, not proof of an integrated workflow; no P2P optimization is a current chat goal.
- [ ] Test browser-native media permissions, MediaDevices/MediaRecorder/WebCodecs and any provider/JMAP/MQTT integrations only when built and explicitly authorized. No user-supplied AI provider is currently configured; keep missing provider-dependent features on the running deferred list.

## 6. Electronics, fabrication and games

- [ ] **Arduino/AVR8js:** run actual firmware, GPIO/timers/UART examples, open/save source and firmware, distinguish simulation from physical execution. Evaluate and benchmark browser compiler vs v86 toolchain before promising either; Web Serial is separate and opt-in.
- [ ] **Pico/RP2040js:** load real supported firmware, serial and examples; accurately qualify peripherals, simulated flash and reset/save behavior. Warn about unsaved simulation state and never promise physical hardware fidelity.
- [ ] **Digital Logic/Circuit Simulator/Circuit Lab/PCB:** use honest examples and explain combinational/netlist vs analog simulation vs PCB design. Qualify supported components, solver, visual parts and My files separately. Circuit Lab/PCB research is not deployed merely because source exists.
- [ ] **Electronics Design:** provide breadboard, schematic and PCB views that can be arranged side-by-side on large monitors, with simplified touch on phones. Verify component coverage, consistency across views, imports/exports, versioned saves and failure when parts are unsupported.
- [ ] **Replicad, Mesh:Tool, Kiri:Moto and G-code Preview:** test actual model, mesh, slicing and preview workflows, supported formats and output; isolate heavy engines, avoid duplicate copies and report machine/printer limitations. A preview or simulated slice is not a verified physical print.
- [ ] **Game previews:** preserve the four on-disk/menu groupings. For each preview finish a complete ordinary playthrough, rules, controls, pause, account save/reopen where relevant, two windows, audio and actual touch. Add final art as available; XR is a separately tested capability, not implied by a folder name. Keep seven Learning & Strategy rule-only entries disabled until an interface and workflow exist.
- [ ] **Microduck:** preserve the live two-account save/reopen and isolation checks; continue qualification of actual controls, phone use, runner lifecycle, model/reference data and honest physical-simulation limits. Its current 64 MiB project opener is not the general 128 MiB file-service guarantee.

## 7. Native CAD: sketch and parametric foundation

- [ ] Audit each advertised relationship as an explicit mathematical contract: entity types; supporting vs finite geometry; units, signed/unsigned and orientation; endpoint/contact/branch selection; degeneracy; failure and persistence.
- [ ] Correct midpoint as `2P=A+B`, preserving the current midpoint-style Symmetry behavior without duplicate equations. Before release, solve the existing atomic-admission/redundancy/conflict problems: rejected constraints must not move geometry, contaminate later constraints or lose object links; removing a blocker must re-evaluate safely. Test stored constraint orders, repeated solves, invalid input, save/undo/reopen, exceptions and reasonable large connected sketches.
- [ ] Implement driving signed X/Y and projected distances, diameter, concentricity, collinearity, full-entity fix, rigid groups and independent-axis symmetry. Keep reference measurements separate from driving constraints; a radius readout must not be called diameter.
- [ ] Build shared typed measurement/relation operations for equality, ratio and difference of lengths/angles instead of separate inconsistent subsystems. Geometric unknowns solve together; formulas over existing parameters evaluate in dependency order. Define meaningful underconstrained, locally constrained, redundant, inconsistent, degenerate, failed-convergence and ambiguous-branch states.
- [ ] Preserve user intent for line/segment, circle/arc domains, directed/minor/supplementary angles, internal/external contact and zero-length geometry. Test tolerances at different scales, residuals, rank/singularity, warm starts, failed edit rollback and explicit repair. A failed solve is not automatically proof of impossibility.
- [ ] Add typed units, formulas, dependency/cycle errors, integer/boolean domains, reference/driving conversion and configurations. Do not silently round a dimension or invent a physical unit. The WebOS numeric parser differs from a standalone `eval` path; audit the actual mode and do not claim full unit/dependency support yet.
- [ ] Qualify real model history for datums, extrusion/revolve/booleans, holes, fillets/chamfers, patterns, shell/draft, sweep/loft and multiple bodies. Preserve authored input and clearly mark stale/failed geometry after regeneration. Test changes, undo/redo, save/reopen and failure recovery.
- [ ] Strengthen stable authored feature/part IDs and generated-topology provenance. A UUID or array index on a reconstructed face is not enough. On split, merge, disappearance or ambiguity, preserve intent and request repair rather than silently binding the wrong geometry. Support OCC and Native Mesh only for actually implemented operations; no parity claim.

## 8. Core model 3MF manufacturing milestone

- [ ] Native project is the editable source; the core 3MF is a manufacturing handoff from a specific design revision. The format is not fixed and the old importer is not required. Protect files from accidental overwrite and reject unsupported/corrupt formats clearly.
- [ ] Persist deliberate, named parts/regions, units, authored grouping, transforms, material identity and independent appearance. Ordinary parameter edits must preserve verified assignments or clearly mark missing/split/merged/ambiguous bindings for explicit repair. Color is not material identity.
- [ ] Represent **one printable object with multiple aligned material regions** separately from **multiple independently printable objects**. The author selects the grouping; do not infer it from color. Preserve source revision, build items, components and transforms. Do not require printer, filament, slicer or Bambu-project settings in core model 3MF.
- [ ] Generate model-derived geometry, not camera/display meshes. Request a controlled tessellation tolerance without modifying the live CAD model, retain orientation and placement, and ensure correct units. OCC's current `Interrogate` remeshes at a fixed tolerance; the research copied-shape path and exact-box indexing are not general curved/cavity solutions.
- [ ] Validate finite coordinates, triangle indices, closed/watertight orientation, non-manifold edges/vertices, degeneracy, self-intersection and inter-region overlap/contact. Preserve real shared interfaces and report uncertain cases; do not use a special rectangular-pocket exception as a substitute for general validation. Bound memory, time and cancellation.
- [ ] Write standards-conforming 3MF core ZIP, XML, resources, base materials, build objects/components and transforms to My files with conflict-safe save. Independently read/validate names, units, bounds, materials/colors, grouping, mesh and revision; measure resource use. No claim that color alone specifies physical properties or actual printer compatibility.
- [ ] End-to-end acceptance: create an enclosure body, separately printable lid and contrasting inset label grouped with the lid; change width and wall thickness; save/sync/reopen the native design; export 3MF; independently verify two build objects, three assigned regions, placements and dimensions. Test stale revision, split/missing body, invalid mesh, overlapping regions, cancellation, two accounts and interrupted output. Simulated manufacturing feedback can be used with stated assumptions. **Bambu Studio, physical filament assignment and a real print are optional, not gates.**

## 9. Curves and demanding profiles (after the mechanical vertical slice)

- [ ] Qualify ellipse axes/orientation, general point-on-curve, curve normals at a defined point, arc/path length and fraction-by-parameter versus fraction-by-arc-length.
- [ ] Add spline endpoint tangency and explicit G0/G1/G2 behavior with stable contact/branch choices, continuity diagnostics, degenerate derivatives and save/undo/reopen. A circular fillet tangent to lines is not automatically G2.
- [ ] Add associative projection, intersection and pierce with persistent references, explicit multiple-solution choices and failure repair; avoid silent rebinding. Start area/perimeter as measurements and add driving global constraints only for a demonstrated workflow.
- [ ] Prove a curved handle/cover through major parameter edits, continuity inspection, regeneration, export and honest limits across the engines that actually support it.

## 10. Physical-system document and materials

- [ ] Make the authored physical system a coherent model: geometry and meaningful regions, material definitions, assignments/orientations, interfaces, physical formulations, operating conditions and design requirements. A CAD body, material region, print object and surrounding analysis domain can differ.
- [ ] Keep a real material's supported physical properties together; represent scalar, directional/tensor, state-dependent and history-dependent laws where required. Store units, source/revision, applicable range, calibration and uncertainty. Unknown values stay unknown; do not silently insert attractive defaults.
- [ ] Separate a material definition from region assignment and orientation so two regions can use one material differently. Represent bonded/sliding/contact, thermal, electrical and field interfaces explicitly; a geometric union must not silently erase a needed interface.
- [ ] Version and persist sources/excitations, mechanical loads/supports, environmental/initial conditions, motion states and operating ranges. Test ordinary geometry edits and explicit unresolved references after topology changes. Distinguish modeled deformation from an authored design change.
- [ ] Reuse the same validated document operations for UI and authorized agents; enforce revision, permissions, cancellation and provenance in both. A model, an analysis mesh and a result are different artifacts with explicit dependencies.

## 11. Forward studies, form finding and solver tools

- [ ] Keep three workflows distinct: forward simulation predicts behavior for a specified system; physical form finding finds an equilibrium/evolving state; inverse design searches allowed design variables for better objectives. Do not turn a predicted deformation into permanent geometry without an explicit action.
- [ ] Qualify actual meshing/solver runtimes before exposing them as usable system tools: Gmsh may have a browser WASM path; Elmer and GetDP require verified ports or controlled backend execution. Review licensing, resources, sandboxing, cancellation, CSP, repeatability and source availability; a menu entry is not integration.
- [ ] Derive a tagged numerical mesh from the revisioned model and region/boundary assignments. Specify analysis domain—including surrounding air where relevant—formulation, units, boundary conditions, materials, operating cases, requested outputs, tolerances and software versions.
- [ ] Run and retain reproducible studies; record inputs, solver/mesh settings, convergence, failures, warnings and provenance. Validate against analytical or trusted reference cases, mesh refinement/sensitivity and material applicability. Label stale results and prohibit presenting a failed solve as a valid candidate.
- [ ] Test thermal, structural, electrical and magnetic extensions only as actually implemented; distinguish quasistatic/transient, nonlinear and coupled assumptions. Compare simulation with physical measurements only when such evidence is available and clearly identify uncertainty.

## 12. First magnetic design and inverse-search milestone

- [ ] Create a magnetic sensor fixture with named solid and surrounding regions, a meaningful sensing region, packaging/assembly constraints and operating positions/range. Define desired response and explicit allowed dimensional/material/orientation changes.
- [ ] Supply a small curated set of real material models with appropriate magnetic laws, units, sources, ranges and orientation; unknown properties remain unknown. Distinguish linear/nonlinear response, saturation, permanent magnets, anisotropy, hysteresis/loss and temperature only where the chosen study supports them.
- [ ] Show that changing geometry or material yields a reproducible, physically justified change in a region-based quantity, not just a color plot or single hand-picked point. Validate units, domain/boundary treatment and appropriate mesh refinement against a trusted reference.
- [ ] Run a bounded search over declared dimensions/materials/conditions, with resource budgets, cancellation, invalid-candidate handling, reproducible seeds and no unauthorized variable changes. Measure performance across required operating cases and preserve every candidate's input and evidence.
- [ ] Regenerate a selected manufacturable design and independently reanalyze it. Report a better feasible candidate, a local optimum or tradeoffs only as established; do not invent a material by independently tuning incompatible properties or imply a global optimum/physical validation.

## 13. Future mechanisms, materials research and additional domains

- [ ] Make assembly instances and saved references durable, then qualify fixed, revolute, prismatic, cylindrical, planar and spherical joints, limits and couplings with a linkage/slider and closed-loop tests. Current assembly registry and unsupported snapshot behavior are not a complete mechanism system.
- [ ] Separate kinematics from collision, physical dynamics, clearances and manufacturing tolerances. Couple structural deformation and magnetic fields only through an explicitly specified and validated study.
- [ ] Add material-distribution/topology optimization, advanced surfacing, sheet metal, routing, drawings and specialized analysis only against a concrete use case; maintain explainable assumptions, model-specific validation and provenance across scales.
- [ ] Defer provider-dependent AI, optional P2P/WebRTC features, CDN/distribution and optional real printing/slicer projects until separately selected. Preserve architecture hooks without treating any of them as prerequisites for the current 3MF milestone.

## 14. Release, testing, handoff and acceleration

- [ ] For every change, run focused unit and failure tests, then a representative end-to-end account/browser workflow. Test real generated artifacts with independent readers or implementations. Do not repeat broad tests without a reason; do not substitute mocks for the required real boundary.
- [ ] Stage code-only, content-addressed releases from clean source. Preserve current live flags, ports, account data, other sites and the /desktop prototype. Verify exact runtime/dependency/manifest hashes, CSP and service state. Test upgrade, interruption, recovery and code-only rollback before changing live; a committed-journal exception needs explicit phase-aware recovery.
- [ ] After an authorized live update, verify the changed workflow, login/files, account isolation, app/worker cleanup, unrelated sites and disk headroom. Capture truthful evidence and update guides/status; clean test files/accounts only by exact ownership, and leave no unnecessary old releases or build artifacts.
- [ ] Use independent worktrees/branches for parallel app, CAD, storage and validation work. Assign each agent concrete files, scope, tests and a no-overwrite rule. Integrate tested slices promptly, resolve actual conflicts deliberately, and back source/notes up to box-git. Never send data to GitHub while its remote is removed.
- [ ] Speed up through reusable fixtures, common app services, incremental hashing/sync, shared protocol test vectors, caching with correct invalidation, small representative designs, and parallel work that does not contend for heavy builds. Optimize measured bottlenecks without replacing the user's end goal with a permanently narrow special case.
- [ ] Re-evaluate the sequence as evidence improves. Keep this full list, the actual app inventory, deferred third-party features and specific acceptance examples current. An agent must stop and report a genuine external blocker; it must not declare the program finished merely because a single slice works.

## 15. Agent and subagent execution plan

### How to split the work

Use one integration lead and as many workers as are useful. A worker can delegate its own **non-overlapping** subtask when its tools and instructions permit. Smaller models should receive one bounded task with specific files, tests and expected output—not the whole program and a vague instruction to finish it. The lead remains responsible for the complete user-visible result, resolving conflicts, checking source and test evidence, and integrating approved, qualified work. The following lanes are opportunities for parallelism, not a requirement to start all tasks at once.

1. **Storage protocol lane:** one owner specifies/version-controls the chunk manifest, IDs, upload/download operations, integrity and compatibility test vectors. Subagents may separately investigate chunk boundary algorithms, adversarial behavior and protocol tests. Nobody changes production HTTP behavior until the contract is agreed in the candidate branch.
2. **Server storage lane:** implement signed/authorized per-account manifest/chunk operations, private staging, filesystem publication and recovery under the protocol contract. Delegate fault-injection/GC tests independently. Own `active-system/gateway_service/` and any necessary server release/operator files in a dedicated worktree. Coordinate exact shared interfaces with the protocol owner; never replace the production `user_store.py` with unfinished research wholesale.
3. **Browser storage lane:** implement persistent verified chunks/manifests, incremental hashing, bounded workers, download/upload, multi-tab locking, cancellation and conflict UX against the same protocol. Own `active-system/storage/browser/` and the browser gateway client; coordinate any edits to the shared client with the server owner. Delegate phone/memory and two-device tests.
4. **Storage integration/release lane:** merge protocol, server and browser candidates in an isolated integration branch; run real signed two-account, 104/128 MiB, inserted-byte, crash/recovery and simultaneous-tab tests. Independently inspect authorization, update/rollback and data integrity. The lead—or one designated operator—prepares and applies the managed live release after gates pass; do not have several agents changing server config at once.
5. **App lanes:** assign one app or tightly coupled group per worker, such as Files; Text; documents/PDF; spreadsheet/data; notebooks; image; audio; diagrams; electronics; fabrication; games. Each owns its `apps/system/<app>/` or `apps/games/<group>/<app>/` and app-specific tests/docs. A worker proposes changes to shared desktop services through the lead rather than editing the same shared file concurrently. Prioritize complete user workflows and real problems found during use.
6. **Desktop host lane:** one owner handles `active-system/app.js`, launcher/taskbar/workspaces, common file dialogs, application lifecycle, CSP and cross-app services. Other app agents request small interface changes with an example and test; the host owner integrates them and runs regression tests. Do not create a second desktop architecture for each app.
7. **CAD solver lane:** in the JSKetcher repository, qualify midpoint/constraint semantics, atomic failed admission, deterministic priority, parameters and persistent references. Independent reviewers add counterexamples and actual sketch/save/undo tests. Keep conflicting or slow research variants off the integration branch until proven.
8. **3MF geometry lane:** own model-derived tessellation, units/transforms, topology/mesh validation, core package writer and independent lib3mf/other-reader tests. One subagent may work on OCC and another on Native Mesh, but neither may claim support for the other's unsupported operations or substitute display meshes. Handle shared material-interface/contact uncertainty explicitly.
9. **Manufacturing-document lane:** own native project metadata for material identities, independent appearance, authored print objects/regions, grouping, placement and revision, with safe rebinding after edits. Coordinate a versioned contract with the geometry and desktop-host owners. Test actual save/reopen, current account, concurrent edits and split/merge ambiguity.
10. **Enclosure integration lane:** merge CAD, manufacturing metadata, file-host and 3MF work; implement the real enclosure/separate lid/grouped label workflow. Verify parameter changes and native My files save/reopen, then independently inspect core 3MF. Do not substitute a hard-coded rectangular-pocket exception for general interference handling. Bambu/real print are optional.
11. **Physical model and solver lanes, later:** separately design versioned physical-system/material/interface/study models and qualify actual Gmsh/Elmer/GetDP runtimes. Integrate only after a reproducible forward model and reference tests exist. The magnetic-fixture lane combines these with a bounded search and independent final reanalysis; do not start by claiming all physics or global optimization works.
12. **Cross-cutting QA/security lane:** review other workers' exact code/artifacts rather than trusting their summary. Add adversarial inputs, account isolation, interruption, concurrency, resource and lifecycle tests. Identify what is proven vs simulated vs unknown; independently test a representative end-to-end workflow before release. Report a concrete reproducer when a gate fails.
13. **Documentation/inventory lane:** maintain the app table, student guide, deferred provider/AI feature list, source/license notes, implementation decisions and this program. Documentation describes observed state; it never makes an unfinished tool appear complete or blocks independent implementation while waiting for prose.

### Dependency map and safe parallelism

- Storage protocol -> server and browser work **in parallel** -> signed end-to-end integration -> crash-tested rollout. Existing full-file saves remain the safety baseline during development.
- CAD semantic/solver qualification + manufacturing document + geometry extraction can advance **in parallel** behind explicit contracts -> combined native-project/3MF fixture -> real My files enclosure workflow -> independent 3MF verification. A partially working solver is not a reason to hide unsupported geometry.
- Each app worker can improve its own menu, UX, examples and lifecycle while the common file service advances. Integrate to the shared contract and rerun only the affected end-to-end tests after its interfaces change.
- Physical-system data design can proceed alongside 3MF, but reliable solver results and inverse search depend on qualified geometry, assignments, study definitions and reproducible forward models. The first magnetic fixture is a vertical gate, not a promise to implement every physics domain first.
- Tests and implementation for the same feature should run together, not in years-long isolated phases. Use one small golden workflow early and broaden to failures, device sizes and scale as evidence warrants. One project owner chooses which slice matters next and merges compatible work; avoid requiring all agents to wait for every other lane.

### Worktree and branch procedure for another machine

1. Check that the relevant repository/branch and intended base commit actually exist on box-git. Clone or fetch over the authorized LAN connection. Example for the desktop repository: `git clone box-git:/srv/data/git/CodiServer-distro.git codi-desktop`; for CAD: `git clone box-git:/srv/data/git/JSKetcher.git jsketcher`. The clone's `origin` then points to box-git. Do not configure or push a GitHub remote for jSketcher while the user has asked to keep it LAN-only.
2. Fetch and inspect the chosen base with `git fetch origin` and `git log -1 --oneline <base>`. Create a distinct branch/worktree per task, for example `git worktree add -b agent/<task> ../agent-<task> <base>`. Never choose a base solely from an old note; ask the integration lead which candidate contains the latest relevant work when branches differ.
3. Current reference points, **not permanent targets**: desktop `simplified` was `c78b40341`, while live Microduck source was on `research/microduck-desktop-integration-20261102` at `f6cc1ca55`; chunk research was `research/chunk-sync-prototype` at `f2402f81b`. JSKetcher `webos-integration` was `518a4666`; later 3MF, metadata and solver research are separate `research/*` branches. Fetch and recheck before starting; do not assume a live release equals the tip of `simplified`.
4. Read applicable `AGENTS.md`, app docs and test prerequisites. Install dependencies only in the isolated checkout/project environment as needed; user has authorized required installs/downloads. Keep source, manifests and notes in Git; do not commit generated build outputs, caches, private keys, credentials or test account data. Before and after heavyweight builds, inspect free disk/RAM; coordinate a single heavy build slot if resources are tight.
5. Commit focused source/test/doc changes to the task branch and push only that branch to the appropriate box-git repository. Give the lead the exact repository, branch, full commit hash and parent/base. The lead reviews and merges/cherry-picks into an integration worktree, resolves actual conflicts, reruns combined tests and backs up the resulting branch. Do not force-push or rewrite unrelated branches.

### A precise task template for any model

Give each worker this filled-in brief:

```text
Task: <one observable outcome>
Repository and box-git branch/base SHA: <exact values>
Owned paths: <app/service and tests; list shared files requiring coordination>
Inputs and current evidence: <source paths, known behavior, fixture>
Must preserve: <account data, APIs, other apps, version/conflict semantics>
Implement: <concrete changes and user-visible workflow>
Tests: <exact scenarios, actual browser/server/device boundaries, limits>
Not in scope: <explicit deferred work, e.g. no live deploy or no provider>
Done when: <observable end-to-end result and required evidence>
Return: <commit SHA, branch, files, commands, results, failures, limitations>
```

The worker should inspect the real code, run a bounded failing reproduction where appropriate, implement the change, test its actual behavior, document remaining limits and commit. If a test cannot run, report exactly why and continue independent work; do not invent success. A worker may make ordinary choices, install authorized dependencies and use synthetic accounts in its isolated fixture. It must not delete unrelated data, publish externally, alter a shared live service or overwrite another worker's uncommitted work unless that specific action is assigned. If live rollout is assigned, follow the already authorized managed workflow and verify it; do not create a new approval ceremony. The lead must not interpret a worker's completion message as proof without inspecting the diff and relevant evidence.

### First assignable work packages

- [ ] **C1 — Chunk specification:** write the versioned bidirectional protocol and browser/server test vectors, including content-defined boundaries, flat-SHA compatibility vs new Merkle roots, account scoping and ABA/version behavior. Deliver spec, reference encoder/decoder and corruption/adversarial tests; no live server changes.
- [ ] **C2 — Chunk server:** build signed per-account stage/read/commit, CAS, bounded storage, leases/GC and crash recovery against C1. Deliver isolated real-gateway tests for two accounts, fsync/rename failures, replay and unchanged-byte transfer; no private data copied into fixtures.
- [ ] **C3 — Chunk browser:** implement the matching IndexedDB cache, incremental hash/reuse, changed-only upload/download, two-tab and cancellation handling. Deliver Chromium real-account and memory tests for edits, insertion, conflict, cache eviction and fresh-device recovery.
- [ ] **C4 — Storage integration:** combine C1–C3; compare exact files and transferred bytes for 104 MiB/128 MiB cases, concurrent accounts, slow disk and interrupted/lost-acknowledgment recovery. Prepare managed operator upgrade/rollback against the **current** live worker; report any unqualified case before rollout.
- [ ] **A1…An — One app each:** choose an app from the current inventory; open/edit/save/reopen with My files; integrate its own file menu, suppress unwanted account flows, test touch/desktop and repeated disposal, and document real limitations. Each agent owns only its app-specific source/tests; shared-service changes route through the host lane.
- [ ] **M1 — CAD constraints:** start from actual JSKetcher integration candidate and the saved midpoint/cascade regressions. Make the corrected equations, rejection atomicity and save/reopen branch behavior correct, with rank/degeneracy warnings and bounded performance; no live release based on a single passing synthetic example.
- [ ] **M2 — Native manufacturing model:** implement versioned units, region/material/appearance identity, authored object grouping, transforms and revision; verify parameter edits, stale/split/merge behavior and real native project save/reopen. Do not pretend reconstructed face IDs are stable without evidence.
- [ ] **M3 — Geometry and 3MF:** obtain current model geometry at requested tolerance, validate supported solids/interfaces, write core 3MF and independently read it. Test separate build objects and grouped multiple-material regions, cavity/holes/curves, invalid meshes and cancellation; do not silently weld distinct nearby surfaces.
- [ ] **M4 — Enclosure vertical slice:** integrate M1–M3 with desktop/My files; build, edit and reopen the real enclosure/lid/label design, then export and independently verify the two-object 3MF. No Bambu or physical printer required. Record unsupported cases honestly.
- [ ] **P1 — Physical document:** define regions, evidence-backed materials, orientations, interfaces, conditions, studies and revision/provenance without claiming a solver exists. Use the same operations and authorization for people and agents.
- [ ] **P2 — Magnetic fixture:** after a qualified mesher and forward solver exist, implement the explicit bounded sensor-fixture study/search/reanalysis acceptance in section 12. Test known references and convergence; unknown data or failed solves are not valid candidates.

## 16. Deferred spatial XR workshop — lower-priority stretch

User clarified on 2026-11-04: keep this below foundational Files, useful CAD,
single-part learning, human/agent commands and ordinary-browser CSG/motion work.
Plan a separate fork branch (`research/xr-spatial-workshop`, reserved name only).
It is not a requirement for the active Files/JSketcher/core-3MF release.

- [ ] Follow `docs/planning/CAD-LEARNING-CSG-XR.md`: standard single-part learning
  fixtures, explicit fast-interactive versus qualified-engineering paths, then
  the deferred spatial workshop.
- [ ] Reuse authored designs, stable IDs, account-bound files and validated
  commands for phone/desktop, agents and eventual Galaxy XR browser interaction.
- [ ] Prototype correct-scale viewing and minimal spatial manipulation before
  whole-desktop panels, environments/artwork or complex XR authoring.
- [ ] Qualify physical headset interaction, stereo performance, session
  interruption, 2D return and saved-model integrity independently.
