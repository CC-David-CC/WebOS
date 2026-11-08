# WebOS native CAD project

Decision,2026-11-06: use our own `.cad` project format. It may be a ZIP container;
no third-party CAD format is required as its editable source. This is a recorded
design decision. A new archive codec/host source packet now exists, pending its
composed complete runtime qualification; this is not a working/deployed claim. Current qualified
native Save/Open fixtures are JSON and remain evidence of those exact builds.
Prototype accounts do not require a legacy-file migration project.

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

## Container requirements to implement

- [ ] Recognizable versioned manifest, independent of the filename extension.
- [ ] Explicit canonical units, design revision, stable entity/feature references
      and declared entry roles; keep kernel-specific handles out of authored data.
- [ ] Separate authored document pieces and large content-addressed binary entries;
      optional derived caches remain separately attributable and discardable.
- [ ] Bounded Worker-based streaming read/write/validation using the shared archive
      capability where appropriate. No heavy hashing/compression on the UI thread.
- [ ] Deterministic entry order/metadata and independent entry compression. Reuse
      unchanged content instead of recompressing the entire project as one stream.
- [ ] Validate supported versions, entry identities/sizes/hashes and references
      before atomically replacing the accepted document. Failed Open preserves it.
- [ ] Preserve native undo/reopen expectations, model intent and assignment identity;
      do not claim the transient Undo journal is saved unless explicitly supported.
- [ ] Native Save/Open and normal My files browser/server synchronization, including
      a second save with one small edit and fresh-account-session reopening.

ZIP alone does not establish efficient incremental synchronization. Test actual
archive layout, changed-chunk transfer bytes, peak memory, cancellation and Worker
cleanup. A tiny authored edit must not force rebuilding/retransferring unchanged
large cache entries. Native archive tests are ordinary app file workflows; the
cancelled Files race/security test is not resumed by this decision.

## Acceptance

- [ ] Original-rectangle plate workflow preserves the complete authored graph,
      parameters, units, identities and materials through `.cad` Save/Open.
- [ ] Pattern, dimension and region edits remain editable after reopening.
- [ ] Missing/stale optional caches regenerate or are explicitly unavailable.
- [ ] Malformed or unsupported projects refuse without corrupting accepted state.
- [ ] Worker processing, ownership cleanup, changed-chunk cost and transfer-memory
      bounds have measured evidence on actual Chromium/My files workflows.
- [ ] STEP/3MF and other qualified exports are generated from the same chosen native
      design revision; export never substitutes for native project persistence.
