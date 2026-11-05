# WebOS work queues and progress ledger

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

## Latest bounded acceptance — 2026-11-04

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
