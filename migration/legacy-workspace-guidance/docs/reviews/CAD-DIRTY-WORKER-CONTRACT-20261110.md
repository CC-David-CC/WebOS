# CAD saved-content comparison: implementation contract (SOURCE PLAN ONLY)

Status: source investigation and bounded implementation plan. No product fix,
build, test, runtime deployment, memory measurement or qualification is claimed.
Parent integration may use this contract to split a coherent Core/Host packet.

## Confirmed cost and the tempting incorrect replacement

Host `apps/system/jsketcher/index.mjs` currently calls `snapshotCurrentProject`
and JSON.stringify for close checks, New/Open/exports, and native-save baseline
capture. Read-only `inspect` additionally JSON-clones the model and parses every
sketch, then `inspect-state.mjs` parses and serializes the complete baseline.
Core `projectManagerBundle.ts:captureCurrentProject` already serializes/parses
captureModel and parses each sketch; `capturedManufacturingJob` can then clone
the detached envelope again. Native archive preparation avoids that complete
JSON snapshot, but Host calls it before native encoding anyway.

`inspectDocumentRevision` is an opaque identity of the current mutation epoch.
It is appropriate for request fencing, not content equality: Undo returning to
a saved definition can have a different token. A revision-only dirty check
would regress exact undo-to-saved semantics. A hash match alone also must not
be promoted to exact content equality. Failed/stale inspection is not clean.

## Concrete Core boundary

Add a **document-owned saved-content comparison owner**, separate from mutation
revision and separate from the archive codec's current encoding operation.
The manager owns the Worker, baseline and private preparation capabilities.
The Host cannot submit serialized replacement content or public proof flags.

Suggested private methods (names illustrative until implementation review):

- `prepareHostContentBaseline(options)` returns a privately branded capture,
  source revision, `isCurrent`, and `release`. Preparation captures the same
  source as the forthcoming native save, not an unrelated second snapshot.
- `acceptHostContentBaseline(capture)` atomically adopts the exact captured
  content after a confirmed Files write (or verified successful Open/New),
  regardless of whether newer authored edits exist. It increments a private
  baseline generation. It does not adopt the then-current model by accident.
- `compareHostSavedContent(options)` returns `{revision, baselineGeneration,
  equal}` only after exact Worker comparison and currentness checks. It has
  no model-edit authority. Superseded replies cannot update a Host cache.
- `inspectHostSavedContent()` returns one bounded synchronous observation:
  current revision, baseline generation, and `equal | different | unknown`.
  `unknown` schedules/awaits comparison where appropriate, never means clean.

Use the existing `streamNativeArchiveSource` credit/ack transport design
(64 KiB token credit; cooperative yields; bounded node/depth/entry/128 MiB
limits). Refactor its source-capture half for reuse rather than calling
`snapshotCurrentProject` or structuredClone on the complete document. Guard
manager/project/craft/storage identity, generation, namespace revision,
history, expression revisions, material/surface/presentation/drawing state,
source counters, host validity and AbortSignals before and after every credit.
Capture counters via their known schema; never walk arbitrary class objects.
Existing serializers that clone surfacing must be audited separately and
must not be silently called bounded merely because transport is bounded.

Worker equality must preserve the existing authored-envelope comparison:
model, sketches in sorted namespace order, manufacturing, presentation and
linked drawings. Sketch raw text is parsed in the Worker; whitespace/property
serialization follows the existing envelope serializer. Derived tessellation,
solver execution counts, runtime epochs, paths and viewport do not enter the
saved source. Preserve current JSON number/undefined-optional semantics; do
not round coordinates or add a geometric tolerance. Preserve relevant object
order until an explicit schema/version change authorizes canonical ordering.

Maintain an exact baseline stream/rope in the Worker with explicit aggregate
bounds. Compare exact tokens/UTF-8 bytes; hashes may filter unequal inputs but
matching digests alone cannot establish equality. Retain at most one active
baseline plus one bounded pending save capture, not a copy per inspection.
Avoid producing ZIP/compressing/re-hashing an archive solely to compare dirty
state. Both frames own separate baselines; a hidden Open candidate never
replaces the active baseline before the existing successful publication.

## Host changes, after the Core interface exists

1. Replace `snapshot`/`unchanged` guards with opaque captured-currentness
   guards for operation fencing. Keep these separate from saved equality.
   A failed guard preserves existing stale/unknown outcomes.
2. Make command `inspect` await the private exact comparison, derive dirty
   from its current answer, and retain its existing final identity checks.
   Remove its whole-model/sketch JSON clone and `inspectedProjectIsDirty`
   dependency. Its bounded operation summary may read current accepted
   history; it must not create an independent editable model copy.
3. `state.hasChanges` remains synchronous. Return false only for an exact
   cached equal result whose revision AND baseline generation match now;
   return true for different/unknown/busy/unavailable. Asynchronously refresh
   unknown state in a coalesced owner. New/Open and actual close confirmation
   should await comparison before prompting where the host API permits it;
   conservative prompting on an unknown synchronous guard is documented,
   never silent discard. Keep the existing close/save coordination lease.
4. For Save capture the baseline with the same prepared source. Adopt only
   after the Files write result is known and associated path/version is
   published. During the write newer edits can exist; they remain dirty.
   Archive rebase is an optimization: rebase failure must not undo a known
   committed write or replace its saved-content baseline with current source.
5. Successful Open/New prepare a candidate baseline before publication; a
   cancelled/rejected candidate releases it. Existing active content and
   baseline remain authoritative until atomic replacement. Dispose releases
   all Worker/baseline/capture ownership. Unknown writes retain custody.
6. Remove the legacy full JSON save path only under the separately approved
   native-format contract. Otherwise move its encoding to the same Worker;
   do not call it solved while legacy Save still stringifies on Main.

## Transition rules and race obligations

| Current state/event | Result and invariant |
|---|---|
| No baseline / document unavailable | Unknown, conservative dirty; cannot claim clean |
| Baseline accepted for capture R | Saved source is R even if current revision has advanced |
| Revision or baseline generation changes | Old comparison loses authority immediately |
| Comparison completes with current identities | Publish exact equal/different observation |
| Comparison completes stale, cancelled or failed | No cache publication; release pending work |
| Undo reaches saved authored content | A fresh exact comparison may establish clean |
| Same-revision repeated inspect | Reuse current exact observation without source traversal |
| Rejected model operation | No baseline change; accepted source remains authoritative |
| Save commits then model edits | Baseline remains saved capture; current document dirty |
| Open/New rejected/cancelled | Existing frame, baseline, path and document token retained |
| Worker close fails | Fence comparison/save owner; report error, never clean |
| Forced tab crash | No cleanup guarantee; reopen last confirmed saved file |

## Implementation grouping and one final acceptance packet

A. Core capture extraction + exact Worker stream comparator + private capability
owner and lifetime integration. Review capture equivalence against the current
snapshot envelope before deleting any callers.
B. Host baseline adoption/currentness/inspect/close integration, including
legacy format disposition. Update native archive preparation so its capture
can be reused instead of collecting the source a second time.
C. Prepare one grouped E2E packet and independent reader, then build once.
No test/build was run during this source-plan investigation.

The whole workflow must cover fresh clean -> edit -> Save -> edit -> Undo back
to saved -> Redo; material, display-unit, drawing, expression and sketch-source
changes; save of an earlier revision while a newer edit remains; cancelled
New/Open; exact native save/reopen; stale comparison after baseline replacement;
repeated inspect without reserialization; and document/window disposal.
Use ordinary isolated owned account flows, not the cancelled filesystem-race
or foreign-account probes. Include one representative large project with
Main-task gaps, peak/retained memory, credits and cleanup measured. Independent
readback checks the actual saved definition. A compile or a cache hit alone
cannot establish correct dirty state, responsiveness or bounded memory.

## Why this is a coordinated packet

A Host-only cache of mutation revisions cannot establish content equality.
A Worker receiving `snapshotCurrentProject()` has merely moved the final
comparison after the costly Main clone. Encoding full ZIPs after every edit
would move unnecessary work into a Worker without removing it. The Core
capture authority and Host baseline publication must therefore land together.

## Implementation status update

Source packet now exists across Core branch fix/cad-saved-content-worker-20261110
and this Host branch. Host index no longer serializes/clones full documents for
close/inspect/operation fences/native save. Core owns exact baseline comparison
and both native/legacy JSON encoding. Async inspect and idle refresh establish
content equality; synchronous close remains conservative for unknown or drafts.
Save adopts its captured source after a confirmed Files write, before optional
rebase. Hidden New/Open candidates establish their own baseline before atomic
publication. Implementation is source-only: independent review, build and
one grouped E2E/resource packet remain pending. This supersedes only the earlier
implementation-pending status, not its acceptance obligations.
