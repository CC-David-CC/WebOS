# Workflow state machines and invariants

Canonical maintained inventory for the current WebOS Files/CAD foundation.
Update this file and WEBOS-WORK-QUEUES.md when a state, guard, transition, defect,
regression or integration status changes. Audit receipts are evidence, not
competing specifications. This is a first pass, not exhaustive safety proof.
Third-party editor/kernel internals, games and future physics are outside this
pass unless they affect the shared workflow.

## Counting and representation

Currently **20 identified workflow families**: 15 implicit, three hybrid, one
explicit, one awaiting classification. These are logical families with named
owners, not 20 independent minimized automata. Nested protocols may be split or
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
| U04 | Per-window DocumentOperations | I | idle → operating(token) → idle; live → disposed | Stale finish cannot finish new work; busy derived; 16 controls mapped. |
| U05 | Session document claims | I | unclaimed → claimed(path/tree,owner) → released | No overlapping owners, including reentrant notifications. |
| U06 | Command registry/scoped settlement | I | registered/current → pending → settled/lifetime-lost | No stale result payload; known commit outcome retained; ST03 bounded Save/Close contract passes. |
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
| W03 | Source/semantic/project/hash clients | ? | queued → running → reply/refuse/cancel → settled/disposed | Late replies never publish; client families being reconciled. |

Derived status is not another machine unless independently stored authority can
drift. Validity/representation/qualification are revision-bound classifications,
not automatically lifecycle machines. Unreviewed rows are not proof of safety.

## Confirmed issues, grouped by impact

| Group | Impact | Confirmed behavior | Current repair/evidence |
|---|---|---|---|
| ST01/F02 | P1 silent stale data | Unrelated failing file retains checked progress; healthy remote changes are skipped, even on a pass reporting completion. | Fresh/continuation repair integrated;10 focused controls, retained suite and8 real IDB/OPFS browser scenarios pass; combined signed check pending. |
| LR01/U03 | P1 unusable desktop | Late stopped recovery re-blocks roots without overlay; deadline admits overlapping recovery; failed recovery strands disabled Retry. | Owned-operation repair passes3 real Chromium regressions and5 retained checks; pins in tests/state-machine-audit-lifecycle/evidence/verification.json. |
| ST02/F03 | P1 unresolved-side logical loss | A conflicted directory can lose its child reference when only the remote directory returns; a clean conflicted file loses its reference when remote disappears. | Both real IDB/OPFS traces fail on frozen b911, retained in desktop b95b646c7. Earlier candidate is not integrated. Durable protection/reconciliation repair in progress; physical byte erasure and public incidents are not established. |
| WR01/W01 | P2 cleanup contract | Falsey cleanup throws fail to latch; throwing close accessor strands a reservation. | Injected faults, not observed kernel incidents; repair integrated at CAD061551b93;22 focused/retained resource controls pass. |
| WR02/W02 | P2 direct Worker boundary | Duplicate initialization stalls; concurrent same-token work creates two native names but retains only one token. | Genuine Worker reproduction. Normal controller rejects concurrency; gate repair integrated at CAD920dc619d. Six direct-Worker controls plus new/retained native corpus pass; combined app replay pending. |
| MG01/C05 | P2 service reentrancy | Final caller guard can accept a newer display edit/start a pipeline, then the old setter commits. | Repair integrated at CAD94cf5fa19;5 regressions +14 retained manager controls pass. No public incident/new signed-build claim. |
| WR03/W02+W03 | P2 termination-fault contract | Throwing Worker termination strands readiness/pending promises; the same pattern occurs in three disposable clients. | Controller repair integrated at CAD334ceba19;44 metadata/resource controls and3 actual Chromium post-termination injected faults pass. Three client recurrences reproduced; repair and allocation fence in progress. No ordinary termination incident claim. |
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
local acknowledgement. Current host treats CAD busy as dirty and permits
Discard, so this stricter behavior is not yet implemented. Forced unload, account
revocation and process failure still require truthful unknown-outcome handling.
Review shared per-window operation ownership rather than add app saving flags.

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
| U06 pending | Core settles while scope current | Return exact receipt/error once, remove timer/listener | Preserve known committed outcome; lifetime-loss uncertainty is not a successful retry authorization |
| U06 pending | Actual owned window closes before held genuine native reply | Cancel, terminate owned Worker; late reply inert | No command resurrection; freshly reopened saved document retains accepted intent |

Feature-ID high-water is deliberately monotonic; refusal may skip IDs. It is not
accepted geometry or another history. Native documents remain authoritative;
tessellation/export/analysis are derived and revision-bound.

## W02/W03 Worker transitions and settlement

| Owner / from | Event | Required transition and invariant | Qualified scope |
|---|---|---|---|
| Native Worker / new | init | Reserve initializing synchronously before awaiting native initialization | Duplicate init refuses without disturbing the first; exactly one ready |
| Native Worker / ready | supported job | Reserve busy before the first await; retain exact token/native-name custody | Same-token concurrent call refuses BUSY; first result remains disposable |
| Native Worker / busy | typed recoverable refusal or accepted result | Release only this job back to ready | Refusal then healthy retry tested with actual native geometry |
| Native Worker / initializing,busy,ready | fatal error | Send terminal error and close; late events cannot publish ready/results | Fatal-init and exact mesh-range catch controls; not general public reachability |
| Controller / initializing,ready+pending | reply, deadline, abort or close | Settle each readiness/request once; clear timers/listeners even when terminate throws |44 metadata/resource controls and3 real Chromium post-termination faults |
| Controller / closed | close again or late reply | No second termination; explicit close surfaces retained exact cleanup cause | A falsey thrown value still counts as cleanup failure |
| Disposable source/semantic/parameter client / queued | WebLock admission | Capture lifetime/deadline/nonce before allocation; stale admission refuses | Inspected source; not implied by controller tests |
| Disposable client / running | finish and terminate fault | Current code can strand promise/bookkeeping; repair must settle and fence later allocation | Reproduced in all three actual imported clients with injected transport; no geometry/math success claim |

Controller busy derives from its pending owner. Native cumulative admission/name
counters differ from live native object count; disposal does not reset the
former. Capability flags are immutable configuration. Do not collapse these
facts into a second independent busy/ready authority.

A cleanup error is terminal evidence, not proof that a Worker stopped. If
termination throws before physical release, a client must not report successful
cleanup or keep allocating replacement Workers. The proposed per-module failure
fence must describe its real lifetime; closing/reopening an app does not
necessarily reload a shared JavaScript module. Project/hash-client coverage is
still pending. Supporting evidence lives in the CAD repository under
`test/state-machine-audit-workers/WORKER-CONTROLLER-FINDINGS.md`; this file remains
the canonical inventory.

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
policy needs its own regression and must not erase this historical evidence.

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
