# Edge-treatment creation history acceptance — preparation

**Prepared only. No browser execution or passing qualification is claimed.** Parent must provide the new frozen app, exact full runtime/outer pins and signed fixture before running. The previous broad-pass CAD84406/desktop792 app does not support creation Undo and is explicitly refused by this harness.

All source is confined to this new test directory. The harness derives from the qualified source-bound-hole public harness; all geometry mutations use existing registered desktop commands, except real trusted Ctrl+Z/Ctrl+Shift+Z keyboard input in a visibly focused CAD iframe. No private action invocation, timeline pointer, history writer/native seed, fake Worker output, UI mock, Files audit or filesystem-race test.

The product scope is deliberately narrow: `WORKER_SOLID_EDGE_TREATMENT_V1` append transactions share the existing session-local authored edit journal. It is not creation Undo for sketch/profile/hole/Boolean/other commands, and not the timeline history cursor.

## Prepared path and independent oracles

1. Real public constrained rectangle100×50, selected-profile depth20, source-bound centered D10 and four-corner D4/offset8 holes. Discover actual original outer edge IDs.
2. Fillet two opposite vertical cornersR3; chamfer the remaining two size1. Before ANY numeric edit, assert `undoTarget.kind:'operation-append'`, exact feature ID and operation type. Undo restores real fillet output; Redo restores the same chamfer feature/body/opaque source-derived keys/native bounds/volume/topology and counter highwater.
3. Repeat creation travel through **real focused iframe Ctrl+Z / Ctrl+Shift+Z**. The helper clicks the actual viewport canvas, confirms iframe focus, sends trusted key events and polls public accepted state. It never invokes actionService or a timeline method.
4. Undo the original chamfer, edit fillet3→4 and create a fresh chamfer. Assert chronological UndoCreate/UndoEdit/RedoEdit/RedoCreate. Returned IDs and inspected journal targets are authoritative.
5. Undo chamfer; attempt an excessive-size replacement through the public command. Refusal must preserve accepted source/history/geometry and Redo. A failed operation may consume/skip an ID: the test checks monotonic highwater, not counter rollback. Then an accepted size1.5 replacement must allocate above observed highwater and truncate Redo.
6. Save the **UNDONE** fillet prefix normally, sync, fresh public Open. Native history contains one treatment and no hidden future chamfer; counters retain allocated highwater. Session-local journal resets explicitly on Open. New creation uses an ID above persisted highwater.
7. Three bounded Undo/Redo cycles compare resource owner/candidate/accepted/detached/mount counts and cleanup status, accepted outputs and counters. No heap benchmark or unbounded soak.

Independent expected volume is `100*50*20 - pi*20*(5^2+4*2^2) -2*20*r^2*(1-pi/4) -20*c^2`, with true native validity, one solid and100×50×20 native bounds. The shared source-bound arithmetic oracle also checks actual topology census and available sourceContext/selection contracts. Raw native metrics and source bytes are read only. Snapshots are detached through the public project's existing snapshot function; there is no model import/authoring via those readers.

Readonly observations use `craftService.engineResourceUsage`, `craftService.isProcessing`, `projectService.counterGenerator.projectCounters`, accepted native snapshots and inspected current public solids/journal. Counter equality is deliberately excluded only for the known `featureId` highwater when comparing a previous prefix or failed creation; every observed highwater is independently required to be monotonic. Other native fields/source/history remain exact. Save/Open must preserve the persisted counter.

## Future execution

Do not point at20919 or reuse the broad-pass pins. Once parent supplies NEW matched pins/fixture:

```sh
CODI_TEST_URL=http://127.0.0.1:NEW_PORT/ \
CODI_TEST_CDP=http://127.0.0.1:19329/ \
CODI_SIGNED_PINS=/absolute/new/runtime-pins.json \
CODI_EVIDENCE=/tmp/NEW-creation-history-output \
PUPPETEER_CORE_PATH=/tmp/codi-occt-release-control/node_modules/puppeteer-core \
/tmp/codi-files-move-node/bin/node test/agent-cad-corpus/creation-history/signed.test.mjs
```

Output must be new. The harness pins every declared core asset and the actual mounted outer index before authoring. Actual failures retain receipt/stack/source pins. Parent owns fixture cleanup; the runner closes only its own browser context and disconnects from shared Chrome.

Preparation validation: Node `--check` on both modules only. Actual keyboard focus, new journal chronology, native generation, publication/persistence and resource stability remain **unexecuted** until the new app is supplied.

## First actual R1 result — retained

New98fe85145/desktop247b222e app on parent20920: genuine source-bound plate/fillet/chamfer creation and immediate public UndoCreate/RedoCreate passed independent geometry/source/opaque IDs/counter assertions. The keyboard helper then stopped **before sending CtrlZ** at `CAD iframe must have actual focus` after its canvas click. Session87878 exited1, own context closed. `evidence-r1/receipt.json` and its source pins retain this incomplete attempt. Actual keyboard, later mixed chronology/replacement/persistence/resource checks are not qualified by R1. Focus precondition is being diagnosed; no product defect is inferred from that assertion alone.

### Natural focus diagnosis / grounded keyboard precondition

Three fresh actual focus diagnostics are retained. Both canvas-center clicks hit the true iframe while the top document remained focused/visible, activeBODY and inner document unfocused. Thus background-tab behavior was excluded. `CADTrackballControls.js` mousedown prevents default; root independently confirmed the input integration defect and owns its later product fix. A **real File menu click then Escape** naturally focuses top activeIFRAME/inner focusedBODY. Keyboard acceptance now uses that ordinary UI path followed by a trusted canvas click, with both actual focus assertions retained. No `focus()` call, synthetic event, key dispatcher or model mutation workaround. This can qualify the real shortcut once focused; it does not qualify natural canvas-first focus in the old98fe runtime.
