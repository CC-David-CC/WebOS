# Signed Collinear — scoped end-to-end PASS

New isolated fixture20396 uses desktop adapter source `ac85b0fcb`, actual CAD
runtime `724178adc` and core evidence checkpoint `aa68f2e8f`. Exact app, Worker,
planner, host/catalog and file hashes are in `signed-r1-receipt.json`.
No private account state was copied from another fixture.

Public geometry commands build a100×50mm rectangle, four construction segments,
a Point and a real20mm Worker extrusion. A second publicly authored plane holds
two10mm horizontal supports constrained5mm apart. There are no native/formula
seeds, private authoring helpers, fake successful solver outputs or geometry UI
substitutes. Passive native reads are test-only independent oracles.

The command is exactly:

```js
apply-closed-sketch-line-relation {
  revision, faceId, kind: 'collinear', ids: [segmentA, segmentB]
}
```

Discovery uses `inspect-closed-sketches` and `inspect-closed-sketch` with actual
native IDs. The actual backend relation concerns infinite supporting lines and
requires both live directions to remain valid. Its full contract/transport proof
is in the CAD repository's `test/headless-line-relations/README.md` at `aa68`.

| Actual signed host control | Result |
| --- | --- |
| Collinear applied to consumed rectangle construction segments | PASS: independent supporting-line measurements; actual100×50×20 plate unchanged |
| Same pair reversed | PASS: changed:false/authoredUndo:false, exact native/stream/geometry/journal no-op |
| Undo/redo relation | PASS: exact prior/accepted native project snapshot |
| Contradictory separated supports | PASS: genuine solve refused and prior state preserved |
| Stale/missing/wrong-type/cross-face/same-ID/unqualified kind | PASS: refusal and preservation |
| Consumed signed X=10, Y=0 and live projected distance=20 | PASS: independent local endpoint measurements, same plate |
| Real successful Worker candidate held during File→Open | PASS: actual themed unsaved confirmation, cancellation then Keep editing |
| Original late event released untouched; next public apply | PASS: late event inert, next operation accepted |
| Real successful candidate held during visible Close | PASS: cancellation/termination and saved file unchanged |
| Normal public Save/browser-server sync | PASS: matching hashes, native constraint families and exact source retained |
| Other synthetic account | PASS: owning server file denied403/404 |
| Fresh login and actual Files→Open | PASS: exact native sketches and actual body geometry; relation/projection measured again |

The seven adapter boundary tests pass separately. Actual core geometry is
established by this signed run, not the boundary stubs. Refusal comparisons permit
only opaque inspected/journal revision changes where replay refreshes them;
authored bytes, streams, geometry and history remain compared. Duplicate/stale
controls compare the complete captured state. Undo/redo compare exact native
snapshots while allowing ordinary successful-travel stream revisions.

Lifecycle interception retains one successful message from the actual production
Worker task `sketch-transition-line-relation`. It never manufactures a successful
reply, changes its bytes or calls a private publication helper. Normal host Open
and Close invalidate the operation's real lifetime. Public caller AbortSignal or
second-command implicit preemption is not claimed.

Run against a fresh loopback signed fixture with the matching reviewed runtime:

```sh
CODI_TEST_URL=http://127.0.0.1:20396/ CODI_TEST_CDP=http://127.0.0.1:19329/ \
node test/agent-cad-corpus/line-relations/signed.test.mjs
node --test tests/jsketcher-closed-sketch-commands.test.mjs
```

This lane reuses generic login/Files helpers from the earlier numeric-expression
lane and ID/measurement helpers from signed-distance; dependency hashes are in
the receipt. Each run creates its own synthetic accounts, closes only its own
browser contexts and disconnects from the shared Chromium instance. Prior
fixtures/public sites stay unchanged. Raw log backup is
`/mnt/data10tb/codi-collinear-signed-evidence-20261105/`.

Scope excludes the old active-editor geometry UI, full CAD1/Gate1, general DOF,
arbitrary generated/reference/stage/typed cases, every kernel and Files reaudit.
There is no public deployment. Git contains source/tests/receipts/notes only,
without account DBs, keys, dependencies or generated runtime output.

## Proposed next bounded core: independent-axis symmetry

Reuse the same method with kind:'axis-symmetry' and three inspected IDs:
`[pointP,pointQ,liveAxisSegment]`. Extend only the closed enum/count and existing
shared admission; retain the current AxisSymmetry equations. Success identifies
typeId:'AxisSymmetry'. Existing unordered point pair with the same axis remains
an exact no-op, while a new relation authors one native row. Distinct IDs may
legitimately occupy the same point on the axis; only the axis direction must
remain nondegenerate. Reflection is about the infinite live line.

Before advertising it, qualify actual horizontal/oblique/reversed axes, live-axis
edits, coincident-on-axis points, contradiction and malformed/stale targets,
exact travel/native reopen and consumed construction geometry retaining the plate.
Keep the same whitelisted exact-source verifier and finite-geometry/metadata
tampering controls, then repeat signed host lifetime/persistence/account proof.
No new solver math, document format, import path, AI provider or human UI is needed.
The current public adapter deliberately refuses this kind until that work passes.
