# Sweep acceptance contract and independent fixture oracle

**No native, Worker, browser, public agent, history replay or Save/Open sweep is
qualified by this directory yet.** The current source readiness audit exposes a
legacy `SWEEP` operation using `MSketchLoop`/DRAW `mksweep/addsweep/buildsweep` and
`getShell`. That path supplies no evidence for the shared owned Worker feature.
Gate1 E14 remains open. Native and shared-model work belongs to other agents.

This directory owns offline arithmetic, source/identity corroboration and
acceptance cases. It imports no production geometry engine or solver, generates
no native geometry and fabricates no successful Worker response. Unit tests use
explicit synthetic source and metadata examples to test the oracle itself.
`cases.mjs` provides optional **native component inputs**, with fixture-only IDs;
using them does not constitute genuine public authoring or saved-document proof.

## Agreed authored and transient contracts

One existing design document/history, with exactly **eleven** authored fields:

```js
{version:1,unit:'millimeter',engine:'occ',engineRevision,featureId,
 faceId,regionId,pathFaceId,
 pathCurves:[{curveId,reversed:boolean}], // ordered actual source-local refs
 transport:'corrected-frenet',bodyPolicy:'separate'}
```

No solved geometry, frame, digest, native handle or cached output is saved in
these parameters. Profile and separate path source are captured from the same
current project revision/generation, solved separately, and bound into **one**
ephemeral evaluation request. Saved fields preserve the selected build and
ordered direction references across edits/replay/Open; no fallback engine.

The root-owned transient contract is:

```js
{op:'solid.profile.sweep',version:1,unit:'millimeter',
 source:{faceId,sourceSha256},frame,region,
 path:{source:{faceId,sourceSha256},frame,
       curves:[{kind:'segment'|'arc',id,a:[u,v],b:[u,v],
                c:[u,v], // Arc only
                reversed:boolean}]},
 transport:'corrected-frenet'}
```

The source Arc is the actual `a/b/c` native object, with **CCW a→b** semantics.
`reversed` follows that same branch backward, starting at b. Swapping endpoints
without preserving branch semantics must not turn a major arc into a shortest
minor arc. The inherited source full-circle predicate is exactly
`abs(a.u-b.u)<1e-6 && abs(a.v-b.v)<1e-6` (strict inequalities); this declared source
meaning is not a newly invented geometric repair tolerance.

Placement preserves the actual source geometry. The profile **plane** contains
the directed path start and its normal is parallel or antiparallel to the initial
tangent. Neither frame-origin nor profile-centroid equality is a general
requirement. No hidden translation/rotation/scaling, path rounding or twist is
permitted. Corrected-Frenet supplies the declared transport; no added twist.
Both source frames are right-handed orthonormal millimeter frames.

Native first scope is one nonzero Segment or one open circular Arc. Longer G1
chains, corners, branches, closed paths, guide/twist/taper and cut/Join policies
remain separate capability work, not invalid drawable geometry by definition.

## Frozen analytic cases

Native volume tolerance is **absolute1e-6 mm³**, bounds **absolute1e-6 mm**.
Oracle frame admission uses1e-12 dimensionless orthonormality and1e-9 mm plane/
center checks. These do not rewrite any coordinates or change application/kernel
tolerances. Analytic point classifications are separate from volume/bounds and
must come from actual native queries bound to the output and query coordinates.

| Case | True volume | World bounds |
|---|---|---|
| Straight disk r2, length10 along+Z | 40π | [-2,-2,0]→[2,2,10] |
| Straight annulus ro2/ri1, length10 | 30π | Same outer bounds |
| Straight rectangle4×1, length10 | 40 | [-2,-.5,0]→[2,.5,10] |
| Quarter disk r2 on radius10 path | 20π² | [0,0,-2]→[12,12,2] |
| Quarter annulus ro2/ri1, radius10 | 15π² | Same outer bounds |
| Quarter radial4×vertical1 rectangle, radius10 | 20π | [0,0,-.5]→[12,12,.5] |

Straight profiles use an XY section and a separate path source frame
U=+X,V=+Z,N=−Y; the Segment is local(0,0)→(0,10). Reverse references start at the
other end; ±parallel section normals are accepted. Straight volume is source
area times physical path length. Disk/annulus bounds use analytic circle
extents in the actual source frame; polygon bounds use the real source vertices
and translated end section. Off-center straight profiles are covered.

Quarter path: source XY, center(0,0), a=(10,0), b=(0,10), CCW. Initial section is
at(10,0,0), U=+X,V=−Z,N=+Y. Reversal starts at(0,10,0), with fixture section
U=+Y,V=+Z,N=+X. It reverses the **same quarter**, not the complementary arc.
The centered quarter fixture uses `V=area*R*abs(angle)`. Its section is carried
in radial/binormal coordinates; angular endpoints and quadrant critical angles
give the exact coordinate extrema. No mesh or kernel volume feeds expectations.

Probes include material, exterior, side wall, flat cap and beyond-start points;
annuli additionally require bore-outside and inner-wall-boundary. The asymmetric
quarter rectangle has material at `[11.5/√2,11.5/√2,0]`; a90° roll changes that
point from inside to outside and changes its z bounds. Round sections alone
cannot qualify roll. A cavity/bore is legitimate geometry, not multiple physical
material definitions or a reason to require a single boundary surface.

For independent native **major-arc** control (outside this first oracle domain),
source a=(0,10)→b=(10,0) CCW is3π/2: disk60π², annulus45π², rectangle60π, bounds
[-12,-12,-ro]→[12,12,ro] (rectangle z±.5). It must not be shortened. The oracle
explicitly refuses that unqualified domain instead of calling it invalid.

Similarly, independent native off-center controls may use a circular section
whose centroid is one millimeter radially outward: radius10 path/r2 section
then has centroid track radius11, volume22π² and bounds[0,0,-2]→[13,13,2]. A
one-millimeter +localV offset with initial V=−Z instead yields20π² and z[-3,1].
These formulas explain why blindly applying profileArea×originalPathLength to
all off-center curved profiles is wrong. They are not covered by this centered
oracle's acceptance function and do not authorize rejecting valid native input.

## Test-only observation adapter

`deriveSweepExpectation` takes a read-only capture:

```js
{unit:'millimeter',featureId,engineRevision,transport:'corrected-frenet',
 profile:{faceId,digest,frame,sketch:{objects:[/*actual source objects*/]},
          region:{regionId,outerCurveIds,holeCurveIds}},
 path:{faceId,digest,frame,sketch:{objects:[/*actual source objects*/]},
       refs:[{curveId,reversed}]}}
```

This is an oracle capture, **not** another public API or document format. IDs
come from real authoring/discovery or explicitly labeled native fixture inputs;
no opaque region ID is decoded. Digest strings are genuine solved-source
bindings, not hashes falsely recomputed from differently serialized authored
JSON. `sourceFingerprints` additionally hashes the complete captured source,
frame and selection for before/after preservation checks.

`corroborateSweepPath` compares the agreed transient path to independently
captured raw source a/b/c, actual ordered IDs/direction and both source envelopes/
frames. Its profile check is envelope/frame/region identity only; genuine profile
curve reconstruction remains the provider's separate obligation.

`checkSweepObservation` requires actual unit/build/feature binding, both source
bindings, real before/after input fingerprints, native validity/one solid,
native volume/bounds and the complete native probe list. Optional retained-owned
geometry snapshots must match. `checkSweepPreservation` also checks refused
operations without claiming an output exists. A standalone call with arbitrary
JSON is **not a native certificate**. The producer must supply genuine native
measurements and queries through the authenticated owned Worker path.

## Refusals and remaining coverage

Counterexamples cover wrong units/build/source/digest, altered frame/radius/path,
wrong native volume/bounds/material probes, changed inputs, wrong saved direction
and unknown native fields. Negative real operations must preserve both sources,
all prior accepted outputs, counters/journal where promised, and resource owners.
Refusal must distinguish invalid request, unavailable source, unsupported
capability/domain, native failure and cancellation; no auto-heal or fallback.

The oracle currently covers circle/one concentric annulus/exact rectangle;
quarter curved sections must be centered and the path frame a translated signed
permutation frame. Arbitrary polygons, off-center curved sections, arbitrary
curved-frame rotations and general path chains may be valid CAD sweeps but are
**oracle-unsupported**, not invalid geometry. Even a tiny mathematically open
arc at the strict source threshold does not prove native small-scale support.
Actual native success/refusal, Worker cancellation/cleanup, source edits,
dependent replay, Undo/Redo, saved intent and fresh Open remain unqualified until
their own genuine component/app evidence exists. These19 offline tests do not
close E14 or the broader Gate1 sweep requirement.

```sh
/tmp/codi-files-move-node/bin/node --test test/agent-cad-corpus/sweep/oracle.test.mjs
```
