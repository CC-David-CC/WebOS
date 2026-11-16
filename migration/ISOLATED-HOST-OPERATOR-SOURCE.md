# Preserved isolated-host deployment source

Twenty-six additional historical Python sources now belong to parent deployment
composition at `deploy/legacy-backend/isolated-hosting/`.

| Captured source | New parent location | Files |
|---|---|---:|
| Reviewed files in `research/beta-isolated-hosting/ops/` | `deploy/legacy-backend/isolated-hosting/` | 25 |
| `research/beta-opfs-release/floor_journal.py` | `deploy/legacy-backend/isolated-hosting/historical-inputs/floor_journal.py` | 1 |

Source definitions establish the ownership boundary: these helpers compose host
locks, rollback/floor journals, route generation, issuer changes, protected health
probes, installation and release/service transitions. The Files router bridges
managed host transitions; it is not an account-document storage implementation.
OPFS floor helpers bind host transitions through supplied adapters. No new shared
service, application grouping or microservice is introduced.

History records a C100 copy from the older floor journal into `opfs_floor.py`.
Both existed at capture and remain separate. All47 retained commit trees match
their original selected-path trees, preserving authors, committers and messages.
The28 historical Python blobs pass syntax and bounded credential-context checks.
All26 current bodies/Git modes match capture, scoped original index/working bytes
and self-contained recovery; original/recovery filesystem permissions also match.

Extraction streamed a path-limited full-history Git export into a new bare filter
target, without force or a large monorepo clone. Recovery was read-only, the
original workspace hidden and networking disabled. Independent integrity checks
found no alternates or shallow dependencies. All26 files restored from the new
repository with original and assembly paths hidden. Private phase83 retains
commands, exit codes, path/commit maps and bounded review metadata.

The source-only mechanical merge precedes documentation in separate commits.
No operator was imported/executed, registered as an entrypoint or given host
authority. Required manifests/configuration and interface/side-effect ports are
still OPEN. Two related operator files remain private pending credential-context
review; Microduck policy is reserved for its component owner. Never infer a
runnable installation from these files or fill gaps with production data.

This closes26 tracked-source ownership records, leaving1,833 unresolved
dispositions. That count is not missing files, overall completion or runtime
support. All124 component pins, active runtime and existing deployment remain
unchanged. Read the source area's restrictions before attempting any port.
