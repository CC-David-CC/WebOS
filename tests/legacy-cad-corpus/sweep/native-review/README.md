# Independent recorded native sweep review — R3

This independently reviews the genuine full-main C++→WASM FFI receipt from
`r730:/mnt/data10tb/codi-occ-owned-sweep-main-20261107-r1/receipt-r3.json`.
The raw208193-byte receipt is preserved with SHA256
`01a4fc7348672264ae6fc6fb0fd0b9da8fb1cdba138c7db5e45598eab9354f2b`.
Native source is `c3e949db01cf646de540e8b6c52e39cd36ebfb8d` in
`feature/owned-sweep-v1-20261107`. This review did **not** execute native code,
run a Worker/browser, mutate producer inputs, or change frozen oracle source.

The producing probe/runner are preserved and match the hashes embedded before
their genuine execution. `runtime-observed.json` independently rehashes the
actual JS/WASM bytes and source files at that commit. This verifies source/pin
consistency; it is not a separate compilation/reproducibility experiment.

## Independent result

`check.mjs` decodes actual numeric profile/path inputs and uses the frozen
`9db942e06` analytic oracle for20 ordinary successful rows. The extra major-arc
success is checked by the previously stated independent formula: actual
a=(0,10)→b=(10,0) CCW is270°, radius10/sectionradius2, so V=60π², not20π².
The source/frame/section parameters are corroborated before that calculation.
No producer `expected` field supplies independent truth: a control corrupts
every one of them and obtains the identical review.

- **21 successful sweep rows** (including8 repeats) agree with independent volume
  and bounds, using the previously frozen1e-6mm³ /1e-6mm absolute tolerances.
- **17 actual native point queries** agree with separate analytic material/void/
  boundary classification at the exact query coordinates. Numeric state mapping
  0=IN,1=OUT,2=ON is checked against the native `TopAbs_State` source and
  `ClassifyOwnedPointV2` implementation (native query tolerance1e-7mm).
- The asymmetric quarter rectangle has volume20π, z bounds±.5, material at
  radialoffset1.5 and a void point at z=.75, corroborating the declared planar
  transport without relying on circular symmetry.
- The annulus cases corroborate real bores and one connected valid solid.
- Reverse, antiparallel-normal, offset-frame-origin and off-center straight
  sections retain the expected source placement and measured geometry.
- **13 ordinary typed refusals** do not allocate a result name; repeated
  successful calls return to the same live-owner baseline and final names=0.
- The retained revolve control is independently1500π from the pinned producer's
  literal profile bands (radius10 overheight10 and radius5 overheight20).

See `review.json` for each actual query, measurement error and observed native
surface classes. No face-count/topology-partition equality is required.

## Honest gaps

Several successful reverse/offset/repeat cases contain **no** native point
queries. Other rows measure different valid points than the full frozen probe
list. `unmeasuredFrozenProbes` preserves every missing probe; no absent
classification is invented. Frozen-point coverage matches supplied query
coordinates only within1e-12 arithmetic roundoff and never substitutes a query
at another position. All17 supplied queries are independently classified
whether or not they coincide with a frozen point.

R3 checks caller float64 payload bytes in genuine WASM memory before freeing
them, and compares the retained seed's real metrics/catalog after operations.
The receipt does not embed full native BRep/tolerance before/after snapshots.
The native agent's separate exact-preservation and Chrome runs remain separate
evidence; this review does not borrow their passes or later R5 observations.

Native numeric payloads have no public face IDs, source digests, authored feature
IDs or persistent topology IDs. The decoder assigns explicit **review locator
labels** and hashes native payloads solely to feed independent arithmetic.
These are not fabricated public identities or solved-sketch digests. We do not
construct a fake strict Worker observation to satisfy missing binding fields.
This is native component geometry evidence, not shared authoring/history,
replay/Undo, Save/Open or complete E14 qualification.

```sh
/tmp/codi-files-move-node/bin/node test/agent-cad-corpus/sweep/native-review/check.mjs
/tmp/codi-files-move-node/bin/node --test test/agent-cad-corpus/sweep/native-review/check.test.mjs
# Read-only provenance refresh, while retained producer files remain available:
ssh r730 python3 - < test/agent-cad-corpus/sweep/native-review/verify-remote.py
```
