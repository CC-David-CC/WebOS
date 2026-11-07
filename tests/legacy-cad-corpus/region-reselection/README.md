# Signed same-feature region reselection

Frozen core b8712790e739f073b2327bed0903a7b61b34069a and desktop 5c5eeba807a939dd39cbbdf206008260fa7a9f3e. The runner verifies every core asset and actual outer bundle before public authoring in each fresh owned signed account/context. It never writes private source/model state. Read-only accepted-state/native mesh observations supplement registered commands.

Six bounded setups:

- Two disjoint rectangles, one extrusion: 20×10 and 30×10 mm, depths 5/7/9 mm. Descriptor-discovered reselection preserves feature/output IDs, source and counters. Depth/region/depth Undo and Redo are interleaved. Stale, unknown and valid no-op requests preserve accepted state.
- Three concentric circles: radius 5 mm disk to radius 15/10 mm annulus at depth 5 mm, volumes 125π and 625π mm³. This does not qualify general circle winding behavior.
- Compatible unchanged Boolean child: a world-space box cuts the lower half of either rectangle. Same child IDs/intent replay to 500/750 mm³.
- Incompatible real fillet child: an advertised old-region connector at radius 1 mm prevents parent retarget. Accepted volume is 1000−5(1−π/4) mm³; all accepted source/history/geometry/journal state must survive refusal.
- A genuine 135-segment simple polygon exceeds the authored opaque-region identity budget while a separate circle remains selectable. All segments come from public primitive append; the unsupported descriptor is retained. This tests an explicit identity domain, not geometric nonexistence.
- A genuine positive native candidate reply is held, the real owned window is closed with trusted controls, and its real late reply must remain inert. Fresh Open preserves the previously saved accepted rectangle.

Volume absolute tolerance 1e-6 mm³; AABB coordinate tolerance 1e-7 mm. Mesh/source/history/counter comparisons are exact where asserted. Save uses the actual JSON native envelope in this frozen build, waits for the same owned file to synchronize, then opens it in a fresh signed context and re-edits. No new ZIP or strict Join claim. Combined rejected-source-edit plus reselection repair remains open. This is not full E05 or Gate1 qualification.

Run with fresh output directory, qualified Node24/Puppeteer24.35 and root-provided frozen fixture:

```sh
CODI_SIGNED_PINS=/tmp/codi-region-reselection-apps-20261106-r1/runtime-pins.json CODI_EVIDENCE=/tmp/codi-region-reselection-proof-r1 CODI_TEST_URL=http://127.0.0.1:20926/ CODI_TEST_CDP=http://127.0.0.1:19329 PUPPETEER_CORE_PATH=/tmp/codi-occt-release-control/node_modules/puppeteer-core /tmp/codi-files-move-node/bin/node test/agent-cad-corpus/region-reselection/signed.test.mjs
```

The runner closes only its own contexts and disconnects from shared Chrome. Root owns the fixture and its cleanup. Failed receipts are retained, never overwritten.
