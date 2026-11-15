# CAD file scope

User clarification, 2026-11-05: only our own editable CAD saves need to open.
Third-party CAD imports are outside this release milestone.

| File | Open/import | Save/export | Purpose |
| --- | --- | --- | --- |
| Native project (`.jsketcher.json`) | Required | Required | Editable source: parameters, constraints, feature history, identities and assignments. |
| DXF (`.dxf`) | Not required | Export only | Supported 2D sketch geometry for external tools. |
| Core model 3MF (`.3mf`) | Not required | Export only | Manufacturing handoff with supported part/region/material structure and units. |

These are scoped capabilities; the passing corpus and explicit unsupported
geometry remain authoritative. A listed extension does not qualify every curve,
profile, body or external consumer. Native saves remain the source of truth;
DXF and 3MF are derived handoffs from a particular accepted revision.

STEP and other interchange imports are not acceptance requirements here.
Future interoperability work may add exports or deliberate imports separately.
Do not build external CAD importers while native persistence, modeling and the
required exports still need qualification. File upload and ordinary file use in
other WebOS apps are unaffected by this CAD-specific decision.

The WebOS Import DXF toolbar/message/host route is removed from the candidate.
Normal Open from My files remains the supported CAD input. No public deployment
is claimed by this scope update; final matched browser/host qualification follows
integration of the remaining core work.
