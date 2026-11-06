# Signed public source-bound through-hole workflow

Prepared only, **not executed or qualified**. Await the final four-method CAD
facade, frozen whole app/bundle/pins and fresh signed fixture. Only this new test
directory changes. Native dd666/8d5/component proofs remain separate exact scopes.

The public driver creates one constrained100×50 rectangle, selects/extrudes20mm,
creates a centeredD10 through-hole and four cornerD4 through-holes at8mm offsets,
then uses discovered original outer connector IDs for twoR3 fillets/two1mm
chamfers. It edits the original rectangle to150×30 and depth25, verifying that
holes move with the source and remain through the new depth. It edits centerD12
and cornerD5/offsets12×10, tests outside/overlap/zero/stale refusal preservation,
and exercises accepted-hole-edit Undo/Redo. Normal native Save/server sync,
fresh public Open, centerD14 reedit/UndoRedo, resave and second Open follow.

All mutations use registered commands/current discovery IDs and revisions. The
native file must contain one source sketch, one selected profile, two semantic
WORKER_THROUGH_HOLES_V1 intents and two edge treatments. It must not store Circle
tool sketches, authored internal Boolean operations, tool extents or native
indices/handles. SourceFeature/face/region and current target/producer stay exact.
Only numeric hole dimensions are edited; feature creation Undo is not claimed.

Native validity, volume, bounds, census and source-origin metadata are independent
public-command oracles. They are separate from preview placement measurements.
The parent-approved readonly display oracle copies the actual current
MWorkerSolid.copyDisplayPositions(), guarded before/after by public revision,
registry/model/feature/runtime identity and an explicit100000triangle bound.
No native handle is read. Float32 positions are detached; Node performs ray/
triangle work outside the page main thread. It checks expected bore voids,
adjacent material and material at former centers after moves. This is display
preview evidence, not native point classification. Qualified component native
cylinder/rim observations remain the separate exact geometry evidence.

`harness.mjs` is a copy of the qualified edge-treatment login/pin/Save/Open helper,
with a new synthetic account prefix and only the detached display-read method
added. Existing helpers/tests/evidence are unchanged. Private __CAD_APP access is
accepted-state/display read-only apart from normal snapshot serialization;
no model, source, history, native JSON or successful Worker output is injected.

```sh
CODI_TEST_URL=http://127.0.0.1:PORT/ CODI_TEST_CDP=http://127.0.0.1:19329/ CODI_SIGNED_PINS=/path/frozen-pins.json PUPPETEER_CORE_PATH=/path/puppeteer-core CODI_EVIDENCE=/tmp/new-source-hole-evidence node test/agent-cad-corpus/source-bound-holes/signed.test.mjs
node test/agent-cad-corpus/source-bound-holes/check-saved.mjs /tmp/new-source-hole-evidence
```

Initial native/copy assertions are provisional to the supplied facade contract;
any actual signature changes will be grounded in final source before execution.
No public deployment, Files re-audit, relay or filesystem-race work occurs here.
This cannot establish all22 Gate1 requirements or generic hole/Boolean robustness.

Facade source84406dea42e4c96613cf0bee54e96e8fc0380831 was read before execution:
creation[kind] uses `nativeResultCost` (not the provisional cost spelling), and
both global/target rows explicitly advertise sourceProfile:selected-rectangle
with sourceQualification:requires-worker-validation. The test checks that honest
qualification. History exposes full captured fields plus index/canEdit/reason,
matching the prepared edit requests. No signature blocker is known; no runtime
has been run yet.
