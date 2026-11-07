# Signed strict Join corpus

R3 prepared against frozen CAD `224f3302d421957a9390879034102660f81d6ac0` and desktop `cf97976d965f0b57689f1d2a8c87a060d0a49369`. Only registered public commands author geometry/history. Read-only live intent, source, counters, material/presentation metadata, assembly constraints, measured model outputs and bounded detached Float32 display copies provide observations. No private source writes, raw native seeds, model replacement, fake UI or fabricated successful replies. Every fresh signed setup verifies all core asset hashes and the mounted outer bundle first.

Seventeen setups: eight each for OCC and SMLib plus one explicitly unqualified Manifold Join control.

- Overlap: 10 mm cubes at x=0 and x=5 Join to 1,500 mm³, bounds [0,0,0]..[15,10,10]. FIRST box Undo reaches truly empty history/output and Redo retains its original ID. Join Undo restores both consumed operands; Redo retains result ID. Upstream first-box width20 gives 2,000 mm³; width4 disconnects the operands and must refuse. Mixed normal travel covers UndoEdit→UndoJoin→UndoBoxB→UndoBoxA, then all four Redo. Save/sync/fresh Open resets session Undo/Redo; upstream reedit width21 gives 2,100 mm³, with ordinary Undo/Redo and another Save/Open.
- Face contact: second cube at x=10 Join gives 2,000 mm³, one native geometric solid, stable creation travel and saved intent.
- Disjoint, edge contact and point contact: origins [20,0,0], [10,10,0], [10,10,10]. OCC must return `JOIN_MULTIPLE_SOLIDS`; SMLib must return `JOIN_MULTIPLE_SOLIDS` for disjoint/point contact and `JOIN_NONMANIFOLD` for edge contact. The point distinction is confirmed separately by a raw union on the same inputs: validLevel0/2 and manifoldPredicate true, two native material regions, no void, volume2,000 mm³ and bounds [0,0,0]..[20,20,20]; ordinary Undo restores both inputs. This is a raw multi-domain result, never successful one-solid Join. Unexpected codes are failures, including generic `ENGINE_FAILURE`.
- Cavity: outer10³ minus inner2³ at [4,4,4], Join a [2,10,10] box at [9,0,0]. Volume 1,000−8+200−100=1,092 mm³; bounds [0,0,0]..[11,10,10]. OCC must show one solid/two boundary shells; SMLib must show one material region/one void with valid manifold native evidence. Detached display parity verifies [5,5,5] remains empty and the extension contains material. Creation Undo/Redo and native Save/Open retain the cavity.
- Reversed overlap and reversed hollow/cavity Join are separate actual setups for both engines. Measures stay unchanged; saved authored operand order remains distinct. A kernel failure is retained as a real scoped failure.
- Manifold must refuse Join with `JOIN_UNQUALIFIED`, preserving both inputs and journal. A subsequent explicitly requested raw union gives 1,500 mm³ and supports normal creation Undo/Redo, native Save/Open and upstream reedit. This is never reported as qualified Manifold Join.

Axis-aligned numerical controls use absolute 1e-6 mm³ volume and 1e-7 mm AABB tolerances. These test literal-box arithmetic; they do not override SMLib's declared native-relative-0.001 measurement quality. Native evidence and detached display parity remain distinct. A cavity is allowed to have two boundary shells; shell/component count is never substituted for solid connectivity proof.

Refusals compare every captured accepted field and mesh exactly, excluding opaque inspection revisions and the separately reported feature-ID high-water alone. The high-water must remain monotonic and may reserve a skipped ID. Normal history travel compares authored/model/source/material state independently of the expected journal cursor and retained ID high-water. Fresh Open additionally ignores only the document-bound material inspection token; all material assignments/metadata, native intent, runtime, measured values and display bytes remain compared. No global source/model snapshot helper writes are used. Session Undo and Redo reset on Open.

Root owns the fixture and cleanup; the runner owns only fresh contexts and disconnects without closing shared Chrome. Native files in this frozen build remain `.jsketcher.json`; no ZIP or hosting change is assumed. This is a bounded strict Join/shared-history qualification, not full E16 or Gate1.

R3 preserves [R2’s exact classification mismatch](FAILURE-R2.md) and applies only the root-approved point-contact expectation correction plus the separate native raw-union/Undo diagnostic. [R3 comparison proof](R3-PREPARATION.json) reverses those exact changes to recover the byte-identical R2 driver. All other assertions, harness and oracle remain unchanged.

R1 found the genuine pristine first-box creation blocker; its exact evidence remains in [FAILURE-R1.md](FAILURE-R1.md). R2 changes only the expected CAD source pin. [R2 preparation](R2-PREPARATION.json) verifies the executing driver is byte-identical to R1 after that single source-string replacement; harness and geometry oracle hashes are unchanged. That R2 checkpoint was executed and its failure is preserved; R3 uses the same frozen product without rebuilding. Optional revolve changes in this candidate are outside this corpus.

After root supplies and authorizes `STRICT_JOIN_PINS` and `STRICT_JOIN_FIXTURE`:

```sh
CODI_SIGNED_PINS="$STRICT_JOIN_PINS" CODI_EVIDENCE=/tmp/codi-strict-join-proof-r3 CODI_TEST_URL="$STRICT_JOIN_FIXTURE" CODI_TEST_CDP=http://127.0.0.1:19329 PUPPETEER_CORE_PATH=/tmp/codi-occt-release-control/node_modules/puppeteer-core /tmp/codi-files-move-node/bin/node test/agent-cad-corpus/strict-join/signed.test.mjs
```

Use a new output directory for every run and preserve all failures. Product mismatches must be reported rather than changing geometry expectations.


## Actual R3 result

**17/17 setups and 70 rows PASS**, Node24.22.1/Puppeteer24.35/actual Chrome155.0.8059.79. [Receipt](evidence-r3/receipt.json), [source/environment readback](evidence-r3/environment.json), [runtime pins](evidence-r3/runtime-pins.json). All executing source hashes matched after completion. Each fresh setup verified all73 core assets and the mounted outer bundle. No product edits or private bootstrap were introduced.

OCC and SMLib each passed all8 setups: overlap/face Join, proper cavity, operand reversal, explicit disjoint/edge/point refusals and shared creation/edit travel. The first-box-to-empty reproducer is closed in the actual signed app. Full mixed box/Join/edit Undo/Redo, same IDs, exact accepted source/model/material/journal preservation and native Save/sync/fresh Open/reedit passed. Failure ID reservations alone may advance: failed Join requests observed2→3; refused upstream width edits preserved3. Counters are reported separately in the receipt.

The separate SMLib point diagnostic confirms validLevel0/2true, manifoldPredicatetrue, materialRegions2, void0, raw union2,000mm³ and bounds0..20, followed by ordinary Undo restoring both inputs. Its Join remains refused. The R2 error-classification mismatch is preserved unchanged; no successful one-solid admission was relaxed. Manifold explicitly refused Join with JOIN_UNQUALIFIED; only its separately requested raw union and chronology/persistence are qualified.

Forward/reversed cavities retained1,092mm³ and bounds[0,0,0]..[11,10,10]: OCC one native solid/two shells; SMLib one native material region/one void. Genuine detached display probes verify[5,5,5] stays empty, including fresh Open. Distinct authored operand order persisted. The independent [13-file saved-intent/formula checker](evidence-r3/saved-oracle.json) passes every actual native file. Session Undo/Redo reset on Open. All owned contexts closed and shared Chrome stayed open; fixture cleanup remains root-owned.

Native validity plus one-solid census is evidence within this tested ordinary boxed/contained-cavity domain, not a universal manifold certificate. The queued outer30cube/exterior-notch/inner-cube self-contact controls on OCC/SMLib remain unexecuted. Full E16/Gate1 and Manifold strict Join remain open. R1 and R2 failures are retained with their exact source-bound evidence.
