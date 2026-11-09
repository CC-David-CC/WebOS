# CAD library integration: current queue

Updated 2026-11-09. Strategy approved; native assessment is PARTIAL. Browser integration remains
unqualified and the production runtime is unchanged. This is the Host coordination entry, not a second CAD model.

The full plan is in ACAD commit
`b6a530e0f8c2de828a022a58ba713e7c62c0125a`, file
`docs/proposals/CAD1-LIBRARY-FIRST-INTEGRATION-20261109.md`.
Retrieve that commit from `box-git:/srv/data/git/ACAD.git` or
`r730:/mnt/data10tb/git/ACAD.git`. Local working copy:
`/tmp/codi-acad-foundation-next-20261109`. A fresh checkout of both repositories
supplies this coordination record and the full plan; no private PC state is
required to understand it. Actual run outputs remain separately bound evidence.

## Baseline and open proof

- Ordinary exercises: **21/21 QUALIFIED**; full Gate 1 remains **OPEN**.
  E17 assembly is Gate 2.
- Current frozen runtime: Core `0afb07fe8e216ba9a03cf21923e0ab70aed72546`,
  Host `be24fbc232c967912f529053d34a9d407b369a39`, 285 pins.
- Extent R4 whole26910 **PASS0**, frozen acceptance7e1e2b6:
  144 rows, 1674 commands, nine native Saves/fresh Opens, 14 artifacts;
  original sources unchanged, writes settled and own contexts retired.
- Six STEP reads **PASS0** after Node24 child-loader correctionf3da26b;
  unchanged compiled reader. First CLI failure remains preserved.
- FIRST artifact oracle62543 **FAIL1**: exact two-XY cylindrical-strip assumption.
  Actual blind mesh generator coordinates differ by nine ULP. This finding
  does not qualify the complete mesh or establish a kernel defect.
- Complete mesh/finite-surface/intent proof and both actual SVG reviews remain
  open. No Root whole/reader/oracle job is currently active. Countersink06b7fe6
  retains its separate completed qualification.

## Native evaluation now completed, full proof still open

Pinned environment and readonly adapter executed on R730. Original six meshes
pass raw indexed topology, Trimesh winding/watertightness and CGAL exact-input
graph/degeneracy/self-intersection/closed-volume checks. All original arrays and
archives remain unchanged. Actual evidence: Core test/library-validation/
evidence-first/ (dc27a53) and evidence-r2/ (b6a530e).

First lib3mf material mismatch was an observer namespace error, diagnosed from
v2.5.0 source3665ff8: XML base indices are not API PropertyIDs. Correction2355b7c
maps actual enumerations, without changing exported material assignments. Its
whole six-file assessment97661 still says package UNCERTAIN at the later metadata
comparison. Missing metadata observations are added in current source, UNRUN.
Do not infer an exporter defect or waive requirements from this incomplete read.
Both batches are terminal; no Root qualification process is active.

L1 inventory41f7189 maps mature OCCT APIs to actual binding/history gaps. A single
source-bound finite-curve interface is the first small package: intersections,
then atomic trim/extend, reused later by projection/offset. Existing history,
transactions and ownership stay authoritative. Native acquisition/adapters do
not close the finite-surface accuracy proof, SVG review or remaining Gate1 scope.

## Library boundaries and serial/parallel queue

| Package | Boundary | Dependency / next action |
|---|---|---|
| Existing OCCT | General operations through current Worker kernel API | Inventory native capability versus missing bindings; keep authored graph/history ours |
| lib3mf | Package, units, component/material associations | Native evaluation first; retain raw Float64 geometry separately from its reviewed single-precision Position/Transform API |
| Trimesh and CGAL | Read-only general mesh checks and bounded geometric comparisons | First compare the six actual meshes; no repair/weld/reindex or volume-only certification |
| CadQuery/OCP | Optional native STEP/operation reference | Add only if useful beyond current reader; it is also OCCT, not an independent kernel |
| TechDraw | Drawing geometry/annotation reference or selected reusable pieces | Keep browser UI and shared document/commands; no whole FreeCAD port |

Run operation inventory, native validator assessment and existing C11 source
work in parallel branches. Root alone integrates common registries/closures and
executes coherent browser wholes. Full-surface proof needs the actual validator
findings; completed whole outputs then receive independent artifact checks and
actual SVG review. Finish resource/cleanup qualification before final combined
beta and handoff. No per-edit microtest loop or repeated unchanged qualified runs.

Reports bind exact inputs, revisions, library/adapter build, units and limits.
Format validity, topology, self-intersection, source intent, deviation and resource
outcomes stay distinct. Qualification is derived from required current evidence.
A geometry edit makes earlier evidence historical, never silently current.

No library becomes an alternate document/history owner. Heavy work stays in
Workers; consume existing versioned My files snapshots and ownership leases.
No main-thread bulk copies, silent tolerance changes or new network relay.
Pinned native evaluation on R730 precedes any selected production WASM adoption.
The detailed plan records precision, license, raw-input preservation, uncertainty,
resource measurements, lane ownership, estimates and final acceptance conditions.

Initial fit assessment remains partial: native geometry results exist; package
metadata and independent full-surface accuracy still need closure. Provisional
remaining work after extrusion qualification stays 1–2 weeks, with a third-week
contingency; it is not a countdown from today. No estimate reduction is claimed
before coverage and integration costs are measured.

Canonical status: [work queues](WEBOS-WORK-QUEUES.md),
[state contracts](STATE-MACHINES.md), [Gate 1](CAD-ENGINE-GATE-1.md).
