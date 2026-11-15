# Minimal origin and delegated P2P support — server-side plan

## Keep the server split honest

`box-webhost` may initially host several processes, but the following are separate
security/resource roles. Adding automatic P2P discovery introduces support services;
it is not free functionality of a static server or a login certificate.

1. **Origin/identity:** public static resources, signup/signin/ANON certificates,
   identity renewal, a signed seed bundle. No chat history, global live presence,
   room heartbeat aggregator, game state or generic user-file storage by default.
2. **codi-steward (planned):** scope-limited directory/rendezvous, signed invitation
   forwarding, expiring local leases, bounded peer samples and optional explicitly
   granted ciphertext/asset retention. Separate UID/state directory, resource limits,
   keys and API surface from codiauth. No native host command endpoint.
3. **TURN (when required):** standard separately configured relay software with
   expiring credentials, allocation/egress quotas and abuse controls. It transports
   encrypted WebRTC traffic, not password operations. An application relay instead
   terminates links and needs end-to-end payload encryption for private content.
4. **Owner file broker (later):** explicit owner authentication and approved host
   paths; keep its existing later gate. Not part of a public steward namespace.

The v0.3 ZIP does NOT start codi-steward/TURN or expose a new endpoint. This is the
implementation/deployment contract. Existing codiauth reference remains unchanged.
No package installation, firewall/DNS/TLS change, SSH operation or public port has
been authorized or performed just by generating this handoff.

## What is retained where

| State | Origin/identity | Steward | Browser |
|---|---|---|---|
| Public application release | Static immutable files | Optional verified cache | Loaded/optional cache |
| Registered credential verifier | Existing account DB | Never | Never sent to peers |
| Signing key | Issuer key only | Scoped service key only | Own session key |
| ANON identity | Short-lived issuance/session bookkeeping | Only leases for joined groups | RAM |
| Routing presence | Not a global table | Its shard, TTL; RAM by default | Small chosen working set |
| Namespace/room descriptors | Signed release seeds only | Assigned descriptor/shard replicas | Bounded lazy cache |
| Chat/game traffic | None | Transit only unless explicit retention | Own subscribed groups |
| User settings | Minimal opt-in encrypted profile, not required now | None by default | Local/explicit export |

Few bytes on disk does not mean little bandwidth: thousands of in-memory signaling
leases still cost connections, timer work, verification and network egress. Include
all of these in capacity reports. A pure browser peer has no always-on commitment;
David's dependable steward roles should be native processes on his machines.

## Rendezvous contract (planned)

Start with one small WSS control protocol in a test daemon. Implement bounded
`REGISTER_LEASE`, `JOIN_LOOKUP`, `FORWARD_SIGNAL`, `RENEW`, `LEAVE` operations under
one authenticated session. Pre-auth byte/time/connection caps apply. Reject
arbitrary URLs, TCP destinations and destination-less broadcast. Forward only to
an admitted destination lease that opted into invitations. Do not make an open proxy.
Offer/answer bodies have strict byte and lifetime ceilings, quotas and no durable
logging. Return a generic unavailable result where enumeration would leak identity.

Lease fields: lease ID, session public-key reference, scoped group discovery key,
routing revision, permitted capability, opaque reply route, issue/expiry times,
monotonic renewal counter, signature. Effective expiry is the earliest of lease,
identity, delegated authority and membership validity. A freshly signed packet
cannot extend a stale admission. Renewal has bounded jitter; no synchronized global
heartbeat. On restart, old RAM leases disappear and clients back off/re-register.

At scale, rendezvous shard storage replicates scoped leases to three independently
placed support peers. This is NOT three separate registrations against the login
server. A conflict/rollback fails closed; cell migration uses an explicit revision.
Replicas on one machine are not high availability. Replication is not authorization.

## Tier/cell assignment and hot keys

Routing uses independently sharded rendezvous keys plus bounded child descriptors.
Popular public discovery entries are cacheable and fan out to many cells; don't
hammer the same closest DHT nodes for every frame or join. Private descriptors are
capability-limited and never crawled globally. On split, immutable descriptors and
forward pointers expire within a finite overlap; repeated old/new dual reads do
not become a permanent duplicate pathway.

Select steward candidates from provisioned operators with resource/failure-domain
metadata, not every anonymous identity. An overlay built only from freely generated
keys can be captured by an adversary manufacturing keys (Sybil/eclipse). Local scores,
quotas, randomized peer selection and diverse bootstrap sources help specific attack
surfaces; they do not prove uniqueness or eliminate adversaries. Measure failures
under compromised peers; do not advertise a solved global trust problem.

## Migration/deployment sequence

Use loopback fake-time tests first. Then two LAN hosts, then two real Internet
networks with candidate diagnostics, then a separately authorized public pilot.
Co-locate roles on box-webhost initially only with independent process identities,
state trees, quotas and logs. Rehoming a steward changes a signed descriptor, not
client code or account ownership. A single 100+ Gbps host remains a single failure
domain and has finite socket, CPU and egress capacity. Scale by shard/provider, not
by making one process discover everybody.

Choose maintained routing and relay components at M04/M09. Vendor or reproducibly
pin dependency versions and licenses; keep executable source off remote peers. Do
not create a Docker requirement or add a database cluster before measured need.
