# Account storage: 100-user planning target

Plan for 100 signed-in users at once, most editing locally or idle, with a
smaller number saving and transferring files concurrently. This is a design
target, not a tested capacity claim. Keep the 128 MiB per-file maximum and the
browser-first, account-isolated storage and conflict guarantees.

## Current findings

* A successful, idle browser mirror now polls at roughly 60 seconds in a
  visible tab and four minutes in a hidden tab, with jitter. Edits and explicit
  sync remain immediate; pending or failed work uses the shorter retry schedule,
  and returning to a stale tab prompts a refresh. Each pass still discovers the tree and checks file versions; the live combined operation now performs those checks together within its bounds. If 100 mirrors were visible, the intervals
  alone would start about 100 passes per minute before counting folders or
  files, already exceeding the former shared 60-per-minute issuer bucket. Account-scoped admission is now live, but the gateway budget still constrains the workload. This is arithmetic, not a capacity claim.
* Each file gateway operation obtains signed authorization using separate
  challenge and authorization requests. The issuer previously limited each file authorization phase to 60 requests per minute per address it observed. The
  live phone-sized tests encountered this limit, including a Files upload
  check after several conflict and upload tests in quick succession; a later
  retry passed. The active Caddy route sends
  file-authorization requests to a loopback issuer without rewriting WSGI
  `REMOTE_ADDR`; the file authority keys its buckets by that address. Legacy callers without a recognized session still share that proxy-observed budget. The live client now supplies its session credential for account-scoped admission; a server-wide ceiling remains.
* The gateway has a bounded global request budget and an active-work limit of
  four. Do not assume four active transfers supports the target or raise it
  blindly: measure transfer memory, file descriptors, latency and disk load.
* Version checks avoid redownloading unchanged file contents. Combined inventory hashes up to 64 files and 32 MiB in one signed operation; beyond that it falls back to bounded batches or individual checks. Large accounts can still be slow even without a download.
* The mirror now remembers completed file-version checks across an interrupted
  scan in the current browser session, so a 429 during the file-check phase can
  make progress on the next attempt. This is not a batch protocol: folder
  listing still starts over on retry, a new tab starts over, and the full scan
  is repeated after completion. This change alone does not establish capacity
  or fix excessive idle traffic. The mirror now adds jitter and bounded
  exponential backoff after a 429; explicit sync still tries immediately; new writes queue behind the retry delay after a rate limit. This reduces synchronized retries but does not increase capacity.

## Design direction

The gateway and browser mirror now support an optional signed, bounded account
inventory. It gathers up to 128 directories and 2,048 entries (with a 512 KiB
path budget) in one discovery operation, or returns no partial inventory and
falls back to ordinary directory listings. A live six-folder account required
one signed inventory request instead of seven list requests; local and live
checks also detected a same-size direct disk edit, and the old-gateway fallback
was exercised. A local eight-account mixed test overlapped inventory with a
2 MiB upload. This reduces work for nested accounts but did not by itself solve the former shared issuer bucket; the account-scoped admission change described below addresses that part, while the gateway budget remains.

The live gateway now offers an optional signed version-batch capability grouping up to 16
files per request, with at most 32 MiB hashed per batch and individual fallback
for larger files. A real local browser/gateway test checked 20 files in two
batch calls, detected a same-size external edit, and verified fallback when the
capability is absent. Account isolation and read-permission tests also passed.
The live browser test also checked 20 files in two signed batch calls. An
eight-account local mixed-workload check overlapped batches with a 2 MiB upload.
It still hashes files and polls folders; these checks do not establish the
100-user target. Larger mixed-load measurements remain necessary.

1. Replace routine full per-file polling with an account-scoped, paginated
   change/index protocol. One authenticated request should summarize many
   entries, with bounded response sizes; use revisions/cursors for incremental
   changes and a full reconciliation path after missed or invalid cursors.
   Preserve discovery of direct changes made on server disk, including same-size
   edits; specify and test how external filesystem changes update the index.
2. Keep actual file data browser-first, transfer only changed files, stream
   large transfers, preserve version checks and hashes, and preserve local edits
   and conflict detection across retries, crashes and multiple devices.
3. Coalesce sync triggers and introduce jitter, slower idle/background polling,
   priority for unsynced edits, and bounded backoff for 429/offline responses.
   A partially completed large scan must make forward progress after a retry.
   Do not present a queued local save as already saved on the server.
4. Review fair per-account and per-source controls, shared NAT behavior, and
   server-wide concurrency limits together. Protect login and storage from
   abuse while avoiding one busy account or school network blocking everyone.
   Tune only from measured service capacity.
5. Test with 100 independently authenticated sessions and realistic mixed
   workloads: mostly idle, a smaller active group, simultaneous logins and
   saves, bursts and reconnects, multi-device edits, external disk changes,
   and several 128 MiB transfers. Include slow connections, server restarts,
   quota/429 responses and cancellation. Bound test duration and resources;
   observe server CPU, memory, disk, network, request rates, pending work and
   user-visible sync latency. Report completion rates and percentiles, not just
   that a test launched. Avoid using production account data for fixtures.

Establish explicit numerical throughput and latency acceptance thresholds from
measured hardware and the desired experience before calling this capacity
supported. Validate on the live testing environment only with isolated test
accounts and remove only the resulting fixtures.


## Account-scoped admission — 2026-10-31

The live issuer groups file-authorization admission by the subject of a live in-memory registered session, with separate bounded legacy and global budgets. The session token selects an admission bucket only: signed one-use proofs, token/key binding, current account policy, gateway permissions and exact-operation checks remain required before access. A modified browser client supplies the token on the issuer challenge; the old issuer ignores the extra authorization header and old clients remain on the legacy budget. Invalid and unknown tokens use the bounded legacy budget. The change is live. A public browser test completed 62 signed inventory operations across two accounts and confirmed isolation; it was not a 100-user load test.

Local tests exercised 100 independently keyed accounts, issuer and gateway signatures, account isolation, legacy callers, independent account budgets and a global ceiling. One sequential issuer/proof run completed 100 authorizations in 0.624 seconds after setup (p95 7.66 ms). In a separate signed HTTP fixture with 100 accounts and one 4-byte file each, concurrency three, all 100 inventories completed in 2.479 seconds after setup (p95 86 ms); the immediately following version checks completed for 27 accounts and 73 hit the separate 256-request/minute gateway budget. Account setup used a permissive fixture, so neither run establishes login-burst capacity. Large files, slow transfers, concurrent bursts, public proxy behavior, sustained throughput, gateway fair scheduling and 100-user end-to-end capacity remain unverified.


## Combined inventory live — 2026-10-31

The live gateway provides one signed account-scoped inventory operation with hashes for up to 64 files and 32 MiB of data. Remaining entries carry no hash and use existing version checks; oversized directory trees fall back without treating partial results as deletions. The operation retains list and read permissions, no-follow descriptor checks, per-file hashing and change-during-read detection. Browser mirror validation rejects malformed, duplicate or inconsistent inventory results. The client and mirror retain fallbacks for older gateway capabilities.

Signed HTTP tests covered account isolation, revoked list/read permissions, anonymous denial, link rejection, bounded hashing, count overflow and same-size external disk edits. Local browser tests checked a six-folder account using one combined signed operation, same-size external edits and both legacy fallbacks; conflict preservation also passed. With 100 distinct authenticated accounts containing one 4-byte file each and only three concurrent operations, a local HTTP fixture completed all combined inventories in 2.647 seconds after setup (p95 91.08 ms), using 200 gateway requests. The earlier two-operation version hit the gateway limit for 73 subsequent version checks. These are narrow test fixtures, not a claim that the gateway supports 100 active users: login bursts, large files, many-file accounts, uploads, slow connections and sustained workloads remain unqualified. The gateway and browser mirror are live. A live phone-sized browser test used one combined check for a six-folder fixture, verified old-protocol fallbacks, and detected a same-size edit made directly on server disk. A live simulated-429 test confirmed a local edit eventually synced. Four exact disposable test accounts and their verified fixture files were removed.


## Local bounded queue candidate — 2026-10-31

The existing gateway rejects a request immediately when four operations are active. In a local fixture with 100 independently signed inventories started together and no retries, that behavior completed 4 and rejected 96. A candidate retains the four-operation processing cap and the 256-request/minute global budget while waiting up to five seconds for a slot, with at most 128 waiters. Overflow and timeout return a retryable limit. Tests verify queue bounds, cancelled waiters, repeated handoff cancellation, releasing a slot when cleanup fails, and that a client disconnected before admission does not consume or execute its signed create. A local repeat completed all 100 simultaneous checks in 2.241 seconds without retry.

A separate unsmoothed local fixture started 100 one-file inventories, eight four-byte edits and one 8 MiB upload with 100 independent registered accounts. All completed in 3.405 seconds after account setup, with inventory p95 2.534 seconds and 218 gateway requests; the combined fixture process peak was 118,464 KiB in that run. The first uninstrumented mixed run showed a much higher reported peak that did not recur in the two instrumented repeats; the cause is unconfirmed. This is one machine and a single-process fixture, not 100 browsers, a live capacity test, or a sustained-load result. The queue does not reserve capacity for small checks when all four slots are occupied by slow transfers, and the gateway budget remains shared. The candidate has not yet been deployed.
