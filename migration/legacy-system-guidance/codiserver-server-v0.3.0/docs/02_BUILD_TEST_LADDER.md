# Unified build/test ladder v0.3.0

The previous identity/v86/desktop gates are retained, not erased or automatically
marked passed. David asked to assume those prerequisites for this design. Bind the
local workspace's existing evidence rather than rebuilding or relitigating them.
Pure model tests can run immediately without any daemon or guest assets. Before a
production integration gate depends on a baseline feature, attach its real witness.

The final implementation must have one browser session, one pooled transport and
explicitly scoped group services, not a second independent desktop or P2P engine.

## Inherited foundation

The original 15 gates remain: G00 source; W01–W05 ANON/RTC/desktop/v86; S00–S04
identity/service/deployment; I01 connected browser identity; P01 WAN; H01/H02
owner host files. The owner-file gates remain a separate feature and are NOT a
prerequisite for P2P groups. See contracts/acceptance.json for original obligations.

## P2P extension

### M00 — Bind the new domain and preserve existing evidence

Dependencies: G00. Two bounded tickets; six obligations.

**M00-01:** Bind current namespace and distinguish labels, nodes, rooms, key epochs and routes. Evidence: model + workspace inspection. Pass oracle: Fixture rename/move retains room ID; no invented old tree imported as fact.

**M00-02:** Record baseline identity/v86 as supplied assumptions or linked evidence, not new passes. Evidence: review. Pass oracle: Evidence distinguishes assumed prerequisites from measured real-browser execution.

**M00-03:** Freeze draft group framing, schemas and protocol negotiation before live forwarding. Evidence: protocol fixtures. Pass oracle: Unknown versions, duplicate JSON keys, malformed lengths and unsupported modes rejected.

**M00-04:** Bind the single global resource policy and threat model. Evidence: review + unit. Pass oracle: No per-window, per-room, cached hint or pending handshake bypasses global limits.

**M00-05:** Select maintained routing/crypto dependencies without adding a client build requirement. Evidence: review. Pass oracle: Record source/version/license/reproducible asset hash and why each dependency is necessary.

**M00-06:** Keep origin, stewards, TURN and owner-files authority independent. Evidence: review. Pass oracle: No public exposure or private key/owner permission acquired by role/name alone.

### M01 — Tree nodes with their own explicitly subscribed chats

Dependencies: M00. Two bounded tickets; six obligations.

**M01-01:** Create separate room identity for every eligible namespace node. Evidence: unit + real browser. Pass oracle: Parent, child and sibling events never appear in each other without explicit publication.

**M01-02:** Fetch namespace pages/path proofs lazily with hard bounds. Evidence: unit + real browser. Pass oracle: Huge/deep tree, cycle, unknown ancestor and oversize page produce bounded refusal.

**M01-03:** Authorize node create/move/delete and reject stale/conflicting descriptors. Evidence: protocol + integration. Pass oracle: Unauthorized move and signed descriptor fork are visible failures, not timestamp-wins merges.

**M01-04:** Separate bookmarks from hot subscriptions. Evidence: instrumented browser. Pass oracle: Thousands of saved descriptors do not start thousands of joins/sockets/timers.

**M01-05:** Reference-count room views within one browser session. Evidence: real browser. Pass oracle: Opening two views shares a subscription; closing the last view releases it once.

**M01-06:** Preserve existing desktop and v86 lifetimes. Evidence: browser regression. Pass oracle: Redraw/menu/workspace operations never restart the network or guest or fabricate transcript.

### M02 — One bounded pool of physical peer connections

Dependencies: M01, W02. Two bounded tickets; six obligations.

**M02-01:** Multiplex several admitted rooms over a deduplicated peer pool. Evidence: RTCStats witness. Pass oracle: Two rooms sharing a remote session use one physical RTC peer connection.

**M02-02:** Count pending and replacement connections against the same ceiling. Evidence: instrumented browser. Pass oracle: Simultaneous joins/reconnects remain at or below the configured global cap.

**M02-03:** Implement atomic join rejection and deliberate idle/unsubscribe. Evidence: unit + browser. Pass oracle: Failed join leaves existing admitted room state and queues intact.

**M02-04:** Bound crypto/parsing work before expensive verification. Evidence: adversarial test. Pass oracle: Oversized/unknown-key flood cannot allocate an unbounded task queue.

**M02-05:** Implement byte-aware fair scheduling across fixed traffic classes. Evidence: traffic measurement. Pass oracle: Bulk saturation cannot starve control/interactive work; reliable sends are accepted or explicitly rejected.

**M02-06:** Dispose session resources and expose honest state. Evidence: browser lifecycle. Pass oracle: Logout closes links/workers/timers and clears ANON data; no unload callback guarantee assumed.

### M03 — Origin-authenticated routed events for public groups

Dependencies: M02. Two bounded tickets; six obligations.

**M03-01:** Replace link-only packet assumptions with origin-event and hop-frame boundaries. Evidence: protocol + real RTC. Pass oracle: Forwarded event still verifies its original author; transplant to wrong group/link rejected.

**M03-02:** Use signature-independent event IDs and bounded verified deduplication. Evidence: crypto negative fixtures. Pass oracle: Alternate valid ES256 signature over same signing input cannot trigger duplicate delivery.

**M03-03:** Accept bounded out-of-order sequences per admitted stream. Evidence: protocol + unit. Pass oracle: Reorder within window accepted once; duplicates, old window and giant attacker allocations rejected.

**M03-04:** Keep replay floors for complete live acceptance windows. Evidence: adversarial test. Pass oracle: Cache/stream pressure cannot reset replay protection for still-admissible old streams.

**M03-05:** Demonstrate four simultaneous rooms with eight actual browser contexts. Evidence: real RTC integration. Pass oracle: Per-room recipient denominator and zero unintended-room deliveries recorded; BroadcastChannel not used.

**M03-06:** Bound forwarding and missing-history repair. Evidence: fault injection. Pass oracle: Loop, lost neighbor, expired event, hop exhaustion and full repair queue produce measured bounded work.

### M04 — Delegated rendezvous without expanding the login service

Dependencies: M03, S00. Two bounded tickets; six obligations.

**M04-01:** Implement loopback steward admission with explicitly scoped service keys. Evidence: real HTTP/WSS. Pass oracle: Unprovisioned self-promoted steward, expired grant and wrong room range rejected.

**M04-02:** Publish expiring authenticated leases with capped replies. Evidence: unit + real network. Pass oracle: Lease expiry capped by all relevant grants; no entire-room/global roster response.

**M04-03:** Carry signed offers/answers through intended invited routes only. Evidence: adversarial network. Pass oracle: Oversize SDP, expired replay, arbitrary destination URL and unsolicited broadcast rejected.

**M04-04:** Keep private room discovery opaque and permission-scoped. Evidence: inspection + privacy tests. Pass oracle: No private names, memberships, candidate SDP or content exported to public directory/logs.

**M04-05:** Handle steward restart and seed loss with bounded jittered retry. Evidence: fault injection. Pass oracle: RAM lease loss is visible; no reconnect storm or fake availability.

**M04-06:** Keep support processes separate from origin identity and host files. Evidence: network trace + privilege tests. Pass oracle: Ordinary posts bypass codiauth; role credentials cannot read host paths or issue account certificates.

### M05 — Reviewed private-group admission and rekey lifecycle

Dependencies: M03. Two bounded tickets; six obligations.

**M05-01:** Bind one reviewed group-key profile/library and documented trust boundary. Evidence: security review. Pass oracle: Private routed UI remains blocked until this gate; raw per-hop DTLS never mislabeled as relay-private.

**M05-02:** Authenticate control epochs and membership independently of routing cells. Evidence: crypto integration. Pass oracle: Cell migration cannot grant membership or reuse wrong-epoch private data.

**M05-03:** Test add/remove/rekey and pre/post-removal traffic. Evidence: multi-peer crypto. Pass oracle: Removed member cannot read/publish new canonical epoch content; overlap does not revive grants.

**M05-04:** Define honest partition behavior without automatic competing canonical key schedules. Evidence: fault injection. Pass oracle: Controller loss blocks canonical membership changes; optional new groups have distinct IDs.

**M05-05:** Test join/leave storms, lost key updates and bounded catch-up. Evidence: load + privacy. Pass oracle: Memory/CPU/key material/history buffers capped; unavailable keys fail clearly.

**M05-06:** Separate identity, authorization, secrecy and truth in UI/protocol. Evidence: negative cases. Pass oracle: Valid signature cannot create privileges or validate a false game result; expired identity not silently downgraded.

### M06 — Verified local caches and explicit retention

Dependencies: M03. Two bounded tickets; six obligations.

**M06-01:** Implement hash-addressed binary chunks and trusted publisher binding. Evidence: storage + crypto. Pass oracle: Wrong bytes rejected; untrusted but hash-correct code never executed automatically.

**M06-02:** Keep ephemeral ANON data in memory by default. Evidence: browser storage inspection. Pass oracle: Reload/logout clears user state; opting into public asset cache does not persist identity or chat.

**M06-03:** Enforce bytes, count, quota, TTL and pin budgets. Evidence: browser fault tests. Pass oracle: Pinned-full/eviction/quota denial returns capacity; no silent reliable data loss promise.

**M06-04:** Advertise only held verified chunks and withdraw on expiry/eviction. Evidence: P2P transfer. Pass oracle: Disappeared provider or partial chunk retries within a bound; no fake successful fetch.

**M06-05:** Implement explicit retained ciphertext leases and bounded offline mailbox scope. Evidence: multi-host integration. Pass oracle: No origin chat storage; lost replicas and expiry visible; remote erasure not promised.

**M06-06:** Measure bulk fairness while chat/game/control are active. Evidence: browser performance. Pass oracle: Large model/guest/image transfer remains chunked; controls meet recorded latency targets.

### M07 — Sharded routing, cell split/merge and migration

Dependencies: M04. Two bounded tickets; six obligations.

**M07-01:** Use bounded directory lookups among provisioned stable stewards. Evidence: network + algorithm tests. Pass oracle: No global enumeration; parallelism/work/wall-time caps enforced on adversarial replies.

**M07-02:** Assign members to bounded discovery/delivery cells without full mesh. Evidence: model + real pilot. Pass oracle: Peer degree stays capped while cell membership increases; hot-key metrics recorded.

**M07-03:** Sequence split descriptors with finite migration overlap. Evidence: migration tests. Pass oracle: Duplicate path deliveries deduplicate; stale split/grant rejected and old routes expire.

**M07-04:** Prove replica/failure-domain accounting and single-writer fencing policy. Evidence: failure injection. Pass oracle: Same-host replicas not counted independent; controller fork stops changes visibly.

**M07-05:** Merge only with hysteresis and preserve room/content IDs. Evidence: load + fault. Pass oracle: Rapid threshold oscillation does not cause endless resharding or lose acknowledged events.

**M07-06:** Expose large-room semantics instead of hiding fan-out. Evidence: browser UX + counters. Pass oracle: Announcement recipients receive every accepted announcement; separate conversations have distinct visible IDs.

### M08 — Games and app-scoped group capabilities

Dependencies: M03. Two bounded tickets; six obligations.

**M08-01:** Create per-match groups separate from lobby/parent chat. Evidence: real browsers. Pass oracle: Unrelated spectators/rooms do not receive input/state unless explicitly subscribed.

**M08-02:** Separate reliable actions/checkpoints from expiring latest-state updates. Evidence: fault injection. Pass oracle: Packet loss does not queue obsolete positions indefinitely; commands remain attributable.

**M08-03:** Define game authority and result validation rather than trusting signatures. Evidence: game oracle. Pass oracle: Signed impossible race/board state rejected by rules/replay or labeled unverified.

**M08-04:** Constrain apps/guest bridges to scoped capabilities. Evidence: security integration. Pass oracle: Peer messages and game scripts cannot invoke host files, guest shell or authority signing.

**M08-05:** Publish bounded-rate spectator snapshots separately. Evidence: load measurement. Pass oracle: Spectator growth cannot silently expand player mesh or tick broadcast denominator.

**M08-06:** Choose measurable per-game latency and migration rules. Evidence: real network. Pass oracle: Controller departure pauses/reconciles or ends match honestly; no global deterministic realtime promise.

### M09 — NAT, suspension, partitions and malicious peers

Dependencies: M04, M05, P01. Two bounded tickets; six obligations.

**M09-01:** Prove direct and relay-only connections across distinct real networks. Evidence: WAN RTCStats. Pass oracle: Record actual candidate types; blocked NAT without relay fails rather than HTTP chat fallback.

**M09-02:** Freeze/discard/sleep/restart browsers while rooms are active. Evidence: browser lifecycle. Pass oracle: Leases expire and peers repair; resumed browser revalidates before live sends.

**M09-03:** Inject whole-steward/operator loss and split networks. Evidence: multi-host faults. Pass oracle: Report reachable recipient denominator, lost history, authority outage and recovery work.

**M09-04:** Exercise Sybil/eclipse/spam threats with capped admission and diverse provisioned support. Evidence: adversarial pilot. Pass oracle: No claim that certificates/peer scores prove unique humans or defeat arbitrary adversaries.

**M09-05:** Test relay privacy and traffic quotas. Evidence: security + traffic traces. Pass oracle: Application relay cannot read private payload; TURN/forwarding limits prevent open-proxy abuse.

**M09-06:** Test reordered, duplicated, delayed and forged packets at scale. Evidence: fuzz + faults. Pass oracle: No unverified cache poisoning/replay-state advance; logs bounded and redact sensitive data.

### M10 — Measured load ladder and ten-billion-device accounting

Dependencies: M06, M07, M08, M09. Two bounded tickets; six obligations.

**M10-01:** Run real groups at 2/8/32 peers within available hardware and state exact topology. Evidence: real load. Pass oracle: Missing hardware capacity is blocked, not fabricated; actual separate processes distinguished from simulation.

**M10-02:** Run event simulations at 1k/10k/100k with realistic skew/churn scenarios. Evidence: simulation. Pass oracle: Report modeled mechanisms/omissions; ideal graph toy does not count as distributed-protocol proof.

**M10-03:** Measure CPU, memory, bytes, queue depth, retransmits and p50/p95/p99 latency. Evidence: instrumentation. Pass oracle: Published denominators include all admitted jobs/recipients, losses and failed reconnects.

**M10-04:** Project 10^10 population with explicit online fraction, room mix and relay rate. Evidence: accounting review. Pass oracle: Analytical result labeled extrapolation; no ten-billion live test claimed.

**M10-05:** Demonstrate offered load below measured forwarding capacity or enforce refusal. Evidence: capacity admission. Pass oracle: Constrained/noncontributing users cannot create an unfunded perpetual relay/storage commitment.

**M10-06:** Falsify root/global-hotspot assumptions. Evidence: fault + load. Pass oracle: Root disconnect leaves valid local groups independent; hot discovery key overload triggers sharding/refusal not global scan.

### M11 — Explicitly approved staged public operation

Dependencies: M10, S04. Two bounded tickets; six obligations.

**M11-01:** Prepare process/key/state layout for box-webhost and delegated peers. Evidence: operator review. Pass oracle: Origin, stewardship, TURN and owner broker separated; no public deployment without authorization.

**M11-02:** Pin binaries/dependencies and rotate scoped keys with rollback protection. Evidence: security rollout. Pass oracle: Compromised/revoked service key fails after its authority lifetime; no issuer secret in peer assets.

**M11-03:** Run small public pilot with limits and privacy-preserving telemetry. Evidence: pilot. Pass oracle: Track failure domains and real bandwidth/connection capacity; no generic global analytics beacon.

**M11-04:** Practice draining/rehome/backup/restore of assigned portions. Evidence: ops rehearsal. Pass oracle: Signed descriptor change works without client code rewrite; immutable source remains recoverable.

**M11-05:** Verify authority outage/expiry and disaster recovery. Evidence: fault rehearsal. Pass oracle: No fabricated freshness, automatic trust downgrade or indefinitely live revoked authority.

**M11-06:** Publish evidence ledger and only expand after declared thresholds. Evidence: review. Pass oracle: Passed/failed/blocked/assumed/model-only statuses remain separate; no scale claim from artifact count.

## Evidence progression

Start with node/room isolation and one pooled transport on two browsers. Then
four rooms/eight browser contexts, a delegated loopback rendezvous peer, private
rekeying, bounded cache transfers, sharding and game-specific traffic. Only then
advance to WAN fault tests and larger simulations/pilots. The next ticket is M00-T01.
Do not deploy a global DHT, TURN farm or cloud fleet just to demonstrate two rooms.

The graph fixture and pure model tests only test their explicit idealized rules.
No acceptance gate above is marked passed by those tests. The model is a reference
oracle, not a parallel production processing path.
