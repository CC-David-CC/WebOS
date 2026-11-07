# Separate-parts complete workflow oracle

`two_objects.py` consumes the already completed real public workflow in Desktop
`92dc8e59a`, `two-object-evidence-r1/`. Run only against its entire output directory:

    python3 oracle/two_objects.py /path/to/two-object-evidence-r1 > result.json

The original primary `check.py` and its frozen tolerances are unchanged. This
separate intake checks the actual four-feature native history, rectangle source
curve IDs against public region descriptors, public plate/box body bindings,
material assignments and each exact file SHA against the full workflow receipt.
It derives the plate at depth20 then25 with the same D10 through-hole, plus the
unchanged separate 10x20x30 box at [120,0,0]. Expected volumes are
`(5000-25*pi)*depth` and `6000` mm3. Exact cylinder volume is distinct from mesh
approximation, whose admissible excess comes from observed angular sampling/sag.

ZIP/CRC/XML checks follow the two real build entries and writer-generated integer
resource associations. Both parts legitimately have a region named `main`;
part/region pairs are distinct, as are public bodies and mesh/component/build
resources. The independent mesh helper checks topology, surfaces, bounds,
orientation, volume and safe material/void windings for each part. The separate
box must retain its exact canonical oriented triangles across the plate edit and
fresh Open; the edited and reopened plate must likewise agree.

Source is frozen before this whole-file oracle runs. No isolated predicate tests,
runtime changes, new browser authoring or fabricated successful geometry are part
of this extension. This remains a bounded measurable fixture oracle, not a
general embedding validator or slicer/physical-print qualification.

Actual complete-output check: PASS, source5e9d18e44. Three exported files, six
independent part mesh checks: plate residuals0.650928483/0.813660604/0.813660604mm3
are below measured sag bounds0.976464543/1.220580429/1.220580429mm3. Each box has
exact volume6000mm3 and the identical oriented triangle digest before/after the
plate edit and fresh Open. Edited/reopened plate triangles also agree exactly.
Both scoped `main` region mappings and all runtime/file/assignment bindings pass.
Portable result and source-bound producer record are in `two-object-evidence-r1/`.
