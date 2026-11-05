# Current Files and CAD handoff

The full goal remains active. This replaces older checkpoint status, not the original scope. Read FILES-CAD-RELEASE-OBJECTIVE.txt, then CAD-FUNCTIONAL-GATES.md and the latest WEBOS-WORK-QUEUES.md entries.

## Current status

- Files foundation: accepted within its signed-account, representative-128-MiB scope. Persistence, isolation, conflicts, changed-chunk sync and interruption/crash recovery have evidence. No new Files-service defect is established. This does not qualify every app, automatic GC, classroom load or power-loss durability.
- CAD: active and incomplete. Combined 15a7e2a5 passed signed enclosure/insert creation, material UI/shared command, edit/rebind, Save/fresh Files reopen and initial/edited core 3MF. Root independently checked the actual files: two print objects, three regions, units/grouping/appearance, closed meshes and expected bounds/volumes in the supported domain.
- Bracket: scoped ordinary signed workflow now passes on unchanged 15a7 app assets: edited five-hole model, rejected edit, undo/redo, actual Save without extra prepareHostSave, matching server bytes and fresh Files reopen/account denial. Integrated desktop tests are 16469c245/7b126d83f/5988dbd8e. Five independent exact-helper-only controls also passed; blanket interception had intermittent unanswered module/WASM requests. Original cause is still unproven; no product timeout was raised. Preserve r8 context. This pass uses private test helpers for some edits, so supported agent editing remains a separate gap.
- Splines: undo/redo reused numeric ID 86 for distinct points. Root fix a22859f5 reserves saved IDs before reconstruction; project preflight allocation is temporary. Three allocation controls, strict IO and owner rebuilt desktop/phone draw/history/drag/native replay pass. Corrupt duplicate-ID samples remain rejected. Matching browser receipt ff250ba6 is integrated as c9e05a18; root independently repeated desktop and emulated-phone spline history/replay plus all three stored clean/corrupt controls on fixture19709.
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

1. Mechanical agent: /tmp/codi-mechanical-constraint-gap, research/mechanical-constraint-gap-20261104 from c9e05a18. Equal Length/Radius/Coincident action history fix065a6fee has focused regressions; real browser and conflicting-group admission qualification follows.
2. Worker/lifecycle agent: independent simultaneous CAD instances, close during native work and repeated disposal, using actual workers; no shared browser shutdown or timeout inflation.
3. Shared command agent: public feature inspection/edit/undo/redo using existing craft candidate guards; unify UI and agent routes, prove rejection/lifetime behavior, then signed full-agent bracket. No raw history replacement or private-helper acceptance shortcut. Owns workerFeatureCommands.ts, desktop feature-commands.mjs and narrowly coordinated craftBundle wiring.
4. Root: independent carried-feature regressions, integrate source/evidence, original-rectangle dimension operation and final combined qualification. Packaging remains deferred.
Shared combined fixture: loopback 19707 standalone CAD, 19708 signed desktop, CDP 19329. Combined app SHA c35bce15493022ef28d0aa8b8d503f3bea4deeb980f4b1a3a8013e14515758bf. New spline-fix build: 19709; verify its matching app/workers/helper before tests. Do not mix copied old workers with a new app. The fixture's old .rev is not its authoritative runtime identity.

A failed bracket context was retained on CDP 19329 (process session 21308), with /tmp/codi-signed-four-combined-review-r8.log and /tmp/inspect-preserved-bracket.cjs. Verify handles exist before use. Do not close the shared browser or unrelated contexts.

Node: /tmp/codi-files-move-node/bin/node. Puppeteer: /tmp/codi-occt-release-control/node_modules/puppeteer-core. Use R730 for large builds; workstation space is tight. Temporary Linux remains separate from My files. Essential source/tests/notes belong in Git; delete only identified disposable artifacts.

Last verified Files deployment: main frontend f2e2ed4d, issuer adc693e4, gateway dd8cbea7, SDK44da; beta Files frontend 830ca4f1. These are earlier deployment receipts, not a fresh live health claim. Later activation must use managed hosting/recovery, preserve main and /desktop, and keep beta identities separate. Never hand-edit derived Caddy.
