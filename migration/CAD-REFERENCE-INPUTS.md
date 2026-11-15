# Referenced legacy CAD review inputs

Eight original frozen inputs now accompany the parent-owned cross-component CAD test source. A corrected AST scan found 12 static read sites referring to these files. Earlier path analysis missed `import.meta.url` member naming; both reports and the correction remain in private phase47. Dynamic/environment/Python paths remain open and absence of a static match does not prove an input unused.

| Captured original | Parent source |
|---|---|
| `test/agent-cad-corpus/gate1-wide-pass-20261106/evidence/enclosure-complete/enclosure.3mf` | `tests/legacy-cad-corpus/gate1-wide-pass-20261106/evidence/enclosure-complete/enclosure.3mf` |
| `test/agent-cad-corpus/source-plane-depth/preparation/receipt.json` | `tests/legacy-cad-corpus/source-plane-depth/preparation/receipt.json` |
| `test/agent-cad-corpus/step-export/evidence-route/manifest.json` | `tests/legacy-cad-corpus/step-export/evidence-route/manifest.json` |
| `test/agent-cad-corpus/step-ui/preparation/stylesheet-before.sha256` | `tests/legacy-cad-corpus/step-ui/preparation/stylesheet-before.sha256` |
| `test/agent-cad-corpus/sweep/native-review/raw-receipt-r3.json` | `tests/legacy-cad-corpus/sweep/native-review/raw-receipt-r3.json` |
| `test/agent-cad-corpus/sweep/native-review/runtime-pins.json` | `tests/legacy-cad-corpus/sweep/native-review/runtime-pins.json` |
| `test/agent-cad-corpus/sweep/signed-capacity-evidence-r1/receipt.json` | `tests/legacy-cad-corpus/sweep/signed-capacity-evidence-r1/receipt.json` |
| `test/agent-cad-corpus/sweep/signed-capacity-evidence-r2/receipt.json` | `tests/legacy-cad-corpus/sweep/signed-capacity-evidence-r2/receipt.json` |

## Actual verification

All eight files match original blobs and modes and retain their selected histories. JSON parses, the stylesheet pin has SHA256 syntax, and the 3MF archive passes CRC/member-text checks. Bounded credential/opaque screens passed; this is not full external-publication clearance. No archive was extracted over a source directory.

Three original offline recorded-data reviewer tests pass in a private exact-source snapshot and in the complete clean assembly, with original source and primary working tree hidden and external networking disabled. They check recorded-data consistency, independence from producer expected fields, and rejection of altered measurements/payloads. No geometry/native kernel, Worker, browser, sign-in, account synchronization or current CAD authoring acceptance follows.

The remaining reference drivers retain old host/import/dependency and side-effect gates. No broad legacy discovery was run. These fixtures remain outside production assets and supported default test entrypoints. Historical bulk run outputs remain in private recovery; only these eight explicitly referenced inputs were retained here.

Mechanical filtered baseline `6c61cd2178909141f563436ed3cf0cbe7829db1e`; parent merge `94a63874299210c01a5dd44345317e4527ced83f`. All 124 component pins and current implementation/dependency/build/deployment entrypoints are unchanged. Maps, structure checks, graph correction, baseline logs and clean-source proofs remain private under phase48.
