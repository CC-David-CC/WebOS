# Account storage: 100-user planning target

Plan for 100 signed-in users at once, most editing locally or idle, with a
smaller number saving and transferring files concurrently. This is a design
target, not a tested capacity claim. Keep the 128 MiB per-file maximum and the
browser-first, account-isolated storage and conflict guarantees.

## Current findings

* The browser mirror starts a sync about every 15 seconds. A sync lists every
  folder and requests a version for each server file; even idle users therefore
  consume requests and server disk work. With 100 users, the intervals alone
  could start about 400 passes per minute, before counting each folder and file.
  This arithmetic is not a load measurement.
* Each file gateway operation obtains signed authorization using separate
  challenge and authorization requests. The issuer currently limits each file
  authorization phase to 60 requests per minute per address it observes. The
  live phone-sized test encountered this limit during cleanup. Confirm how the
  trusted proxy supplies that address before treating this as a per-visitor
  budget: multiple visitors behind NAT or a proxy may share it.
* The gateway has a bounded global request budget and an active-work limit of
  four. Do not assume four active transfers supports the target or raise it
  blindly: measure transfer memory, file descriptors, latency and disk load.
* Version checks avoid redownloading unchanged file contents, but currently
  still incur one signed request and server hash per file. Large accounts can
  therefore be slow even without a download.
* The mirror now remembers completed file-version checks across an interrupted
  scan in the current browser session, so a 429 during the file-check phase can
  make progress on the next attempt. This is not a batch protocol: folder
  listing still starts over on retry, a new tab starts over, and the full scan
  is repeated after completion. This change alone does not establish capacity
  or fix excessive idle traffic.

## Design direction

Local candidate: an optional signed version-batch capability groups up to 16
files per request, with at most 32 MiB hashed per batch and individual fallback
for larger files. A real local browser/gateway test checked 20 files in two
batch calls, detected a same-size external edit, and verified fallback when the
capability is absent. Account isolation and read-permission tests also passed.
This candidate is not deployed and still hashes files and polls folders; it is
not yet evidence that the 100-user target is supported. It needs guarded
gateway rollout, live testing and mixed-load measurements.

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
