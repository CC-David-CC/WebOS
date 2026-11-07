# Independent E13 fixture oracle

This is an offline, bounded arithmetic oracle. It constructs no geometry and
imports no production geometry, solver, Worker, mesh or CAD code. Unit tests use
explicit synthetic source/metadata examples, not simulated native successes.
Actual acceptance waits for the separate agent's public authoring and saved
native evidence on the source-matched runtime.

Frozen before runtime observations: volume tolerance **absolute 1e-6 mm³**, bounds
tolerance **absolute 1e-6 mm**. The authoring driver's independently frozen bounds
check remains stricter at **1e-7 mm**; this oracle does not replace that check.
No relative widening, global epsilon, snapping or repair is introduced.

Required actual receipt row:

```js
{label,savedFile,sha256,
 binding:{faceId,profileSegmentIds:[/*4 real public IDs*/],axisSegmentId,
          featureId,bodyId,regionId,engineRevision,sourceDigest,angleRadians},
 discovery: /* unchanged public inspect-worker-revolve-regions result */,
 before:{revision,featureId,bodyId,engineRevision,metrics},
 after: {revision,featureId,bodyId,engineRevision,metrics}}
```

`angleRadians` comes from the **current** public revolve history, not an old
creation receipt after an angle edit. Optional `binding.authored` corroborates
all ten saved fields against that public history entry. Region/curve/axis/body
IDs remain opaque and are matched verbatim against real discovery/receipts.
Explicit region descriptor membership is required; no region ID is decoded.

The raw Save SHA binds the native bytes. Discovery's digest belongs to the
**solved source serialization**, so it is checked only as a public cross-evidence
binding. This oracle neither re-solves nor falsely hashes authored JSON as that
solved serialization. Revisions are nonempty evidence tokens; explicit
`expectedRevision` can reject a mismatched same-state observation. A fresh Open
may legitimately have a new token. Offline files alone cannot establish temporal
currentness; the authoring driver owns capture/currentness guards.

Initial domain: one native v2 millimeter design, canonical XY plane at zero
depth without datum, one stage, four actual normal Segment edges forming one
exact closed rectangle strictly right of one nonzero vertical source Segment
axis, and one `WORKER_SELECTED_PROFILE_REVOLVE_V1` with exactly ten authored
fields. Unknown profile/plane/axis classes return **ORACLE_UNSUPPORTED**, which
does not imply invalid geometry. No torus or generic geometry engine is implied.

From saved coordinates, let inner/outer radii be `xmin-axisX`, `xmax-axisX`, height
`ymax-ymin`, and signed sweep `a`. Then
`V=abs(a)*(outer²-inner²)*height/2`. Native world coordinates are
`x=axisX+r*cos(t)`, `z=-r*sin(t)`, with `t` running from zero to `a*axisYSign`.
Extrema use both radii, interval endpoints and exact quadrant critical angles;
they are not sampled from tessellation. For x=[2,4], y=[0,5], axis +Y at x=0:

- Full ±2π: volume60π, bounds[-4,0,-4]→[4,5,4].
- +π: volume30π, bounds[-4,0,-4]→[4,5,0].
- -π: volume30π, bounds[-4,0,0]→[4,5,4].

Axis reversal swaps the two half-volume angular bounds. Source and axis edits
derive fresh dimensions from the saved coordinates, without changing identity
bindings or using baseline hardcoded dimensions. Native acceptance additionally
requires finite measurements, one actual valid solid and exact build identity.

```sh
/tmp/codi-files-move-node/bin/node --test test/agent-cad-corpus/revolve/oracle.test.mjs
/tmp/codi-files-move-node/bin/node test/agent-cad-corpus/revolve/check-saved.mjs OUTPUT_DIRECTORY
```
