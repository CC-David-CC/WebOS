# Workflow state machines and invariants

Canonical maintained inventory for the current WebOS Files/CAD foundation.
Update this file and WEBOS-WORK-QUEUES.md when a state, guard, transition, defect,
regression or integration status changes. Audit receipts are evidence, not
competing specifications. This is a first pass, not exhaustive safety proof.
Third-party editor/kernel internals, games and future physics are outside this
pass unless they affect the shared workflow.

## Activation authority repair and encoder custody — 2026-11-07

Core9df225f4d repairs the previously open activation cases. The closure captures
its manager installation authority once; jobs/snapshots may not adopt a later
manager. Externalvalid callbacks are checked before destructive document change,
and passive checks follow without invoking them again at that boundary. Late old
failure cleanup cannot invalidate the replacement manager's project. Unchanged
independent regressions plus83core/77host/10signal root repeats pass; no generic
hot-reload metadata migration or browser drawing qualification is claimed.

Controlled3MF encoder: admitted metadata/attached binary → transfer attempted
(not consumed/consumed/unknown) → Worker encode → validated response → terminated.
Failure always establishes no file write in this encoder layer; file settlement
belongs to the existing host writer. Transfer uncertainty requires fresh private
artifacts, not retrying detached input. Two parts may reuse a local region ID;
resource IDs/bodies remain globally unique. Producer/currentness authority is
outside serialized buffer metadata and must be held by the protected replay
owner. Private batch orchestration remains in progress. Curved closed-cavity
Native geometry is correct; the current nesting validator refuses it, openfix.

## Drawing manager-instance custody audit — 2026-11-07

New source retains V3drawing definitions through normal and material-aware Save
using the actual validation Worker for string and byte entry points. Root34
positive controls pass. Drawing lifetime follows its actual document signal;
revision includes drawing identity, and absent getter fails closed in hostdirty
inspection. These are not full workflow qualifications.

Two open confirmed transitions require a per-activation manager authority:
externalvalidcallback→managerreplacement→beginDocumentChange must refuse before
advancing/aborting the document; old-manager Save→new-current-manager must never
return currentness true for orphaned state. The initial after-await guard alone
is insufficient. Preserve failed counterexamples and fix the related invariant
once across relevant jobs, without inventing parallel document state. No new
combined drawing runtime until repaired regressions pass.

## Manufacturing normal path and signal truth — 2026-11-07

Genuine signed public authoring/assignment/no-op/Undo/Redo/Save/freshOpen now
passes for one Native plate. Exact assignments and unchanged native bytes survive
reopen. This proves that normal path, without implying every failure transition.

Review found actual preaborted AbortSignal with own aborted:false could pass old
property-based guards and commit. Native-branded capture alone was insufficient.
Coree8ae8c449 reads intrinsic native abort state and uses intrinsic listeners in
document/hash/preparation ownership. Source integrated; new proof/rebuilt browser
scope remains pending. This is a synthetic injected-signal contract defect, not
an observed live incident. Preserve the original BEFORE packet. Do not infer
cancellation from an overrideable convenience property.

## Manufacturing publication and observation authority — 2026-11-07

Manufacturing proposal: preparing → privately prepared → synchronously committed
assignment/journal/tip → notifying. Stale/aborted/refused preparation publishes
nothing. No-op does not churn tokens or discard Redo. Once committed, observer
failure cannot roll back or overwrite a newer reentrant edit; report committed
outcome. Undo/Redo uses the same bounded authored journal and no Native replay.
Worker cleanup must succeed before admission to publication. Service controls
27focused+171retained pass; geometry is an explicit protocol fixture here.

Evaluation ownership: captured purpose=model or observation at begin. Observation
owners remain unpublishable across awaits and after successful reads. Currentness
and private ledger bind actual owner/runtime/body. Cancel/failed read retires its
observation candidate, preserving the separate accepted model. Recheck owner cap
after external lifetime callbacks; use intrinsic native signal registration and
removal so own-method overrides cannot strand custody. BEFORE6FAIL/1PASS;
AFTER7new+15retained PASS. Actual NativeSignal, synthetic closable mounts.

No additional top-level state-machine count is claimed. These tighten existing
publication/resource families. Full drawing custody and combined browser runs
remain open. See evidence/manufacturing-worker-root-20261107.

## Save/watcher repair — 2026-11-07

Desktop5c4fa703a shares no-write → pending → acknowledged settlement between
Save/export. Own-data receipt validation precedes acknowledgement/publication.
Later failure cannot downgrade acknowledgement. No receipt means uncertainty,
not proof of rollback. Primary falsey errors survive reporting/finish faults.
Browser acknowledgement is separate from server synchronization.

Retain watcher unsubscribe custody until successful return. Activation failure
preserves old custody; repeated successful release is a no-op. Provider failure
leaves release unconfirmed; disposal reports it and continues other cleanup.
No crash cleanup promise. 70 Save/cleanup plus111 retained controls pass using
actual host functions and synthetic providers. Fresh signed normal proof also
passes: three real native Saves, D10→D14 edit, fresh-session Open and unchanged
reopened bytes. Scope/pins: native-save-outcomes/signed-evidence-r1.
See test/agent-cad-corpus/native-save-outcomes/repair-evidence-r1.

## Drawing witness invariant — 2026-11-07

Pure cylinderCutWitness adds no state owner/family. Actual prism→original-source
Cut B ancestry chooses the descendant; geometric comparison only verifies it.
Never choose by nominal/nearest geometry, compose copy twice or save native slots.
Fresh3Native/Node Worker cases pass. Production current owner/source/build/
lifetime admission and full E22 remain open; family count unchanged.

## Counting and representation

Currently **21 identified workflow families**: 16 implicit, four hybrid, one
explicit (20 runtime families plus one build-staging family). Classification is
mapped for this inventory, not exhaustive coverage. These are logical families with named
owners, not 21 independent minimized automata. Nested protocols may be split or
merged after review; repeated windows and kernel instances do not increase the
count. Classification and coverage below are provisional.

Count owners/events/guarded transitions, not every boolean. Derive dirty, busy,
canSave/canUndo and stale status from authoritative revisions, operations and
ownership. Necessary history such as ever-connected cannot be derived from the
present. Small implicit machines are fine when legal combinations and comments
are clear; an enum is useful when it removes ambiguity, not when it merely
combines independent facts into a huge state list.

Capture immutable inputs/lifetime, prepare privately, validate, publish at one
boundary, retire old resources. Failure retains accepted authored state.
Cancellation, caller loss, native completion, local commit, remote commit and
acknowledgement differ. Unknown outcome requires inspection before retry.
Terminal states are absorbing. Every confirmed defect needs a repair, regression
and documentation; a green component count is not end-to-end qualification.

## Inventory

I=implicit, H=hybrid, E=explicit, ?=not yet classified. Evidence is mapped, not
silently rerun. CAD sources live in the separate JSKetcher repository.

| ID | Owner / source | Type | States / transitions | Main invariant / coverage |
|---|---|---|---|---|
| U01 | Account transition, app.js | I | signed out → signing in → active → ending/recovering | Credentials, revocation and retained work differ; review open. |
| U02 | App mount, desktop-apps/app-instance | I | placeholder → loading → mounted → disposing → disposed | Late imports cannot resurrect removed windows; tests mapped. |
| U03 | Desktop lifecycle.mjs | H | idle → checking → recovering → idle; live → stopped | One owned operation; stopped continuation cannot re-block UI; LR01. |
| U04 | Per-window DocumentOperations | H | idle → prepare(token) → local-write(token) → idle; live → disposed | Stale finish cannot finish new work; busy/phase derived from owner;20 coordinator controls pass. |
| U05 | Session document claims | I | unclaimed → claimed(path/tree,owner) → released | No overlapping owners, including reentrant notifications. |
| U06 | Command registry/scoped settlement | I | registered/current document → guarded dispatch → pending → settled/lifetime-lost | Whole-recipe document token derives from authoritative signal; recheck after caller serialization; known commit outcome retained. RC01/CMD01 component regressions pass, signed New/Open pending. |
| F01 | Mirror row, mirror.mjs | I | clean/dirty/tombstone/conflicted/moving → sync/conflict | Bytes, remote base and intent agree; combinations under review. |
| F02 | Mirror scan/retry | I | fresh → running → continuation/backoff → completed/failed | Retained progress is not fresh verification; ST01. |
| F03 | File/folder conflict | I | detected → resolution prepared → CAS/publication → resolved | Preserve both sides until accepted resolution; ST02. |
| F04 | Durable rename recovery | I | intent → remote/local steps → complete; interruption → recover | Preserve exact identities/versions; evidence mapped. |
| F05 | App Save | I | capture → claim → write → local commit → baseline update → sync | Later edits stay dirty; local commit differs from remote sync. |
| F06 | Verified content/OPFS leases | H | stage → verify → publish; lease → copy → release | Published immutable generation stays leased through actual copy. |
| C01 | CAD iframe/project replacement | I | active → candidate load/restore → verified swap → retire old | Failed candidate retains active project; bounded New/Open proof. |
| C02 | CAD project generation/restore | I | empty/current → restoring → ready; superseded → reject | Document/host lifetime remains current across awaits. |
| C03 | Craft model publication | I | pristine-unbound → candidate → accepted tip; failure/rewind/close | Model/history/source/material/journal publish together; CG01. |
| C04 | Authored journal | I | tip ↔ Undo/Redo; accepted branch truncates redo; New resets | Authored intent only; mixed creation/edit native proofs pass. |
| C05 | Sketch/parameter transaction | I | begin → edit/solve → accept/reject; interruption → recover | Equation validity, authored source and retained output differ. |
| W01 | Evaluation owner, evaluationResources | E | candidate → accepted → detached → closed; candidate → closed | Reservation/cleanup follows ownership; WR01. |
| W02 | Engine controller/Worker | H | controller: initializing → ready (+pending) → closed; Worker: new → initializing → ready↔busy → closed | One request owner, synchronous admission and bound replies; WR02/WR03. |
| W03 | Source/semantic/parameter/project/hash clients | I | admission/queued → running → settled; healthy → cleanup-failed fence | Late replies never publish; exactly-once cleanup/settlement and module fencing mapped; client/manager component regressions pass. |
| B01 | Native build staging | I | cache input → verified → private temporary copy → generated target | BR01 raw-SMLib atomic cache repair passes; sweep bootstrap pin controls pass. Full prism stager still deletes prior private output before later failure; atomicity OPEN, not covered by BR01. |

Derived status is not another machine unless independently stored authority can
drift. Validity/representation/qualification are revision-bound classifications,
not automatically lifecycle machines. Unreviewed rows are not proof of safety.

## Two-source sweep preparation — 2026-11-07

C05/W03 extend to profile+path input capture: copy both frames and ordered
source references before either digest suspends; verify each solved source's
hash/frame/membership independently; retain a single document generation through
later native publication. CAD8f093da6b has21 offline contract controls (36 with
retained revolve controls), including mutation across asynchronous capture.
Revision-string equality is not document ownership. This is preparation only;
actual Worker lifecycle/publication/history and Save/Open remain unqualified.
CAD45e0fc67d additionally passes six independent source probes and seven actual
production semantic-Worker browser checks under strict CSP. The latter prove
data preparation/refusal transport only, using hand-authored fixtures; native
evaluation, app publication and signed document lifetime remain unqualified.
No new independent lifecycle owner or parallel copy of authored geometry is
introduced. The canonical runtime-family count remains21.

CADa9e0c2933 extends W01/C05 ledger admission: exact source binding includes
both face identities plus ordered path references/direction. Both faces must
exist before allocation and match again at publication; native mount capability
and positive valid single-solid output remain mandatory. Ten admission-only
regressions pass (52 combined with retained controls), TypeScript passes. These
refusal tests create no successful native geometry; actual publication proof
remains pending with the shared operation and new Worker runtime.
Root CAD437cda96b adds12 real planner→WASM FFI controls: native names return to
zero per case and both input buffers remain unchanged while independent
volume/bounds/material/void/roll observations pass. These are native component
lifetimes, not a new production Worker cancellation or document-publication
proof; those transitions remain pending.
CAD54ce073a3 extends W02's existing machine with explicit pinned sweep init,
request/binding capture, native result ownership and typed refusal admission.
Five transport-double controls pass (54 with retained source/protocol controls),
including pre-abort and fatal input-integrity failure. No fake native success
reply is used. Actual production-adapter Chromium lifetime/publication proof
remains pending, distinct from direct FFI and native-lane Worker tests.

Retained original-plate workflow on CAD73c888/desktop36b8 passes22 signed and7
browser-only rows with3 saved files, stable settled ownership counts and four
owned contexts released. This proves bounded ordinary composed lifetimes, not
new termination-fault injection, RSS reclamation or every C05 transition.

CAD62fcf04b3 derives backend ownership and native-result budget membership from
one immutable authored-solid vocabulary, including sweep. C05 fast-save source
dependencies include both profile and path through generic body ancestry.
Five policy controls pass (67 with retained controls), TypeScript passes. This
does not register a backend or validate the new operation; unsupported builds
remain explicit refusals and full source edits still require atomic replay.

CAD6a796ba80 extends C04's existing operation-append transition to sweep,
without a new journal or stored geometry. Directed path identity is compared by
value after strict capture; nested arrays detach/freeze and their actual JSON
size is charged in bounded fragments. Five pure journal controls pass (72
combined); TypeScript passes. Live Craft/app Undo/Redo and Save/Open remain
unqualified until the genuine shared-operation replay.

New RV02/C05, P3 (unpublished shared sweep): an actual current Circle selected
as path is rejected as STALE_PATH instead of unsupported curve type. Existing
rejection preserves accepted geometry; root's12 source controls did not cover
this distinction. Repair CAD07f7677ad separates absent identity from unsupported
type; the owner passes13 real Worker groups with153 started/153 terminated.
Final source-bound evidence is integrated; root combined build d33a929ea repeats
all13 actual operation Worker controls with153 starts/terminations and clean
TypeScript. Actual combined native/app publication qualification remains open;
no accepted geometry changed in this fix.

Craft append admission now derives directly from its journal capture/key
registry (CADa246e0d82), including sweep, instead of a separately synchronized
allowlist. Seventy-seven retained controls/TSC pass. Actual signed replay is
still required; this source change does not prove publication/Save correctness.

Desktop sweep bridge a29fd9d1c reuses U06 scoped settlement for four commands.
Nested path references detach before dispatch; account/document/realm/Close loss
settles honestly and late results stay inert. Committed and unknown outcomes
use the existing shared policy. Thirteen new transport controls and retained
controls pass; root repeated sweep+revolve19 after integration. These are bridge
controls, not actual CAD publication or native Save/Open evidence. No new
lifecycle machine, retry policy or duplicate document state is introduced.

Sweep reply-binding controls CAD0b04f3c64 exercise W02's pre-handle publication
gate with an actual recorded native reply:12 routing/tamper/accessor controls
pass, without a new native execution. Public native point inspection remains an
explicit gap: detached accepted models have no live native shape handles. Any
new query path must own temporary re-evaluation and lifetime binding rather than
borrow dead resources or silently promote preview classifications to native.

RC01/U06 recipe-target lifetime (unpublished helper, transport counterexample):
the window/session identity remains current after a successful same-window
New/Open, so a multi-step recipe that reacquires fresh revisions can continue
writing into the replacement document. Per-command scope does not establish
whole-recipe intent. This is not an observed live corruption incident; the
signed browser reproduction remains required. A repair lane now owns stable
document binding through the public registry, with an atomic pre-dispatch
expected-document guard and one pin across recipe steps. Inspect-then-execute
alone is insufficient. Explicit New/Open receipts and existing account/window
committed/unknown outcomes must retain their semantics. Regression/repair and
actual signed acceptance are pending; the sweep example remains unqualified.

CMD01/U06 metadata admission: the registry's total 8,192-character JSON limit
rejects a legal 8,192-character region identity once required command fields are
included (8,571 serialized bytes, zero handler calls). This is a confirmed
transport compatibility defect, not a native geometry failure. The retained
source-bound reproduction is `test/command-argument-limit/before.json`.
The repair lane is implementing one bounded UTF-8 metadata budget and boundary
controls, preserving document revalidation after serialization. File payload
limits are unrelated. Repair and combined-app validation remain pending.

B01 retained staging pin drift: after reviewed sweep transport54ce073, the
selected-profile stager still expected the old bootstrap hash. Actual normal
build11558ed2a refuses before output replacement; native glue/WASM still match.
Repair dce53517e binds the reviewed aa7f6433 Worker with native pins unchanged.
Fresh R2 staging passes; full normal build and independent negative controls
remain in progress. This is a build integration defect, not native CAD failure.

RC01/CMD01 repair integration: desktop64664b0c0/50ffd4e69 and
source/evidenceb651786a4 are merged. Root independently runs61 combined command,
recipe, lifetime and sweep-bridge controls: PASS. Review finds no concrete
dispatch/receipt flaw. A legal region now reaches the actual bridge and the
intentional NATIVE_NOT_RUN boundary (after.json), rather than failing registry
metadata admission. These supersede pending source/component repair above;
genuine signed same-window New/Open controls remain pending. Opaque token is
derived from the authoritative document AbortSignal, not a second generation.

B01 pin repair has six independent staging controls PASS (CADdb34c89f1),
including actual reviewed native bytes and helper tamper/refusal checks.
Separate full-prism-stager regression confirms prior-output deletion before an
ordinary missing dependency; that staging atomicity defect remains OPEN. It is
not a user file mutation. Fresh owned qualification directories avoid relying
on old staged output, without claiming the defect is fixed.

AR01/C05 confirmed shared Arc edit gap: signed quarter-Arc sweep creates,
saves and reopens, but inspection returned zero Arc point IDs and coordinate
admission excluded Arc. CAD6725b03eb repairs both through existing native IDs,
transactions, solver and independent verifier.8 genuine Worker controls and15
retained service groups PASS;36 new-test Workers retired; TypeScript PASS.
Independent review and repeat8controls pass. After-fix signed app run pending.

RC01 actual immutable helper/browser controls PASS on9c6dc2eb2/50ffd4e69:
external same-window New/Open make old helper refuse with accepted state intact.
See sweep/signed-document-scope-evidence-r1. This closes bounded replacement
proof, not all interrupted recipe-step cases or receipt adoption scenarios.

AR01 after-fix signed app PASS:4source-authored sweep cases, forward/reverse
Arc edits, UndoRedo and12native Save/reopens. Root independently checks24native
observations from saved source. Same6725/50ffd runtime helper New/Open alsoPASS.
This supersedes pending signed repair above; failedR2 retained. No full E14,
general path or native-point-query qualification implied.

W01/W02/C03 read-only native point replay now source-implemented and component
controlled: genuine private pipeline, exclusive lease, complete frozen source,
restored ID context, candidate-only handles, cleanup-before-receipt. No epoch,
feature counter/history/model/source publication. First actual disk query/repeat
pass accepted-state preservation; full geometry/performance corpus stillrunning.
CAD64aac/72bcb, host9ff89. Added read transition, not another state family.

Current W01/W02/C03 point-read evidence:13actualqueries/77nativeclasses pass
with exact acceptedstate/netpool preservation; independent257points/35Workers
also pass. Broad capacity/lifetime remains unqualified. Repeated immutableWASM
network cost is confirmed W02 initialization work; nativeHTTPcache integration
is pending. Eligibility must derive from registered hashed software paths/body
SHA, never account/API/userfile responses. No new workflow family introduced.

W02 loft component now uses the existing pending request owner: preparation
may refuse before any prepared binding; native execution begins only after one
Worker-computed prepared binding, and the result must match that exact binding.
Duplicate/out-of-order/missing preparation or changed source/seam metadata closes
the request; late messages after cancellation cannot publish. The phase derives
from binding presence, rather than an independently synchronized state flag.
Component Chromium geometry/refusal/cancel/resource controls pass; root repeated
40 focused controls, the retained analytic checker and TypeScript. Shared loft
source-authoring/history/public command/persistence remain unqualified.

W02 cache update is not qualified by build or headers: combined1668/d633 private
runtime still transfers35,204,843 encoded WASM bytes in each of3 real passive
queries, while geometry and accepted-state checks pass. Diagnostic setup also
refuses on retained app Workers. Response headers are immutable; browser cache
retention/eligibility and inspector assumptions remain under investigation.
Account/API/My files responses are outside this software-only policy. No new
state family or HTTP-cache success claim is introduced.

W01/W02/C03 capacity R1 now corroborates the read/write distinction at the
native-result limit:32 actual accepted outputs, planned32/remaining0/withinLimit
true/canAppendfalse,33rd create RESOURCE_LIMIT with unchanged feature high-water
and accepted state. A5-point native observation returns at quota (~40.67s under
existing60s limit) without accepted-state/resource changes. The runner then fails
an unsorted expected-key assertion; original failure retained, root independent
actual-data checker and two schema regression controls pass. Full-capacity native
Save/Open was never started in R1 and remains pending; no complete run claim.
[Raw and independent scope](../test/agent-cad-corpus/sweep/signed-capacity-evidence-r1/README.md).

W02 ordinary-profile cache qualification supersedes the pending policy verdict
above for private1668/d633 only:3 genuine native queries/192 point observations pass with
HTTP-cache flags and completed0 encoded WASM transfer; accepted state/resources
and all21 Worker retirements preserved. Root repeats captured-facts checker and
10 instrumentation controls. Isolated/private-context large-WASM misses remain;
small JS caches in both profile types. No new retained JS buffer/cache authority
was added. Live Caddy delivery and broader latency/RAM remain unqualified.
[Exact cache scope](../research/native-app-cache-proof-20261107/RESULTS.md).

## Confirmed issues, grouped by impact

| Group | Impact | Confirmed behavior | Current repair/evidence |
|---|---|---|---|
| NM01/W02+C04 | P2 native metrology reporting discrepancy, scoped repair qualified | Quarter-phase circle loft radius2→3 reports785.3981615793532mm³ versus analytic250π=785.3981633974482; absolute1.818095029e-6 exceeds frozen1e-6 tolerance. | Actual R3 FAIL af6ec8acc retained;3 completed saved/native checkpoints and36 point classes separately pass. Fresh diagnostic preserves exact radius/frame/seam and repeats same value after Save/Open; all6 points match. Same-BRep comparison0ffcca87 reproduces the default exactly; adaptive1e-10 gives785.3981630662182 within unchanged oracle. Native repair4d086f46/evidence39d47907 passes component, production, Boolean and plate controls without changing geometry/tolerances. Registered explicit adaptive cohort and combined signed app proof482cc886f pass both circle workflows,4 native files/8 queries/48 points under unchanged oracle. Original old-build failure stays retained. This closes the scoped reporting defect, not all-shape accuracy; integration estimate is not ideal-geometry error bound. |
| MD01/W03 | P2 component metadata bound | Loft semantic value65,406 bytes fits the value cap, but full success envelope65,821 bytes exceeds64KiB for an allowed128-character job ID. | Repair integrated CAD2f2e09afb/caa5a132e: genuine boundary now returns bounded475-byte RESOURCE_LIMIT;19 source groups/24 Chromium Workers pass. Full app workflow remains unqualified. |
| RB01/C02 | P1 saved project cannot reopen | Valid32body saved project requires44s rebuild; fixed30s restore wait rejects it despite intact saved data. | CAD594cc042b derives finite wait from validated history:60s+5s/entry, capped600s;22 source controls pass. Genuine fresh Open44.063s/native query43.031s/unchanged saved SHA pass in desktop909aa055f; root independent checker passes. Original failed run retained. No all-project timing guarantee. |
| LP01/C04+W03 | P2 circle loft admission mismatch | Producer emits qualified curve identity; ledger compared it against local saved circle identity, rejecting genuine payload and admitting wrong namespace to the next boundary. | CAD904a28409 shares one opaque qualification helper across producer/descriptor/admission;6 genuine-payload controls/18 ledger controls/32 retained controls and TypeScript pass. Root repeats19 genuine source groups/45 terminated Node Workers. Full shared-app circle loft remains pending. |
| ST01/F02 | P1 silent stale data | Unrelated failing file retains checked progress; healthy remote changes are skipped, even on a pass reporting completion. | Fresh/continuation repair integrated;10 focused controls, retained suite and8 real IDB/OPFS browser scenarios pass; combined signed check pending. |
| LR01/U03 | P1 unusable desktop | Late stopped recovery re-blocks roots without overlay; deadline admits overlapping recovery; failed recovery strands disabled Retry. | Owned-operation repair passes3 real Chromium regressions and5 retained checks; pins in tests/state-machine-audit-lifecycle/evidence/verification.json. |
| ST02/F03 | P1 unresolved-side logical loss | A conflicted directory can lose its child reference when only the remote directory returns; a clean conflicted file loses its reference when remote disappears. | Both real IDB/OPFS traces fail on frozen b911, retained in desktop e6492bf63. Durable repair integrated at c91aee0b2;8 new Node groups and10 actual browser scenarios pass, plus retained controls. Root merged coordinator/storage run38 groups and retained scan10 pass. Signed composed-app replay pending; physical byte erasure/public incidents not established. |
| WR01/W01 | P2 cleanup contract | Falsey cleanup throws fail to latch; throwing close accessor strands a reservation. | Injected faults, not observed kernel incidents; repair integrated at CAD061551b93;22 focused/retained resource controls pass. |
| WR02/W02 | P2 direct Worker boundary | Duplicate initialization stalls; concurrent same-token work creates two native names but retains only one token. | Genuine Worker reproduction. Normal controller rejects concurrency; gate repair integrated at CAD920dc619d. Six direct-Worker controls plus new/retained native corpus pass; combined app replay pending. |
| MG01/C05 | P2 service reentrancy | Final caller guard can accept a newer display edit/start a pipeline, then the old setter commits. | Repair integrated at CAD94cf5fa19;5 regressions +14 retained manager controls pass. No public incident/new signed-build claim. |
| WR03/W02+W03 | P2 termination-fault contract | Throwing Worker termination strands readiness/pending promises; the same pattern occurs in three disposable clients. | Controller repair integrated at CAD334ceba19;44 metadata/resource controls and3 actual Chromium post-termination injected faults pass. Three-client repair integrated at CAD625eed661:51 controls and9 genuine Chromium CPU Worker checks pass. Project/hash repair integrated at CAD5a022f6a6:33 focused and36 retained controls pass, including real Node Workers; no ordinary termination incident or composed-app claim. |
| WR04/W02 | P2 cancellation-hook settlement contract | Throwing removal clears pending/timer before settling; throwing registration or opaque postMessage coercion can strand BUSY. Reproduced with synthetic error-only transport, including true native signals; no public incident claimed. | CAD e55f03573 repairs pending custody, registration/cleanup reentrancy, exactly-once removal and exact cause retention. 42 new +10 retained Node controls and6 actual same/cross-realm Chromium signal controls pass; root repeats42 +full TypeScript. Full app on revised controller remains pending. Source-plane and point callers are separately repaired under WR05/WR06; this controller proof alone does not qualify those callers. |
| WR05/W03+C03 | P2 source-plane cleanup outcome loss | Native-signal instance registration can leak an earlier listener; throwing removal can skip workspace discard and replace an ordinary or committed-marked outcome. | CAD1dda17e77 repairs tracked setup, intrinsic removal fallback, all-cleanup attempts and guarded exact-cause release-unconfirmed diagnostics. Root35 service groups +2 irrecoverable controls pass; genuine source Workers/error-only submit, not native publication. Signed revised runtime pending. |
| WR06/W03 | P2 point-query cleanup outcome loss | Same native-signal registration/removal pattern leaks subscriptions or replaces original evaluator failure. | CAD7fbc6d123 repairs setup/finally without new authoritative flags. Root44 groups and TypeScript pass; admission doubles/error-only evaluator are labeled. Successful classification on newly composed runtime pending. |
| RV01/C04 | P2 new feature edit blocked; bounded repair qualified | Actual public revolve creation worked but angle edit reached an older unsupported-kind guard despite downstream implementation. | R1 retained at desktopfe4cb99df; exact two-list fix CADd81bb8b97. Genuine CAD73c888/desktop36b8 R2 unchanged driver passes4 cases/30 rows/6 saved files; separate six-edge stepped workflow passes14 rows/4 saved files. Independent oracle10 files/20 observations passes. Broader domains/human parity remain open; no deployment claim. |
| BR02/B01+U02 | P1 app cannot start | Builder/backend512MiB accepted the370857213byte app, but browser loader retained320MiB and displayed App bundle too large before any CAD iframe/command. | Actual signed failure retained897cdcdf9. Repair dea2518a3 uses one JS inventory policy for builder+browser;6 actual-loader metadata regressions before2FAIL/4PASS→after6PASS. Sparse builder/backend agreement and retained72-app build/load/129-refusal PASS. Private20938 corrected loader bytes verified; actual signed CAD launch passes, and combined adaptive20939 package407168387bytes also launches and passes the circle workflow. No geometry failure or public incident claimed. |
| BR01/B01 | P2 repeat-build failure | Readonly cache copy leaves generated WASM0444; a second normal build fails EACCES. | Repair integrated at CADb612285f3; actual first/second builds and malformed-input preservation pass. Fixed64KiB hash scratch and verified same-directory temporary rename; native bytes/defaults unchanged. |
| CG01/C03 | P1 regression, repaired | First creation required evaluated metadata; journal generation0 differed from project generation1. | CAD224f3302d signed17 Join setups plus retained6 region setups pass. |

ST03 Save/late-close is a tested contract-consistent boundary, not a confirmed
corruption defect: the independent observer proves local commit; the interrupted
caller reports unavailable outcome. Desktop4963c3bf8 records exact bytes, later
sync and fresh Open, with two saved files. Absent committed/possiblyCommitted
properties remain UNKNOWN, never false. Logout/revocation/work-retention
combinations remain unqualified. Existing Files acceptance is reopened only for
specific proven gaps. Rank observed consequence, not invented incidents.

User-directed close-policy follow-up: ordinary app Close should retain the
window through pending local Save confirmation; remote sync may continue after
local acknowledgement. The new candidate host guard inspects the mounted owner’s local-write phase at
request and final Discard action. CAD Save/Save As/3MF/DXF, Text and Calculator
enter that phase immediately before writing;20 coordinator controls pass. Actual
signed CAD host5/5 scenarios pass at069/224f, integrated evidence3ab74fadd. Files
now adopts18 mutation sites at854787d91 with32 callback controls. Signed Files
evidence2b98ddcce adds7 main controls and3 resolution controls: real held upload,
remove and use-server-resolution receipts block ordinary Close; reads/chooser
remain cancellable and explicit Save/Open retains exact bytes. The remaining15
mutation-site classes have callback coverage, not all-UI qualification. Other
app write paths are not adopted, so this is not all-app qualification. Forced unload, account
revocation and process failure still require truthful unknown-outcome handling.
Review shared per-window operation ownership rather than add app saving flags.

## B01 build-staging boundary

Installed trusted app inventory now has a512MiB bound shared by builder and
server admission (desktopbdbff555b), with256MiB/file and4096files/app retained.
Six cross-component boundary cases use real sparse catalog files and pure builder
admission;12 retained HTTP/cache controls pass. This is code inventory, not
resident memory or user data allowance. Optional loft availability remains
derived from explicitly staged verified assets; catalog registration alone is
insufficient. No new workflow family or deployment is implied.


Verify both pinned cache inputs before touching generated output. Compile/check
the Worker, copy native WASM to an exclusive same-directory temporary file,
verify that copy with bounded64KiB hash scratch, then atomically rename only the
generated WASM target. Remove only the owned temporary file on failure. Readonly
source cache remains immutable; repeated staging replaces the generated inode
without opening a readonly old target for writing. Malformed input preserves
prior generated bytes/modes/inodes/mtime. A failed build is not permission to
package partially generated artifacts. The atomic claim concerns WASM target
replacement, not a transaction across the whole output directory.

Evidence: CAD test/raw-smlib-repeat-build. This is build lifecycle, not a native
geometry or public app incident. The already frozen combined3d111 runtime used a
fresh first build; this later repair changes staging behavior, not its native
hashes or retrospective source identity.

## U03 transition table

Authority is a stopped lifetime plus null/one operation {controller,phase};
outward phase is derived. An aborted request does not mean recovery settled.
Blocked DOM is applied presentation with restoration obligations.

| From | Event | Guard / action | To |
|---|---|---|---|
| idle | timer / online / Retry | live; acquire one operation | checking |
| checking | valid same epoch | current owner; apply, release/schedule | idle |
| checking | valid changed epoch | current owner; await recovery | recovering |
| checking | failure | retain work; count failure; release/schedule | idle/error facts |
| recovering | success | same live owner; then accept epoch | idle |
| recovering | failure | retain prior epoch; expose usable retry | idle/disconnected |
| checking/recovering | deadline / repeat event | no second owner until settlement | unchanged |
| live | stop | invalidate owner, abort, clear timers/listeners, restore roots/remove overlay | stopped |
| stopped | late callback/reply/timer/repeated stop | no publication, work or DOM mutation | stopped |

Regression: tests/state-machine-audit-lifecycle/browser.mjs uses the actual
module, separate real Chromium and controlled loopback HTTP/recovery. No fake
browser globals, production account or shared CAD browser. Before-fix failures
are retained. Final same-assertion before3FAIL/after3PASS and five original checks
pass locally; no signed/deployed-site claim.

## CAD ownership, states and transitions

| Canonical family | Concrete owner / source | Authoritative state and legal combinations | Derived status |
| --- | --- | --- | --- |
| C01 iframe/project replacement | Desktop `apps/system/jsketcher/index.mjs`: createFrame, openFile/newProject, detach; per-window operation token | One active frame; zero/one private candidate with exact token/frame/file version; candidate publication precedes old-frame retirement. Failure before publication leaves active intact. | Staging DOM class, title/path warning and busy controls do not authorize publication. |
| C02 project generation/restore | `projectBundle.ts`; `projectManager/documentLifetime.ts`, `hostLifetime.mjs`; manager documentJob/restorePending/restoringSnapshot | Current generation+signal+service+host ownership; generation replacement revokes predecessor, even equal bytes. Restore belongs to one exact disposable empty workspace. Disposed is absorbing. | isCurrent/isRestoring/restoreUnavailable derive from owned jobs and lifetime. A host-valid callback returning true is insufficient without the post-callback ownership checks. |
| C03 accepted Craft publication | `craft/craftBundle.ts`: evaluatePipeline, intercept, preparePublication; `lstream/stateBatch.js` | Pristine-unbound; private queued/evaluating/prepared candidate; accepted full tip; accepted rewind; explicitly failed authored replay retaining old display; closed/cleanup-blocked. Epoch and owned immutable definition bind candidate. Models/history/registry/source/journal install before notifications. | isProcessing/ready/retained display are classifications of that composite state, not separate machines. A retained display is not proof that failed requested intent evaluated. |
| C04 authored history/journal | `craft/authoredEditJournal.mjs`; Craft authoredFeatureOperation/authoredEditTravel, journalHeadDefinition | Exact document/revision, immutable entries and cursor plus owned full-tip definition/source/material baselines. Tip→Undo prefix→Redo same IDs; accepted new branch truncates future; rejection preserves it. Timeline rewind is a different operation. | canUndo/canRedo require full-tip/current baselines; an empty journal is not generic timeline travel. Feature-ID high-water is allocator history and never rolls back with geometry. |
| C05 sketch/parameter/readiness transaction | `closedSketchTransitions.ts`, `sketchRevision.mjs`, `expressions/expressionsBundle.ts`; manager source/material/presentation revisions | Accepted raw source and key/namespace versions; current typed physical result/table; candidate source/facade kept private; accepted material/surface baseline. Presentation has its own document revision and preserves canonical mm/radians. Same bytes after another write remain a different revision. | Source/material/typed readiness and display controls derive from those owners. Invalid or unqualified data never becomes accepted merely because a numeric solve or tessellation exists. |
| W01 native evaluation custody | `craft/evaluationResources.mjs` and Craft accepted/lastComplete resource references | Candidate(unsealed/sealed)→accepted→detached→closed; candidate→closed on refusal/cancel. Pool reservation precedes factory allocation; close is idempotent. Cleanup-poisoned blocks new work. | Pool usage counters expose ownership; they do not establish native geometric validity or global memory limits. Detaching native handles does not create a second authored model. |
| U06 command lifetime/outcome | Desktop command registry, `apps/system/jsketcher/scoped-command.mjs`, core guarded facades | Registered/current→pending→settled; lifetime loss may yield unknown outcome. Core committed outcome, cancellation and unavailable outcome differ. Hidden-frame publication and native model publication are separate boundaries. | A timeout/window disappearance or missing committed flag alone does not prove that a submitted operation did not commit. Inspect before retry when outcome is unavailable. |

### CAD transition table

| Family / from | Event and guard | Publication / next | Required failure behavior |
| --- | --- | --- | --- |
| C01 active | New/Open captures token, active identity and baseline; privately prepare candidate | Verify current file/model/frame then swap once; retire old | Discard only owned candidate; keep accepted frame/document; committed marker if loss follows swap |
| C01 candidate | File/model/token changes or caller closes | Abort/dispose candidate | Late readiness/replay cannot replace active frame |
| C02 current generation | begin replacement | Publish successor generation+signal before aborting predecessor | Reentrant replacement cannot be adopted by its predecessor; old token stays stale |
| C02 empty disposable owner | Validated restore/replay | Install only supported fully reconstructed envelope; then restore optional metadata | Rollback receipts and revoke exact failed owner; never dispose later generation/service |
| C02 current/closed | Host abort/dispose | Terminal closed | Duplicate abort/old finalizer inert; no resurrection |
| C03 pristine-unbound | First supported creation, with no source/history/models/entries/native owners/baselines/failures | Propose current-generation journal, evaluate, atomically publish | No manufactured full-tip baseline before successful model publication |
| C03 accepted tip | Current create/edit/travel with exact source/material/services/streams | Full private replay, preflight participants, synchronous installs, then guarded notify | Command refusal/cancel retains exact accepted definition/source/model/journal; candidate owner closes |
| C03 prepared | Notification replaces document after installation | Already committed, then superseded | Report committed outcome; suppress stale later observer delivery |
| C03 raw authored replay | Evaluation fails without guarded command callback | Retain requested failed intent plus explicitly stale display | Save/readiness must refuse using retained display as current evaluated intent |
| C04 current tip | Ordinary Undo/Redo exact target/operation/baselines | Full-tip shortened/restored authored graph with same IDs | No ID allocation during travel; no hidden timeline tail serialized |
| C04 redo tail | New operation/edit accepted versus rejected | Truncate only with successful publication | Rejected candidate cannot discard Redo or move cursor |
| C04 current | Native Save then fresh Open | Save current accepted prefix; reconstruct it; reset session journal | Do not promise persisted Undo/Redo or recreate hidden future |
| C05 accepted source | Prepare supported source delta | Real Worker validation + full suffix replay where consumed, one prepared source/model/journal publication | Stale/rejected source leaves accepted bytes/history/geometry unchanged |
| C05 captured metadata revision | External validity callback accepts newer change / starts pipeline / replaces service | Recheck revision, readiness and custody **after** callback, before no-op/mutation | Stale request cannot overwrite newer metadata or commit while busy; fixed by root94cf5fa19 (source853bd4b90) |
| C05 accepted source | Nesting-changing source edit plus existing-region replacement | No qualified combined public transition in this slice | Keep it explicitly unfinished; separate rejection/reselection success is not joint repair |
| W01 candidate | Reserve/create/seal with document/lifetime/publication checks | Accept without external callback in atomic step, detach after publication, retire unused | Failed factory/candidate cleanup cannot release another owner's reservation or close accepted owner |
| W01 live owner | Document abort or cleanup failure | Close exactly once; latch cleanup poison | WR01 now covers falsey/accessor cleanup faults; every cleanup failure fences new work |
| U06 current | Caller JSON/toJSON or source reader replaces document before dispatch | Recheck entry/session/access and exact signal-derived document token; refuse before handler | No mutation in the replacement document; no revision recapture bypass |
| U06 pending New/Open | Own operation publishes a replacement document | Capture published token before callbacks; retain committed receipt | Helper adopts only its own named New/Open receipt matching current token; later replacement keeps helper stale |
| U06 metadata admission | Serialized arguments exceed 64 KiB UTF-8 | Refuse before handler with explicit metadata-contract error | File payload budget is separate; field maxima do not waive total metadata bound |
| U06 pending | Core settles while scope current | Return exact receipt/error once, remove timer/listener | Preserve known committed outcome; lifetime-loss uncertainty is not a successful retry authorization |
| U06 pending | Actual owned window closes before held genuine native reply | Cancel, terminate owned Worker; late reply inert | No command resurrection; freshly reopened saved document retains accepted intent |

Feature-ID high-water is deliberately monotonic; refusal may skip IDs. It is not
accepted geometry or another history. Native documents remain authoritative;
tessellation/export/analysis are derived and revision-bound.

## F03 durable conflict reconciliation

| From | Event / proof | Publication or retained state |
|---|---|---|
| Accepted clean file/folder | Incompatible remote kind | Persist unresolved conflict; preserve local bytes/reference |
| Unresolved file | Remote disappears or changes | Ordinary pull/deletion cannot resolve the choice; explicit existing local/server resolution remains available |
| Unresolved directory | Remote directory returns without a retained clean child | Keep parent conflict and protected subtree through repeat scans/reopen |
| Unresolved directory | Every retained clean child has matching remote kind and authenticated file SHA | Recheck complete local cohort membership/version/purpose atomically, then clear only parent conflict |
| Candidate reconciliation | Local cohort changes, lifetime changes or metadata is unknown | Refuse publication; retain authoritative intent/conflict; a fresh scan may retry |
| Ordinary nonconflicted clean row | Accepted remote absence | Existing ordinary deletion behavior is unchanged |

Protection derives from current persisted conflict owners and canonical path
segments, not a one-pass exemption or second journal. Pull and deletion both
respect it. Dirty/deleted child intent stays in the existing CAS pipeline.
Compatibility uses authenticated inventory SHA or at most64 extra metadata paths
per pass, batched at most16 paths/8192 encoded path bytes; no whole-file fallback.
Unknown/over-budget proof retains conflict, so broad large-subtree recovery
liveness is not qualified. Metadata spans a bounded observation interval, not an
atomic remote snapshot. Local parent/cohort publication is atomic. Evidence and
limits: tests/state-machine-audit-storage/PERSISTENT-COHORT-REPAIR.md.

## W02/W03 Worker transitions and settlement

| Owner / from | Event | Required transition and invariant | Qualified scope |
|---|---|---|---|
| Native Worker / new | init | Reserve initializing synchronously before awaiting native initialization | Duplicate init refuses without disturbing the first; exactly one ready |
| Native Worker / ready | supported job | Reserve busy before the first await; retain exact token/native-name custody | Same-token concurrent call refuses BUSY; first result remains disposable |
| Native Worker / busy | typed recoverable refusal or accepted result | Release only this job back to ready | Refusal then healthy retry tested with actual native geometry |
| Native Worker / initializing,busy,ready | fatal error | Send terminal error and close; late events cannot publish ready/results | Fatal-init and exact mesh-range catch controls; not general public reachability |
| Controller / initializing,ready+pending | reply, deadline, abort or close | Settle each readiness/request once; clear timers/listeners even when terminate throws |44 metadata/resource controls and3 real Chromium post-termination faults |
| Controller / closed | close again or late reply | No second termination; explicit close surfaces retained exact cleanup cause | A falsey thrown value still counts as cleanup failure |
| Controller / pending | Cancellation listener removal invokes caller code | Retain pending custody until callback returns; reentrant close settles once; hook failure retires mount, preserving known Worker failure | WR04 synthetic native/duck/cross-realm controls; success is not invented |
| Controller / ready | Cancellation registration or request transport fails | Settle exact original cause, retire mount, never post after reentrant abort/close | WR04; no orphan BUSY/promise |
| Disposable source/semantic/parameter client / queued | WebLock admission | Capture lifetime/deadline/nonce before allocation; stale admission refuses | Inspected source; not implied by controller tests |
| Disposable client / running | finish and terminate fault | Settle exactly once, retire bookkeeping, retain exact cleanup cause/original operation failure; terminal module fence | Repaired in all three imported clients at CAD625eed661;51 controls +9 genuine Chromium CPU Worker checks; no full app/native claim |
| Disposable client / queued | acquire WebLock after predecessor cleanup fails | Recheck module fence before Worker construction; refuse without allocation | Three queued-successor controls pass; one original Worker per trace |

Controller busy derives from its pending owner. Native cumulative admission/name
counters differ from live native object count; disposal does not reset the
former. Capability flags are immutable configuration. Do not collapse these
facts into a second independent busy/ready authority.

A cleanup error is terminal evidence, not proof that a Worker stopped. If
termination throws before physical release, a client must not report successful
cleanup or keep allocating replacement Workers. The integrated per-module failure
fence lasts for that imported module instance; closing/reopening an app does not
necessarily reload a shared JavaScript module. Project/hash-client cleanup coverage now includes actual whole-manager and real
validation/hash Node Workers, with existing labeled UI/storage/pipeline doubles.
Validation and every hash exchange settle once; the hash owner removes caller
and document listeners even when release fails. A weak close-once record shares
termination custody between hash abort and owner finally. It neither retains a
strong Worker inventory nor retries failed termination. Material-role assignment
now awaits successful owner cleanup, then rechecks currentness before mutation;
the former ordering was a static finding, not a demonstrated native incident.
Original3 focused failures are retained;33 repaired controls and36 retained
manager/hash/material tests pass. A full browser Save/Open replay remains pending. Supporting evidence lives in the CAD repository under
`test/state-machine-audit-workers/WORKER-CONTROLLER-FINDINGS.md` and
`test/state-machine-audit-disposable-clients/README.md` and
`test/state-machine-audit-project-workers/README.md`; this file remains the
canonical inventory. Normal parameters compute mm(4)=4; the actual sketch Worker
builds a10×5 rectangle and the semantic Worker prepares that generated source.
Fault cases throw after genuine termination or hold a genuine reply through
abort. These are component computations, not a native solid or full CAD workflow.

## F05/U06 Save acknowledgement boundary

| Observation | Meaning / required behavior |
|---|---|
| A normal host write returns its local receipt | Browser-local commit confirmed; remote synchronization is a separate outcome |
| Window lifetime is lost before caller receives the receipt | Caller outcome may be UNKNOWN; do not claim uncommitted or stale success |
| Independent test reads committed bytes before releasing held receipt | Proves that test's local commit, not what the interrupted caller knew |
| Late receipt after disposal | Must not resurrect window, baseline or command |
| Fresh ordinary Open reconstructs exact saved intent | Reconciles current stored result; inspect before retrying an unknown operation |

Frozen224f/cf979 signed test passes this boundary: width10 baseline, width17 edit,
real local commit, Close/Discard under the old policy, truthful AbortError,
unchanged bytes, subsequent sync and fresh Open at1700mm³. It delays only the
genuine receipt, with no concurrent write, account switch or cancelled filesystem
race. This does not qualify every Save/export/logout boundary. New ordinary-close
policy has5/5 actual signed CAD regressions at069/224f (tests/state-machine-audit-close),
without erasing this historical evidence. Each fixture has exact source pins;
before/after mirrors differ and neither run qualifies the later c91 storage
repair in a composed app. Four saved-native-file SHA/intent checks pass.

User-confirmed persistence policy: explicit Save is the durable boundary; Open
reads the last committed revision. Unsaved RAM edits can be lost on normal close
or a crash. Do not add shutdown autosave, recovery writes or compensating rollback
writes. “Rolled back” means reopening the last committed revision, not undoing a
save that already committed before its acknowledgement was interrupted. Normal
resource disposal remains required by the app mount contract; it does not save
or repair document content.

Crash/forced-tab-close scope: no guarantee of shutdown JavaScript execution.
Preserve complete durable revisions and reconcile which revision survived. The old/new complete-version publication
invariant remains required; a passed late-acknowledgement test is not itself a
power-loss, browser-eviction or process-crash proof. No cancelled filesystem race
or security probe is resumed to claim those results.

## U04/U05/U06 transition rules

| Owner | Transition | Invariant |
|---|---|---|
| Document operation | idle→operating(token) | set active before notifications; reentrant second begin refuses |
| Coordinator | claim path/tree | no other overlapping owner; stale release never clears new claims |
| Document operation | matching finish→idle | release only its claims; stale/repeated finish inert |
| Document operation | live→disposed | abort token, release/unregister; no resurrection |
| Public command | current→invoked | bounded inputs/lifetime; recheck after awaits |
| Public command | caller lost after possible commit | retain known commit separately; inspect unknown outcome before retry |
| Scoped command | pending→settled/lost | exactly once; release timer/listener even if iframe disappears |

The local-write phase is owned by the existing operation record, not a new
saving flag. `token.enterLocalWrite()` reserves it before notifications and
rechecks owner/lifetime afterward. A false result forbids starting the write.
The phase remains through the returned local receipt and baseline publication,
then `finish()` retires it. Error paths also finish, so retry is available.
Preparation, read/native work, peer contention and background server sync do not
hold this close protection. Ordinary Close refuses while the live mounted owner
is in local-write; it does not queue a future close that could discard later
edits. Final Discard rechecks ownership after its dialog. Forced disposal still
revokes work and can leave unknown outcomes; it does not masquerade as an
ordinary successful Close. Adoption by other app writers remains queued.

Controls are advisory derivatives. Writes still claim/check currentness at the
actual boundary; correct disabled styling does not prove serialization.

## Shared repair principles

Cancellation requested is not work settled: retain an owner until settlement and
revoke late continuations at lifetime end. Terminal state and cleanup must agree:
settle promises and retire bookkeeping even when cleanup throws. Error presence
is not JavaScript truthiness: preserve the first cause in an unambiguous record.
Historical scan progress is not current remote proof. External callbacks can
reenter: recheck revision/readiness/custody after the last callback, before no-op
or publication. A missing commit marker means unknown, not false.

Scheduling caches may remain when asynchronous reads make eager derivation
impractical. Document authority, revision/invalidation and coverage; a hint cannot
silently become proof of current data, permission or accepted geometry.

## Remaining review and maintenance

For each family finish: source/owner, authoritative versus derived fields, legal
combinations, guarded transition table, invariants/publication point, retry and
idempotency, reentrancy/concurrency, actual integration/regression scope, confirmed
bugs and hypotheses. Unexpanded tables remain queued work. Three audit lanes
feed this file; do not fork canonical inventories.

Each repair retains a failing reproducer, tests the real boundary, runs related
retained controls, updates this inventory/queue and records applicable pins.
Components alone do not sign off a signed app workflow. The cancelled filesystem
race/security probes remain cancelled.


## STEP composition and owned-solid inspection —2026-11-07

This supplements existing W02/W03/WR04–WR06; it adds no authoritative busy flag.

| Issue | Confirmed defect and scope | Repair / current evidence |
|---|---|---|
| NI01 | Nonempty owned solids could fail legacy analytic inspection above32 faces, despite valid Native owned facts. | CAD8c28a9a4e uses the strict owned V2 envelope for facts and summary, crosschecked with topology census. Genuine32/64/128-hole component results and retained old cohorts pass. Full authored app proof remains pending. |
| STP01 / W02 | A null sentinel and truthiness discarded falsey exceptions; error accessors could replace the original write outcome. | Desktopb2a2e60a9/d41bbe648 use a tagged failure record and bounded descriptor-only reporting. Exact cause (including undefined), primary/finish precedence, confirmed/potential commit distinctions and no automatic retry are regression-tested. |
| STP02 / W02+W03 | Reusing public readiness as the pending guard rejected the controller's own exclusive Core read because that read truthfully reports busy. | Host pending guard checks captured lifetime and token. Core checks immutable source during evaluation; host checks both revisions before/after preparation and prewrite. Source-backed before failure and repaired component control retained. |
| SEL01 / W03 | New-part selected-profile discovery ignored explicit runtime revision and chose the old default, preventing ordinary STEP-enabled plate authoring. | Optional exact build request plus trusted staged inventory; no persisted selection flag or backend migration. Actual Worker discovery and unavailable/mixed/withdrawn/lifetime controls pass. Native creation remains for combined app proof. |

STEP transition contract: capture current source → preparation lease → body/path
choice → target claim and no-overwrite check → fresh read-only kernel replay →
artifact/revision recheck → mandatory local-write admission → pending or confirmed
browser receipt → finish. Cancellation before local write produces no claimed
commit; failures after write admission explicitly retain possibly-committed or
confirmed outcome. Export does not modify the native project's save baseline,
path, title or dirty state. Crash/forced closure does not run cleanup or promise
to rescue unsaved edits. A browser commit is distinct from server synchronization.

## Legacy export and parent-command settlement repair —2026-11-07

Related families remain W02/W03; this does not add a second document coordinator.

| Issue | Confirmed counterexample | Current repair/evidence |
|---|---|---|
| STP03/W02 | Actual extracted3MF/DXF routes lose falsey causes or invoke error getters, forget known commit after finish/notice faults, and accept malformed browser receipts. | Desktop ea1a0c190 shares descriptor-only formatting/outcome settlement with STEP; null/no-write→pending→validated committed.27new +100retained Node controlsPASS, synthetic artifact/storage only. Signed normal f714/5b export smoke also passes4exports, native Save/freshOpen, actual My files/server bytes and independent3MF/DXF oracles; no injected browser faults or generic3MF claim. |
| WR07/W02 | Shared parent helper resolves rejected falsey values as success; synchronous registration cancellation starts an orphan interval after settlement. | Rejection/fulfillment use separate discriminants; input observed before registration, no timer after reentrant completion, intrinsic listener removal fallback and explicit opaque cleanup failure. Source-backed before2FAIL/1PASS; after rejection/lifetime/cleanup controlsPASS. |

| State / event | Required transition and invariant |
|---|---|
| Preparation / failure or UI cancellation | No write claim; release coordinator; preserve exact arbitrary cause. |
| Local-write admission / reentrant lifetime loss | Recheck before storage invocation; no write after invalidation. |
| Write submitted / throw or malformed receipt | Pending/possiblyCommitted, exact cause; no automatic retry. |
| Valid browser receipt / later notice, finish or lifetime failure | Committed stays committed; never expose old-account path; server sync remains independent. |
| Promise rejected / any value including undefined | Reject that value; never treat it as successful fulfillment. |
| Listener setup reenters cancellation | Settle once; remove attempted listener; never allocate a later timer. |
| Listener cleanup cannot be confirmed | Attempt all cleanup, retain primary cause and known commit marker; report cleanupUnconfirmed. |

The native-project Save host catch has a similar source pattern and remains an
open integration follow-up; export component tests do not qualify that route.
No filesystem race/security test, private state copy or public deployment occurs.
