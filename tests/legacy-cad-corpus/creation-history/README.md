# Edge-treatment creation history acceptance — actual R2

**R2 actual signed public path passed10 rows on98fe85145/desktop247b222e.** Parent provided the frozen app and signed20920 fixture. The previous broad-pass CAD84406/desktop792 app does not support creation Undo and is explicitly refused by this harness.

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

Preparation initially had Node syntax checks only. Actual R1 stopped at focus; actual R2 qualification and limits are below.

## First actual R1 result — retained

New98fe85145/desktop247b222e app on parent20920: genuine source-bound plate/fillet/chamfer creation and immediate public UndoCreate/RedoCreate passed independent geometry/source/opaque IDs/counter assertions. The keyboard helper then stopped **before sending CtrlZ** at `CAD iframe must have actual focus` after its canvas click. Session87878 exited1, own context closed. `evidence-r1/receipt.json` and its source pins retain this incomplete attempt. Actual keyboard, later mixed chronology/replacement/persistence/resource checks are not qualified by R1. Focus precondition is being diagnosed; no product defect is inferred from that assertion alone.

### Natural focus diagnosis / grounded keyboard precondition

Three fresh actual focus diagnostics are retained. Both canvas-center clicks hit the true iframe while the top document remained focused/visible, activeBODY and inner document unfocused. Thus background-tab behavior was excluded. `CADTrackballControls.js` mousedown prevents default; root independently confirmed the input integration defect and owns its later product fix. A **real File menu click then Escape** naturally focuses top activeIFRAME/inner focusedBODY. Keyboard acceptance now uses that ordinary UI path followed by a trusted canvas click, with both actual focus assertions retained. No `focus()` call, synthetic event, key dispatcher or model mutation workaround. This can qualify the real shortcut once focused; it does not qualify natural canvas-first focus in the old98fe runtime.

## Actual R2 scoped qualification

- Exact core98fe85145d12dab8089a1cf6d75e114e679798bc, desktop247b222e522680e122b7697df0f8d0b41fa0511c, outerbbe367ef935ee79b1cc91f6704d71e686764b00eeb9f95fc2f615d5272032b2f/index940336b50da6260d6829fdfe321117c511a7da7008494d222d3d62cbcc0de3de; all67 declared core files checked through actual mounted frame, native dd666/8d5 unchanged.
-10 actual recorded rows PASS, session3623exit0; rawreceipt/source pins unchanged in `evidence-r2/`. Own contexts closed, parent20920/shared19329 untouched. Keyboard uses the measured real File-menu focus path; canvas-first focus remains separately unqualified in this runtime/root-owned future fix.
- Chronology and exact source/history/opaque selection identity assertions passed. Refused excessive chamfer returned `EDGE_TREATMENT_FAILED`, kept Redo and accepted geometry/journal while counter7→8 legitimately skipped an ID. Accepted replacement ID9 truncated Redo.
- UNDONE-prefix native file5203B SHA0bbdd04123917760d704e4695d4e3cae677be3abe3924ad1daaab76dd30d20c2 has exactly5 history records: PLANE, selectedprofile, centerhole, fourcornerholes, fillet size4. No hidden future chamfer is saved. Highwater9 persists; session journal resets on fresh Open; new actual creation gets10.
-3 bounded creation Undo/Redo cycles hold counters10 and identical resource census: owners1, detached1, mounts0, candidates0, accepted0, cleanupFailedfalse. These are actual detached accepted-result resource observations; not a heap/memory benchmark or indefinite leak proof.
- `check-saved.mjs evidence-r2` independently verifies raw saved intent and5 recorded native metric states against analytical volume, expected bounds, full compound/compsolid/solid/shell/face/wire/edge/vertex census and real source contexts. No fresh native call/point classifier is claimed by that offline checker.

Two checker-development errors are retained under `checker-development/`: first incorrectly assumed the native census contained only3 keys, then incorrectly required bitwise zero instead of geometric tolerance for bounds (actual−4.440892098500626e−16). The final checker checks all8 native census categories and1e−7mm geometric bounds; runtime exact replay/source/identity/counter assertions are unchanged. Both original failing checker sources/logs are preserved. This fixes oracle-schema/roundoff assumptions, not product geometry.

No full Gate1 claim, generic feature-creation Undo claim, timeline travel, persistent journal future or arbitrary history-operation support follows. The bounded successful product scope is the existing same-journal EDGE operation append and accepted numeric edit history on this genuine source-bound plate.
