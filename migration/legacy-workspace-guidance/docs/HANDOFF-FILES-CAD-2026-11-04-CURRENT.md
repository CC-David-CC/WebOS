# Current Files and CAD integration handoff

This supersedes checkpoint status in `HANDOFF-FILES-CAD-2026-11-04.md`.
The user requested a handoff, not a pause. The full goal remains active.
Read `FILES-CAD-RELEASE-OBJECTIVE.txt` first: it is a verbatim copy of the active
user objective, so another machine does not need the original chat attachment.

## Start here

1. Fetch current branches, inspect working trees and coordinate with running
   agents before edits. Do not restart a test because its observation timed out.
2. Read `WEBOS-WORK-QUEUES.md`, `WEBOS-SILOED-WORK.md`,
   `HANDOFF-STORAGE-BETA-2026-11-02.md`, `JSKETCHER_UPSTREAM_WORK.md`,
   `JSKETCHER_ENGINE_COMPARISON.md`, and CAD's `docs/MECHANICAL-CAD-AUDIT.md`
   and `docs/MANUFACTURING-AND-PHYSICS-ROADMAP.md`.
3. Review the signed material receipt and beta operator candidate below. Continue
   manufacturing mesh/export and remaining CAD save processing. Do not restart
   upstream merges or replace the existing Files service.

## Repositories and current source

| Repository | Integration branch | Head before this handoff |
|---|---|---|
| `box-git:/srv/data/git/CodiServer-distro.git` | `integration/files-jsketcher-release-20261103` | `96e5faead6c15183c7af522f359112b51b9f3455` |
| `box-git:/srv/data/git/JSKetcher.git` | `integration/files-cad-release-20261104` | `34bbabea6dc11a27842c92f6cb75b47180588da2` |

Backup repositories: `r730:/mnt/data10tb/git/CodiServer.git` and
`r730:/mnt/data10tb/git/JSKetcher.git`. The desktop tip advances with this handoff.
Use branch tips, not the historical source branches named in the objective.
No GitHub publication is requested.

Lead worktrees: `/tmp/codi-webos-cad-merge` and
`/tmp/codi-jsketcher-release-integration-20261104`. CAD's untracked `.build/`
contains useful build/cache inputs; do not blindly delete it. No private account
data or keys should enter source or public bundles.

## Working and tested

### Files

The accepted main release passes normal signed Files/Text creation, editing,
Save, automatic sync, exact-byte recovery after fresh login, and second-account
denial. See `tests/main-opfs-public-normal.test.cjs` and its evidence note.
Broader fault/128 MiB evidence is in the storage handoff/queue; this one workflow
does not prove every app, failure mode or concurrency target. My files is
browser/server backed; temporary v86 files remain separate.

Previously verified live main pins, not re-polled for this handoff:

- Frontend `f2e2ed4d3b75e8c40992a18bf83db7937fe90615bf1151e1b51ed3b0a8012f4a`.
- Issuer `adc693e4bfe418f950eedd5be0f70ecc7b82c6268e14ebed6eeba64e95740414`.
- Gateway `dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1`.
- SDK `44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869`.
- OPFS backend v1/database v2; main retains its restricted tested app selection.

**None of the latest CAD/material/source-gateway changes is deployed.**

### CAD geometry and lifecycle

- Rectangle/plate, centered hole and four edge-offset holes have signed save/
  reopen evidence in `tests/jsketcher-four-corner-signed-20261104.md`.
  This is not the full bracket/fillet/pattern acceptance design.
- `WORKER_ENCLOSURE_V1` creates an OCC body and separate lid, with stable
  feature/role identities. Edits, rejection, undo/redo and native replay pass.
- Keep OCC preferred and Native Mesh/Manifold supported honestly. Manifold
  enclosure worker construction exists; current enclosure UI uses OCC.
- Accepted evaluations release workers while keeping current copied model data.
  Pool limits: two mounts per candidate, three total. Native replay reconstructs
  geometry; detached owners cannot regain native capability.
- Root independently ran three actual Chromium cleanup tests: composed model
  created/terminated 13 workers, max two live; queued replay, injected cleanup
  failure, observer-triggered reset and held-work cancellation pass. Cleanup
  failure preserves accepted savable geometry and blocks further evaluation.
- Evidence: CAD `test/enclosure-history/README.md` and three `codi-craft-*.cjs`
  scripts. Root also passed 34 resource/ledger tests and TypeScript noEmit.
- `34bbabea` makes command discovery reflect cleanup unavailability too.

### Material controls and agent access

- Integrated through `7c2fb6e0`: separate BODY/LID material/appearance,
  preserved names/region identities/transforms, material-only revision fencing,
  canonical string feature IDs from the wizard, incremental assignment hashing.
- UI and agents call the same `projectManager.assignEnclosureMaterialRoles`.
  Discovery is `inspectEnclosureMaterialRoles() -> {revision,featureIds}`.
  Assignment takes `(featureId, roles, {revision,signal,valid})`; each BODY/LID
  role has `{material:{id,name},appearance:{id,name,color}|null}`.
- Desktop `012b0846b` adds `inspect-enclosure-materials` and
  `assign-enclosure-materials`; the latter accepts `{featureId,revision,roles}`.
  These are unsaved edits, not implicit writes. Root's 12 command boundary
  tests and 10 assignment/hash/envelope tests pass; TypeScript passes.
- Combined signed PASS is committed on desktop candidate `c70998a69`, in
  `tests/jsketcher-enclosure-signed-20261104.md`: CAD `34bbabea`, actual wizard,
  material UI and desktop commands, stale-token refusal, normal Save, fresh
  Files reopen, exact metadata and other-account 404. Root read the receipt;
  independent combined rerun/test-only integration remains to do.
- R730 combined build: `/mnt/data10tb/codi-material-combined-34bb/dist`;
  app bundle: `/mnt/data10tb/codi-material-combined-signed-bundle`.
  Index SHA `4f762fb3e7855d6f0a4764339323aa4470f421ac83d5f0d1d3cc639c5ee98eab`;
  hash worker `3f7cf784c31276d9cca6f700bb524fd3ecf6cf39763c686e43b5d350fdf08125`.

## Remaining acceptance work

1. **CAD manufacturing save/restore still has an 8 MiB research cap and
   main-thread serialization/canonical work.** Assignment worker hashing does
   not fix the whole path. Reuse existing incremental/worker modules, reliable
   revision guards, and measure memory/responsiveness. Do not claim 128 MiB CAD.
2. Finish manufacturing-qualified live-kernel mesh extraction. Preview triangles
   remain explicitly unqualified. Bounds and volume alone miss shifted cavities.
3. Add contrasting inset label, grouped with lid; export actual model-derived
   core 3MF into My files with revision/account/cancellation guards. Independently
   validate units, dimensions, transforms, materials, two objects/three regions.
4. Existing 3MF research writer has 20 passing writer/adapter/envelope tests.
   `6f05e4fb` independently checks noncommuting transforms and grouping using
   Python ZIP/XML; `8b83aa92` prevents mm geometry being mislabeled as inches.
   Neither proves current worker-enclosure manufacturing export.
5. Finish specified bracket/enclosure parameter/contradiction/history workflows
   and mechanical gates. Do not declare broad CAD 1/2/3 maturity from components.
6. Clean release preparer still pins older CAD `67d34329`. Update source/runtime
   pins, new hash-worker asset receipt and notices, then rebuild/qualify. Shared
   dependency fixture builds are not clean release reproducibility evidence.

## Agent ownership and pending branches

### Material agent storage_browser

Finished; fixture processes/profile cleaned. CAD worktree
`/tmp/codi-enclosure-material`, branch `research/enclosure-material-assignment-20261104`,
test/receipt tip `f4806f5c`. Desktop worktree `/tmp/codi-enclosure-signed-desktop`,
branch `research/enclosure-signed-history-20261104`, tip `c70998a69`.
Both branches backed up to both LANs. Review/integrate remaining test/receipt
commits, including frame CSP scope `f5c7695b4`. Port protection `b6c4508a4`
is already integrated as `96e5faead`.

### Manufacturing agent storage_server

**Still working** on R730 `/mnt/data10tb/codi-enclosure-manufacturing-mesh-20261104`,
branch `research/enclosure-manufacturing-mesh-20261104`, based on `23d5b29b`.
WIP `37512e2386e47d4479fbd2523e504da75c35fc4a` is backed up but explicitly not
integration-ready. Owns new `modules/engine/mount/enclosureManufacturingMesh.mjs`,
mount/controller/OCI/Manifold workers, build inclusion and
`test/enclosure-manufacturing`. Do not edit these concurrently.

Nine pure validator controls pass. Latest uncommitted actual-worker report:
both engines' reconstructed body/lid return 16 indexed vertices, 28 triangles,
11 checked surfaces; deviation/precision refusal, stale handles and copy isolation
pass. Failure/cancellation and stronger coverage negatives are ongoing; obtain
the final commit and inspect evidence before integration.

Proposed API: `readEnclosureManufacturingMesh({op:'solid.enclosure.manufacturing-mesh',version:1,handle,maxDeviationMm},{signal})`
on a newly reconstructed disposable mount. Private captured plan/role,
exact-coordinate indexing, manifold/oriented topology, authored face coverage,
bounds/volume and explicit per-engine deviation precede returned typed buffers.
Root owns export orchestration/materials/3MF. Never relabel preview buffers or
silently weld distinct nearby points. Terminate export owners on every outcome.

### Deployment agent storage_review

Finished candidate in `/tmp/codi-cad-source-access`, branch
`research/cad-source-managed-20261104`, desktop tip
`9799a8cb221eb3a5248e9fb79cce14260929b558`, backed up both LANs.
Review ancestry from `d5f004430`; cherry-picking only the tip omits prerequisites.
Read `research/cad-source-access/BETA-SWITCH-EVIDENCE.md` and `MANAGED-PLAN.md`.
No live staging/mutation. Owned fixtures cleaned.

Candidate gateway `a626ef11bf57a039529abc806a4b39a5881f470557d49f8c715a742c06b5ae08`
adds authenticated source access with unchanged SDK bytes. Final switch bundle
inventory `c1b44f84c081dc5bda8321b3c8a961be04369e765e8ced302a4e4a7aa3071452`;
actor inventory `df0987cd6f38e6a0f2640734baf51ecdf6f0e122d89308a31c47b63182b90ce3`.
Mapped tests cover real disposable systemd gateways, locks, three killed phases,
wrong pins and signed source reads. Production callbacks were substituted there
and separately checked with dependencies stubbed; hosting custody was checked
read-only on box-webhost. Independently review these scopes/current host pins
before use. Existing dd8 SDK-floor marker is historical, not an a626 release floor.

## Deployment and test boundaries

Use managed hosting locks/generation/recovery, never direct derived-Caddy edits.
Preserve main, `/desktop/`, unrelated sites, saved data and account/key separation.
Use beta for iteration. Do not publish all experimental apps/games on main.

The host SDK uses Blob workers in `UserFiles.write`; CAD frame policy forbids
them. Combined signed test retains existing host CSP and adds narrower CAD CSP.
An attempted whole-host no-blob test correctly blocked file writes; do not
misdiagnose that as storage corruption or weaken production policies to pass.

Two Caddy fixtures once shared a port via reuse-port and alternated accounts/
404s. The integrated fixture now checks free port and sole owning listener PID.
Root independently exercised those guards with actual socket/ss. A proposed
extra `files-fixture-port.test.py` was never dispatched; that file does not exist.

## Reproduce and resume

From CAD root:

```sh
node --test test/coreTests/evaluation-resources.test.mjs test/coreTests/evaluation-detachment.test.mjs test/coreTests/candidate-prism-ledger.test.mjs
node --test test/enclosure-material/assignment.test.mjs test/manufacturing/incremental-hash.test.mjs test/project/project-envelope.test.mjs
node --test tests/3mf/manufacturing-adapter.test.mjs tests/3mf/core3mf.test.mjs test/project/project-envelope.test.mjs
node node_modules/typescript/bin/tsc --noEmit
```

Desktop: `node --test tests/jsketcher-material-commands.test.mjs tests/jsketcher-sketch-commands.test.mjs tests/jsketcher-feature-commands.test.mjs`.
Browser commands/pins are in the respective evidence files; use actual workers,
not fake geometry or fake browser UI.

Current workstation conveniences: Node24 `/tmp/codi-files-move-node/bin/node`,
Chromium `/snap/bin/chromium`, Puppeteer Core
`/tmp/codi-occt-release-control/node_modules/puppeteer-core`. Install equivalents
on another machine; these are not source dependencies. Python3 is needed for
XML checks; separate lib3mf setup and fixture Python/Caddy/ss prerequisites are
documented with those tests.

Workstation has only 3.5 GiB free. Use R730 for large builds. Clean only owned
disposable artifacts. Runtime inputs: R730
`/mnt/data10tb/codi-occ-four-corner-clean-20261104/line-frame/main.js` and
`main.wasm`; also box-git `/srv/data/codi-occ-four-corner-clean-20261104/line-frame-8c/`.
WASM pin `13617eda9a2118edfd1244b5d46523e7d9628a87ec995a0237b2b5cc58d532f2`;
current OCI worker `fc43d276fffc6e432b351cbba317fa98546c37ce754a4977018f8f24ecebe062`.
Preserve/review exact source and license archives when rebuilding.

Material agent stopped ports19691/19692/19694/19695 and Chromium19327; root's
independent browsers closed. Other agents' processes must be checked, not killed.

Finish the copied objective: saved-data integrity, consolidated CAD, specified
mechanical designs, material-aware actual core 3MF handoff. Bambu/physical prints,
physics, XR and the full CAD6 roadmap are deferred, not substitutes for this gate.
