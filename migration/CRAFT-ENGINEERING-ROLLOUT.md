# PCBCraft and FieldCraft rollout

The starting release on ksu.codes is `22b0211e018ae27561ce943a666fb730f795a07e3c016bd084c77d415fb51f0f`. It enables 18 distinct Craft editors. Ship the two engineering editors independently as each passes. Keep the active deployment and its exact rollback receipt identified at each step.

| Editor | Source and integration branch | Native fidelity check |
|---|---|---|
| PCBCraft | `apps/pcbcraft`, `webos/pcbcraft-integration`, base `96f31b02442a`, direct target `pcbcraft-web` | Place a pinned resistor symbol on a schematic and its mapped footprint on the board. Save the .pc archive. Verify both views, coordinates, pin mapping and library definitions after a fresh browser opens it from Files. |
| FieldCraft | `apps/fieldcraft`, `webos/fieldcraft-integration`, base `0a5bfdd98592`, direct target `fieldcraft-web` | Import an analysis with known constraints and loads, run the solve, save and reopen its .fieldcraft document, compare the recomputed displacement with the independent expected value. |

For each app, exercise native Save and Save As, check the server revision and preserved original, recover unsaved edits on refresh, and activate an already-open resource through Files and the native Open path. Verify an authorized edit with Undo, then verify account bytes and native content in a separate browser context. Run the affected Desktop and shared release suites against the exact assembled package, publish the static viewer through the existing operator and verify its files and browser startup on ksu.codes.

The public UI uses Electronics → PCBCraft and CAD → FieldCraft in the classic Desktop. The launcher profile enables each app with its verified build. Upstream PCBCraft's GitHub Pages packager is reference material for the standalone site.

## Resumption

Parent assembly branch `webos/engineering-apps-rollout`. Desktop branch `webos/engineering-apps-menu` registers profile-gated entries, window identity and recovery. Build on the R730 data volume with Rust 1.99.1. Both lockfiles pin SolidCraft dependencies and the required commits exist in the local source repo. The private build ledger is `../.webos-migration/craft-engineering-CEGNCJ92/` relative to the WebOS root. Its builder scripts and checkpoint identify the current processes, test evidence and remaining release gates. The previous release and rollback instructions are in the [integration log](CRAFT-INTEGRATION-LOG.md#solidcraft-release-on-ksucodes).
