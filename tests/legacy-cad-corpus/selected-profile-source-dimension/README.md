# Atomic source-dimension and selected-region workflow

SOURCE READY, NOT EXECUTED. Per user direction, no incremental tests, syntax checks, type checks or builds were run while implementing this coherent workflow. Parent composes the shared core, Craft splice and public registration, builds once, then runs this complete workflow against exact served pins. No E04/E05/full Gate 1 pass is claimed here.

The authored factory rectangle is initially 100×50 mm on its actual independent XY plane. Four publicly appended ordinary Segments form a second closed rectangle at x110..140/y10..40. Every curve ID comes from actual creation/inspection. Initially these components are disjoint, and only the factory rectangle is extruded 20 mm. Increasing its existing driving width to 150 mm makes the second rectangle a hole. The original selected-region ID consequently becomes stale. Crossing-loop/arrangement topology is deliberately not used as a substitute for this supported nested-region domain.

The driver performs three complete setups:

1. Ordinary width150 refuses without changing accepted intent. Read-only proposal reconstructs the dimension edit privately and advertises both nested bounded regions. Wrong digest, unknown region, unchanged dimension, touching width110 and stale-after-depth-edit refuse. Explicit descriptor-backed outer-with-hole selection publishes source and the same extrusion atomically. Interleaved depth/source-region UndoRedo restores exact source/feature identity. Normal Save, browser/server SHA agreement, fresh signed Open, width160 reedit, UndoRedo, resave and another Open retain native editable intent.
2. A real world-space box subtracts y≤25 from the original extrusion. The same unchanged Boolean child replays after source/region repair. Its IDs and full authored parameters remain exact; UndoRedo and Save/Open follow.
3. A second separate extrusion still consumes the original outer-only region. Repairing only the first must refuse full replay with STALE_REGION, preserving both original records, both native outputs, all source bytes, journal/material/counters and document binding. No implicit child retargeting.

Analytic expectations, frozen before execution:

| State | Volume mm³ | Native bounds mm |
|---|---:|---|
| Original | 100000 | [0,0,0]..[100,50,20] |
| Nested width150 | (150×50−30×30)×20 = 132000 | [0,0,0]..[150,50,20] |
| Nested depth25 | 165000 | [0,0,0]..[150,50,25] |
| Fresh Open width160 | 142000 | [0,0,0]..[160,50,20] |
| Lower-half cut original | 50000 | [0,25,0]..[100,50,20] |
| Lower-half cut nested | (150×25−30×15)×20 = 66000 | [0,25,0]..[150,50,20] |

Absolute native volume tolerance is 1e-6 mm³; bounds tolerance is 1e-6 mm. Require exact recorded JS/WASM revision, native valid single-solid census, same feature/output IDs and counters. Accepted resource owners must all be retired after each invocation. Unrelated appended Segment records, all curve IDs and source frame remain exact. Saved nine-field extrusion intent is checked against actual accepted history; there are no persisted proposal bytes, locators, opaque-ID parsing, private source setters or synthetic successful native replies.

Same-window read-only/proposal and pre-native refusals compare every captured field/revision exactly. Evaluated Native refusals may advance only three opaque inspection revision fields (solid, authored-edit and host inspection); the driver records the raw before/after tokens and otherwise compares all accepted fields exactly. This is explicit evaluation bookkeeping, not permission to change accepted authored intent, document token, native geometry, baseline, journal contents, source/material, or ID high-water. Fresh Open legitimately rebinds session revision tokens and resets session Undo.

Run only after parent provides the complete runtime and authorizes its browser. Use a fresh evidence directory and existing shared Chrome with owned contexts only:

```sh
CODI_SIGNED_PINS=/absolute/runtime-pins.json \
CODI_EXPECT_SOURCE=exact-composed-core-source \
CODI_EXPECT_DESKTOP=exact-composed-host-source \
CODI_SOURCE_REGION_ENGINE_REVISION=sha256:exact-js:exact-wasm \
CODI_TEST_URL=http://127.0.0.1:PORT/ \
CODI_TEST_CDP=http://127.0.0.1:19329 \
PUPPETEER_CORE_PATH=/absolute/puppeteer-core \
CODI_EVIDENCE=/tmp/fresh-source-region-proof \
/tmp/codi-files-move-node/bin/node test/agent-cad-corpus/selected-profile-source-dimension/driver.mjs
```

The driver pins executing source, shared harness and actual served assets, preserves the first failure, and never closes a context during a submitted durable write. Parent owns the fixture and shared browser; the driver retires only its own contexts. Typed project bindings, manufacturing-assigned parts, referenced boundaries, arrangements/crossing loops, circle winding, human viewport selection and comprehensive Gate 1 remain outside this bounded source slice.

Public wiring: import/register `registerSelectedProfileSourceDimensionCommands` from `apps/system/jsketcher/selected-profile-source-dimension-commands.mjs`. Export `createSourceDimensionRegionExample` from `apps/system/jsketcher/examples/source-dimension-region.mjs` through the existing app module. The example uses the existing document-pinned createCadAgent and requires explicit supported region choice from actual proposal metadata.
