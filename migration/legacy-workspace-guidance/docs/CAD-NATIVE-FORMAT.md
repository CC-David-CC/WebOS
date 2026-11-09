# WebOS native CAD project

Decision,2026-11-06: our editable native format is `.cad`, with a versioned ZIP
container. Its ordinary functional lifecycle is qualified; it is no longer a
JSON-only or pending-codec project. Exact ACAD proof is
`test/native-cad-container/evidence-r6`: Core32ae9c8a10659e43a3c5a5f4f51602b8aad64161 /
Host60ec30ee9ea30790162e61b5e5e43e5696d00034: 38 whole checkpoints, four actual
native Saves with server-byte equality, fresh Opens, twelve derived exports, six own
malformed Open refusals and ten observed codec Workers all retired. FIRST
independent source/archive/artifact oracle passed. Other later finite `.cad`
workflows retain their own exact producer/evidence; they do not establish a
universal document/resource qualification.

The active remaining limitation is the representative-size resource envelope:
large authored content, changed-chunk/unchanged-span costs, peak memory, heavy
main-thread dirty comparisons/source hydration and cleanup/capacity measurement.
No account migration is needed. Historical JSON evidence remains evidence of
its original builds, not the current native container or a migration requirement.

## Authority and scope

The native project preserves authored parameters/units, sketches/constraints,
feature definitions/dependencies, persistent identities and material assignments.
The selected kernel evaluates B-rep geometry for that revision. Display meshes,
manufacturing meshes and previews are derived; optional caches must identify
source revision, kernel/build and quality settings, and cannot override authored
intent. A project remains editable without an agent provider or cached viewport.

Only our native project requires editable import now. STEP/core3MF/DXF and later
STL/glTF are export or optional viewing boundaries. Viewing foreign geometry does
not recover our feature history. STEP exports evaluated CAD geometry; core3MF
exports manufacturing geometry and supported units/parts/material structure.
Their actual support status remains in CAD-ENGINE-GATE-1.md.

## Container requirements and bounded current evidence

- [x] Recognizable versioned manifest, independent of the filename extension.
- [x] Explicit canonical units, design revision, stable entity/feature references
      and declared entry roles; keep kernel-specific handles out of authored data.
- [~] Separate authored pieces/content identities are functional. Large binary/cache
      producers and their representative-size cost are not qualified. Optional
      derived caches remain separately attributable and discardable.
- [~] Functional bounded Worker-based read/write/validation using the shared archive
      capability is qualified in the finite archive workflow. Codec JSON/UTF-8/
      hash/CRC/compression is in its Worker; existing main-thread capture/dirty
      comparisons/hydration and large capacity remain open.
- [x] Deterministic entry order/metadata and independent entry compression. Reuse
      unchanged content instead of recompressing the entire project as one stream:
      exact unchanged Save SHA/zero changed-entry encoding and956bytes of actual
      compressed/local drawing-span reuse after Open/reedit independently proved.
- [x] Validate supported versions, entry identities/sizes/hashes and references
      before atomically replacing the accepted document. Failed Open preserves it.
- [x] Preserve native undo/reopen expectations, model intent and assignment identity;
      do not claim the transient Undo journal is saved unless explicitly supported.
- [x] Native Save/Open and normal My files browser/server synchronization, including
      a second save with one small edit and fresh signed-session reopening.

ZIP alone does not establish efficient incremental synchronization. Test actual
archive layout, changed-chunk transfer bytes, peak memory, cancellation and Worker
cleanup. A tiny authored edit must not force rebuilding/retransferring unchanged
large cache entries. Native archive tests are ordinary app file workflows; the
cancelled Files race/security test is not resumed by this decision.

## Acceptance

- [~] Typed plate/hole/material/drawing native workflow preserves the authored graph,
      parameters, units, identities and materials through `.cad` Save/Open. Final
      affected original-rectangle/pattern/treatment composition retains its own
      qualification requirement; older JSON proofs are not relabeled `.cad`.
- [~] Actual native dimension/reedit/travel is qualified; remaining combined
      pattern/region/document domains need their exact current producer evidence.
- [~] Optional caches remain non-authoritative and separately attributable; no
      automatic public cache producer or broad cache-acceleration claim is made.
- [x] Six exact own malformed variants refuse without corrupting accepted state;
      qualified valid Open and reedit prove healthy continuation.
- [~] Functional Worker ownership/retirement has evidence. Representative-size
      changed-chunk cost, responsiveness and transfer-memory bounds remain unqualified.
- [x] Twelve actual STEP/core3MF/SVG exports from the recorded native lifecycle
      are independently checked and bound to the same chosen native
      design revision; export never substitutes for native project persistence.


Checkboxes describe the finite evidence above, not arbitrary size/backend/input
coverage or a whole-Gate1 signoff. Native container admission ceiling is 128 MiB; it is an
admission ceiling, not a measured capacity/performance result. Unchanged entry
reuse still requires complete integrity verification and Files performs its own
outer integrity/delta scans. Do not claim zero hashing, zero copies, a network
saving or immediate physical RAM reclamation from codec ownership alone.

Current release status is maintained in `docs/evidence/CAD-GATE1-BASELINE-20261106.md`;
`docs/WEBOS-WORK-QUEUES.md` owns scheduling and `docs/STATE-MACHINES.md` owns
transitions/unknown-write/ownership invariants. No Files race or foreign-account
campaign is resumed by resource qualification.
