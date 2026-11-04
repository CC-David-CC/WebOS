# Active Files and JSketcher release milestone — 2026-11-03

User resumed development through the attached goal. The complete goal is
preserved in `docs/goals/FILES-JSKETCHER-RELEASE-20261103.txt`. This milestone
does not shrink its scope; the table below is the completion audit to maintain.

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
| F01 | Saved browser data survives close/reopen and fresh-session recovery | open | OPFS research tests exist; product adapter/migration required |
| F02 | Account invalidation, cancellation and independent sessions preserve isolation | open | Carry beta guards into product path; real signed regression |
| F03 | Stale windows/concurrent devices preserve edits and explicit conflicts | open | Product and multi-device conflict/resolution tests |
| F04 | Lost replies/uncertain writes reconcile without duplicate mutation | open | Real socket-cut baseline exists; retest integrated store |
| F05 | Downloads publish only complete verified generations | open | Research pull exists; integrated fault and version races |
| F06 | Cleanup cannot remove committed/in-flight data | open | Research staging journal exists; migration and crash tests |
| F07 | Heavy work stays in workers with measured responsiveness/resources | open | Research is not proof of strict browser memory limits |
| F08 | Changed-data transfers and safe first/legacy reads through 128 MiB | open | Product signed byte/resource measurements |
| F09 | Files create/open/rename/move/copy/delete/upload/download and truthful status | open | Actual UI plus server/browser interruption tests |
| F10 | Temporary Linux remains separate; existing app contract compatible | open | Existing callers and Linux-home integration tests |
| C01 | One coherent buildable fork preserves intended existing integrated work | open | Reuse 518a4666 descendants; exact selected base and feature map |
| C02 | OCC and Native Mesh capabilities, source/licenses and CSP are qualified | open | Actual build provenance and supported-operation evidence |
| C03 | Splines/history/selection/DXF/camera/reconstruction work together | open | Existing focused tests; combined app regression |
| C04 | CAD My files, independent instances, disposal and shared commands | open | Signed host workflow against product file contract |
| M01 | Atomic acceptance/rejection, midpoint and deterministic persistence | open | Admission research baseline; remaining solver failures/performance |
| M02 | Driving X/Y/projected/diameter and geometric relations/fix/groups/symmetry | open | Actual model commands and mechanical sketches |
| M03 | Equality/ratio/difference and driving/reference roles | open | Typed simultaneous relations and reference DOF tests |
| M04 | Typed parameters/formulas/dependencies/configurations | open | Bracket/enclosure edits with explicit errors |
| M05 | Regeneration/reference repair preserves authored intent | open | Missing/ambiguous references and failed-edit recovery |
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

Keep three independent implementation lanes active where their contracts permit.
Review actual commits and representative runtime evidence before integration.
Do not drop a requirement to make a test pass, equate synthetic results with
physical evidence, or restart completed source integration from old notes.
No global framework, new physics platform, printer or Bambu workflow is required
for this release. Continue until the complete stated bounded milestone passes,
or report a genuine blocker under the active goal's rules.
