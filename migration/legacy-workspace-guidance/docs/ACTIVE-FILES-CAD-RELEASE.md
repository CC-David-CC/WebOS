# Active Files and JSketcher release milestone — 2026-11-03

User resumed development through the attached goal. The complete goal is
preserved in `docs/goals/FILES-JSKETCHER-RELEASE-20261103.txt`, with the
2026-11-04 architecture amendment. The completion audit below retains its scope.

## Current architectural direction — 2026-11-04

The user authorizes using JSketcher as inspiration and replacing coupled code
where needed. Keep useful proven components, but production computational
workers must not require canvas, DOM, editor windows or fake browser UI.
`CAD-CORE-SEPARATION.md` defines the required boundaries, ARC01–ARC10 packages
and ENG01–ENG08 engine-mount work.
Separate the revisioned authored model, shared human/agent commands, formulas
and simultaneous constraints, computational core, jobs, generated references,
derived representations and saved files/caches. Extend the checklist when a
real missing core requirement is found, with a test and bounded ownership.

Current work extracts a data-only sketch solver and connects it to automatic
dependent-feature regeneration. A stale-boundary refusal protects the old model
but does not qualify ordinary supported resizing. The full Gate 1 and
bracket/enclosure/core-3MF acceptance remain required; later gates stay queued.

Latest successor entry point: `HANDOFF-FILES-CAD-2026-11-04.md` and the
copyable `goals/FILES-CAD-NEXT-AGENT.txt`. OpenCascade is preferred and Native
Mesh/Manifold secondary; both need broad capability support through swappable,
versioned mounts and explicit conversion/composition boundaries. R730 compute/
storage, llm-60 compute/testing and LAN repository creation/cloning are authorized.
This updates the goal, not the completion state of the implementation.

Root fork `2b3f2c0f` now integrates the headless worker/caller, corrected axis
semantics/admission, private atomic replay and document-lifetime guards. The
lead's exact app `aff1befe` passes build/typecheck, 11 browser regressions and
9 unit checks. Plate resize/native reopen, last-valid failed-edit recovery,
occupied-open refusal, service replacement and surface cleanup/reload pass.
Read the fork's `DOCUMENT-LIFETIME-REPLAY-20261104.md`. This is local evidence;
the earlier `794c14a3` host package has now been superseded locally by
`d3d36bc5`. Desktop `73c1e8b13` packages both workers and passes signed small
model and dependent-plate save/reopen at phone/1080p/4K. Ordinary OCC fillet
and chamfer, explicit Native refusal and useful wizard errors also pass.
See `evidence/cad-packaged-workers-20261104.md`. This is not a public release.

The Files beta candidate and issuer/config/session fixture are integrated at
desktop `2e312b797`, but managed transition/recovery and public qualification
remain open. `research/beta-opfs-release/README.md` records exact pins.

## Integration ownership and verified starting state

- Lead integration branch: `integration/files-jsketcher-release-20261103`,
  based on planning/integration source `3c17a9888`. That source is not a byte
  copy of the deployed beta release and must not be deployed wholesale.
- Files/storage owner: isolated `research/storage-product-20261103` on R730;
  carries forward the deployed guarded mirror before integrating OPFS research
  `796a10f6`. Owns file-store modules, signed adapter and Files app/tests.
- CAD consolidation owner: isolated JSKetcher branch chosen from the existing
  `518a4666` integration and descendant manufacturing/export branches. Owns
  build/runtime/engine and model integration; coordinates shared solver files.
- Mechanical owner: isolated JSKetcher `research/mechanical-cad-resume-20261103`
  starting at `aad3312f` with existing admission research. Owns constraints,
  numeric solver and parameter work/tests.
- Lead owns shared host APIs, integration/review, exact release packages and
  deployment. Agents do not independently change hosting or the main site.

Read-only 2026-11-03 checks: main and beta HTTPS returned 200. Beta issuer,
gateway and frontend were active/enabled; public SDK hash was
`44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869`.
Beta issuer advertises `https://beta.ksu.codes`. Workstation had about 49 GiB
free; recheck resource headroom before large work. Historical handoff disk
figures are not current guarantees.

## Required file and host contract

Keep `host.storage.mirrorFileContext()` account-bound and compatible with
existing applications: `{owner, files, valid, path, name}`. Scope binds stable
issuer plus account ID; session validity is checked at each asynchronous
boundary. Linux guest paths remain a distinct temporary capability.

- Preserve list/stat/read/readBounded/write, directory and file operations,
  status/subscribe/sync/resolve/close semantics used by the current apps.
  Add Blob/stream APIs without silently changing byte-returning callers.
- `version` is an opaque local edit token. SHA-256 is content identity, not a
  unique edit revision or proof of which writer committed bytes. Do not mix
  local UUID/CAS tokens with server hash expectations or claim ABA protection
  from a hash alone.
- `write(..., expected=null)` is create-only; replacements require the
  expected local version. An unresolved conflict cannot be overwritten,
  deleted or moved by an ordinary operation.
- Durable attempted-write metadata survives local edits and ambiguous outcomes.
  A dispatched write that may have committed is reconciled, not blindly retried.
- Return immutable verified data snapshots; validate byte size/hash and
  expected version before publication. File chooser result, content read and
  application mutation must remain owned by the same account/window.
- Cancellation before dispatch differs from cancellation after a possible
  commit. Preserve status and saved bytes; app disposal does not revoke a File
  already returned to another caller.
- OPFS migration must preserve existing saved, pending, conflict and attempted
  records. Existing beta guarded clients/hashed assets are a rollback floor.
  A new implementation cannot rely on an unguarded older writer being safe.
- One shared file stack serves apps. Do not add an app-private account mirror.
  A simulator's resettable working state is distinct from a committed project.

The Files owner returns any necessary API extension before dependent host/CAD
changes are integrated. The lead owns changes to shared desktop wiring.

## Completion audit

Each row needs actual source/artifact and matching runtime/test evidence.
`open` includes partial implementations; it is not a claim no work exists.

| ID | Required outcome | State | Evidence / next gate |
|---|---|---|---|
| F01 | Saved browser data survives close/reopen and fresh-session recovery | partial | Opt-in product adapter and complete-row migration integrated; staged Chromium reopen passes; deployed/fresh-session acceptance remains |
| F02 | Account invalidation, cancellation and independent sessions preserve isolation | partial | Guarded beta source carried forward; signed owner tests and bounded-read worker cancellation pass; full integration remains |
| F03 | Stale windows/concurrent devices preserve edits and explicit conflicts | partial | 2cec3e7e2: actual Files/Text UI, two independent Chromium processes/profiles, offline edits, stale resolution, preserving both copies and fresh signed reopen pass; final integrated rollout remains. |
| F04 | Lost replies/uncertain writes reconcile without duplicate mutation | partial | Real committed-response socket cut reconciled with one upload; injected newer-edit tests also pass. Full release transition still open. |
| F05 | Downloads publish only complete verified generations | partial | 218536add: real signed cold/replacement TCP cuts, OPFS row inspection, browser kill/restart and independent hashes pass; SDK still constructs a Blob before capture. |
| F06 | Cleanup cannot remove committed/in-flight data | partial | Explicit reader-aware collector has bounded paging, writer/reader/attempt/conflict and unlink/crash tests; automatic retention/UI and wider scale remain open (ADAPTER-2026-11-03.md). |
| F07 | Heavy work stays in workers with measured responsiveness/resources | partial | 544480232: lead two-tab capture/read, cancellation, FIFO/deadline, worker failure and renderer-crash test passes with max 1 heavy content worker; SDK/app memory and whole-release qualification remain. |
| F08 | Changed-data transfers and safe first/legacy reads through 128 MiB | partial | 7064310e1: signed 128 MiB plus queued/cancelled second-tab capture passes; one-byte edit 71,470 request-body bytes, sampled summed Chrome RSS 1.32 GiB, foreground heartbeat max 32.2 ms. These are observations, not a total-memory guarantee. |
| F09 | Files create/open/rename/move/copy/delete/upload/download and truthful status | partial | 99bc3ba06 actual signed UI workflows and cancellation/stale/collision tests pass; later F10 covers real Linux separation. Physical phone, full catalog and final release remain. |
| F10 | Temporary Linux remains separate; existing app contract compatible | partial | 9f753a95c: actual v86 guest-home Files/Text/signed-server separation and reboot reset pass; all-app compatibility and deployed qualification remain. |
| C01 | One coherent buildable fork preserves intended existing integrated work | partial | Integrated replay/lifetime/solver and fillet fixes packaged at d3d36bc5; nine lead browser runs and worker inventory checks pass. Broad carried-feature and release qualification remain. |
| C02 | OCC and Native Mesh capabilities, source/licenses and CSP are qualified | partial | Source-built OCC and both engines pass bounded strict-CSP checks; ENG01–ENG08 add broad capability inventory, swappable mounts, explicit conversions/composition and qualification. Linked-source evidence remains open. |
| C03 | Splines/history/selection/DXF/camera/reconstruction work together | partial | Consolidation owner ran real carried-feature checks; integrated host and final fork regression remain |
| C04 | CAD My files, independent instances, disposal and shared commands | partial | Desktop 73c1e8b13: signed native-v2 small models and dependent five-hole/fillet plate pass phone/1080p/4K, both packaged workers, exact server bytes, account denial and closed-command rejection. Full agent part, all lifetimes and large-model gates remain. |
| C05 | Agent-driven CAD uses the same validated operations as the UI | open | Discover commands and stable entity IDs; build/edit bracket, reject contradiction without damage, undo/redo and account-backed save/reopen; no AI provider required |
| A00 | Beginner single-part fixtures precede the bracket | open | Start from empty documents: dimensioned block, washer and drilled plate through UI/shared commands; see learning progression |
| M01 | Atomic acceptance/rejection, midpoint and deterministic persistence | partial | Reclassification/drag/restore fixes reviewed; independent cross-stage failure controls found further rollback work |
| M02 | Driving X/Y/projected/diameter and geometric relations/fix/groups/symmetry | open | Actual model commands and mechanical sketches |
| M03 | Equality/ratio/difference and driving/reference roles | open | Typed simultaneous relations and reference DOF tests |
| M04 | Typed parameters/formulas/dependencies/configurations | open | Bracket/enclosure edits with explicit errors |
| M05 | Regeneration/reference repair preserves authored intent | active | Combined plate resize/reopen, ordinary OCC fillet/chamfer, last-valid failed-edit recovery and late-result/document replacement pass; new worker graph is signed-host tested. Feature patterns, units, full Gate 1 and all operation contexts remain. |
| ARC | Computational core operates independently of UI and publishes only current validated results | active | CAD-CORE-SEPARATION.md: no canvas/DOM/fake UI; actual equations, bounded jobs, residual/geometry checks, cancellation, IDs/revisions and explicit failure. |
| A01 | Mounting bracket substantial edits, contradictions, undo and reopen | open | Real integrated acceptance model |
| A02 | Enclosure/separate lid substantial edits, contradictions, save/reopen | open | Real integrated acceptance model |
| E01 | Named material/region/appearance/group/placement persists | open | Reuse manufacturing metadata; native edit/reopen |
| E02 | Inset label remains deliberately grouped with lid | open | Alignment and assignment through parameter changes |
| E03 | Model-derived core 3MF independently verified | open | Two build objects/three assigned regions; units/transforms/materials |
| E04 | Invalid/unsupported geometry fails without replacing good output | open | Mesh/interface, cancellation and signed-save fault cases |
| R01 | Reproducible source/runtime/test prerequisites on another machine | open | Clean checkout/build proof; source notes alone insufficient |
| R02 | Beta-only qualified rollout preserves main/prototype and guarded floor | open | Exact staged artifact, transition/recovery and public tests |
| R03 | Source/tests/evidence/handoff backed up to box-git and R730 | active | Checkpoint each integrated slice; final remote-ref verification |

## Execution rules

Current source/test details and limits: `docs/evidence/storage-product-integration-20261104.md`.

Latest priority: `docs/JSKETCHER-FOUNDATION-MATRIX.md` makes the basic shape,
constraint, solid-operation and persistence qualification explicit. Repair
confirmed failures before expanding the feature catalogue. Tonight remains
Files, correcting wrong JSketcher implementations and useful tested parts.

The user has now defined the broader CAD-engine program explicitly:
`CAD-ENGINE-GATE-1.md` is foundation competency (12 areas, 22 exercises and the
coupled dimensional-change workflow); `CAD-ENGINE-GATE-2.md` is intermediate
mechanical CAD. The original attached release audit remains historical/current
slice evidence; it must not be presented as completion of these larger gates.
Advanced Gate 3 is recorded separately in `CAD-ENGINE-GATE-3.md`, with ten
groups. The user intentionally split the other six into `CAD-ENGINE-GATE-4.md`;
they are not missing Gate 3 requirements. `CAD-ENGINE-GATES.md` indexes the
program and requires later needs to inform early design. Do not start Gate 2–5
implementation instead of finishing Gate 1. Gate 5 is now defined in
`CAD-ENGINE-GATE-5.md`, including the conceptual CAD 1.0–6.0 ladder, traceable
requirements, experiments and system synthesis. `CAD-ENGINE-END-TO-END.md` maps
inputs, outputs, failure handoffs and actual acceptance workflows. Gates 2–5
remain queued. Competency priority and implementation dependency order are
distinct.

### Explicit agent acceptance gate

Agent use is part of this release, not a separate geometry representation. A
browser API client must discover supported operations and entities, target stable
IDs, and invoke the same validated model commands as the user interface. Test
the bracket workflow through that API: create the model, change a parameter or
dimension, inspect the result, attempt and recover from a contradictory edit,
undo/redo, then save/sync/close/reopen through the account-bound host services.
Compare the authored relationships and geometry before and after reopening.
The API must report unsupported operations, conflicts and failures explicitly;
stale document IDs, closed windows or changed accounts cannot apply mutations.
An AI provider, autonomous search or private agent-only solver is not required.
The current existence of individual callable CAD actions is partial evidence,
not proof of this end-to-end acceptance gate.

The starting exercises and longer-term CSG/motion paths are in
`docs/planning/CAD-LEARNING-CSG-XR.md`. XR is a lower-priority, separate-branch
stretch goal and does not block this release. Fast interactive physics and
qualified engineering analysis remain distinct future paths on shared authored
designs; this milestone does not require either complete physics stack.

Keep three independent implementation lanes active where their contracts permit.
Review actual commits and representative runtime evidence before integration.
Do not drop a requirement to make a test pass, equate synthetic results with
physical evidence, or restart completed source integration from old notes.
No global framework, new physics platform, printer or Bambu workflow is required
for this release. Continue until the complete stated bounded milestone passes,
or report a genuine blocker under the active goal's rules.
