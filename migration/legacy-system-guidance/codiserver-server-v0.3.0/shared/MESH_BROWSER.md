# Browser ownership, scheduling and storage

## One session-owned runtime

The existing session owns one PeerManager; views request subscriptions by stable
room ID. A redraw, new terminal, reopened game menu or second chat pane must not
create another independent network. Use reference-counted subscriptions; close the
last view to release its lease unless the user explicitly keeps it active.

Keep RTCPeerConnection construction/negotiation in a Window-compatible context.
Move bounded hashing, parsing, crypto and optional OPFS work to dedicated workers.
Do not assume an RTC connection can be constructed inside a ServiceWorker or
SharedWorker. DataChannel transfer to a dedicated worker is an optional separately
feature-tested optimization, not the baseline architecture. Multiple browser tabs
are separate session/device participants for the first slice; do not claim a
shared-worker daemon will keep them alive after all tabs close.

Pipeline (logical components, not mandated classes/frameworks):
`UI → subscription intent → admission/budget → PeerManager → verify/decrypt → app`.
Expensive work is queued with per-peer and global ceilings before starting crypto.
Use real backpressure from RTCDataChannel.bufferedAmount as well as application
queue accounting. Enforce byte/count/time limits before allocating/parsing nested
untrusted payloads. The DOM only sees bounded validated application events.

## Resource policy

shared/mesh-policy.json is the single source of proposed defaults, not a measured
Chrome limit. Start with 24 physical connections INCLUDING negotiating replacements,
4 hot groups, 4 target mesh neighbors per hot group, 2 support links and a 2-slot
repair reserve. These counts interact: there is no promise every role always fits.
Deduplicate endpoints, admit under the global ceiling, idle a nonessential group or
report capacity. Never let each window claim its own fresh 24 connections.

Known-peer hints, replay streams, certificate/descriptor caches, verification jobs,
fetches, timers and histories are separately bounded within an aggregate metadata
budget. 32 MiB is an initial payload-accounting target, NOT total tab memory: v86,
GPU allocations, DOM, JS object/string overhead and Chrome internals are additional.
Measure actual heap/RSS/GPU as separate counters. Anonymous state uses RAM by default.

Multiplex a small fixed number of traffic classes per connection:

| Class | Examples | Delivery rule |
|---|---|---|
| Control | Admission, rekey, membership, manifests | Reliable; reserved queue capacity and bounded rate |
| Interactive | Chat, discrete game actions | Reliable with bounded queues; report rejected sends |
| Transient state | Position, cursor, presence | Latest value wins; expiry; unordered/limited retransmission when useful |
| Bulk | Chunked images, v86/model assets | Low priority, chunked, byte-window backpressure |

Separate channels still share congestion/underlying transport; they are not separate
bandwidth reservations. Do not claim no head-of-line effects or hard real-time QoS.
Use deficit/weighted fair scheduling, cap even control traffic and never silently
drop an acknowledged reliable chat. An oversized transfer must not starve logout,
key changes or a small game input. Realtime games need measured p95/p99 latency;
an acceptable multi-hop metadata delay is not an acceptable physics tick delay.

## Persistence classes

- **Session-private:** identity keys, live joins, ANON history, routing leases and
  private workspaces; RAM, released on logout. No anonymous browser DB surprise.
- **Disposable public assets:** optionally persist verified immutable release,
  guest, model or image chunks in OPFS/Cache API after a clear opt-in. Hash manifest,
  bounded chunk sizes, resume, quota and eviction are part of the storage contract.
- **User-retained data:** explicit export or user-selected persistent storage;
  authenticated encryption where appropriate, user controls key/backup semantics.
- **Steward-retained data:** negotiated ciphertext/asset leases with byte count,
  expiry, retention scope and failure-domain replicas; not the identity database.

Store binaries once by content hash; keep metadata references rather than copying
same blob for every room. Never advertise a chunk unless fully verified and still
held. Eviction withdraws advertisements; lost peers cause retry, not silent success.
A content hash must not permit path traversal or automatic execution. Never share
local/host files merely because a room asks for them.

The only initial user-facing network choices should be joining/leaving rooms,
explicitly allowing contributed upload/cache resources, and explicitly retaining
local data. Numerical routing/TTL/queue parameters are internal measured policies,
not a wall of settings. A resource profile reduces capabilities before exhaustion;
it does not silently violate delivery or privacy semantics.

## Browser suspension and recovery

Hidden/frozen/discarded tabs are intermittent participants. Presence is an expiring
lease, not a leave-event expectation. On resume: verify time/credentials, abandon
stale routes, pull bounded current descriptors and missing ranges, refresh admission,
then rejoin with jitter. Do not replay a giant timed-out queue at once. A restarted
anonymous tab starts a new session. Offline UI must show stopped/stale networking.
No service worker keeps an arbitrary P2P process alive forever.

## Apps and v86

Games get narrow send/subscribe/storage capabilities scoped to their group. Guest
serial text is never a peer-command evaluator. Do not expose host-files credentials,
issuer keys, owner resource grants or unrestricted PeerManager references to v86.
Host-files access remains a distinct authenticated broker capability, NOT an
implication of directory stewardship or a server-validated identity badge.
