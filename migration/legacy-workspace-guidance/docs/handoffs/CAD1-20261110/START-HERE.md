# CAD 1.0 restart handoff — 10 November 2026

This is the entry point for resuming ACAD within the WebOS. The user requested a verified portable checkpoint, then a pause. Read VERIFICATION.md before trusting any restart claim. Gate 1 remains OPEN. Do not resume implementation until the user resumes it.

## What the projects are

Desktop Preview is the complete browser WebOS: login, windows, menus, My files, shared app lifecycle and many separately integrated applications. Its current integration source is the CodiServer-distro repository on box-git (CodiServer.git on R730). `active-system/` contains the functional desktop; `apps/` contains the app integrations. The older `desktop-lab/` and `/desktop/` sizing prototype are separate.

ACAD (agent computer aided design) is an independent CAD repository, derived from JSketcher inspiration. The desktop bundles its compiled output into `apps/system/jsketcher`: that is a legacy internal integration ID, not a second CAD engine or source of truth. ACAD owns authoring, constraints, feature history, geometry adapters and CAD serialization. The desktop owns account files and mounted window lifecycle. Human and agent commands must converge on the same checked operations.

The original JSKetcher.git fork is frozen separately. Do not put ACAD changes back there. The many other desktop apps have their own folders and varying maturity; their presence does not mean qualification. CURRENT-CODE is an inspection snapshot, not the authoritative integration checkout.

## Repositories and exact checkpoint

| Repository | box-git | R730 | Integration branch / current source |
|---|---|---|---|
| ACAD | `/srv/data/git/ACAD.git` | `/mnt/data10tb/git/ACAD.git` | `integration/foundation-next-20261109`; pre-handoff `cf81fbb111f38d03c68897a35ecb3718754f1436` |
| Desktop | `/srv/data/git/CodiServer-distro.git` | `/mnt/data10tb/git/CodiServer.git` | same branch; pre-handoff `1d1abd9c6d49e47352f7d0184e122e1690d71b88` |
| Native dependencies | `occt-interpreter-codi.git`, `usd-brep.git`, `manifold-codi.git` | same names plus `smlib-wasm.git` | all-ref bundles in the private handoff; exact runtime inputs are independently pinned |
| Original inspiration | `/srv/data/git/JSKetcher.git` | `/mnt/data10tb/git/JSKetcher.git` | preserve frozen fork; independent from ACAD |

Later handoff-only commits are recorded in the external CHECKPOINT manifest to avoid a self-referential Git hash. Do not assume a documentation HEAD is a compiled application revision.

The actually exercised R8 runtime is ACAD `4fa264907c9bf44a6a0d857aa5495bc2c3cc6073` plus Desktop `64e70e9b548e41006f8334d7b349654f88459732`. Original build/stage are `/mnt/data10tb/codi-acad-assembled-build-20261110-r8`, `/mnt/data10tb/codi-desktop-assembled-20261110-r8`, `/mnt/data10tb/codi-acad-assembled-stage-20261110-r8` and its `-apps` sibling. Corrected saved-content acceptance is `ec14fc8fdf34548319d2953a776e443097a408ab`.

## Where to start on another machine

The durable private directory is `r730:/mnt/data10tb/codi-handoffs/CAD1-20261110/`. A second copy is maintained under `box-git:/srv/data/codi-handoffs/CAD1-20261110/`. Read the final CHECKPOINT/VERIFICATION receipts and SHA256SUMS there. The local convenience copy is `/home/dflanag3/CodiServer/desktop-preview/HANDOFF-CAD1-20261110/`.

With authorized LAN SSH access:

```sh
git clone --branch integration/foundation-next-20261109 box-git:/srv/data/git/CodiServer-distro.git desktop
git clone --branch integration/foundation-next-20261109 box-git:/srv/data/git/ACAD.git acad
# Read before doing work:
cat desktop/docs/handoffs/CAD1-20261110/START-HERE.md
```

Source Git alone does not contain ignored dependency caches and every compiled native input. Use the verified R730 runtime-input backup and build recipe in RESTART.md. No browser profile, existing tab, cookie, key or service account state from this PC is required. A replacement machine still needs authorized LAN credentials, Linux build/browser system libraries and network access to the LAN machines; secret credentials are deliberately not bundled.

## Goal, scope and reading order

Qualify CAD Gate 1 as an agent-drivable, human-viewable parts system with common operations, explicit failure semantics, persistent intent and end-to-end saved-file workflows. Gate 1 includes the saved 21 representative exercises and the broader required competency/edge-case inventory; exercise 17 (hinged assembly) was moved to Gate 2. Passing representative exercises does not close the full competency gate. No new human UI is the priority.

1. This directory: STATUS.md, RESTART.md, SILOS.md, VERIFICATION.md.
2. Desktop `docs/WEBOS-WORK-QUEUES.md` (operational queue), `docs/STATE-MACHINES.md` (states/invariants/transitions), `docs/evidence/CAD-GATE1-BASELINE-20261106.md` (scope/evidence).
3. ACAD `docs/handoffs/CAD1-CURRENT-GOALS.md`; its top dated checkpoint supersedes chronological entries below. Old text saying RUNNING is historical, not a live process handle.
4. Desktop `docs/HANDOFF-FILES-CAD-2026-11-04-CURRENT.md`, plus the saved CAD capability ladder/plans linked by the queues. Preserve CAD 2–6 and XR research as later scope, not Gate 1 blockers unless explicitly required by Gate 1.

## Constraints that must survive the handoff

- One authored parametric document, stable identities, explicit transactions and shared UI/agent operations. Render meshes are derived, never the editable source.
- OCCT remains preferred. Retain SMLib and secondary mesh/manifold adapters where actually supported; report unsupported operations honestly. Choose a backend per regeneration, not silent mid-history fallback. A kernel agreement is not independent truth.
- Heavy calculations, hashing, encoding and geometry stay in Workers. Derive state where possible. Preserve the last valid authored model on rejection; distinguish invalid geometry, inconsistent constraints, planar topology, failed kernel operations and broken dependencies.
- Native `.cad` is the editable source; STEP/3MF/STL/DXF/other qualified exports are handoffs, not recoverable feature history. Material identity, region identity and independently arrangeable objects versus aligned regions remain explicit.
- Saved data is recoverable; unsaved edits need not survive forced tab/process closure. Do not depend on crash cleanup. Do not close a normal app until a save has acknowledged its browser generation, unless the user deliberately discards.
- Keep existing file-size/storage guards; chunk/stream transfers and only changed chunks where supported. Do not treat narrow CAD file tests as complete Files/capacity proof.
- No external network relay through box-webhost, including ping. No filesystem-race, foreign-account or fault-injection tests: those were cancelled. No new tests/retries after two failed attempts without notes and user notice.
- Do the bounded implementation/review batch, then grouped end-to-end qualification. Do not test every tiny edit. Preserve original failures and independent verifier custody.
- No deployment during this handoff. Never hand-edit derived Caddy; use reviewed managed hosting workflow. `/desktop/` stays untouched. Later beta changes do not automatically promote main.
- Source-distribution/release packaging waits for qualification. These are private recovery backups, not a release or gate signoff.

## Restart instruction to give a new Codex

“Read desktop/docs/handoffs/CAD1-20261110/START-HERE.md and the matching private verification receipts on R730. Verify the checkpoint, then resume CAD 1.0 from the documented queue. Preserve the separate ACAD and Desktop repositories, historical scope and unmerged silos. Use bounded parallel source silos with one integrator; shared-file composition, coherent builds and browser whole runs are serial. Keep all source and required runtime inputs on R730/box-git and keep local disk small. Do not repeat qualified workflows without a relevant changed dependency. Do not call Gate 1 complete until its full competency matrix, resources and combined beta delivery pass.”
