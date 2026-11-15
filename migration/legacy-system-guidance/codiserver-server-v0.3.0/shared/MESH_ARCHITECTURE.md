# CodiServer P2P tiers and per-node groups — design v0.3.0

Status: implementation handoff; login and v86 are assumed prerequisites for this
planning slice, not newly claimed measurements. Ten billion addressable devices
is a design envelope. No ten-billion-device deployment or performance result is
claimed. The existing v0.2 application remains the executable starting point.

## 1. Goal and the invariant

Every browser runs its own desktop, games, group memberships, peer connections,
verification, guest, caches and application state. A few permanent services supply
identity, bootstrap and explicitly delegated support. The application must not
need a globally replicated users list, a universal chat room, a global clocked
membership heartbeat, a global consensus log, or a permanent socket to one root.

**An ordinary peer's active state and traffic are bounded by its chosen work and
local resource budget, not by the total population.** Aggregate infrastructure
still grows with active users, retained bytes and recipients. There is no claim
that ten billion active devices can be supported by today's small personal fleet.

## 2. Preserve the earlier idea, fix the abstraction

Recovered history: the August 2025 direction was a pyramid hybrid, eventually
correct, with selected high-uptime/high-speed peers carrying backbone metadata;
channels can be joined and removed. `realm → gameType → lobby → table → chat`
was an earlier proposed hierarchy, not evidence that exact names are mandatory.
Titan later separated DM/group/channel lanes, membership manifests, signed key
epochs and offline catch-up. Titan/Mutt had root/admin and autonomous edge roles.

Carry those goals forward. Do NOT silently substitute an unrelated syllabus tree.
The exact live menu tree must be bound from the user's current workspace at M00.
Examples below are illustrative. They are not a recovered directory listing.

Three relationships must be separate:

1. **Namespace tree:** where something appears in the UI and who governs it.
2. **Membership/key structure:** who can read/write that group's content.
3. **Transport graph:** which machines currently exchange bytes.

One is not a second representation of another: their lifetimes and authority are
genuinely different. A room can move in the menu without rekeying all its members.
A link can fail without deleting the room. A file cache can serve ciphertext
without becoming a room member. Ancestor visibility is not descendant access.

```text
Realm                                     [its own chat]
├── Games                                 [its own chat]
│   ├── Chess                             [its own chat]
│   │   ├── Lobby                         [its own chat]
│   │   └── Match 7                       [match chat + bounded game session]
│   └── Racing                            [its own chat]
└── Projects                              [its own chat]
    └── Robotics                          [its own chat + approved assets]
```

Every node may expose its own room. Opening Games does not subscribe a browser to
all matches. Joining Match 7 does not copy its chat to Games or Realm. A subscribed
ancestor receives only its own events or separately authorized bounded summaries.
A parent live-member counter is approximate; an exact recursive global roster is
not an implicit feature. No cross-room forwarding without an explicit publication.

## 3. One stable identity for each domain object

Use opaque random 256-bit node IDs; stable room IDs derive with domain-separated
SHA-256 from node IDs and a lane label. Names/paths are presentation, not identity.
A signed NodeDescriptor names node ID, parent ID, descriptor sequence and previous
hash, display data, controller keys, policy hash and current routing descriptor.
Moving a node changes the authorized parent edge, not the node ID or room history.
Moves require grants from both affected parents; cycles, missing ancestors, stale
versions and unauthorized links fail. Directory pages and path proofs are bounded.
Very deep trees are fetched lazily; never traverse the entire realm at startup.

An implementation must explicitly distinguish:
- saved/bookmarked membership descriptors (local, can be paged),
- live subscriptions (cost network/memory and have a small global cap),
- transport neighbors (shared across subscriptions),
- a live presence lease (expires), and
- a storage retention lease (bytes, expiry and replicas, not implied by presence).

Do not give each app its own peer network. Chat, Games and Files use the same
browser PeerManager and connection pool. Do not instantiate a worker or socket
per menu node. v86 remains an isolated application consumer, not the P2P kernel.

## 4. Tiers are responsibilities, not trust inferred from popularity

| Role | Responsibility | What it does not gain |
|---|---|---|
| Realm authority | Signs release/namespace policies and delegated authority | No mandatory transit of ordinary messages |
| Rendezvous/directory steward | Owns assigned discovery shards, verifies short leases, returns bounded hints | No global browser roster or private group keys by default |
| Room/cell steward | Supports selected rooms, current descriptors, optional retained ciphertext | No authority to invent user messages or arbitrary host access |
| Ordinary browser | Participates in selected rooms; optionally forwards/cache-shares under budget | No permanent uptime or storage promise |

A machine may hold several explicitly granted roles. Initial stewards may be
David's machines, but each assignment has a signed scope (IDs/ranges), public key,
expiry and capacity declaration. Other stable operators can be delegated later.
Score/reputation is local routing evidence, NOT an identity or authorization grant.
No free anonymous key can declare itself a realm controller or global DHT server.

Root policy is cached and verified. Root unavailability blocks new authority
changes after validity expires; it does not force currently valid local room data
through a dead root. Directory replication does not replicate the authority's
private signing key. Three replicas on one power circuit are one failure domain.

## 5. Discovery: no magic first connection

The static release includes a signed seed descriptor with several explicit
rendezvous contacts, keys, protocol versions and expiry. Initially those may be
co-located for testing; evidence must label this as a shared failure domain.

The browser opens at most two outbound control links to authorized reachable
stewards. The first implementation can use WSS on an explicitly deployed support
service. That is signaling infrastructure, not a password service or a hidden chat
backend. Existing P2P links can subsequently carry signed invitations. Manual
exchange remains a bounded diagnostic workflow, not the global join experience.

To join a node's room:
1. Fetch/verify a bounded descriptor or accept a verified invitation.
2. Resolve a cell/rendezvous key with a capped lookup; cache the signed result.
3. Obtain a bounded random/diverse sample, never the entire membership list.
4. Exchange signed SDP/candidates via the chosen rendezvous route.
5. Perform live key possession + group admission and establish RTCDataChannels.
6. Send ordinary room traffic among the admitted peers; renew only local leases.

Browser contact records contain rendezvous reachability/capabilities, not an
assumption that the browser is listening on a public IP port. Private room discovery
keys are opaque capabilities; never publish private names, memberships or SDP in
a global public DHT. A hash of a predictable private name is not secret.

For large deployment, use a vetted Kademlia-style discovery implementation among
provisioned, reachable stewards; browsers are clients. Query concurrency, hop/work
count, replies, caches and total wall time are bounded; failing lookups return
unavailable rather than walking the population. Bootstrap samples are diverse and
expire. Peer exchange must validate new hints and never become unlimited crawling.
No claim of logarithmic lookup for an untested custom replacement algorithm.

## 6. Local cells and large groups

A cell is a bounded rendezvous/delivery unit, initially targeting 256 active
members; proposed test thresholds are in mesh-policy.json. Each browser keeps a
small neighbor set per hot group while the pooled connection cap applies globally.
Cells are not a requirement to make a 256-person full mesh. Use a sparse topic
mesh with duplicate suppression and bounded repair/anti-entropy.

A directory shard contains pointers to child shards/cells, not all descendants.
A hot shard splits into explicit hash ranges using a signed descriptor revision.
Use a single authorized writer initially. Sequence+previous-hash prevent rollback;
they do NOT stop that writer equivocating. Conflicting valid revisions stop topology
changes and require resolution. Later replicated controller failover must use an
established consensus implementation, not timestamp-wins or homemade voting.

Partition migration needs a cutover descriptor, old/new ranges and a finite overlap
interval. Origin events retain IDs across copies; consumers deduplicate. Stop old
leases at expiry, transfer bounded records, preserve admission rules and reject
stale authority. Partition controls are separate from group key epochs. A hash
split does not silently remove members, decrypt content or rotate application keys.
Merge needs hysteresis and a measured low-load interval to avoid thrashing.

**Sharding delivery does not abolish fan-out.** If R people must see a message of B
bytes, at least roughly R×B recipient bytes must be delivered. A globally popular
room is either a low-rate announcement stream, or an explicitly displayed space
containing smaller conversations. Do not silently show different posts to users
while claiming they are in one fully shared chat. Private group cryptography also
has membership costs; do not create one ten-billion-member key group.

## 7. Group data and the packet boundary

The v0.2 packet is link/recipient-bound with strict next-sequence checks. Forwarding
it unchanged over multiple hops cannot work correctly. Re-signing it as the relay
would lose author authentication. Therefore the planned generalization has:

- an immutable **origin event**, bound to room, epoch, author session, stream
  incarnation, sequence, time/expiry and the payload/ciphertext;
- a **transport frame**, bound to the actual link, with bounded routing metadata.

This is a required boundary, not a compatibility shim. Retain v0.2 as baseline
until the new transport is proven; then replace its single-peer-only API with one
multiplexed implementation. Do not keep parallel direct/group chat engines in the
finished product. Version negotiation must reject unsupported formats explicitly.
See MESH_WIRE.md for planned validation order and replay semantics.

Within a public room, authenticated append events may use bounded gossip repair.
Private routed content is encrypted for its authorized members before any relay
sees it. DTLS between hops alone does not hide plaintext from an application relay.
Public cache content is validated by hashes AND a trusted release/publisher record
before execution. A self-consistent malicious hash is not a trusted application.

## 8. Availability and consistency promises

Room posts have per-author ordering, bounded live replay protection and explicit
missing-history markers; no global total order is promised. Control changes
(membership, role grants, rekeys, shard revisions) are sequenced by the group's
authorized controller, not merged with timestamp-wins. Game state has its own
per-match authority/verification policy. These are real domain distinctions.

During partition, existing valid memberships may continue permitted work within
their credential/epoch freshness period. Membership changes do not fork the same
canonical group behind the user's back. Autonomous new partition groups require
new IDs and explicit membership; later merging content is not merging key epochs.
After credentials expire, the official path stops accepting new live actions until
revalidated. Pure-ANON deployment uses its explicitly configured admission model;
it is not a fallback from a failed official certificate. Cached history may display
as historical, never as a newly validated live act. An origin timestamp alone is
not a trusted proof that a historical packet predates certificate expiry.

If every holder of an ephemeral conversation closes its browser, that history can
be gone. Offline delivery requires an explicit mailbox/retention provider and TTL.
None is silently provided by the login server. A saved receipt is not a permanent
backup guarantee. Local deletion cannot force malicious remote peers to forget.

## 9. Implementation selection

Keep HTML/CSS/native modules and static delivery. No React/Node application backend
is required. Do not implement new cryptographic primitives or a complete ad hoc
Internet routing stack to preserve a cosmetic zero-library rule. At the selection
gate, prefer maintained protocol implementations, vendored/pinned assets and a
small audited binding. A prebuilt JS/WASM dependency can be served statically with
no user-side build. Record its provenance, license, build process and attack surface.
The included accounting/model code is not a libp2p implementation.
