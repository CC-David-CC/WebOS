# Current Files and CAD handoff

The full goal remains active. This replaces older checkpoint status, not the original scope. Read FILES-CAD-RELEASE-OBJECTIVE.txt, then CAD-FUNCTIONAL-GATES.md and the latest WEBOS-WORK-QUEUES.md entries.

## Current status

- Files foundation: accepted within its signed-account, representative-128-MiB scope. Persistence, isolation, conflicts, changed-chunk sync and interruption/crash recovery have evidence. No new Files-service defect is established. This does not qualify every app, automatic GC, classroom load or power-loss durability.
- CAD: active and incomplete. Combined 15a7e2a5 passed signed enclosure/insert creation, material UI/shared command, edit/rebind, Save/fresh Files reopen and initial/edited core 3MF. Root independently checked the actual files: two print objects, three regions, units/grouping/appearance, closed meshes and expected bounds/volumes in the supported domain.
- Bracket reliability: open. The signed five-hole workflow passed once; repeats exposed deadlines and reopen/save failures. Last-valid geometry is retained. Recent traced stalls include unanswered browser module/WASM requests before native execution; a direct request can succeed concurrently. Do not label these proven OCC hangs or fix them by extending deadlines. Diagnose fixture interception/request delivery and normal app behavior.
- Splines: undo/redo reused numeric ID 86 for distinct points. Root fix a22859f5 reserves saved IDs before reconstruction; project preflight allocation is temporary. Three allocation controls, strict IO and owner rebuilt desktop/phone draw/history/drag/native replay pass. Corrupt duplicate-ID samples remain rejected. Matching browser receipt ff250ba6 is ready for integration.
- Packaging: explicitly deferred until functional gates qualify. Pending packaging edit was discarded. No new CAD activation on main or beta.

## Worktrees and backups

Desktop: /tmp/codi-webos-cad-merge, branch integration/files-jsketcher-release-20261103.
CAD: /tmp/codi-jsketcher-release-integration-20261104, branch integration/files-cad-release-20261104.
Checkpoint before this documentation update: desktop 380974789, CAD a22859f5. Both were pushed to box-git and R730. Verify current Git refs rather than treating these pointers as permanent HEADs.

Desktop remote: box-git:/srv/data/git/CodiServer-distro.git; backup r730:/mnt/data10tb/git/CodiServer.git.
CAD remote: box-git:/srv/data/git/JSKetcher.git; backup r730:/mnt/data10tb/git/JSKetcher.git.
No GitHub publication is part of current work.

## Reuse this evidence

- docs/evidence/files-stage1-objective-audit-20261104.md, tests/files-foundation-exit-20261104.md and tests/files-session-expiry-20261104.md cover Files and session recovery.
- Desktop tests/jsketcher-enclosure-v2-export-signed-20261104.md; CAD test/enclosure-v2-functional/README.md and check-v2-3mf.py cover the signed three-region workflow. Root reran the oracle on both signed files and checked their hashes.
- CAD test/webos/BASIC-SOLID-GATE-20261104.md covers bounded block/washer core and replay. Washer uses legacy OCC extrusion, not rectangle-worker inner-loop support.
- CAD test/enclosure-history/LABEL-HISTORY-RESEARCH.md and surfacing receipts record history, cancellation and the Push/Pull Escape fix. These do not qualify all advanced CAD.
- Bracket failure tests/evidence are on desktop research/signed-four-corner-combined-20261104 at d5aa62dd9; not yet integrated. Preserve the retained failure context while diagnosing it.

## Immediate ownership and next actions

1. Browser agent: matching spline-fix browser receipt and affected carried-feature tests. Root owns id-generator.js/io.ts integration.
2. Native worker agent: isolate request/startup/native timing for intermittent bracket replay deadlines. Identical history can finish in seconds or stall; native execution is not established in every timeout.
3. Bracket agent: ordinary edit/reject/undo/Save/fresh Files reopen, with actual status/error capture and failed-context preservation. Extra diagnostic preparation can affect timing; do not count it as a plain-Save proof.
4. Root: integrate fixes/evidence and finish remaining mechanical/parameter/shared-command and combined-app gates. Only afterwards resume final source/runtime packaging and managed beta qualification. The full scope is in the unchanged objective and functional gates.

Shared combined fixture: loopback 19707 standalone CAD, 19708 signed desktop, CDP 19329. Combined app SHA c35bce15493022ef28d0aa8b8d503f3bea4deeb980f4b1a3a8013e14515758bf. New spline-fix build: 19709; verify its matching app/workers/helper before tests. Do not mix copied old workers with a new app. The fixture's old .rev is not its authoritative runtime identity.

A failed bracket context was retained on CDP 19329 (process session 21308), with /tmp/codi-signed-four-combined-review-r8.log and /tmp/inspect-preserved-bracket.cjs. Verify handles exist before use. Do not close the shared browser or unrelated contexts.

Node: /tmp/codi-files-move-node/bin/node. Puppeteer: /tmp/codi-occt-release-control/node_modules/puppeteer-core. Use R730 for large builds; workstation space is tight. Temporary Linux remains separate from My files. Essential source/tests/notes belong in Git; delete only identified disposable artifacts.

Last verified Files deployment: main frontend f2e2ed4d, issuer adc693e4, gateway dd8cbea7, SDK44da; beta Files frontend 830ca4f1. These are earlier deployment receipts, not a fresh live health claim. Later activation must use managed hosting/recovery, preserve main and /desktop, and keep beta identities separate. Never hand-edit derived Caddy.
