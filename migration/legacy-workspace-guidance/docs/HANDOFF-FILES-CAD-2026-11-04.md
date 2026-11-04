# Files and CAD successor handoff

Checkpoint date: 2026-11-04. This is the starting plan for another integration
agent, including Sol. **The bounded Files beta foundation is accepted; CAD Gate 1
is incomplete.** Main storage promotion, per-app integration, automatic retention
and classroom/100-user capacity are separate open work. The full Files/CAD goal
remains active; this handoff does not pause it.

The immediate job is to finish dependable saved data and safe dependent CAD
regeneration, then qualify useful parametric parts through the same UI and
agent commands. The long-term CAD 1.0–6.0 program informs these boundaries;
it is not the next agent's first implementation task.

## Current operational checkpoint

**Latest user policy:** main and beta are both no-user test deployments. Replace
the release; reloads are expected. Do not spend further work supporting old app
windows/caches or qualifying historical release combinations. Retain actual
file-integrity, account-isolation, resource/lifecycle and basic workflow checks.
Already-proven deployment mechanisms may be reused without expanding them.

Main now serves **0366e10a**: Files, Text, Terminal, Calculator, Help and the
CodeMirror dependency. ZIP actions are omitted because their dependency is not
in the main catalog. Broader apps/games remain on beta. These are integration
targets with bounded evidence, not fully validated libraries or applications.

Beta now serves **830ca4f1** with issuer **853c12e5**, gateway **dd8cbea7** and
SDK **44da83bd**. The reviewed installer and asset actor plan/apply passed on the
actual host. The existing managed controller then changed only main's static
selector from e7 to 0366. Beta's route block stayed byte-identical. Both saved
storage floors remain; transient journals are absent. All ten hosted-service
health checks and both login entry pages passed; `/desktop/` remains byte-identical.
The renewal timer is back to its prior active/enabled state; its service was
already failed and this release does not claim to repair renewal.

Exact receipt: `evidence/files-830-and-main-0366-activation-20261104.json`.
Guard ca25, generator e06f, hosting manifest e9fdd7bb and Caddy 7d17e426 are
recorded there. The installed actor is
`/srv/codi-connected/operators/beta-files-830c-v1/ops/asset-launch.py`; the four
obsolete fixed entrypoints were retired. Do not run them. No further historical
window/cache qualification is required. Fresh public Files/Text save/reopen and beta account-denial acceptance passed,
including normal fresh login and Files opening with no manual storage calls.
The main menus passed desktop and phone emulation. See
`tests/files-public-830-continuity-20261104.md`. R02 is complete for this bounded
beta release. Main's storage code remains older than beta; 0366 corrects its ZIP UI,
not its storage engine.

The bounded F01–F10 and R01 source evidence is reconciled in
`tests/files-foundation-exit-20261104.md`: signed isolation/conflicts, 128 MiB
socket interruption, changed-data transfer, worker cleanup, exact gateway disk/
process faults, actual guest separation and offline reproduction. The fresh public acceptance now closes this bounded beta foundation release. Classroom load,
automatic published-generation cleanup and all-app qualification remain separate.

Desktop branch: `integration/files-jsketcher-release-20261103`. CAD integration
is now `c55bce60`, with candidate association/projection invariants integrated
and independently checked by 12 unit tests and two actual Chromium/OCC suites; the cylindrical through-cut and
analytic inner-loop path are active. The full plate and CAD Gate 1 remain open.
The lanes are CAD analytic hole projection and CAD worker cut/runtime qualification;
the Files acceptance agent has completed its bounded package. Root owns integration and hosting.

## Prior integrated checkpoint (historical; superseded above)

**Current integrated result (supersedes earlier snapshots below):** desktop
`5af7c1bc7` includes shared document operations for Text, Calculator, Files,
Circuit Lab, Digital Logic and the CAD parent. The subtree/advisory controller
has 16 passing primitive checks; independent lead actual-app/engine runs are
recorded in `89236be4d`. Those lead runs use in-memory storage. The separate
signed Files fixture proves real 8 MiB + 7 byte worker-copy cancellation through
the Close button, one worker termination, released locks, no late URL, and an
exact-byte download after reopening at desktop and phone-sized viewports. Its
create/Text-save/rename/move/copy/download/delete UI chain passes too, including
fresh-context readBlob plus independent hash. Chromium download handoff passes,
but completion was observed before the close command returned: this does not
prove a still-running browser download survives closure. No app deployment.

CAD `715628d1` statically embeds pinned OCI glue, preserves live heap access
after growth and verifies WASM. Lead fresh build/integrity and actual
self-only-CSP worker/parent tests pass. Owner signed fixture passes width edit,
worker extrusion and signed save/reopen. Its test package is not a promoted
runtime. `effc3717` records the dependent centered-through-hole contract;
candidate-owned source association is in independent review, while cylindrical
cut and analytic inner-loop projection are next. Full plate and Gate 1 stay open.

Main e7e8 remains unchanged. Existing beta recovery pins the old controller/main
selector, so a recover-only successor with two exact post-floor snapshot families
must be qualified and installed together with the proposed guard. Packaging and
model tests pass in the owner branch. Actual Caddy qualification is active; its
first seed had inconsistent generated auxiliary files and was correctly refused.
No live operator changed. Preserve the existing beta floor and recovery path.

### Earlier checkpoints and evidence boundaries

**Latest review:** Text correction `06e696262` and subtree controller
`63271e457` pass lead real Text/Calculator Chromium tests at 1366/390 and
15 primitive checks. Circuit/Digital Logic migration `e8e6338b5` has owner
real-engine tests with held in-memory storage; native Circuit upload-picker
admission is a remaining correction. Files migration is active. Folder claims
are cooperative, session-local and released on disposal; they do not replace
CAS or establish atomic multi-file operations/cancellation of dispatched writes.

Main e7e8 now has isolated signed Files→Text create/save/fresh-session reopen,
other-account denial, Calculator and real v86 Terminal/nano proof. Forward
transaction, auxiliary render inventory and a proposed distinct-journal CLI
guard are integrated (`53928d31d`, `2855183a9`, `3da83123d`); lead disposable
tests pass. The protected launcher, real-Caddy recovery and current installed
entrypoint coordination are unfinished. **No main activation occurred.**

The signed parent worker-extrusion test exposed a script-policy failure:
verified-blob importScripts is forbidden by that worker response's CSP. Earlier
standalone tests allowed blob scripts and must not be described as production
policy proof. A contained statically bundled worker with wrapper provenance and
verified WASM is being qualified; no global CSP widening or runtime promotion.
Full plate and Gate 1 remain open.

**Main/beta and Save policy:** all games and unfinished integrations must move
off main to beta. Candidate e7e8fb9f keeps Files, Text, Terminal, Calculator and
Help plus CodeMirror; isolated signed admission/layout and actual service-worker
transition checks pass. Main is not yet changed. Saved files and beta layout
remain; old loaded/offline clients may retain old code until updated. Core
workflow qualification and a same-lock managed transaction are underway. Do not
use pre-floor controllers or modify derived Caddy directly.

Desktop `9fa27ad72` installs mount-owned `host.documentOperations`, with
session-local active file claims, synchronous begin, observable busy state and
cleanup. `3f6d745d0` migrates Text/Calculator. Owner and lead independently
rebuilt/reran actual mounted-app Chromium tests at desktop/phone sizes; storage
and accounts were stubs. Remaining apps are in migration, not qualified. No
queued manual Save or app-private controllers; background sync stays separate.

**Worker-history slice:** CAD `d64c506c` matches owner `4ed4a5ec` by tree and
adds `WORKER_RECTANGLE_EXTRUDE_V1`. Host binder `138eff3f` and parent binding/
disposal desktop `ed86194bd` tie owned work to the mounted frame. Isolated
strict-CSP tests pass actual wizard/craft, bounds/topology, width/depth edits,
rejection, undo/redo/native reopen and reset/test-host cancellation. Signed
parent/My files and shared Save integration remain open. Full plate and Gate 1
do not pass. Root typecheck/helper tests pass on the integrated tree.

**Latest user/source rule:** all JSketcher features are suspect and used for
reference/inspiration. Keep code only where independent tests establish its
explicit contract; rewrite inherited behavior/architecture as needed. Later
layers inform early contracts but stubs never count as passed features. The
copyable successor goal has been rewritten to remove superseded v1/operator
and old CAD checkpoint instructions.

**New integration:** `e4a21e7c` adds representation/registration admission,
including all Boolean operands, implicit targets, raw worker-ID names, native
mesh preflight and classifier pointers. Its focused spies and typecheck pass;
`5e54c5a5` carries the real OCC positive plus injected nonzero-registration
regression. `7090a161` integrates transient-reference and generated-face sketch
guards with owner real-worker/GUI/native-ID-boundary tests. `29c89c67` integrates
the real authored rectangle/OCC/semantic-worker/model adapter and owner tests.
These packages are not yet qualified as a deployed signed worker-history workflow.
Registry collision/ID/stored-sketch guards are integrated at `9bb3eae0`, with
owner real-worker tests. Combined application qualification passed at `4cae31eb`;
the later worker-history slice is described above. Public CAD remains
`d3d36bc5` until separate qualification; main removal is pending.

**New Files evidence:** desktop `4613eebae`/`7a119bc4f` records all ordinary Files
UI actions on beta in desktop and phone-sized emulation. Fresh-session `stat`
is explicitly metadata evidence; independent byte-readback evidence is separate.
`37af97707` records identical clean R730 Files builds and focused signed tests,
using existing toolchain/cache prerequisites that are not yet sealed. `12b634976`
records one isolated signed 128 MiB measurement with Linux/speech excluded:
fresh-read PSS max 1,026,091,008 bytes versus 611,861,504 immediately before that
phase, but browser/test verification remains included and sampling is not a
continuous allocation/peak proof. No public deployment changed. Network
efficiency is sufficient for this milestone. Source `0801ea2d7`, integrated as
`72c7fdbc6` after independent review, removes two redundant detached-copy
verification passes. Actual Chromium corruption, local-edit race and account
invalidation controls pass. A full detached Blob still exists; no physical
memory improvement or deployment is claimed. Cold-download streaming contract
`0480d3f52` is recorded in `tests/files-cold-download-stream-contract-20261104.md`;
SDK/source qualification is now recorded at `5974d91dd`: two clean R730 builds
from `90a963920` reproduce the pinned deployed `44da` client byte for byte.
Streaming implementation remains separate work.

**Latest Files priority:** a full detached copy is explicitly acceptable when
released cleanly after use. Prioritize ownership/lifecycle evidence and fixing
retention over removing all full-file materialization. Consumers must clear
references/revoke their object URLs, and jobs/leases must settle on completion,
cancellation and disposal. Handed-out copies stay alive while their recipient
owns them; release does not delete the saved file. Chromium controls physical
reclamation timing, so no immediate RSS-drop guarantee. Repeated real-browser
copy/use/drop cycles and representative host/app cleanup are being examined.

**Earlier qualified ownership/projection checkpoint:** CAD `efb96770`
qualifies internal candidate/accepted engine-resource ownership using source
`531cc24d`: nine pool tests and six actual-browser scripts pass, including real
OCC worker termination, failed/rejected replay, history rollback, setup failure,
document reset, existing rectangle undo/native reopen and both-engine registry
IDs. See the fork's `test/webos/craft-engine-resources-evidence-20261104.json`
and README. This is a real engine lifetime probe in PLANE replay, not worker-prism
model publication. The `engineEvaluation` contract is ready for that caller.

Private projection `6cbee3a7`, integrated as `d6f7dfb0`, constructs real Shell /
MBrepShell objects from the bounded previously validated worker result. Owner
and independent strict-CSP tests pass supported durable IDs under width edits
and reordered local tokens, registry lookup and collision refusal. Lead integrated qualification also passed, recorded at `91c8d95c` in
`test/prism-model-projection/lead-evidence-20261104.json`. Four connector edges and eight vertices stay explicitly
transient; no native pointer or handle is serialized. Shared consumers do not
honor representation restrictions automatically, so this model is unpublished.

The current serial exit checklist is:

1. [x] Authored rectangle profile → actual OCC worker result, bounded strict
   reader, live mount binding and structured source roles (`4b6528e9`).
2. [x] Candidate/displayed/full-tip engine ownership and reset/rejection cleanup
   (`efb96770`, per-document bounds, not a total RAM guarantee).
3. [x] Review and qualify bounded JS model projection on the integrated tree
   (`91c8d95c`); model remains unpublished until the next checks.
4. [~] Gate unsupported legacy consumers and transient durable references;
   connect the exact result to current document/engine ownership and publish
   matching model/history/registry together. Explicitly reject failed legacy
   pushModel rather than invoking an OCC name or silently dropping a target.
   Keep generated reference IDs within native restore limits until a compact
   injective encoding and its round trip are qualified. The exact functions and
   rejection matrix are in the fork
   `docs/research/WORKER-PRISM-CONSUMER-GATES-20261104.md` (`672efcdb`).
   The source packages listed above implement the local consumer/reference
   guards and registry preflight; combined tests and publication remain open.
5. [ ] Prove width/depth edit, rejected change, undo/redo and native save/reopen
   on that complete worker-solid path; then exercise it through My files.
6. [ ] Expand to dependent holes/cuts/fillets/patterns and the full plate test.

The two engines need honest support and failure semantics, not identical
geometry or capabilities. Full Gate 1 remains open. The ordinary desktop CAD
runtime stays `d3d36bc5`; no public CAD repin/deployment occurred.

**Files deployment:** the actual protected plan and apply passed on box-webhost,
activating candidate `3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc`
with issuer `853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21`.
Gateway `dd8cbea7` is unchanged. Signed known-file health passed. Independent
inventory/unit/custody/public checks passed, and the protected v2 floor remains
while all named transient journals are cleared. See
`evidence/files-beta-activation-20261104.json`,
`evidence/files-protected-install-20261104.json`, and
`evidence/files-probe-entry-lead-20261104.json`.

The exact protected forward/recovery entry is
`/srv/codi-connected/operators/files-bundle-ce18b7794adc2472/ops/beta_files_launch.py`,
run with `/srv/codi-connected/venvs/517179c/bin/python -I -B` as root.
`plan` and `apply` are pre-floor actions and must not be rerun on the completed
state. The reviewed `recover` action handles verified forward recovery if
needed; never restore a v1 client below the floor. Do not hand-edit Caddy.
The private probe remains solely on the server at
`/var/lib/webhost-ops/beta-files-probe/probe.json`; no credentials belong in Git
or another machine's checkout. The earlier probe provision entry is pre-floor.

Current hosting pins: generator `d11755a1…`, manifest `2c3987d4…`, derived Caddy
`95cecea4…`, guarded webctl `84c09e08…`; full hashes and service identities are
in the activation receipt. Main and `/desktop/` remain on their existing
releases. No account/key copying occurred. The 5 GiB account reserve is unchanged;
7,301,079,040 bytes were free after activation, not a capacity guarantee.
The main renewal timer is active/waiting; its renewal service remains failed
with no PID as before this work, a separate existing issue.

Public small-file, account-isolation and two-process conflict receipts are
reviewed and integrated. Lead reran the strengthened positive-upload/authorization
measurement: the 1 MiB one-byte edit used 69,283 request-body bytes. See
`tests/files-public-beta-lead-result-20261104.json`. A serialized public 128 MiB
create, separate fresh-profile read, one-byte replacement and verified deletion
also pass independently computed hashes: 71,530 changed-operation request-body
bytes including the 65,951-byte delta. Source/evidence and memory audit are under
`tests/files-public-beta-128m*`. Dedicated test accounts remain; the large file is
verified absent. Initial failed test cases and the held-read Text readiness
control are retained; no lost accepted edit was reproduced.

The ~3.49 GB sampled profile-process RSS is not a physical-memory bound; both
desktop sessions, test Blob/worker and unknown guest/voice residency contributed.
Two isolated 16 MiB phase/PSS runs now pass: both real Linux guests reached
ready; the explicitly stubbed comparison reported guest errors as intended.
Observed second-guest-wait PSS peaks were ~1.38 GB real/~0.53 GB stub, with
different sample durations. This points to guest startup as a contributor, not
an exact causal allocation or public128 budget. See the isolated memory receipt. Wider crash,
real interruption and resource/concurrency qualification remain; public success
does not close Files. The speech vendor JS 404 remains separate. Beta has no
consumers and its services may be replaced; main and `/desktop/` stay protected.

### Prior component checkpoint (historical next-step wording)

The latest integrated CAD checkpoint is `c672d0d1` (tested worker code
`25050c16`, tested full application `228cde72`). The lead combined actual
authored-profile OCC extrusion, unsnapped version-2 profile input, polygon-area
volume checks and dense response validation. Thirteen focused data/math tests,
the real sketch-to-OCC worker workflow, lifecycle/forged-response controls and
existing OCI box/Boolean suite pass serially under the research CSP. Source
edge-to-swept-face ancestry is checked against actual kernel generation history;
100/150 mm widths give the expected measured volume and bounds. See the fork's
`test/engine-extrude/lead-evidence-20261104.json` for exact hashes and outputs.

The retained reversed solver result has zero endpoint gap but a tiny axis
deviation. Profile v2 preserves its actual endpoints rather than snapping;
v1 keeps its original exact policy. A different thin trapezoid demonstrates
that the old adjacent-edge-product volume check accepted a wrong mesh; the
corrected authored polygon-area check refuses it without widening tolerance.
These are mesh/structural checks, not BRepCheck, single-solid or manufacturing
certification. The worker remains separate from editable model/history and
production host commands. Caller-side solver/document/frame/account lifetime
validation remains required. Whole-worker termination is the native cleanup
boundary, with eight lifetime reservations; global worker budgets remain open.

ARC15's concrete vertex ID-type defect is corrected at `228cde72`. A fresh
lead build with matching embedded revision passes typechecking and the real
OCC/Native Mesh registry/replay, rectangle extrusion and craft publication
tests. See `test/webos/brep-vertex-ids-evidence-20261104.json`. Producer labels
remain unqualified and ordinal IDs unstable; vertex picking and durable
vertex-dependent features are not qualified. Root test ports 19982/19983/19986
are closed and the disposable OCC fixture was removed.

ARC14 now has a bounded portable analytic descriptor at `25050c16`, after
independent review caught sparse plane-normal acceptance and unnecessary
main-thread transfer in the first candidate. Dense-data checks, count limits,
a 16 KiB UTF-8 serialized limit and explicit versioned research opt-in are
enforced inside the worker before sending. Ordinary controller requests do
not build or transfer it. The lead passes seventeen combined data/math tests,
real normal/translated/reversed topology extraction, ordinary no-transfer,
profile regression and lifecycle tests. See
`test/engine-topology/lead-evidence-20261104.json`. These are response-local
IDs and measured planes/loops, not durable references or an editable CAD model.
Next: strict data-only JS BREP reader, mount ownership and guarded history
publication. Read `docs/research/WORKER-PRISM-MODEL-BRIDGE-20261104.md`.
The selected pinned OCC runtime is separate from replacement-build research.
The legacy Shell/Face import graph eagerly reaches global Verb; ARC16 records
this coupling. The reader prototype must use the real pinned library headlessly
if needed, never a fake browser environment or fake engine implementation.

Earlier tested CAD code is `9bde6b291f859660db3fe14613ceff9851148391`.
Desktop `64becedd8` integrates the reviewed Add-menu dialog, scoped rectangle
commands and signed acceptance test. The lead independently built the actual
CAD output with its matching revision, passed typechecking, eight command tests,
the atomic-creation and host-menu browser suites, then the signed account test.
The diagnostic follow-up distinguishes coordinate-domain from precision refusal;
its real built-core boundary/notification suite and injected dispatcher unit
test also pass. The signed workflow was repeated on the diagnostic build.

The signed workflow creates a rectangle, verifies server bytes and SHA-256,
denies another account access, closes/reopens in a fresh session, edits the
driving width from 100 to 150 mm in the actual sketch editor, and verifies a
second signed save/reopen. Existing UI extrusion then produces measured
150×50×10 mm bounds. This is not a volume/manifold/manufacturing proof. See
`evidence/cad-rectangle-host-20261104.json` and
`evidence/cad-rectangle-diagnostics-20261104.json`. Test-only overrides retain
older source/provenance notices and use a raised fixture request limit. The
packaged runtime pin remains `d3d36bc5`; nothing was deployed.

**Next CAD boundary:** the existing extrusion kernel and topology work still
run on the UI thread. Research OCC/Manifold mounts have box/Boolean operations,
and OCC now has a bounded authored-profile prism. They do not yet connect
worker-owned BREP, persistent topology,
history and downstream use. Do not expose raw `craft.modify`, substitute a BOX,
or present a mesh preview as that integration. Read the fork's
`docs/research/RECTANGLE-EXTRUSION-BOUNDARY-20261104.md`. ARC13's bounded profile
preparation and actual OCC worker operation are qualified within the scope
above; ARC14 still needs the model/provenance bridge and guarded publication
before shared command exposure.
Keep both engines and explicit capability differences. Full Gate 1,
bracket/enclosure, parameter/unit and core-3MF acceptance remain open.

Files recovery source is integrated through desktop `de71f56b8`, taking only
the reviewed subtree through `ba65151d2`. The `a1e9e215c` correction resolves the
three gate-recovery findings; independent exact-launcher fault tests and seven
lead integrated checks pass. The owner then passed four interruption stages
using real sealed services, distinct DynamicUsers and a real disposable timer.
The marker-free fixture derives the executable from exact operator-written unit
bytes; independent review reproduced unit-write and old/bad-unit controls. Lead
verified the integrated subtree exactly matches, Python syntax and entrypoint.
This remains mapped fixture evidence: production paths/policy/TLS/main health
are substituted; timer firing and protected installation are not qualified. See
`evidence/files-operator-source-integration-20261104.md`.
The protected-install readiness packet is integrated at `ad25aaded`:
`research/beta-isolated-hosting/FILES-INSTALL-READINESS-2026-11-04.md`.
It records observed live pins and required protected bundle/guard/probe work.
Agent source through `0f9d46d87` is integrated at `1dc60b460`. The six lead
installer/bootstrap/legacy-process tests pass on that exact combined source;
see `evidence/files-install-lead-20261104.json` for hashes and scope. Protected
placement and actual production process inventory/freeze remain open. No
installer is qualified on the real host or installed yet. `/srv/data` has a
user-owned ancestor and is not the protected bundle destination; do not change
all hosting ownership to bypass this check. The reviewed bootstrap reads only
pinned public source data from a trusted administrator staging tree. Root owns
its verified protected placement and the later managed install/activation.

The root volume's immediate capacity shortage was removed by archiving twelve
unused public staging directories onto the separate larger drive, comparing
archive contents before and after retirement. Root free space rose from
5,576,151,040 to 7,297,232,896 bytes; the 5 GiB reserve is unchanged. Account
data, current releases, routes, services and floors were untouched. Main, beta
and `/desktop/` still returned 200. This is headroom for further bounded tests,
not concurrency qualification. See `evidence/webhost-staging-archive-20261104.json`.

### Earlier atomic-rectangle checkpoint (historical next-step wording)

CAD `ec2e0156129c02c66fa11177077cc9c212ea318f` records implementation
`07316f8f`: a core command evaluates an XY plane privately, runs the real
rectangle worker, checks its exact intent/evidence, and publishes sketch bytes
with matching history/model/registry/status. Read the fork's
`docs/RECTANGLE-CREATION-20261104.md` and
`test/webos/rectangle-creation-evidence-20261104.json` (SHA256
`b45afb16a41549e1281e3c7e2b57ac951338df282c00677290ff2cdb8aefa369`).

Lead app/helper builds, typecheck, seven pure workspace tests, stream coordinator
and nine Chromium scripts pass against explicitly selected current assets. The
new suite covers two sketches, nonzero plane/local origin, first-observer
consistency, undo/redo, native reopen, held-worker cancel/stale work, same-counter
service replacement, pre-install failure, post-commit reset, malformed worker
intent/evidence and parent-frame arguments/AbortSignal.

**Next:** register discovery and the core operation through the authorized
host, connect a human-facing action, then prove editor edits and durable My files
save/reopen. Parent-frame transport is not a signed host command qualification.
`persistence: volatile-workspace` does not mean server save. The full Gate 1,
named parameters, units, bracket/enclosure and core 3MF remain. The desktop
package stays `d3d36bc5`; nothing deployed. Built files carry parent `c3c54f94`
because implementation was built before commit; the receipt binds actual code
and assets, not a clean post-commit build.

Always set `JSKETCHER_TEST_URL` and `CODI_TEST_CDP`. An earlier run reached
historical fixtures through old defaults and is retained but not current-build
evidence. Identified retired CAD test browsers on 19331 and 19875 were closed.

Parallel returns are backed separately: engine `0431dff0` on
`research/occ-shapefix-repro-20261104` records controlled compiler differences,
four matching per-process-no-ASLR trials and four direct gap cases. This is
scoped correlation/behavior evidence, not full-build reproducibility or general
semantic equivalence. Do not weaken production ASLR or promote the new WASM.
Files `fa228b79c` adds the exact integration/capacity handoff under
`research/beta-isolated-hosting/FILES-RELEASE-HANDOFF-2026-11-04.md`. The later
`c204b753b` gate-recovery candidate has confirmed apply-finalization exposure
and partial-asset inventory gaps found in independent review; its author is
fixing both. Do not integrate that
candidate as ready. Real loopback Caddy/disposable systemd checks still include
explicit main/policy/unit/timer substitutions. No live activation. The account
volume remains short of the 128 MiB test headroom above its 5 GiB reserve;
separate `/srv/data` can hold public staging, not enlarge that account volume.

### Previous workspace checkpoint (historical next-step wording)

Fork `3e42030fa3d094afdb5a36ac13c00b5549a6ca5d` records private workspace
implementation `67b8888f` and lead evidence. Seven pure workspace tests, the
stream coordinator, six legacy staged-write adapter checks, build/typecheck,
and eight actual Chromium scripts pass. A real before-control proves the old
last-value throttle omitted the first of two modified faces. Both now refresh;
deleted/replaced sketch objects and loops leave the registry. Prepared bytes
stay private until commit, and stale document/service work cannot publish or
roll back a newer lifetime. New private preparation has explicit size and
single-candidate bounds. Read the fork's updated `CRAFT-PUBLICATION-20261104.md`
and `test/webos/workspace-preparation-evidence-20261104.json`.

This supplies the storage participant for ARC11; **the complete plane + worker
sketch + history/model transaction is still next**. No new command, desktop
package or deployment. The built application stamp is parent `5b77f71d` because
the implementation was built before commit; the receipt binds exact source and
served bytes. Do not describe it as a clean post-commit build.

Rectangle parity branch `research/cad-rectangle-parity-20261104` at `e6db73ea`
records the verified eleven-asset editor provenance and agent-run visible-editor
versus data-only worker geometry/constraint/resize/rejection/reopen controls.
The editor uses named parameters and the factory uses numeric driving values;
shared-command and named-parameter parity remain open. The factory is still
research, not registered or integrated by these workspace changes.

Engine checkpoint `239c64b4` on `research/occ-cleanup-audit-20261104` records an
agent-run clean full non-instrumented source `5a4e14ce` build and exact-output
Chromium session checks. Clean WASM `abb23bdd…` differs from incremental
`b39e7a26…`; the difference is narrowed to `ShapeFix_Wire_1.cxx.o` with matching
source bytes and changed compiled branch tables. A standalone recompile gave a
third variant. Cause and semantic equivalence are unknown, so promotion remains
blocked. The lead has not qualified this as the replacement runtime. Artifacts
and provenance are on R730 at `/mnt/data10tb/codi-occ-session-full-build-20261104`.

Files operator branch `research/beta-files-operator-20261104` at `6fdc8d5a0`
adds a documented single runner for clean apply, forced issuer-switch
interruption, forward recovery and idempotent recovery. Agent-run fixture uses
the real protected launcher, lock, inventories, journals and disposable signed
issuer/gateway. Main readiness, policy/origin mapping, systemd and Caddy routing
are explicitly simulated. Read that branch's
`research/beta-isolated-hosting/SIGNED-PROBE-NOTES.md`; preserve its unrelated
hosting base and integrate scoped paths only after lead review. No activation.

Earlier checkpoints below retain their original evidence and limits.

Fork `5b77f71d` now includes craft publication implementation `ccb66be7` and
its exact evidence. History, geometry, registry and failure status are installed
together; reset stops stale delivery, and rejected commands preserve a valid,
saveable accepted document. The lead passed build/typecheck, stream tests and
12 actual Chromium regression scripts. Read the fork's
`docs/CRAFT-PUBLICATION-20261104.md` and
`test/webos/craft-publication-evidence-20261104.json`. The receipt preserves the
failing before-control, fixture corrections and corrected pattern rollback
oracle. This is evaluated craft-state publication, not yet atomic sketch-storage
or entire-document publication. Desktop package still selects `d3d36bc5`.

The next CAD dependency is a privately prepared plane plus strict sketch bytes,
published with matching document generation/revision and model/history/registry
in one transaction. A rejected or stale preparation must remain invisible;
retain feature-ID gaps and require no rendered editor. Worker factory branch
`research/cad-agent-plate-20261104` at `508d54e4` now prepares a validated,
dimensioned XY rectangle, with agent-run worker tests. It is not yet integrated
or exposed by the desktop command registry.

Engine research `ce47a866` qualifies a non-instrumented session candidate from
source `5a4e14ce`, independently of fault-instrumented source `4ef86f9e`.
Agent tests cover bounded session ownership, partial construction/serialization
failures, aliases, stale/foreign handles and termination. These are incremental
relinks, not clean full builds or proof of allocator leak freedom. Legacy raw
pointer paths remain; no runtime/package pin has changed. Keep these separate
from the lead-tested craft publication results.

Fork `bdc4ff2b` integrates verified OCI/Manifold worker mounts (`6486b1ef`),
the bounded associative circular-cut pattern (`854dc3b3`), discoverable seed
picker (`0680b40b`) and Boolean preprocessing control (`f83eec0c`). The lead
independently passed both real engine suites/four contract checks, the combined
build/typecheck/eight CAD browser regressions, then a fresh picker build and
three targeted scripts. The later preprocessing control passed too. Exact
source, asset hashes, outputs and limits are in the fork's
`test/webos/combined-pattern-mount-evidence-20261104.json`.

The pattern requires an immediately preceding circular through-cut on an
unrotated rectangular OCC plate, bounded count and signed X/Y spacing. It
discovers the seed without manual IDs and requires explicit repair if the
authored circle is replaced. Native Mesh refuses this operation. The new engine
mounts remain disconnected from CAD. **The desktop package still selects
`d3d36bc5`; this is not a new public release.** Full units/agent/part coverage,
general patterns and long-session native ownership remain open.

The command-registry negative control on desktop branch
`research/cad-agent-plate-desktop-20261104` (`c24c29290`) confirms that the
current signed app exposes inspect, circular-object listing and concentricity,
but cannot start a sketch from an empty document. Rejection leaves the model
unchanged. It used the existing d3 package, not a newly packaged 068 build.
The next slice is atomic data-only sketch creation using existing project
validation/staging where possible. A rendered editor is an optional view,
not a computational prerequisite. The full agent workflow remains unfinished.

Earlier checkpoint descriptions below are historical where these later results
supersede them. Verify current branch tips before continuing.

## Read first

Read these in order; use the rest as references instead of restarting the
whole historical audit:

1. This handoff and `goals/FILES-CAD-NEXT-AGENT.txt`.
2. `CAD-CORE-SEPARATION.md` — current architecture and engine-mount requirements.
3. `ACTIVE-FILES-CAD-RELEASE.md` — the release acceptance audit.
4. `FILES-BETA-RELEASE-READINESS-2026-11-04.md` — exact observed beta boundary,
   storage migration, capacity and deployment gaps.
5. `WEBOS-WORK-QUEUES.md` — update this operational ledger as work progresses.

Then read JSketcher's `docs/HEADLESS-SKETCH-SOLVE.md`,
`test/webos/plate-parametric-README.md`, `docs/CRAFT-REPLAY-NORMALIZATION.md`
and `docs/WEBOS-REPRODUCIBLE-BUILD.md` for the first CAD task.
`CAD-ENGINE-GATE-1.md` and `JSKETCHER-FOUNDATION-MATRIX.md` define the larger
foundation acceptance; `CAD-ENGINE-GATES.md` indexes the later gates.
The complete original goal and amendments are preserved in
`goals/FILES-JSKETCHER-RELEASE-20261103.txt`.

## Repositories and exact starting points

| Repository | Integration branch | Code checkpoint before this handoff |
|---|---|---|
| `box-git:/srv/data/git/CodiServer-distro.git` | `integration/files-jsketcher-release-20261103` | `541db60789a2910f2a92a1023fe765ea902d43a0` |
| `box-git:/srv/data/git/JSKetcher.git` | `integration/files-cad-release-20261104` | `ec2e0156` (rectangle implementation `07316f8f`) |

The desktop branch's later handoff commit adds documentation to that code
checkpoint. Verify branch tips with `git ls-remote` before starting; another
agent may have advanced them. Do not substitute `main`, `simplified`, an old
`webos-integration` tip, or an old research branch for these bases.

Backups use the same integration branch names at:

- `r730:/mnt/data10tb/git/CodiServer.git`
- `r730:/mnt/data10tb/git/JSKetcher.git`

Example fresh working copies:

```sh
git clone --branch integration/files-jsketcher-release-20261103 box-git:/srv/data/git/CodiServer-distro.git webos
git clone --branch integration/files-cad-release-20261104 box-git:/srv/data/git/JSKetcher.git jsketcher
git -C webos status --short --branch
git -C jsketcher status --short --branch
git -C webos rev-parse HEAD
git -C jsketcher rev-parse HEAD
```

Make new named worktrees/branches from verified bases. Preserve the user's
dirty `/home/dflanag3/CodiServer/desktop-preview/SIMPLIFIED` checkout. Current
integration worktrees on this workstation are `/tmp/codi-webos-cad-merge` and
`/tmp/codi-jsketcher-release-integration-20261104`; they are conveniences, not
the source of truth for another machine.

### Integrated since the initial handoff

JSketcher `2b3f2c0fdfd84bcda7db4f5244e1da40b4113813` now reconciles the
axis/admission work (`68e51e03`), private atomic replay (`35f3e2ef`), lifetime
and staging guards (`1be74426`, `274a361c`) and subsequent document/surfacing
boundary fixes (`aff1befe`). Do not merge the older `089ed178` tree again or
reintroduce its global registry overlay. Normalization and feature-ID allocation
remain integrated.

The lead's combined app build/typecheck, 11 real Chromium regression scripts
and 9 unit checks pass. Read the fork's
`docs/DOCUMENT-LIFETIME-REPLAY-20261104.md` and machine-readable
`test/webos/document-replay-evidence-20261104.json` for exact tested source,
asset hashes, negative controls, commands and limits. This is not the full CAD
gate. The newer package and research results below supersede the old
not-yet-packaged status.

Desktop `73c1e8b13` packages fork `d3d36bc5`, including ordinary OCC fillet/
chamfer guards and visible errors, with both required worker assets. Nine lead
browser runs pass: two signed host workflows at phone/1080p/4K plus the three
fillet/chamfer/refusal regressions. The dependent plate is opened through Files,
saved through My files with exact server bytes, then reopened in a fresh signed
session. See `evidence/cad-packaged-workers-20261104.md` and its JSON receipt.

Fork `7d08c159` additionally merges `1a6e5b77` engine-mount research, which is
not connected to the application or selected by the package. Real Manifold
and OCI worker boxes pass independent lead checks. The selected interpreter
does not export the legacy SPI box/dispose functions. Its original wrapper
requires `window`; the research wrapper uses a portable exchange callback.
Whole-worker termination is its current cleanup boundary. Broad bindings,
trusted installation, resource budgets and production integration remain open.

Desktop `2e312b7975d92882c9ff74803066abe089d9ca59` integrates the Files-only
beta candidate builder and tests. Candidate `3ad04c48…` supersedes `feaa1c6f…`,
which had a real session-layout return-value defect. The agent exercised signed
controlled-tab migration, Files/Text, sign-out cancellation/failure/stale worker
and second-account login; the lead independently verified the sealed 87-file
inventory. Actual derived issuer/guest config tests pass separately. These are
isolated fixtures, not a durable managed activation/recovery operator. See
`../research/beta-opfs-release/README.md`.

Files checkpoint `b391e259b` adds signed account/file continuity across the exact
issuer restart and a filesystem/process-tested forward-only floor journal.
Lead journal fault tests pass. Managed adapter prototype `e4a6c2ec6` stays on
`research/beta-opfs-managed-bind-20261104`, based on hosting `cf04068aa`; do not
merge/deploy that unrelated hosting branch wholesale. Damaged-journal re-gating,
actual protected launcher/issuer switching, custody and host capacity remain
unqualified. The account volume had 208.8 MiB above its 5 GiB reserve at the
recorded check. Read `../research/beta-opfs-release/CAPACITY-2026-11-04.md`.

### Interpreter source repair and current parallel work

The original OCC wrapper has borrowed-name, duplicate-allocation,
unknown-command and interrogation-pointer ownership defects. Do not treat the
old runtime as memory-safe or free retained C++ pointers from JavaScript.
Repair source lives at `box-git:/srv/data/git/occt-interpreter-codi.git`, backed
by `r730:/mnt/data10tb/git/occt-interpreter-codi.git`; no GitHub publication.

- `source-repair-20261104` at `5c353d62fac9dd7836105b26cf4cb612ebe81ca5`
  owns named-shape keys and safely handles absent names/commands. Full
  Emscripten 2.0.30 build and agent-run real Chromium controls pass.
- `source-owned-model-names-20261104` at
  `eac1772379ea1cbaede47abc3e7bccedbf3f3dd1` owns additional model-name tables.
  Its separate incremental relink passes point/circle/spline/plane/history
  controls with freed and churned strings, plus missing-name/dispatch/Boolean
  tests. This is not an independent clean rebuild or complete memory proof.
- R730 outputs/logs: `/mnt/data10tb/codi-occ-safe-build-20261104` and
  `/mnt/data10tb/codi-occ-owned-names-build-20261104`. Full-build WASM SHA-256
  `23d27bddf4af1b0fedb0c55956b7e17a34a7e1639661de32c26a01136c5da46a`;
  incremental WASM
  `5140643df8ef1180fc91c991a84da670b38f5fd950fc1403a678cac01a841ab3`.
  Both generated JS files hash to
  `21624d1322b63969dbb3ce165a8a56f51dd089f531d77c75ab9632813549f450`.
- JSketcher `research/occ-cleanup-audit-20261104`, checkpoint `623c9c9a`,
  holds controls and the versioned interrogation-session proposal. Engine work
  now prototypes that ownership API separately while preserving the legacy ABI.
  The lead has not yet qualified a replacement runtime/package.
- JSketcher `research/cad-agent-plate-20261104` at `83f428f3` adds a
  worker-only empty-sketch factory using actual headless IO. Agent-run tests
  cover valid frames and invalid units/frame data. It does not prove face
  ownership or publish a plane/sketch. Desktop `942f5edaf` records why current
  restore/staged-storage primitives still need an atomic publication boundary.

Files has advanced beyond the early managed prototype described above. The lead
independently passed `c2d6f696` render-inventory, managed-binding,
copied-controller/real-Caddy and maintenance-transaction tests.
`docs/evidence/files-managed-lead-20261104.json` records those lead results.
The assembled operator continues on
`research/beta-files-operator-20261104`; its current checkpoints add retained
issuer recovery state, exact routes, process-death and local Caddy/systemd
fixtures. Protected launcher and combined signed-service qualification remain.
Do not merge its unrelated hosting base wholesale or deploy fixture callbacks.
One lock must cover gate, durable forward floor, issuer switch, service health,
v2 exposure and finalization. Post-floor recovery may gate or advance, never
restore v1. Unrelated-site maintenance must still work while preserving beta.

The last account-volume check had about 204 MiB above the required 5 GiB
reserve. A measured disposable issuer stage used about 115 MiB allocated;
an additional concurrent 128 MiB stage would exceed the remaining headroom.
The proposed extra 256 MiB margin is separate from the required reserve, and
total working space remains unmeasured. Artifact-drive capacity does not add
account-volume capacity. Preserve accounts and reserve; validate trusted admin
inputs/pins under lock without claiming protection against deliberate admin
bypass. Nothing in these checkpoints changes live services.

## What works and what is still open

These are bounded results. A passing small model is not a completed CAD gate;
one worker is not a browser-wide RAM guarantee.

| Area | Demonstrated | Open or failing |
|---|---|---|
| Saved files | Opt-in OPFS My files; signed operations; sealed candidate/controlled-tab migration; actual signed continuity across issuer restart and tested floor journal. | Qualified managed transition/recovery operator, headroom and full app compatibility. |
| Conflicts | Two independent Chromium processes/profiles, actual Files/Text offline edits, cancellation, a newer edit during resolution, keep-both and fresh reopen. | Final assembled release and broader failure matrix. |
| Interrupted transfer | Real committed-upload reply cut reconciles without blind duplicate write; actual download cuts preserve complete verified generations and earlier bytes. | Crash during publication, physical power loss, exact release transition. |
| Changed data | A signed 128 MiB file's one-byte edit sent 71,470 request-body bytes in the recorded run; final local/server hashes agreed. | This excludes responses and HTTP/TLS overhead. SDK still builds a Blob before OPFS capture; no complete zero-copy or total-memory claim. |
| File worker resources | One cooperating VerifiedContent worker across tabs; queue, cancellation, timeout and renderer-crash recovery. | SDK/app workers and allocations are outside that cap. Sampled summed Chromium RSS was about 1.32 GiB in the large-file run, with shared pages counted multiple times. |
| Temporary Linux | Real v86 boot; Files can browse guest home; identically named My files stays separate; guest reboot resets temporary content. | This is not a synchronized Linux Account mount. All-app compatibility remains. |
| CAD host integration | Packaged fork `d3d36bc5`: actual signed small-model and dependent-plate save/reopen with both workers, independent OCC/Native windows, account denial and closed-command rejection at simulated phone, 1080p and 4K. | Large-model resource qualification, shared agent workflow, heavy snapshot/stringification and public release remain. |
| Headless sketch solve | Actual IO/solver in a real worker, no canvas/DOM/fake editor; restricted plate fixtures, residual and finite-geometry checks. | Not all entity/constraint families, exact general DOF, arbitrary region extraction or all kernels. |
| Dependent plate | 100×50×20 → 150×30×20 with centered Ø10 hole and four constrained corner holes, ordinary OCC fillet/chamfer; undo/redo, geometry rays, native-v2 and signed reopen. | Bounded associative pattern/picker passes locally at bdc4ff2b; the complete coupled chain, general patterns, inch display and full shared-agent workflow remain. Native sketch extrusion and fillets are explicitly unsupported in these paths. |
| Rejected CAD regeneration | Impossible 15×15 edit retains last complete plate, marks it stale and refuses save/3MF; correcting it regenerates. Held replay leaves accepted registry/model intact. | Broader operation-context/native-handle isolation, full feature chain and resource bounds. |
| Document lifetime | Monotonic generation plus exact service/storage ownership; held validator/replay reset, staged rollback, late reply, service replacement and surface cleanup/reload controls pass. | All async services and noncooperative kernel interruption are not qualified. |
| Material-aware 3MF | Existing research and independent limited lib3mf fixtures. | Full editable enclosure/body/lid/inset workflow and manufacturing handoff remain unqualified. |

Key desktop evidence: `evidence/storage-product-integration-20261104.md`,
`evidence/cad-files-combined-20261104.md`,
`../tests/files-two-profile-conflict.md`,
`../tests/files-desktop-signed-fixture.md`,
`../research/opfs-storage/DOWNLOAD-TCP-CUT-20261104.md`, and
`../research/opfs-storage/WORKER-BUDGET-128-20261104.md`.

## Current decisions and guardrails

- Chromium is the supported browser target for this work. Phone layout tests
  are emulation unless explicitly identified as physical-device evidence.
- The user authorizes a deeper rewrite of coupled JSketcher internals. Preserve
  useful tested components and already integrated upstream features. Do not
  repeat the old upstream merge or replace working code just to start over.
- **OpenCascade is preferred; Native Mesh/Manifold is secondary.** Properly
  support each library's relevant capabilities, beyond today's menu subset.
  Use discoverable, versioned engine mounts/adapters; retain engine-specific
  capabilities rather than reducing everything to their common subset.
- Engine combination requires explicit representation conversion, tolerance,
  units, provenance, ownership and identity-loss rules. Never silently switch
  engines after a failed operation. A tessellated approximation is not an exact
  replacement for the authored B-rep. See ENG01–ENG08 in the core checklist.
- Production computation belongs in workers with explicit model data, not an
  invisible editor, fake `window`, canvas or ToolManager. The real UI may render
  to a canvas. Heavy hashing, parsing and geometry processing must not block it.
- Keep representability, constraint satisfaction, planar regions, kernel output
  validity and dependency meaning as five separate validation responsibilities.
- One revisioned authored model and one validated command path serve people and
  agents. Jobs cannot bypass account, expected-revision, disposal or stale-result
  checks. Content hashes are not authorization or edit/lifetime generations.
- My files is the shared account-bound storage authority. Preserve opaque local
  versions/CAS, create-only `expected=null`, conflicts and uncertain-write
  reconciliation. No app-private account mirror. Temporary Linux is separate.
- Keep production CSP; no `unsafe-eval` or test CSP bypass to make a library work.
- No GitHub publication for JSketcher now. Back up source/tests/notes to box-git
  and R730. The user authorizes new LAN repos and source clones where needed.
- R730 storage/compute and llm-60 compute/testing are authorized. R730 works.
  llm-60 access was not established: no verified SSH host-key pin was available.
  Do not bypass host verification; obtain a trusted fingerprint/username only if
  that machine becomes necessary. R730 lets current work continue.
- Preserve main `ksu.codes`, `/desktop/`, account data, keys and unrelated work.
  Beta is the iteration target. No new router ports are currently needed.
- Do not repeatedly ask permission for authorized tests, builds or scoped
  implementation. Review the concrete deployment artifacts and recovery path
  before any hosting mutation. Never hand-edit generated Caddy.

## First bounded work packages

Use one lead and three agents in isolated worktrees. Assign paths before edits.
The bounded implementation/test work in packages 1A–1C and the local combined
checks in package 2 have now passed the recorded controls. Extend unresolved
coverage and proceed to host packaging; do not redo completed merges.

Each agent returns a commit, tests/negative controls, limitations and evidence.
Shared contracts, merge decisions, release packaging and hosting have one owner.

| Order | Owner | Package and owned area | Acceptance and stopping point |
|---|---|---|---|
| 0 | Lead | Verify refs, candidate ancestry, resources and prerequisite artifacts. | Clean branches; reproducible dependencies or explicitly recorded gaps; no accidental deployment. |
| 1A | Lead | Document-lifetime contract: `projectBundle.ts`, `projectManager/projectManagerBundle.ts`; coordinate its API with replay owner. | Synchronous monotonic generation on document replacement/reset/restore entry; every async result checks captured generation and current owner. Reset/reopen of identical content cannot admit an old result. |
| 1B | CAD replay agent | Atomic replay: `craft/craftBundle.ts`, private evaluation registry, non-rendering sketch initialization, narrow same-ID scene replacement. | Complete candidate evaluated privately; publish once only when all required operations and guards pass. Failed replay retains the last complete accepted solid and inspectable failed intent. No mutation of accepted inputs. |
| 1C | CAD core agent | Review axis-domain/admission candidate, own `sketcher/headless/` and its tests. | H/V domains correct; single cooperating CAD worker, bounded queue/total deadline, queued cancel, renderer-crash progress. No overlapping edits to replay or project lifetime. |
| 1D | Files agent | Beta-derived immutable storage package and transition/operator work from the readiness plan. | Preserve selected guarded baseline and full catalog; prove v2 migration/forward recovery; no independent live mutation. Lead owns shared host changes. |
| 2 | Lead | Merge 1A–1C and rebuild the exact fork; review rather than assuming each isolated pass composes. | Run last-valid, stale/reset, successful five-hole edit, undo/redo, save/reopen and normalization/allocator controls on the combined build. |
| 3 | Lead plus independent review | Package new worker assets and exact fork in the desktop app; source/notices/CSP checks. | Real signed My files workflow at phone/1080p/4K; independent windows/account change/disposal; inspect actual served hashes. |
| 4 | Reassign agents | Gate 1 matrix and coupled rectangle chain, then bracket/enclosure through UI and discoverable commands. | Useful parametric part edits survive or fail explicitly; both engine statuses recorded. Unsupported and untested never count as pass. |
| 5 | Manufacturing owner after dependencies | Core 3MF body + separate lid + aligned label region. | Independent units/dimensions/transforms/materials: two print objects, three assigned regions; native project remains editable source. No physical printer/Bambu requirement. |

Engine capability inventory, provenance and adapter-contract design may run in
parallel on owned documents/modules when a lane is free. Do not make completion
of every engine capability a prerequisite for fixing today's rejected edit.
Conversely, do not close the broad engine-support queue after wrapping only the
few operations currently used by the desktop.

### Document generation and atomic replay details

The implemented API is `ctx.projectService.documentGeneration`,
`documentSignal`, `beginDocumentChange()`, `isDocumentCurrent(generation)` and
`dispose()`. The combined tests cover reset/reopen of identical content,
service replacement, old callbacks, staging ownership and surface domains.
Continue qualifying callers against this contract; do not recreate the API.
Account/window lifetime checks remain separate. A content hash, equal history
or re-created face ID cannot distinguish identical documents across lifetimes.

An occupied-workspace restore must reject **before** starting a replacement;
repeat the empty check after validation. `craftService.reset()` replaces craft
history, not all document domains. Use `projectService.empty()` for a new blank
document. Explicit same-project `loadStrict()` preserves its saved surface
sidecar; a new native envelope supplies its own surface section.

Guard both before and after worker/restore awaits. Restore must distinguish
its own intentional generation transition from an unrelated replacement; do
not update a guard opportunistically to whatever generation is current. Cover
JSON restore, Blob/worker restore, empty/reset, cancellation and disposal.

Atomic replay must preserve a separate last-complete result even across
deliberate history navigation. Evaluate against a private registry and avoid
mutating accepted bodies through shared references. Publish the completed
candidate only after validation and lifetime/revision checks. Scene views must
replace a changed model object even if its stable ID is unchanged. Label stale
geometry and failed/stale descendants; never save partial output as success.

The retained negative control is
`test/webos/plate-parametric-last-valid-browser.test.cjs`. Its impossible 15×15
edit must keep the previous complete 100×50 five-hole solid, not merely the
preceding plane or partial seven-face output. The successful resize must still
work; refusing every edit is not the fix. Add held-worker/reset/same-content
reopen, competing replay, failure-then-valid-edit and undo/redo tests.

## Reproduction and portability

Use Node 24.22.1, Chromium and `puppeteer-core` 24.35.0 for the recorded browser
checks. Python needs aiohttp, argon2 and cryptography; the repository's pinned
requirements and app-builder locks remain authoritative. Caddy is needed for
the isolated signed fixture. Use loopback and disposable profiles/accounts.
Choose unused ports; stop only processes owned by your fixture.

**A fully independent clean-machine release build is still an open gate.**
Source and recipes are backed up, but runtime provenance, some artifact
retrieval and final combined build qualification are incomplete. Do not claim
that cloning either repository alone supplies a ready release.

### CAD worker checks without a canvas or CAD engine build

On the current integrated fork, with locked dependencies installed:

```sh
CYPRESS_INSTALL_BINARY=0 npm ci --ignore-scripts
node build/precompile-numeric.cjs
./node_modules/.bin/webpack --config build/webpack.headless-sketch-worker.cjs
./node_modules/.bin/webpack --config test/webos/headless-sketch-client.config.cjs
./node_modules/.bin/webpack --config test/mechanical/webpack.axis-angle-domain.config.cjs
node /tmp/codi-axis-angle-domain/tests.cjs
```

The two test configurations intentionally generate disposable files under
`/tmp`. The source and configuration are in Git. `puppeteer-core` is not a
JSketcher dependency; install the test harness separately. Run from the fork:

```sh
npm install --prefix /tmp/codi-sketch-test-harness --no-save puppeteer-core@24.35.0
export PUPPETEER_CORE_PATH=/tmp/codi-sketch-test-harness/node_modules/puppeteer-core
export CHROMIUM_PATH=/snap/bin/chromium
mkdir -p /tmp/codi-headless-web/static /tmp/codi-headless-web/lib
cp .build/headless-sketch-worker/worker.js /tmp/codi-headless-web/static/worker.js
cp web/lib/verb.js /tmp/codi-headless-web/lib/verb.js
cp test/webos/headless-worker-{stall,wrong-revision,malformed,delayed}.js /tmp/codi-headless-web/static/
printf '<!doctype html><title>Sketch worker test</title>\n' > /tmp/codi-headless-web/index.html
python3 -m http.server 19340 --bind 127.0.0.1 --directory /tmp/codi-headless-web
```

Select the installed Chromium path on the new machine. Keep the static server
in its own terminal. It is the minimal worker harness, not the full-app strict
CSP qualification. Numeric execution does not need a rendered editor. See the
candidate's `docs/HEADLESS-SKETCH-SOLVE.md` and test headers for scope.

`headless-sketch-admission.test.cjs` launches and cleans its own browser. For
the other tests, start a disposable CDP browser in another terminal:

```sh
CAD_TEST_PROFILE=$(mktemp -d /tmp/codi-sketch-profile.XXXXXX)
"$CHROMIUM_PATH" --headless --disable-gpu --remote-debugging-address=127.0.0.1 --remote-debugging-port=19331 --user-data-dir="$CAD_TEST_PROFILE"
```

Keep this isolated from an everyday browser profile and close only this process
after testing. Use available ports; `CODI_TEST_CDP` and `JSKETCHER_TEST_URL`
override the default loopback CDP 19331 and fixture 19340 URLs. In a test terminal
with the harness environment exported, run:

```sh
node test/webos/headless-sketch-admission.test.cjs
node test/webos/headless-axis-domain-negative.cjs
node test/webos/headless-axis-domain.test.cjs
node test/webos/headless-sketch-worker.test.cjs
node test/webos/headless-sketch-lifecycle.test.cjs
node test/webos/headless-sketch-deadline.test.cjs
```

The axis negative control previously failed at `e20e27bd`; the current fix
must satisfy the intended invariant. The admission tests establish Web Lock
release, disappearance of the old dedicated Worker target and queued progress
after renderer crash, **not OS memory reclamation**. There is no separate
committed execution receipt for that candidate; rerun for fresh evidence.

### Full CAD build and integration checks

Follow JSketcher's `docs/WEBOS-REPRODUCIBLE-BUILD.md`. Prepare exact source-built
OCCT/Manifold artifacts through `build/prepare-webos-runtime.cjs`, then run:

```sh
CODI_EMBED_NUMERIC=1 CODI_EMBED_MANIFOLD=1 npm run build
CODI_EMBED_NUMERIC=1 CODI_EMBED_MANIFOLD=1 ./node_modules/.bin/webpack --config test/webos/webpack.config.cjs
npm run check-code
```

The exact eight preparer runtime inputs are also preserved, independently
content-verified, at `r730:/mnt/data10tb/codi-cad-runtime-inputs-ced603b99f8d`.
Its `manifest.json` SHA-256 is
`ced603b99f8d27577ba43256e6c391627a7e52f7465784a28ebf63b6b01aa6a5`.
Copy it to a private local directory, verify the closed file inventory and
every recorded size/hash, then pass its `manifold/` and `occt/` directories to
the desktop preparer. `evidence/cad-runtime-inputs-20261104.json` records paths
and hashes. This is a LAN backup of selected research prerequisites, not public
distribution clearance or a guarantee of a fully offline build; locked npm
dependencies still require installation. No generated app/dependency tree is
committed to Git.

Serve `dist` with production-style CSP, permitting WebAssembly but not
JavaScript `unsafe-eval`. Use the plate README and actual browser tests,
including `plate-parametric-centered-browser.test.cjs`, the last-valid control,
the document/surface/service replacement controls and `axis-domain-project-restore.test.cjs`.
Inspect assertions and their scope, not only the test's filename or exit code.

OCCT source archive is on R730 at
`/mnt/data10tb/CodiServer/source-archives/occt-interpreter/5efaf53accb45bac475155fc4d5552642c19e91e/source.tar.gz`,
SHA-256 `86ccaa4d1974b15a1ee8a26e69db20e7c04f5000ffd4924008cebcd1a82fb9e4`.
Read `docs/occt-source-rebuild-20261102/RESULTS.md` and
`third_party/occt-interpreter/README.md`. Independent complete OCCT builds are
not proven bit reproducible; a matching hash alone does not close source/notice
requirements. Manifold's CSP-safe source build is documented in
`test/webos/README-surfacing-research.md`. Do not substitute unverified npm
binaries or publish runtime inputs before the recorded distribution gaps close.

The desktop preparer at `apps/system/jsketcher/prepare.py` now pins `d3d36bc5`,
including both content-addressed workers. Further updates require an exact
commit, emitted worker graph and notice/source inventory, followed by preparer/package
tests and signed host tests. A stale `dist` can pass old tests while new source
remains untested: always record the built commit and served asset hashes.

### Files tests

Start with the staged storage tests documented in
`evidence/storage-product-integration-20261104.md`, then use the signed fixture
in `../tests/files-desktop-signed-fixture.md` for actual UI and authorization.
Build Files/Text with pinned app-builder and CodeMirror dependencies. That test
catalog contains only Files/Text/CodeMirror and must never replace the full site
catalog. CAD host fixtures add JSketcher but still are not full catalogs.

`tests/files-desktop-signed-fixture.py` accepts `CODI_GATEWAY_ROOT`, `CODI_SDK`,
`CODI_APPS_BUNDLE`, `CODI_CADDY`, `CODI_DESKTOP_FIXTURE_PORT`; override machine-local
defaults. It requires gateway manifest SHA-256
`c0465afeb10dac4a761b274eb6871a8af750fccc5523a333da2c98dac8b90960`
and SDK SHA-256
`44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869`.
These are candidate fixture inputs; beta's gateway is still `dd8cbea7…`.
Recover/rebuild and verify these inputs before testing; do not remove the pins
to make a fresh machine pass. Their complete clean-build retrieval remains
part of package 0 if the named artifacts are unavailable.

Representative tests, selected according to changed code:

- `tests/files-desktop-signed-workflow.test.mjs`
- `tests/files-two-profile-conflict.test.cjs`
- `tests/files-signout-worker-lifecycle.test.cjs`
- `tests/files-worker-budget.test.cjs` against a static checkout server;
  set `CODI_TEST_RENDERER_CRASH=1` for its renderer-crash variant.
- `tests/mirror-opfs-worker-budget-large.test.mjs` with the isolated R730
  fixture described in `../research/opfs-storage/WORKER-BUDGET-128-20261104.md`.
- `tests/files-real-linux-separation.test.mjs` with
  `CODI_TEST_REAL_LINUX=1`; the ordinary fixture deliberately blocks guest boot.

Do not reuse a running fixture after source or staging changes without checking
which bytes it serves. The lead-owned old fixtures on workstation ports 19976,
19885 and 19886 were stopped during handoff after checking their process
arguments and working directories. Recreate them for the source under test;
do not assume a port is still free or stop an unrelated process using it later.

## Beta release remains a separate serial gate

The last read-only observation found beta on guarded IndexedDB v1, SDK `44da`,
gateway `dd8`; the OPFS candidate is not live. Query-bearing bootstrap URLs
select different bytes from bare URLs. The readiness document contains exact
hashes and is the reference for the actual selected baseline.

Before any activation:

1. Recheck live pins, service identities, data roots, filesystem headroom and
   all-site/main/prototype health. The previous 5.3 GiB free space on root was
   only about 218 MiB above the gateway's 5 GiB reserve. `/srv/data` had much
   more space; that does not automatically give the account filesystem room.
2. Audit obsolete releases before any cleanup/move. Hardlinks invalidate naive
   sums of directory sizes. Preserve active/retained assets and account data.
3. Review the existing `3ad04c48…` beta-derived candidate and `853c12e5…` issuer, then complete the managed transition. Preserve a complete immutable
   module/worker graph and a full catalog preserving unrelated applications.
   The research integration tree is not a deployable whole-site replacement.
4. Qualify migration and recovery from the real guarded baseline, including old
   tabs, controlled service workers, pending writes, conflicts and interruption.
   Database v2 is a forward-only writer floor: v1 cannot read OPFS references.
   Recovery must retain a usable v2 client; deleting data is not recovery.
5. Supply and test a pinned managed transaction/recovery operator. The observed
   protected hosting reconciler is plan-only; its `apply`/`recover` refuse.
   Old guarded-v1 deployment journals do not prove v2 recovery.
6. Only the release owner applies the qualified beta change, then checks actual
   signed public behavior and served hashes, with main and `/desktop/` unchanged.

## Required result from every package

Return the exact base and commit, changed paths, capability/status changes,
commands and actual results, a preserved failing control where applicable,
test limitations, resource observations and remaining dependencies. Update the
operational queue and relevant matrix. Commit source, tests, recipes, needed
final runtime inputs under the existing repository policy, and notes; exclude
generated working builds, dependency directories, accounts and secrets.

Push the named branch to box-git and R730 and verify both remote refs. Mark
tested, integrated, packaged and deployed separately. Do not use passing test
counts as a percentage of CAD 1.0–6.0 or report a gate complete by weakening it.
When a package finishes, choose the next bounded dependency-ready item; keep
shared-file edits and deployment serial.

## Historical replay failure retained as a control

The original `089ed178` owner prototype followed a confirmed failure where an
impossible edit exposed only a partial solid. Its missing type declaration,
older normalization base and absent lifetime hook were real blockers at that
checkpoint. They are superseded by the integrated fixes and combined lead
results above; do not restart the old merge or quote that failure as current.
The full Gate 1 and release still remain open for the listed reasons.

## CAD continuation: guarded centered-hole integration

CAD integration branch `integration/files-cad-release-20261104` is now at
`39ed306b` (box-git and R730). Files deployment is unchanged. This remains source
work, not a new public CAD release or completion of the mechanical plate gate.

- Candidate ledger and authored LID intent: `0465f861`, 18 focused checks pass.
  Independent actual Chromium/OCC parent-ledger regression passes, including
  14 projected-model mutation refusals. Parent association still belongs to a
  single private evaluation owner and worker mount.
- History descriptor/admission hook: `59caa7ad`, compiled but unregistered.
  The factory installs the adapter's synchronous publication guard; legacy
  operations retain their existing representation checks. Actual hole replay,
  undo/redo and native/signed My files reopen remain open.
- Analytic drilled projection and ancestry-role checks are integrated through
  `39ed306b`. Eleven focused circle/cylinder/orientation/role tests pass.
  Retained authored outputs cover 100×50×20 and 150×30×35 translated plates,
  with moved centers, diameter 10, through openings and expected analytic
  volume. These retained-data tests do not establish live parent-index binding.
- Native/worker lane has actual authored-prism and private mount controls,
  including no-op rejection/termination and caller-handle mutation refusal.
  Its next source checkpoint is pending integration. Persistent role assignment
  requires authenticated parent-index correspondence and same-operation cutter
  wall/rim ancestry; do not replace this with nearest-face matching.

Next: integrate checked native/mount and projection adapter, then register and
exercise the real history operation, parent edits, late mutation/cancellation,
undo/redo and reopen. UI and agent commands must use that same history path.
Detailed implementation queue and limits are in the CAD repository's
`docs/research/CENTERED-THROUGH-HOLE-CONTRACT-20261104.md`.

## Current continuation — test deployment policy and CAD metadata guards

Both beta.ksu.codes and ksu.codes are test deployments without real users.
The user authorizes direct replacement/reload of test services; do not add
old-window or prior-test-version compatibility campaigns. Preserve saved-file
correctness, account isolation, cleanup, unrelated sites and /desktop. Use
the existing managed deployment workflow.

CAD integration is now cb7c43bba6544728caaf42f6cf8413e7cf015980, backed up
to box-git and R730. The centered-hole history operation is registered in
source. Prism and drilled projection guards now detect metadata-container
and transient edge/vertex identity replacement. Independent review reproduced
the original defects in Chromium/OCC; independent post-fix review is pending.
The implementation agent reports the added actual-browser mutation controls
passing. Root's 10 plan/topology/section tests pass after integration. These
are internal consistency guards, not hostile same-realm JavaScript isolation.

Agent-reported full-app history checks pass resizing to 150×30, depth35,
undo/redo, refusing an oversized edit of the existing hole while preserving
history, and fresh-session native reopen. A wizard-helper run creates the
same operation; this is not physical-pointer evidence. Final receipts rebuilt
against metadata fixes are pending. Signed My files hole reopen remains open.
R730 clean native build remains running (PID554079, last observed53%).
No public deployment changed in this continuation.

## Signed hole workflow and newly found display failure

The signed desktop continuation now saves the separate centered-hole history
through My files and reopens it in a fresh authenticated session. Browser and
server bytes/hashes match; bounds/rims and history survive; a second account
is denied. See evidence/cad-centered-hole-signed-20261104.json. This is a
disposable real issuer/gateway fixture, not public deployment.

This test exposed an actual display integration defect: FaceView/updateSketch
and MBrepFace/setSketch reach generic simple-surface detection on the analytic
cylinder, which calls an unsupported degree operation. Save/reopen passing
does not establish correct rendering. Browser agent owns the analytic surface
consumer correction and a rebuild with CODI_EMBED_MANIFOLD=1; the previous
fixture omitted that flag and the secondary runtime correctly failed strict
CSP. Do not relax CSP. First fixture also reused feature ID3; corrected test
uses the actual project counter generator. Split chunks are now copied by the
test-only overlay builder. Rerun the signed check after these corrections.

Run with CODI_TEST_CENTERED_HOLE=1 and the existing signed rectangle test;
CODI_TEST_URL/CDP must be loopback. Fixture port20054, browser20055, staged
test bundle /tmp/codi-hole-signed-bundle-20261104-r2. Test setup remains the
existing files-desktop-signed-fixture.py; no new storage stack.

## Corrected display and signed recheck

Cylinder nonplanar/tangent-frame fix is integrated as CAD8b02fdff; independent
review passed. Signed test now asserts all seven face meshes have finite data
and fails on observer or secondary-runtime startup errors. Both embedded
numeric and Manifold build flags are enabled. Traced and subsequent untraced
signed runs pass persistence, fresh reopen, views and account denial. One
initial untraced run timed out rebuilding a saved prism; cause remains unknown
and no timeout was increased. The exact-sandbox hidden-iframe control passed
separately (CAD4f8b45f4). See evidence/cad-centered-hole-display-signed-20261104.json.
Phone screenshot shows the part/hole but automatic camera framing is too small;
this is not polished phone UX.

Clean R730 OCC build and three actual worker suites passed, receipt integrated
as CADf22dd5e9. Native agent is preparing normal-build clean-worker packaging;
legacy main-thread consumers still use their separate existing dependency.
Next: integrate clean-worker pins/source prerequisites and typecheck fixes,
build the actual app normally, then rerun affected signed/display tests. No
public CAD deployment changed.
