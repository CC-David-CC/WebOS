# Signed authored revolve corpus

Preparation frozen before observations. All authoring uses registered public
commands in a real signed account; __CAD_APP is read-only accepted-state and
display evidence. No seeded source/model, fake native success or prism substitute.
Root owns services/package; only owned contexts are closed, shared Chrome kept.

Four setups run serially, stopping at the first failure:
1. Real empty XY plane, four public Segments [2,4]x[0,5]mm and real construction
   axis Segment x0 pointing+Y; explicit registered native build. Full revolve,
   creation Undo/Redo and +/-pi angle edits with mixed LIFO Undo/Redo retaining
   feature/output IDs/counters. Validate no-op/stale/unknown/invalid-angle
   refusals. Normal Save/sync/fresh Open/reedit across full/+half/-half/full.
2. Public point batch changes outer radius4->5, then actual axis x0->-1; full
   replay preserves original intent IDs. Crossing-axis edit rejects atomically;
   source Undo/Redo, Save/Open. No private sketch/model writes.
3. Genuine world-space box cuts lower axial half, then upstream angle edit
   replays unchanged Boolean child with original IDs/intent. Measures original
   and half-angle outputs, normal Undo/Redo. Revolve selections stay unavailable.
4. Hold a genuine positive selected-profile-revolve native reply, normal visible
   Close/Discard, require candidate termination/cancelled command/late inertness;
   fresh Open restores only the explicitly saved accepted revision.

Driver tolerances fixed before observation: native volume absolute1e-6mm^3,
native bounds absolute1e-7mm. Independent saved-source oracle by dxf uses
absolute1e-6 for both; stricter driver bounds remain separately required.
Baseline full60*pi, +/-half30*pi mm^3; right-handed +Y axis yields +half z[-4,0],
-half z[0,4]. Source radial expansion full105*pi; axis at-1 gives radii3..6,
full135*pi, x[-7,5],z[-6,6]. Compatible child's height is2.5mm. Every native
observation requires finite positive volume, valid single solid and exact runtime.

Saved evidence rows: {label,savedFile,sha256,binding,discovery,before,after}.
Binding includes actual returned face/profile Segment/axis/feature/body/region
IDs, engineRevision, current history angleRadians, exact ten authored fields and
sourceDigest from public discovery. IDs are matched verbatim, never parsed.
The saved raw file hash is independent; sourceDigest hashes solved serialization
and is NOT asserted equal to raw authored saved JSON. Closed-sketch inspections
and exact before/after public metrics accompany Save rows. Session Undo resets
on fresh Open. .jsketcher.json native intent remains the actual frozen format.

Run with qualified Node24/Puppeteer24.35 and fresh CODI_EVIDENCE; required env:
CODI_SIGNED_PINS,CODI_EXPECT_SOURCE,CODI_EXPECT_DESKTOP,CODI_TEST_URL,
CODI_TEST_CDP,PUPPETEER_CORE_PATH. Optional CODI_REVOLVE_CASE selects one named
setup. Driver verifies all core and outer pins before authoring. No full E13 or
full Gate1 pass is implied; incompatible-child/general revolve domains remain
outside this bounded corpus and explicit unsupported metadata is preserved.
