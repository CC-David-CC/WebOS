# Planned multi-group wire contract — codi-mesh/1 DRAFT

Not yet implemented/negotiated by the v0.2 runtime. Do not claim interoperability.
Freeze encoding and negative fixtures at M00/M03 before networking integration.
The authoritative identity remains the existing codi-peer/1 certificate contract.
This draft generalizes application events, not the authentication namespace.

## Identity and scope

`node_id`, `room_id`, `membership_epoch`, `routing_revision`, `device_session_id`
and `stream_incarnation` are different fields. A routing migration is not a key
epoch. A display name is not an authorization subject. A random identity proves
neither unique human nor honest behavior. Include protocol/domain separation in
all signed inputs and derive IDs without ambiguous concatenation.

Public live event (conceptual fields):

```
version, room_id, descriptor_hash, membership_epoch,
author_session_id, stream_incarnation, sequence,
issued_at, expires_at, kind, payload_or_ciphertext
```

The authenticated author key must match the admitted session and the event's group
capability; for private content, associated data authenticates routing/group/epoch
fields and encrypts sensitive inner metadata where required. Do not let routing
infrastructure rewrite the author packet. Unknown kinds/versions fail closed.

For an ES256/JWS public envelope, derive event_id from a domain prefix plus the
exact protected-header and payload signing input, EXCLUDING the ECDSA signature.
ECDSA has variable/malleable encodings; hashing the entire signature-bearing token
must not allow another valid signature over the same bytes to evade deduplication.
Verify exact transmitted signed bytes, not reserialized JSON. Strictly reject
duplicate keys, noncanonical encodings and extra fields after the schema is frozen.
Private events adopt the chosen reviewed protocol's native IDs and authentication;
do not bolt on an incompatible JWS wrapper with contradictory sequence semantics.

The transport wrapper carries the origin event, local route request ID, destination
cell, remaining hop allowance and frame type. It is authenticated by the actual
link, bounded and not a new author statement. Hop limits reduce honest forwarding
loops; a malicious relay can reset its own wrapper. Therefore TTL, signed origin
expiry, per-hop/global byte budgets and recipient deduplication are also required.
Never confuse a decrementable unsigned hop count with a cryptographic abuse proof.

## Validation and delivery order

1. Reject wire oversize/invalid type, per-peer rate and global queue overflow.
2. Parse shallow bounded fields and reject impossible version/time/room/length.
3. Look up a bounded authenticated session/key record. Unknowns consume separately
   limited admission work; they do not create an unlimited crypto backlog.
4. Verify identity freshness/admission, author signature/AEAD and exact scope.
5. Verify room control epoch and permitted kind; check origin event ID.
6. Apply per-stream replay window and dedup state. Unverified packets must never
   advance replay state, poison a seen-ID cache or alter group membership.
7. Deliver to one correct subscription, then forward within the bounded topic mesh.

Live stream sequence is an integer in [1, 2^53-1] for the initial JS profile.
Use a sliding 64-entry bitmap to tolerate bounded reordering over different paths;
strict next-sequence rules remain appropriate only for their old single ordered
link domain. Gaps trigger bounded repair. Do not allocate one array up to an attacker
sequence or one replay map per arbitrary unauthenticated ID.

Replay state is scoped by `(room, epoch, author session, stream incarnation)`.
A new incarnation needs live authorized admission and a fresh unpredictable nonce.
Evicting a live replay floor while accepting the same old stream is unsafe: retain
its floor through its full acceptance window, or close it and require a genuinely
new admission. Overflow rejects new streams; it is not LRU-reset replay protection.
History fetch is separately marked historical, bounded and never triggers live
commands or game inputs. Persistent epoch high-water marks must be part of an
explicit persistence grant; ephemeral restarts require fresh signed descriptors.

## Control sequencing, deletion and partition

One group controller initially sequences membership/key changes. Sender events
remain independently append-only. A signed fork is evidence, not permission to
pick the lexicographically smallest fork and call it consensus. Stop security
changes on ambiguous control history and display the condition. Cached read access
uses the last admissible epoch only within its declared validity.

A ban/removal cannot erase old recipient knowledge. It does stop new membership
keys from being given to that member after the canonical removal commits. A
legacy 60-second overlap for packet reordering must NOT become a 60-second permission
for removed members to publish/decrypt new canonical traffic. Independent partition
groups have new IDs, not two key schedules called the same room.

## Security profile decision

Earlier Titan chose LKH and proposed TGDH partition fallback. Preserve the desired
hierarchical administration and efficient rekeying; do not silently import a native
Java/UDP design into a webpage or run two automatic key protocols for one room.
The first private-group gate must bind ONE reviewed profile/library. Evaluate MLS
(RFC 9420) for bounded interactive groups against the earlier centrally managed
LKH requirement (RFC 2627). LKH's key controller knows the group secret; that trust
must be explicit. Neither a design sketch nor a primitive test proves a safe key
management implementation. Private multi-hop messaging remains blocked until the
choice, threat model, test vectors and integration review are complete.

This is a deliberate change from automatic TGDH failover: canonical membership
changes freeze during unresolved controller partitions; independently created
partition rooms are explicit new groups. Consequence: less membership availability
in exchange for not making revocation and identity ambiguous. Chat using existing
valid state may continue under its freshness policy; no fabricated renewal.

## Games and truth

Signed state is attributable state, not correct state. A racing result must be
validated by the game rules/replay witness or an explicitly trusted game authority.
Use bounded per-match groups. Discrete inputs/control are authenticated; high-rate
state can use authenticated channel/session keys and signed checkpoints rather than
expensive public-key signatures on every pixel or physics sample. Spectators use a
separate bounded-rate publication stream. No global consensus is required for chat.
