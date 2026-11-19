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

## PCBCraft release on ksu.codes

Release `18c3c9ccce53f20fd60e1ab981cc1f2f82a238c8484cd1ed9033b5121e46bea9` enables 19 distinct Craft apps. The editor came from `apps/pcbcraft` at `2348195417bfc6349ace2dc9a5709b5db570f319` on `webos/pcbcraft-integration`. The exact assembled site passed 104 Chromium checks. A fresh Chromium context reopened the account .pc archive with the same schematic resistor, pin mapping, board footprint and placement. Editor and Files Open activated the existing document. Account Save, Save As, browser draft recovery and an authorized edit with native Undo passed against isolated accounts.

Hosted verification matched all 813 files, fetched the editor's WASM with the expected digest and MIME type, and started a blank native editor in Chromium. Account edits use explicit server-confirmed saves with browser-local draft recovery. The evidence is under `../.webos-migration/craft-engineering-CEGNCJ92/pcbcraft-2348195417bf/` relative to WebOS. See `gates.json`, `remote-verification.json`, and `hosted-browser.json`. The immediate rollback is `22b0211e018ae27561ce943a666fb730f795a07e3c016bd084c77d415fb51f0f`. The static operator saved the rollback plan on box-webhost at `/var/backups/webos-eng-pcbcraft-2348195417bf/plan.json`.

## FieldCraft release on ksu.codes

Release `d5c94bcda8a6e1db7ad471847b637a57b957d3b2bf3ab3b0a3937af269ce11ec` enables 20 distinct Craft apps. The editor came from `apps/fieldcraft` at `8f14daaa674c60d61534cc224529cbe08ed65bc0` on `webos/fieldcraft-integration`. The exact assembled site passed 48 Chromium checks. A fresh Chromium context reopened the account .fieldcraft analysis with its loads and constraints and reproduced the reference cantilever displacement. Editor and Files Open activated the existing document. Account Save, Save As, browser draft recovery and an authorized edit with native Undo passed against isolated accounts.

Hosted verification matched all 829 files, fetched the editor's WASM with the expected digest and MIME type, and started a blank native editor in Chromium. Account edits use explicit server-confirmed saves with browser-local draft recovery. The evidence is under `../.webos-migration/craft-engineering-CEGNCJ92/fieldcraft-8f14daaa674c/` relative to WebOS. See `gates.json`, `remote-verification.json`, and `hosted-browser.json`. The immediate rollback is `18c3c9ccce53f20fd60e1ab981cc1f2f82a238c8484cd1ed9033b5121e46bea9`. The static operator saved the rollback plan on box-webhost at `/var/backups/webos-eng-fieldcraft-8f14daaa674c/plan.json`.
