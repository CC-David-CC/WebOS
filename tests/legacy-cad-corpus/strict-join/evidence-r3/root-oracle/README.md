# Immutable root oracle artifacts for R3

Artifact review PASS for all **13 unique saved files** from the actual signed R3 producer: executing source4b036e6f8, evidence commit4710881d0, CAD224f3302d / desktopcf97976d9. The exact parent receipt is SHA256 `78f4f007e2da90fa680396968fbf3e8877fe32d92db4d88265f6509aabb6e6bc` (17 setups/70 rows PASS). [Review manifest](review-manifest.json) pins that receipt, its three actual executing sources, every saved file, public producer/output bindings and the supplied artifacts. Saved history/live operand consumption and recorded fresh Open measurements agree with those exact inputs.

Original root outputs are preserved byte-for-byte:

- `root-cell-oracle.json`: `/tmp/codi-join-root-r3-cells.json`.
- `root-cell-state-readback.json`: `/tmp/codi-state-cad-join-root-r3.json`.
- `root-saved-oracle.json`: `/tmp/codi-join-root-r3-saved.json`.

The two cell outputs are byte-identical; they are repeated readbacks, not independent implementations or additional authoring cases. The saved-intent output also agrees with the producer's existing canonical saved-file checker result.

Reviewed Python source is `test/agent-cad-corpus/strict-join/root-cell-oracle.py` at root commit947a58b4f, SHA256 `7c333dc2e5f0f98b378ac9e4c2379f992fd30b8ee98819ff33f546b57b29bb84`; immutable snapshots of it and the canonical Node saved checker are included. The Python script resolves opaque body IDs from actual public creation receipts, partitions raw axis-aligned box coordinates with exact Fraction arithmetic, evaluates Boolean cell sets and compares volume/bounds with recorded fresh Open measurements. Tolerances are1e-6mm³/1e-6mm (the authoring harness has its own stricter AABB check).

Scope stays **PASS_SAVED_SUBSET**: the cell checker treats Join as mathematical union. It does not prove native validity, connectivity/manifoldness, topology/ancestry, point probes, negative/lifetime/history tests or whole-corpus sign-off. The12 OCC/SMLib saved Join results remain distinct from the one Manifold **raw union**. Its output field named `nativeVolume` is a common checker label: for SMLib/Manifold it reads `reportedVolume`; representation/quality remain recorded separately, with no mesh-to-B-rep promotion.

This review read/hashed the supplied evidence and source; it did not rerun a checker, native kernel, browser or account. Original output JSON does not embed an executable digest or command timestamp. The manifest pins the root-supplied artifacts and the committed checker source without inventing that process metadata. Root retains fixture/browser cleanup ownership. No product or canonical state-machine document changed.
