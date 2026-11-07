# Complete 32-hole public export artifact oracle

Source-only preparation; no execution until the complete public workflow produces
all three native files and initial/edited/reopened3MF outputs with terminal PASS.
The previous real failed workflow is used solely to inspect its saved-source and
public receipt structure. Its missing export is not treated as a positive input.

    python3 oracle/thirty_two_holes.py /path/to/complete-32hole-workflow > result.json

The saved model must contain one actual independent XY plane and one selected
profile extrusion, four outer Segment sources and32 Circle sources. The exact
opaque IDs are corroborated against32 actual public append receipts and the
selected region's explicit outer/hole descriptors. Region IDs are compared as
opaque strings; their contents are never parsed. Circle centers/radii are read
from saved data and matched to the public recipe's8x4 grid, centersx10..80/y10..40
and radius2. Plane/curve/feature/body IDs, source data, constraints, manufacturing
identities and all history parameters remain exact except extrusion depth20→25
and the derived manufacturing revision. PLA/blue and one plate/main assignment
must persist across normal Save/fresh Open.

Independent analytic volumes are `(5000-128*pi)*20` and `(5000-128*pi)*25` mm3;
bounds are [0,0,0]..[100,50,depth]. The unchanged mesh helper measures all32 bore
walls and angular rings, validates Euler characteristic2−2*32=−62, independently
checks safe bore-center void/material/exterior winding and bounds, and derives
the source-to-mesh volume allowance from observed per-hole sag/angular sampling.
It does not demand1e-6 equality between curved BRep and mesh volumes. The edited
and reopened oriented triangles must match, independently of index/order.

ZIP/CRC/XML/unit, writer-generated resources, part/region/material/appearance
provenance, browser/server file SHA, runtime/driver pins and exact saved-source
bindings are checked as complete artifacts. Original primary and two-object
oracles remain unchanged. No synthetic successful mesh, Native rerun, browser
runtime, microtest or geometry mutation is part of this source-only preparation.
