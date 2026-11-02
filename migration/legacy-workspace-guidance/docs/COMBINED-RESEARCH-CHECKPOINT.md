# Combined desktop, file sync, and manufacturing research checkpoint

This branch is an integration workspace, not a release or evidence that these
features are available on the live site. The source under test was desktop
commit `ebfa5d6fd0058f6421204b9b690a2cf980de624f` and the CAD host used a
locally prepared JSketcher runtimes from fork commits `4c995a10` and
`f3971dc8`. The latter is the combined manufacturing fork on box-git's
`research/3mf-host-combined-20261102`; it is not connected to a host export
command, and the hand-staged test build is not release-qualified.

## Evidence

- Desktop registration and frozen JavaScript/Python chunk-vector checks passed.
- An isolated signed gateway test passed chunk upload/download, conflict and
  cached-snapshot checks, including account permission and external-file edits.
- An independent signed-account Chrome run against the integrated source passed
  initial sync, no-op, an inserted byte, interrupted download and retry, and
  account isolation. One sample fetched 53,414 encoded bytes in one chunk
  request; this is a test observation, not a performance guarantee.
- Isolated registered-account CAD runs passed with both fork revisions on desktop and at an emulated
  390 × 844 viewport: project save and reopen, explicit review of stale material
  bindings, rejection when changed during review, confirmed manual rebind,
  account isolation and captured frame CSP. This used automated clicks, did not
  test physical touch, changed-chunk transfer, or 3MF export.
- Native CGAL feasibility experiments classified contact, separation, overlap,
  and containment for the regenerated enclosure meshes. They are not a browser
  validator, do not prove agreement with analytic CAD, and require license review.

## Release gates

- Review the patch against the actual deployed source and package only intended
  changes; the research source contains other unfinished work.
- Qualify the combined JSketcher build provenance, connect a real export command, and
  independently inspect its 3MF structure, units, materials and geometry.
- Prove reliable 128 MiB and concurrent-user sync, interruption and recovery,
  cancellation, cache eviction and external-writer behavior. The newer research
  cache reserves within a 1 GiB logical payload budget before staging and counts
  active leases, with a separate 2 GiB free-space reserve. This is not a hard
  physical disk reservation against unrelated writers; real deployment settings,
  filesystem overhead, process crashes and sustained concurrency still need review.
- Avoid full-file JavaScript allocations and repeated whole-file re-chunking;
  the current client reduces transferred data but does not meet the memory and
  incremental-computation goal. Its current integrity check still reads the
  whole reconstructed file. Do not describe it as complete changed-chunk sync.
- Remove the CAD host's temporary 8 MiB/full-hash research limit safely; retain
  account isolation, verified saves, explicit assignment repair and failure
  recovery. Do not infer topology equivalence merely from a producer ID.
- Retest the exact release in real browser workflows and document its results
  before deployment. Neither existing accounts nor unrelated services should be
  changed by these tests.
