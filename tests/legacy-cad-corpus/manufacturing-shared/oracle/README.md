# Complete public3MF workflow oracle

Prepared independently from actual export-workflow source and saved/public binding schema. CONTRACT freezes mm/surface/volume-approximation/probe assumptions before executing on real3MF outputs. This checker imports no production mesh validator, encoder, Native runtime or browser helper.

Run AFTER a complete real export workflow produces its receipt, three raw native snapshot files and initial/edited/reopened3MF:

```
python3 test/agent-cad-corpus/manufacturing-shared/oracle/check.py /path/to/complete-workflow-output > independent-3mf.json
```

The current domain is exact100×50×20 XY plate, centered throughD10→D14, explicit PLA/blue, source/producer/region/body identities corroborated to actual saved history and public discovery/creation values. Region/body IDs remain opaque; no grammar parsing. It checks browser/server artifact SHA records and browser commit receipts separately from geometry, derives source geometry, verifies ZIP/CRC/XML/resources/material/provenance, independently checks indexed topology/surfaces/bore radii/chord sag/volume bounds/material-void points, and compares edited/reopened measured geometry and exact intent. No1e-6mesh/BRep-volume equality is claimed; only optional matching-ring polygon formula arithmetic uses that tolerance. Canonical oriented-triangle equality is reported separately from tolerance equivalence.

The shared mesh helper already accepts a list of up to32 actual circular bores and checks Euler2−2N. A future real32-hole public workflow needs a separately frozen saved-source/receipt intake and independent actual-source centers/radii; none is qualified by this initial centered-hole run. Multiple material regions, arbitrary frames/shapes, slicer/physical print and general production embedding are outside this oracle.
