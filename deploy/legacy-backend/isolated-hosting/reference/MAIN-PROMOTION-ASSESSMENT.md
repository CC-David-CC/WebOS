# Main storage promotion assessment — 2026-11-02

**Decision: do not promote beta's current storage behavior to main as a
finished foundation.** Public beta can register, save, reopen and isolate
small files, but its current frontend can overwrite unresolved conflicts;
interrupted/ambiguous saves and simultaneous edits on one account are not yet
fully qualified. It still uses whole-file fallbacks, not proven changed-chunk
sync. A signed small-file smoke test does not establish crash-safe or
large-file behavior.

## Running baseline observed read-only

Main's managed file worker is release
`ffaa4bc40925db28bf9c8b218abae36350c99b9193ade2b5d77800971c3c9055`,
instance `codi-files-ksu-hidden`, origin `https://ksu.codes`, port 8140,
state `/var/lib/codi-gateway/ksu`, account files
`/var/lib/codi-user-files/ksu`, and the existing issuer-policy pin in
`/etc/codi-user-files/ksu/managed.json`. Main's connected issuer/guest
release is `1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51`;
its current identity/state and signing keys must remain main's. The file
worker, proxy, issuer and guest units were active when inspected.

Beta file-worker release
`71e472bc430fe417ca46f81d7e464697ee7ec0d5c87b7a1d906e20505858b57a`
differs from main in `gateway_service/http.py`, `user_store.py`, and
`client.mjs`. It contains phase-aware responses and a bundled SDK; it has no
qualified chunk/delta endpoint. API similarity does not prove compatibility
with existing state or old browser caches. Beta issuer keys, account database,
file roots, policies, and cookies must never be copied onto main.

## Promotion gates

1. Fix conflict handling so local and remote versions remain available; never
   overwrite a newer committed version by blind retry. Establish explicit
   account-scoped browser state and correct switching/logout behavior.
2. Prove create, replacement, delete, rename and concurrent same-account edits
   with signed real-browser tests. Interrupt transport before and after
   publication, kill/restart a worker and browser, then verify exact bytes and
   distinguish local durability, server commit, conflict, and unknown outcome.
   Preserve committed data and recovery evidence. Exercise large files and
   bounded worker memory; do not claim changed-chunk sync until it exists and
   is proven end to end.
3. Qualify the desired gateway plus frontend as one pinned release, with
   reproducible builds, actual account isolation and no reliance on stale
   service-worker assets. Test old-client behavior or deliberately require a
   fresh coordinated client release; do not erase local pending work.
4. Inspect current permissions and document-operation databases and verify
   schema and storage compatibility on disposable copies, including SQLite
   WAL/SHM consistency, quotas and real file ownership. The known legacy quota
   reservation expiry/live-worker problem is not solved by promoting 71e.
   Do not migrate or delete live reservations merely because their deadlines
   elapsed.
5. Validate and rehearse the actual main-specific stop/replace/restart and
   rollback against an isolated clone using the exact production units,
   configs, manifest pins, origin, issuer-policy shape and disk layout. Capture
   consistent recoverable backups of databases, keys, configuration and user
   files with appropriate permissions; verify restores. Avoid copying secrets
   into build/public artifacts. Confirm disk headroom and no active worker can
   publish during the snapshot or transition.
6. At cutover, use a bounded maintenance window with exclusive managed locks
   and deliberate quiescence: stop admission, drain or explicitly terminate
   in-flight work, confirm no workers are writing, then snapshot. Switch the
   main worker to an independently built, verified candidate while preserving
   main data roots and identity. Revalidate connected-controller pinning and
   managed service/route configuration. Run readiness plus signed create,
   replace, stale-write conflict, restart and account isolation tests using
   disposable test data; verify every other site and the renewal timer.
7. Rollback must be rehearsed for each transition phase, preserve data written
   since cutover, and never restore an old database/files snapshot over newer
   committed user data. If rollback compatibility is not proven, stop and
   reconcile rather than silently revert persistent state. Record the new
   exact pins and receipts.

The user's current instruction is to test on beta and **not modify main**.
No main services, data, keys, or routes were changed for this assessment.
