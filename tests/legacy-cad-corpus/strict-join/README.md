# Signed strict Join corpus

R2 prepared against frozen CAD `224f3302d421957a9390879034102660f81d6ac0` and desktop `cf97976d965f0b57689f1d2a8c87a060d0a49369`. Only registered public commands author geometry/history. Read-only live intent, source, counters, material/presentation metadata, assembly constraints, measured model outputs and bounded detached Float32 display copies provide observations. No private source writes, raw native seeds, model replacement, fake UI or fabricated successful replies. Every fresh signed setup verifies all core asset hashes and the mounted outer bundle first.

Seventeen setups: eight each for OCC and SMLib plus one explicitly unqualified Manifold Join control.

- Overlap: 10 mm cubes at x=0 and x=5 Join to 1,500 mm³, bounds [0,0,0]..[15,10,10]. FIRST box Undo reaches truly empty history/output and Redo retains its original ID. Join Undo restores both consumed operands; Redo retains result ID. Upstream first-box width20 gives 2,000 mm³; width4 disconnects the operands and must refuse. Mixed normal travel covers UndoEdit→UndoJoin→UndoBoxB→UndoBoxA, then all four Redo. Save/sync/fresh Open resets session Undo/Redo; upstream reedit width21 gives 2,100 mm³, with ordinary Undo/Redo and another Save/Open.
- Face contact: second cube at x=10 Join gives 2,000 mm³, one native geometric solid, stable creation travel and saved intent.
- Disjoint, edge contact and point contact: origins [20,0,0], [10,10,0], [10,10,10]. OCC must return `JOIN_MULTIPLE_SOLIDS`; SMLib must return `JOIN_MULTIPLE_SOLIDS` for disjoint and `JOIN_NONMANIFOLD` for edge/point contact. Unexpected codes are failures, including generic `ENGINE_FAILURE`.
- Cavity: outer10³ minus inner2³ at [4,4,4], Join a [2,10,10] box at [9,0,0]. Volume 1,000−8+200−100=1,092 mm³; bounds [0,0,0]..[11,10,10]. OCC must show one solid/two boundary shells; SMLib must show one material region/one void with valid manifold native evidence. Detached display parity verifies [5,5,5] remains empty and the extension contains material. Creation Undo/Redo and native Save/Open retain the cavity.
- Reversed overlap and reversed hollow/cavity Join are separate actual setups for both engines. Measures stay unchanged; saved authored operand order remains distinct. A kernel failure is retained as a real scoped failure.
- Manifold must refuse Join with `JOIN_UNQUALIFIED`, preserving both inputs and journal. A subsequent explicitly requested raw union gives 1,500 mm³ and supports normal creation Undo/Redo, native Save/Open and upstream reedit. This is never reported as qualified Manifold Join.

Axis-aligned numerical controls use absolute 1e-6 mm³ volume and 1e-7 mm AABB tolerances. These test literal-box arithmetic; they do not override SMLib's declared native-relative-0.001 measurement quality. Native evidence and detached display parity remain distinct. A cavity is allowed to have two boundary shells; shell/component count is never substituted for solid connectivity proof.

Refusals compare every captured accepted field and mesh exactly, excluding opaque inspection revisions and the separately reported feature-ID high-water alone. The high-water must remain monotonic and may reserve a skipped ID. Normal history travel compares authored/model/source/material state independently of the expected journal cursor and retained ID high-water. Fresh Open additionally ignores only the document-bound material inspection token; all material assignments/metadata, native intent, runtime, measured values and display bytes remain compared. No global source/model snapshot helper writes are used. Session Undo and Redo reset on Open.

Root owns the fixture and cleanup; the runner owns only fresh contexts and disconnects without closing shared Chrome. Native files in this frozen build remain `.jsketcher.json`; no ZIP or hosting change is assumed. This is a bounded strict Join/shared-history qualification, not full E16 or Gate1.

R1 found the genuine pristine first-box creation blocker; its exact evidence remains in [FAILURE-R1.md](FAILURE-R1.md). R2 changes only the expected CAD source pin. [R2 preparation](R2-PREPARATION.json) verifies the executing driver is byte-identical to R1 after that single source-string replacement; harness and geometry oracle hashes are unchanged. It remains unexecuted until root supplies fresh pins/fixture. Optional revolve changes in this candidate are outside this corpus.

After root supplies and authorizes `STRICT_JOIN_PINS` and `STRICT_JOIN_FIXTURE`:

```sh
CODI_SIGNED_PINS="$STRICT_JOIN_PINS" CODI_EVIDENCE=/tmp/codi-strict-join-proof-r2 CODI_TEST_URL="$STRICT_JOIN_FIXTURE" CODI_TEST_CDP=http://127.0.0.1:19329 PUPPETEER_CORE_PATH=/tmp/codi-occt-release-control/node_modules/puppeteer-core /tmp/codi-files-move-node/bin/node test/agent-cad-corpus/strict-join/signed.test.mjs
```

Use a new output directory for every run and preserve all failures. Product mismatches must be reported rather than changing geometry expectations.
