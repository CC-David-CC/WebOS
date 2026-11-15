# Complete public3MF workflow oracle

Prepared independently from actual export-workflow source and saved/public binding schema. CONTRACT freezes mm/surface/volume-approximation/probe assumptions before executing on real3MF outputs. This checker imports no production mesh validator, encoder, Native runtime or browser helper.

Run AFTER a complete real export workflow produces its receipt, three raw native snapshot files and initial/edited/reopened3MF:

```
python3 test/agent-cad-corpus/manufacturing-shared/oracle/check.py /path/to/complete-workflow-output > independent-3mf.json
```

The current domain is exact100×50×20 XY plate, centered throughD10→D14, explicit PLA/blue, source/producer/region/body identities corroborated to actual saved history and public discovery/creation values. Region/body IDs remain opaque; no grammar parsing. It checks browser/server artifact SHA records and browser commit receipts separately from geometry, derives source geometry, verifies ZIP/CRC/XML/resources/material/provenance, independently checks indexed topology/surfaces/bore radii/chord sag/volume bounds/material-void points, and compares edited/reopened measured geometry and exact intent. No1e-6mesh/BRep-volume equality is claimed; only optional matching-ring polygon formula arithmetic uses that tolerance. Canonical oriented-triangle equality is reported separately from tolerance equivalence.

The shared mesh helper already accepts a list of up to32 actual circular bores and checks Euler2−2N. A future real32-hole public workflow needs a separately frozen saved-source/receipt intake and independent actual-source centers/radii; none is qualified by this initial centered-hole run. Multiple material regions, arbitrary frames/shapes, slicer/physical print and general production embedding are outside this oracle.

Actual complete workflow PASS on /tmp/codi-manufacturing-export-e2e-20261107-r2, CADd0d8f1a0f/Desktop1a0c56dbe, sourcea769 frozen before execution. Portable result/source producer in evidence-r1; exact raw input SHA included.3exports260v/520t/Euler0; all12safe probes pass. D10 analytic98429.2036732051 vsmesh98429.85460168804, excess0.65092848<observed-sagbound0.97646454mm³. D14 analytic96921.239199482 vsmesh96922.51501930856,1.27581983<1.91386954mm³. Polygon formula agrees; edited/reopened canonical oriented triangles exactly equal, volume difference0. Radius6 material→void witness passes.32holes not run/qualified by this result. No new Native/browser/runtime/slicer/print claim.
