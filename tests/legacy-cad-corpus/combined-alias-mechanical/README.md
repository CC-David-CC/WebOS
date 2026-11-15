# Combined alias mechanical composition — scoped PASS

All checks use exact CAD source
`282c0f5ec9709c6ecdbc4f497ebbcce951616442`, ordinary app SHA256
`c8b5e10f3f9dbbe4b123606f96291a098610a4f711d3acad749953e711d1d0a5`
and the existing isolated signed fixture `http://127.0.0.1:20404/`.
Each workflow created new synthetic accounts and browser contexts. No existing
account/key state was copied. The fixture/runtime from the preceding alias
qualification remained unchanged.

| Existing workflow | Actual result |
|---|---|
| Public five-hole bracket | PASS public creation,100×50→150×30 edits, depth20→35, corner-hole edit/refusal, true undo/redo, stable body/face IDs, native Save/sync, foreign-account denial and fresh Files reopen |
| Typed bracket | PASS real Parameters UI, agent bindings/definitions/depth, dimensional rejection, undo/redo, independent analytic geometry, native persistence/reopen and window cancellation |
| Material-aware V2 enclosure | PASS public creation, real material UI/shared agent assignment, width100→120 typed configuration, explicit material rebind, native Save/reopen and two core3MF exports |
| Independent ZIP/XML geometry oracle | PASS both exports:2 print objects,3 regions,84 triangles, millimeter units, expected bounds/volumes, closed edge incidence and920mm² paired lid/label interface |

This is the requested composition regression after the new algebra, exact
reader and Scene disposal changes. It does **not** complete CAD1, qualify every
geometry kernel/feature, establish physical material behavior, verify a printer,
or authorize deployment. No production/old-test files changed.

## Public versus diagnostic access

`bracket.test.mjs` and `typed-bracket.test.mjs` reuse the existing signed tests
from `tests/jsketcher-{agent,typed}-bracket-signed.test.mjs`, preserving their
assertions and authoring paths. Added code only verifies exact runtime assets
and records receipts. Their B-rep access is a passive independent read oracle.
The typed test's older cancellation control suppresses a real task before
execution; it is not represented as a held successful reply. Genuine-success
reply cancellation is separately qualified by the preceding Axis tests.

`enclosure.test.mjs` requalifies the old worker-view composition through the
already-existing public `create-worker-enclosure`, typed binding/configuration,
material assignment/review and export commands. It uses the actual material
dialog and visible File→Export3MF menu/themed host path prompt. It needs **no**
private wizard helper, Cypress shim, raw history edit, geometry writer or
native/formula seed. It requires exactly2 print objects containing3 regions:
separate BODY and grouped LID/LABEL, with durable material/appearance identity.

The edit preserves unresolved assignments until explicit reviewed rebind;
export before rebind is refused without creating a file. Invalid rebind tokens,
stale revisions and export overwrite are rejected. Reopened native geometry,
typed design source and assignments remain authoritative. The 3MFs are derived
manufacturing handoffs, not editable parametric source.

`check-v2-3mf.py` is an unchanged byte copy of the independent checker at exact
CAD source282c, `test/enclosure-v2-functional/check-v2-3mf.py`. It reads ZIP/XML
directly, independently of the exporter and UI. Its source hash is in `pins.json`.

## Evidence and reproduction

`*-receipt.json`, `evidence/*.log` and `pins.json` bind the source, actual app
and sketch/project Workers, native server hashes and output geometry checks.
No failures occurred in these three runs. Output ZIP timestamps can vary.
The actual initial/edited 3MFs are retained outside Git at
`/mnt/data10tb/codi-axis-alias-evidence-20261106/mechanical/` along with all raw
logs/receipts. They are synthetic test outputs, not release/source packages.
Their local originals are under `/tmp/codi-combined-alias-mechanical-20261106`.

The code-only dependencies are the existing signed helper modules and the
preceding `axis-symmetry/combined-alias` exact asset guard. Require private
fixture URL/CDP plus `CODI_SOURCE`, `CODI_EXPECTED_APP_SHA`,
`CODI_EXPECTED_SKETCH_SHA`, `CODI_EXPECTED_PROJECT_SHA`, and per-run
`CODI_RECEIPT`. Asset checks run before authoring and after fresh reopen.
Run the two bracket scripts sequentially, then the enclosure script with an
isolated `CODI_OUTPUT_DIR`. Finally run:

```sh
python3 -B test/agent-cad-corpus/combined-alias-mechanical/check-v2-3mf.py "$CODI_OUTPUT_DIR/initial.3mf" "$CODI_OUTPUT_DIR/edited.3mf"
```

Use the exact source-matched runtime/catalog/fixtures documented in
`axis-symmetry/combined-alias/README.md`. Another revision requires matched
retesting. Close only owned browser contexts and disconnect from shared CDP.
No Files foundation re-audit, new kernel profile, physical printing, source
promotion, binary commitment or public deployment occurred.
