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

1. Authoring journal agent (`storage_browser`): real edit undo/redo; compact authored requests, no meshes/handles, atomic publication with full descendant replay. Feature cursor rollback is separate. Coordinate shared craft hooks with rectangle lane.
2. Rectangle worker agent (`storage_server`): supported dimension discovery/edit and candidate-only sketch read view; solve privately, atomically publish sketch bytes and regenerated full-tip geometry, reject/cancel with prior state intact. Own new rectangleEditing.ts, narrow registry/preparation/replay hooks.
3. Shared command agent (`storage_review`): qualify the new host Save on exact rebuilt source, signed accounts and fresh Files reopen. Continue shared feature/history operations afterward; no private-helper full-agent claim.
4. Root: integrate/review and run independent checks. Grouped Equal Length/Radius/Coincident history and atomic-refusal fixes are integrated through CAD6d34d820; root five focused controls pass, owner real-browser receipt is limited (no CSP, prior worker artifacts reused). Source08e43c19 adds cheap full-document revision; desktopae356553b adds Save through the common UI routine and six adapter controls. Signed Save is now qualified within its V2 enclosure domain: desktopbaf2dd33c records new/existing path save, local/server bytes, material/surface stale revision, occupied filename/changed-version refusal and fresh Files reopen. A fixture initially emitted unaliased numeric; root fixed default worker build1ec4468d (unconditional prepared alias + standalone precompile), independently built with flag unset and validated the same native bytes under strict CSP; emitted workerad525 matches corrected fixture byte for byte. Guarded extrusion edit is CAD4c803640/desktopbfe0a11b0, limited to a rewound feature. Carried regression receipt is CAD e30516e6; root desktop/emulated-phone spline, clean/corrupt IO, DXF, measurement history, selection and marquee checks pass.

See CAD-SHARED-OPERATIONS.md for the exact full-agent acceptance path. It explicitly distinguishes inspecting internals to verify results from using private helpers to perform missing edits.

CAD window-isolation tests integrated as bfb0fe56: actual signed host closes an in-flight window without changing a second, which continues; repeated cycles show no observed worker/lock leaks. One second-frame startup timeout without interception remains unexplained. Its original context was cleaned before preservation; a failure-preserving diagnostic was added and later runs passed. This does not qualify startup reliability.
Shared combined fixture: loopback 19707 standalone CAD, 19708 signed desktop, CDP 19329. Combined app SHA c35bce15493022ef28d0aa8b8d503f3bea4deeb980f4b1a3a8013e14515758bf. New spline-fix build: 19709; verify its matching app/workers/helper before tests. Do not mix copied old workers with a new app. The fixture's old .rev is not its authoritative runtime identity.

A failed bracket context was retained on CDP 19329 (process session 21308), with /tmp/codi-signed-four-combined-review-r8.log and /tmp/inspect-preserved-bracket.cjs. Verify handles exist before use. Do not close the shared browser or unrelated contexts.

Node: /tmp/codi-files-move-node/bin/node. Puppeteer: /tmp/codi-occt-release-control/node_modules/puppeteer-core. Use R730 for large builds; workstation space is tight. Temporary Linux remains separate from My files. Essential source/tests/notes belong in Git; delete only identified disposable artifacts.

Last verified Files deployment: main frontend f2e2ed4d, issuer adc693e4, gateway dd8cbea7, SDK44da; beta Files frontend 830ca4f1. These are earlier deployment receipts, not a fresh live health claim. Later activation must use managed hosting/recovery, preserve main and /desktop, and keep beta identities separate. Never hand-edit derived Caddy.
