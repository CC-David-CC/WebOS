# Workflow state machines and invariants

Canonical maintained inventory for the current WebOS Files/CAD foundation.
Update this file and WEBOS-WORK-QUEUES.md when a state, guard, transition, defect,
regression or integration status changes. Audit receipts are evidence, not
competing specifications. This is a first pass, not exhaustive safety proof.
Third-party editor/kernel internals, games and future physics are outside this
pass unless they affect the shared workflow.

## Counting and representation

Currently **20 identified workflow families**: 14 implicit, two hybrid, one
explicit, three awaiting classification. These are logical families with named
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
| U06 | Command registry/scoped settlement | I | registered/current → pending → settled/lifetime-lost | No stale result payload; known commit outcome retained; Save audit open. |
| F01 | Mirror row, mirror.mjs | I | clean/dirty/tombstone/conflicted/moving → sync/conflict | Bytes, remote base and intent agree; combinations under review. |
| F02 | Mirror scan/retry | I | fresh → running → continuation/backoff → completed/failed | Retained progress is not fresh verification; ST01. |
| F03 | File/folder conflict | I | detected → resolution prepared → CAS/publication → resolved | Preserve both sides until accepted resolution; ST02. |
| F04 | Durable rename recovery | I | intent → remote/local steps → complete; interruption → recover | Preserve exact identities/versions; evidence mapped. |
| F05 | App Save | I | capture → claim → write → local commit → baseline update → sync | Later edits stay dirty; local commit differs from remote sync. |
| F06 | Verified content/OPFS leases | ? | stage → verify → publish; lease → copy → release | Published immutable generation stays leased through actual copy. |
| C01 | CAD iframe/project replacement | I | active → candidate load/restore → verified swap → retire old | Failed candidate retains active project; bounded New/Open proof. |
| C02 | CAD project generation/restore | I | empty/current → restoring → ready; superseded → reject | Document/host lifetime remains current across awaits. |
| C03 | Craft model publication | I | pristine-unbound → candidate → accepted tip; failure/rewind/close | Model/history/source/material/journal publish together; CG01. |
| C04 | Authored journal | I | tip ↔ Undo/Redo; accepted branch truncates redo; New resets | Authored intent only; mixed creation/edit native proofs pass. |
| C05 | Sketch/parameter transaction | ? | begin → edit/solve → accept/reject; interruption → recover | Equation validity, authored source and retained output differ. |
| W01 | Evaluation owner, evaluationResources | E | candidate → accepted → detached → closed; candidate → closed | Reservation/cleanup follows ownership; WR01. |
| W02 | Engine controller/Worker | H | initializing → ready (+ pending request) → closed | One request owner and bound replies; direct Worker gate audit. |
| W03 | Source/semantic/project/hash clients | ? | queued → running → reply/refuse/cancel → settled/disposed | Late replies never publish; client families being reconciled. |

Derived status is not another machine unless independently stored authority can
drift. Validity/representation/qualification are revision-bound classifications,
not automatically lifecycle machines. Unreviewed rows are not proof of safety.

## Confirmed issues, grouped by impact

| Group | Impact | Confirmed behavior | Current repair/evidence |
|---|---|---|---|
| ST01/F02 | P1 silent stale data | Unrelated failing file retains checked progress; healthy remote changes are skipped, even on a pass reporting completion. | Real production mirror/Chromium IDB reproduction; explicit fresh/continuation fix under verification. |
| LR01/U03 | P1 unusable desktop | Late stopped recovery re-blocks roots without overlay; deadline admits overlapping recovery; failed recovery strands disabled Retry. | Owned-operation repair passes3 real Chromium regressions and5 retained checks; pins in tests/state-machine-audit-lifecycle/evidence/verification.json. |
| ST02/F03 | P2 recovery dead end | Directory/file conflict has no resolve/delete/move exit; restoring remote type still leaves conflict. | Real mirror/IDB reproduction; separate safe resolution proposal, no content discarded. |
| WR01/W01 | P2 cleanup contract | Falsey cleanup throws fail to latch; throwing close accessor strands a reservation. | Injected faults, not observed kernel incidents; product3c969bf68 passes22 controls, root integration pending. |
| WR02/W02 | P2 direct Worker boundary | Duplicate initialization stalls; concurrent same-token work creates two native names but retains only one token. | Genuine Worker reproduction. Normal controller rejects concurrency; Worker-side gate repair underway. |
| CG01/C03 | P1 regression, repaired | First creation required evaluated metadata; journal generation0 differed from project generation1. | CAD224f3302d signed17 Join setups plus retained6 region setups pass. |

Save/late-close outcome markers and logout/revocation/work-retention combinations
remain hypotheses until reproduced. Existing Files acceptance is reopened only
for specific proven gaps. Rank observed consequence, not invented incidents.

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

## C03/C04 transition table

Pristine-unbound means no history, source keys, models, entries, native owners or
accepted baseline. It is different from stale nonempty work. Do not manufacture
ready state by copying flags before the first evaluation.

| From | Event | Guard / atomic boundary | To |
|---|---|---|---|
| pristine-unbound | first create | capture empty state; propose current-generation journal; evaluate privately | candidate |
| accepted tip | create/edit/travel | current document/source/material/streams and exact target; full replay | candidate |
| candidate | success | native/result/publication checks; install model/history/journal together | accepted tip |
| candidate | refusal/cancel/stale | close candidate; retain accepted source/history/model/journal | prior accepted/pristine |
| accepted tip | Undo/Redo | exact journal/owned definition; retain authored IDs | tip with moved cursor |
| redo tail | new accepted edit | truncate only at successful publication | new tip |
| live | New/Open/close | new generation or terminal disposal; old callbacks cannot publish | new document/closed |

Feature-ID high-water is deliberately monotonic; refusal may skip IDs. It is not
accepted geometry or another history. Native documents remain authoritative;
tessellation/export/analysis are derived and revision-bound.

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
