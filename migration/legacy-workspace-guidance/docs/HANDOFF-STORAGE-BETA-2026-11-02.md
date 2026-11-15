# Storage and beta handoff — 2026-11-02

**Historical handoff: its paused/incomplete status below is superseded.** Development resumed; the bounded Files foundation is accepted and CAD is active. Read [the current handoff](HANDOFF-FILES-CAD-2026-11-04-CURRENT.md) and [functional gates](CAD-FUNCTIONAL-GATES.md). Historical receipts keep their original scope.

**Paused at the user's request.** Resume only on request. The current bounded
priority is dependable saved data: account isolation, conflicts, interruption
and recovery, and worker-based processing. Continue to maintain
`docs/WEBOS-WORK-QUEUES.md`; do not check off broad gates for partial results.

## What is running

- `https://beta.ksu.codes/` is publicly reachable over trusted HTTPS. It has
  separate issuer keys, account data, service identities and user-file roots.
  Its three services are enabled at boot; an actual host reboot was not tested.
  The guest Internet relay is disabled. Services share the host loopback
  network; per-account isolation is enforced by the gateway, not by a separate
  Unix UID for each user.
- Beta runs gateway worker `dd8cbea7…`, SDK `44da83bd…`, and guarded mirror
  `cbfafe53…`. The public signed Chromium smoke at `5fc0d26ad` verified
  Files/Text save and reopen, account denial, Linux readiness, simulated
  lost-reply recovery, conflict handling and cancellation. Test files were
  removed; disposable beta test accounts remain because account deletion has
  no verified API.
- Beta's guarded loader and mirror are the **minimum rollback floor**. An old
  mirror ignores newer uncertain-write metadata and can leave an unwanted old
  server file after an offline move. Do not automatically revert beta to the
  unguarded mirror. Previously guarded assets remain available. The SDK floor
  marker is enforced only by cooperating versions of its switch operator.
- `https://ksu.codes/` remains on its existing main release. At handoff, both
  main and beta returned HTTP 200 with certificate verification successful.
  Do not copy beta identities, account databases, user files or keys to main.
  The user confirmed there are no real users and authorized beta experimentation;
  beta is not a promise that the overall storage foundation is complete.

## What the current storage can and cannot do

- Beta's signed gateway supports version-checked writes, changed-chunk delta
  uploads and batched chunk downloads. In a public 1 MiB random-file test,
  changing one byte sent 66,233 bytes of instrumented upload request bodies;
  the later download received 146,230 bytes of instrumented response bodies
  plus 584 bytes of request bodies. These exclude authentication, TLS and
  other network overhead and vary with file content. The measurement used two
  mirror scopes of the same signed account/session.
- The server reconstructs a complete temporary file before publishing: wire
  savings do not mean only changed blocks are written on server disk. Its
  5 GiB disk admission floor applies to participating gateway allocations,
  not all programs or metadata; host mount changes and direct writers require
  separate coordination. Main's current gateway is older and must not be
  assumed to have beta's chunk or explicit uncertain-commit behavior.
- A real local TCP response cut after a committed upload was tested: the
  browser reported an uncertain result and reconciled using the server hash
  without a second upload (`c6ab94396`). Browser/process kill tests do not
  prove physical WAN failure or power-loss durability. Direct uncoordinated
  host writes are not serialized with gateway operations.
- An isolated 128 MiB two-session test verified the resulting hash and small
  changed-file transfer, but sampled Chrome RSS was roughly 1.87–2.04 GiB.
  Shared-page accounting and different runs limit comparison; memory remains
  an open problem, not a proved hard bound. The issuer has a per-account
  60/minute challenge limit; naive all-chunk cold download hit HTTP 429 and
  remains disabled. The deadline-based pacing prototype completed 64 two-tab
  reads in about 64 seconds; high request counts need batching or a carefully
  scoped authorization mechanism, not unsafe write retries.

## OPFS research — not deployed

An experimental worker/OPFS store is being developed on
`research/beta-worker-sync-20261102`. It uses staged verified generations,
IndexedDB version checks, per-account coordination and conservative cleanup.
Prototype `3db7f4a99` saved and reopened 128 MiB and survived a Chrome process
kill during replacement; its sampled 1.26 GiB Chrome RSS is not comparable to
the network test and is not a guaranteed memory limit. `f489097e` added
orphan-only staging cleanup and process-kill tests around publication.
`3aec0e59` added indexed bounded cleanup and experimental signed uploads;
independent tests covered more than 4,096 published records, conflicting edits,
lost replies, close during an upload and account separation. This does not
prove hostile same-origin isolation, power-loss behavior or cross-store atomicity.

Remote OPFS download prototype `796a10f6622c7fa9121f772ff4662101e9831761`
passed signed tests for corrupt data, local and remote edit races, account
invalidation and uncertain server commits. Dedicated Chrome SIGKILL before
local pointer publication preserved the prior generation and cleaned its staged
orphan; SIGKILL after publication preserved the new one. Independent signed
Chromium review repeated corruption, concurrent-edit, stale-remote, cancellation
and uncertain-commit tests successfully. The server can change after the final
version check; later sync must detect that. OPFS is not wired into the desktop
and must not be described as live.
Its integration must preserve local edits, verify hash/size, publish only after
the expected local version still matches, and reconcile uncertain writes.

## Where to find the work

- Operational checklist and current research integration: branch
  `research/webos-cad-combined-20261102`, checkout `/tmp/codi-webos-cad-merge`,
  file `docs/WEBOS-WORK-QUEUES.md`. This handoff is committed on that branch.
- OPFS/browser research: `research/beta-worker-sync-20261102`, backed up on
  box-git. See its experimental OPFS docs/tests and the final checkpoint below.
- Gateway, beta worker rollout and server interface notes:
  `research/quota-owner-liveness-20261102` at `f9f5ba0a7` or later;
  `research/beta-delta-candidate/OPFS-SERVER-CONTRACT.md`.
- Hosting route/activation and plan-only audit:
  `research/beta-hosting-isolation` at `cf04068aa` or later. Activation
  receipts explain initial TLS issuance rollback and the guarded floor.
- Both box-git (`box-git:/srv/data/git/CodiServer-distro.git`) and R730
  (`r730:/mnt/data10tb/git/CodiServer.git`) hold the indicated branches where
  noted. Verify actual remote refs before use; a source commit is not a release.
- The `/home/dflanag3/CodiServer/desktop-preview/SIMPLIFIED` checkout has
  pre-existing modified and untracked work. Do not reset, stash, delete or
  overwrite it. Its 9 modified and 26 untracked source/test files were saved
  exactly, without touching its index or worktree, on branch
  `backup/simplified-worktree-20261102` commit
  `4d202d41aaa27b4aa792f3620bfc76592589b32a`, verified on box-git and R730.
  This is a backup, not a reviewed merge or deployment. Build outputs,
  dependencies, private account data and keys were excluded. A bounded secret
  scan found no obvious credentials; it is not a complete security audit.
- Use `docs/WEBOS-WORK-QUEUES.md` for the complete current queue and
  `docs/HANDOFF-2026-11-02-PAUSE.md` for the earlier broad application/CAD
  handoff. Older live-status statements there are superseded by this document.

## Next ordered work

1. Recheck live site/service pins, backup refs, test fixtures and available
   disk. Workstation and webhost each had only about 5 GiB free; run large
   fixtures on R730 and delete only known disposable artifacts.
2. Finish and independently review OPFS remote-download publication, concurrent
   edit/account-change cases, orphan cleanup and process interruption. Prove
   no saved local version is silently lost. Add desktop integration only after
   the browser/server contract and recovery behavior are agreed.
3. Measure real memory and data use with large files, multiple users and slow
   connections. Design bounded streaming without assuming Blob or OPFS rename
   provides a hard RAM bound or atomic cross-store publication.
4. Qualify main promotion separately: preserve its existing accounts, keys and
   files; prove conflicts, interrupted saves, recoverability and a safe rollback.
   The user allows replacing current test services, but that does not authorize
   silently discarding saved work. Avoid changing main during beta experiments.
5. Only after the storage foundation is dependable, resume the larger app-by-app
   desktop, engineering/CAD and other checklist work.

## Final checkpoint

Browser research branch head `796a10f6622c7fa9121f772ff4662101e9831761` is
backed up on box-git and R730. The exact served test store SHA begins
`0a7e4156`. Independent review passed; this is not a production release.
The user requested a pause after the handoff. Do not continue until asked.
