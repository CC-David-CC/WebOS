# Browser and webhost direction

Updated 2026-10-21 from David's long-term direction. This is an implementation
roadmap; a versioned handoff is not evidence that all its features are running.

Current direction,2026-10-25UTC: live chat is DISABLED at the user's request.
All117 saved test messages and33 test rooms were explicitly deleted without a
chat-data backup. Public chat/introduction endpoints are blocked; saved-chat and
coordinator services and its refresh timer are stopped. Desktop, Linux, accounts,
private files, blog and sizing prototype remain available. The unavailable UI
rollout is live and verified; exact final receipt is in the latest handoff.

The bridge-fixed isolated512-agent test passed20checks with16realChrome,
0v86, independent Caddy and production-class coordinator, six bursts and120s
steady sampling. Previous512 fragmented into496/11/5 islands; the new bounded
cross-island probes also pass a real controlled16-agent split/heal regression.
The isolated historical hosted-protocol 2,048-agent run failed after 1,244
admissions: ordinary room/auth bootstrap and the coordinator returned capacity
errors. All 64 owned browsers and fixture resources were cleaned up. This is a
measured failure of that remaining central-service path, not a hard channel
size limit. New peer-owned protocol acceptance, 8k and a fresh outside-WAN proof
remain unfinished.

The eventual design keeps content on participating devices. The server provides
initial introductions and only explicitly chosen bounded fallback; it stores
channel history only when the operator opts in a history-holding supernode.
Separate intentional channels/islands need not mix. Routing stays invisible;
chess legality and optional spectating apply independently of player location.
Always-on supernodes and raised limits are deferred; CDN is deferred. This is a
direction, not a claim that the current hosted protocol already meets it.

Before chat reopens, users must explicitly accept local storage and obtain a
real persistent browser-storage grant. Declining or unsupported storage blocks
chat and other features that rely on local history, while independent tools
remain usable. Permission does not survive user-cleared data/device loss and is
not a server-verifiable authorization signal. Consent and signed-checkpoint
storage components pass 31 actual browser checks, including reload, conflicting
writes and browser-process crash. The shared host integration passes 24 compiled
browser checks and is now included in live SDK9f86587c. Live upgrade, paused
rollback and re-upgrade passed, with Linux and independent apps usable. Chat
remains paused, so its gate and history resources do not start on live. Durable
peer-owned authority, private controller-key custody, chunked replica history
and chess integration remain required before chat can reopen.

The next source increment now passes 28 durable-key checks and 49 compiled
permission/checkpoint workflow checks in Chrome. It verifies current write
permissions, preserves original signed IDs during reinclusion, rejects replay
through sparse operation-set witnesses, checks replica certificates and saved
ancestry, and restores separate legal chess/PGN state. It is not deployed and
does not yet run replica consensus. A source fixed-membership core now passes 28 compiled durability/view-change
checks. Real transport, automatic repair and joint membership, the pending-message
outbox and peer-held history/witness graph remain required. The fixture manually creates certificates in one
browser; it supplies no actual mesh, fault-domain or 8k evidence.

Earlier increment paragraphs below retain their historical artifact scopes.

Current state, 2026-10-24: the actual desktop is live at `https://ksu.codes/`, and
the former homepage is at `/blog/`. `/desktop/` remains the unchanged backend-free
sizing prototype. Native/file/guest and signed root/publisher endpoints were
migrated together after real VM interruption/recovery/forward-rollback tests.
Public root terminal, documents, lifecycle, cache and registered-only guest
Internet checks pass. Current evidence/pins are in `AGENTS.md`,
`active-system/goal-requirements.json` and the latest handoff entries. The early
progress rows/receipts below describe their historical stages. The full active
goal at the end remains in force: scalable islands/gossip, durable checkpoint
convergence, browser PoW, spectator roles and actual8k tests are still unfinished.

Increment 2026-10-25 UTC: native21/5ad8cefa is live with saved public chat and
verified peer checkpoint delivery through the shared pool. A real90000-byte
checkpoint and partial-transfer cancellation pass over public TURN/TLS443 across
two Internet connections. Five-second idle and20-second total bounds replace
the observed five-second total-timeout failure. Native/apps/private backend bytes,
root/blog/prototype and other sites are retained. This is scoped transfer evidence;
automatic hosted member organization, incremental tails, islands/bridges, replica
agreement, full correspondence chess and8k transport/admission are still required.
See `active-system/evidence/hosted-peer-timeout.md` for exact current proof/pins.

The next increment is now live as native21/a5d5a907: negotiated accepted-receipt
tails, full visible-window reload, controller-checkpoint fallback for older gaps,
and stale-read protection. Public peer10 and two-network TURN/TLS13 pass; the
measured short-message update uses17786 authenticated bytes including its notice
versus128301 for the initial window. This is one workload, not8k capacity proof.
Current preservation, rollback, cleanup and boundaries are in
`active-system/evidence/hosted-peer-window.md`. Member organization/islands and
the remaining full goal below are still required.

## Version progression and sources

| Stage | Supplied source | Role | Current evidence in this live workspace |
|---|---|---|---|
| v0.1 | `codiserver-browser-v86-auth-handoff-v0.1.0/` | Browser desktop, local identity, isolated Linux guest | Working desktop and shared guest home; 13 Chromium integration groups passed. The live browser has no login page or account service. |
| v0.2 web | `codiserver-web-v0.2.0/` | Browser session, signed one-peer WebRTC chat, manual signaling, connected identity integration | Direct signed WebRTC chat integrated; two isolated visible Chromium sessions exchanged messages over host candidates. Connected browser identity remains unverified. |
| v0.2 server | `codiserver-server-v0.2.0/` | Small identity issuer and public static resources | 42 reference identity/service tests passed in the project environment; no public deployment is claimed. |
| v0.3 web | `codiserver-web-v0.3.0/` | One bounded peer pool, per-node chats and explicit groups, scoped message routing | Architecture/contracts/model tests supplied; group networking is an implementation task. |
| v0.3 server | `codiserver-server-v0.3.0/` | Small identity origin plus separately delegated support/steward roles | Steward/relay architecture supplied; no deployed steward or TURN service is claimed. |

Current integration target is `active-system/`; `desktop-lab/` independently
holds the backend-free sizing lab. Root files are preserved baseline/reference.
Preserve the real v86 guest, Files, Text Editor, window controls and existing
theme. Use the later packages as contracts and reference code; do not replace
the active system with an older snapshot that lacks the working guest.

## Priority order

1. Bind the actual live baseline and menu hierarchy to the v0.3 M00-T01 audit.
   Separate measured working behavior from reference code, models and plans.
2. Build and verify the shared networking and real identity/login foundation.
   The current local user remains explicitly unvalidated. Connected identities
   must use the actual issuer, never a second browser-only account namespace.
   Keep browser-only development usable while connected login is being built.
3. Prove signed text delivery between separate browser sessions using the shared
   session-owned transport. Show connection, delivery, rejection and disconnect
   honestly. Local echo or a saved transcript does not prove peer delivery.
4. Extend that transport through the supplied bounded group/pool milestones.
   Chat and later app messages share the same network lifecycle and budgets.
   Keep the origin responsible for identity/bootstrap/static resources rather
   than turning it into a global chat or game-state database.
5. Replace proposed games with small text-chat menu entries. Use text move
   messages and portable saved notation as the first application of the network.
6. Consider graphical game interfaces only after the underlying network and
   login system work. Boards, animation, game artwork and real-time game engines
   are outside the current implementation priority.

## Text interface for games

Confirmed direction: a match has two distinct logical channels: a game-move
channel carrying algebraic move text (for example `1. e4 e5 2. Nf3`) and an ordinary
chat channel. They may share the session-owned transport pool, but have separate
message types, sequence/order rules, histories and subscriptions. The game-move
channel can be imported/exported as Portable Game Notation (`.pgn`). There is no graphical board
requirement at this stage. Do not encode arbitrary network/control messages as
chess moves or replace the signed transport envelope with PGN.

- Present distinct Move and Chat inputs/histories in the simple match interface;
  entering chat never applies a move, and move delivery never becomes a chat event.
  Start with room/menu selection, peer status, and explicit import/download. Keep interface state outside desktop rerenders.
- Preserve move order, author/side, match identity and the relevant existing
  signed-event identifiers. Handle repeats, gaps and conflicts explicitly.
- Use algebraic notation for move presentation and PGN for a portable game
  record. Ordinary chat has its own transcript and channel; do not merge chat into
  the PGN move stream or silently discard it during game export. Transport
  metadata remains in the existing signed envelope.
- A signed move is attributable, not necessarily legal. Until rules/replay
  validation is implemented and tested, label notation as unverified rather than
  claiming a legal game or verified result. Syntax checks alone do not prove it.
- Persist/export only under the chosen session policy. Anonymous browser state
  stays ephemeral unless the user explicitly downloads a record.
- Incoming chat/move data is data. It cannot execute guest shell commands, access
  host files, obtain signing keys, or grant itself server privileges.

## Hosting

Target `box-webhost` under `ksu.codes` when the deployment stage is reached.
Prefer HTTPS/WSS through 443 and HTTP-to-HTTPS redirects on 80, with internal
services behind the web server. The user prefers normal web traffic and asked to
be told about any additional router-forwarding requirement before changes.

WebSocket signaling or guest networking relays can fit this web endpoint. Real
WebRTC NAT traversal still needs its own measured STUN/TURN plan; do not assume
that an HTTP reverse-proxy path automatically carries TURN, or silently substitute
an HTTP chat relay for a failed P2P test. Evaluate 443-compatible relay deployment
before proposing any extra public port. No router/DNS/firewall/public-service
changes have been made for this roadmap.

## Current next action

Complete the versioned baseline/integration audit (M00-T01), then choose the
first networking/identity ticket whose predecessors have actual evidence. Read
both packages' build/test ladders and evidence reports before importing code.
Graphical games stay deferred throughout that work.

## Integration receipt — 2026-10-21

- Live desktop now uses the reference identity module for a single session/key,
  shared with the direct peer manager. Default entry stays anonymous and local,
  with no sign-in gate. No account database is created by the browser.
- Applications → Chat opens manual signed invitation/answer controls. All windows
  share one direct link, bounded ephemeral history, and the session lifecycle.
  This is the inherited codi-peer/1 direct chat foundation, not the v0.3 pool.
- `scripts/peer-check.py --visible`: two separate Chromium sessions connected,
  exchanged signed chat in both directions, and rendered HTML as literal text.
  `.build/checks/peer-result.json` reports open RTCDataChannels and host/host
  candidates. Both windows were left open at the user's request. WAN untested.
- `scripts/functional-check.py`: all 13 desktop integration groups passed after
  the shared session and Chat integration; `.build/checks/result.json`.
- Server reference: 42 tests passed using `.build/auth-venv/bin/python` from
  `codiserver-server-v0.3.0/` with `-m unittest discover -s tests -p test_service.py`.
  An initial invocation from the root failed because that directory has no tests/;
  it was corrected by selecting the reference server directory. This is service
  evidence, not yet a connected browser/login integration claim.
- Dependencies installed with explicit user approval in `.build/auth-venv`: use
  its `pip freeze` receipt for exact resolved versions. No public service, router,
  DNS, or system package configuration changed.
- Next: stage only approved public assets separately from issuer state, integrate
  the loopback issuer, and measure connected browser entry/renewal/logout. Keep
  ordinary chat and future chess moves as separate logical channels; the current
  chat protocol does not yet implement chess moves, PGN, groups, or routing.

### Connected identity integration

The live loopback desktop at 8098 now uses the same session/key for anonymous
issuer entry, peer manager and guest metadata. `scripts/serve-connected.py` stages
only public runtime files; the unchanged supplied Python issuer owns separate
private state. HEAD middleware supplies guest asset preflight compatibility.
Browser sign-in remains disabled as requested. The registered-account API uses
one real issuer namespace, with fresh browser session keys on every entry.

`scripts/identity-check.py` exercises real guest boot with a test-server identity,
renewal with stable session/key, repeated registered login with stable account and
fresh sessions, rejection of wrong passwords, revoked-session renewal rejection,
and 404 responses for private state/source paths. This proves loopback browser
integration, not public deployment or WAN behavior. Automatic renewal's due branch
is exercised by advancing only its client scheduling threshold, then verifying a
fresh actual issuer certificate. Existing visible local chat windows are preserved.

Next: record the M00 baseline against the full acceptance registry, then implement
the bounded session pool and separate application channel contracts in dependency
order. Direct chat is working; routed groups and chess move/PGN handling remain
unfinished. Public hardening, deployment and NAT traversal remain separate gates.

M00 audit is recorded in `evidence/M00-baseline.md`. Strict browser JWS parsing
now rejects duplicate decoded names and excessive nesting. Eighteen real-browser
protocol fixtures cover parser bounds, distinct stable room lanes and initial
public mesh framing. M00-T01 is still partial: complete signed origin schema,
admission and replay integration remain. No live routing/private group mode was
enabled. Follow M01 before M02 rather than skipping gate prerequisites.

The protocol receipt now contains 26 passing browser fixtures, including signed
public origin verification, signature-independent IDs, scope/key/expiry rejection
and move/chat separation. The initial public profile is frozen in
`network/MESH-PUBLIC-PROFILE.md`. It is not wired into live links. M00-T02 global
budgets/dependency review is next; no full M00 gate or routed runtime is claimed.

Session resource budgets are now wired into the existing peer runtime, with shared
connection, pending crypto, wire queue and metadata leases. Disposal checks require
zero remaining charges after work settles. `evidence/M00-resource-policy.md`
records the invariant, caps, threat/role boundaries and dependency decision.
M00-T02 remains partial because maintained discovery/routing and reviewed private
crypto choices have not been made. No private forwarding or v0.3 pool is claimed.

Source dependency candidates are pinned with archive/license hashes in
`evidence/network-candidates.json` and evaluated in `evidence/M00-dependency-review.md`.
No new runtime package or private mode is enabled. M00-05 remains partial pending
reviewed integration. The signed public-directory prerequisite is implemented and
fixture-tested in `network/namespace.mjs`; see `evidence/M01-directory-prerequisite.md`.
The protocol suite now has 51 passing browser cases. This is not a live directory
or completed M01 gate. Node creation/moves require controller/parent signatures,
while page/path/cache bounds share the session resource budget.

The original static server's workspace-wide serving was restricted to explicit
public runtime/assets after private issuer state was introduced. Both servers now
reject private/source paths; `.build/checks/public-boundary.json` records actual
HEAD status checks. Existing visible peer windows were preserved during restart.

Direct Chat now uses the session's shared room subscription registry. Real-browser
checks prove duplicate windows/redraws share one subscription and RTC link, the
last close releases the hot room, reopening restores bounded history, and rejected
oversized UTF-8 input does not destroy the link. The registry isolates room/lane
histories and cold bookmarks under global budgets. See
`evidence/M01-subscriptions.md` for bounds, receipts and limits. Verified namespace
rooms are not yet connected to the UI; no full M01 gate or routed pool is claimed.

`network/replay.mjs` now supplies the public-origin replay prerequisite: explicit
admitted streams, signature/scope verification before mutation, 64-entry windows,
no floor eviction, bounded capacity, expiry and disposal. See
`evidence/M03-replay-prerequisite.md`. It is not live forwarding or a completed M03
gate. Next runtime slice: negotiate a public application profile over the existing
peer link, authenticate explicit room admission, then connect verified room events
to the shared subscription UI. Keep the identity/guest and private-profile gates.

The peer transport now supports signed explicit public application negotiation on
the same channel/key. `scripts/application-check.py` proves two real browser sessions
can exchange a room invitation, accept signed two-peer admissions, and verify separate
chat/move origin events on one RTC link. See
`evidence/public-application-integration.md`. This is not yet a Rooms UI or multi-hop
pool; default Chat advertises no application handler until dispatcher integration.
Next: bounded explicit Create/Accept/Decline room controls, session-owned replay
floors, and separate text chat/move views, followed by PGN. Private routing stays off.

The text Rooms UI is now integrated with the live session dispatcher. Create,
Accept and Decline run through authenticated two-peer invitations; room chat and
move notation have separate inputs, histories, scopes and sequence counters on one
RTC link. Local and connected-issuer browser cases passed, including `e4/e5`,
literal HTML, a declined second room, preserved first-room state and zero disposal
charges. See `evidence/rooms-ui.md`. This supersedes earlier notes that default
Chat had no application dispatcher. Next application work is legal notation/replay
and PGN import/export; broader pool/discovery/private-routing gates remain open.

Legal move validation and PGN are now integrated: a pinned self-hosted rules engine,
canonical SAN signed on the move lane, independent receiver validation, separate
PGN/chat downloads, and read-only historical PGN imports in a bounded worker.
Local and issuer-backed UI tests prove invalid moves are not transmitted and
imports do not alter live games or send events. See `evidence/pgn-and-rules.md`.
Next: the broader shared peer pool and discovery/routing milestones. Private
routing, public deployment and WAN behavior remain unproven.

The shared multi-peer pool is live. Three-browser local and issuer-backed cases
show two accepted peers/games, per-window conversation isolation, shared pending
limits, duplicate-session rejection and isolated disconnect without restarting
the guest. `evidence/shared-peer-pool.md` maps the implementation and proof scope.
M02 remains partial: byte-fair scheduling/traffic measurements and broader
contention/glare cases remain; discovery/routing/private/WAN gates are still open.

Session-wide deficit byte scheduling is now integrated with explicit control
reserves, rate/job bounds, cancellation and message deadlines. Actual local and
issuer-backed RTC contention cases deliver control before queued bulk, preserve
strict link sequence and account for explicit backpressure retries. See
`evidence/traffic-scheduling.md`. Ingress attack contention, glare, discovery,
routing/repair, private crypto review and WAN/deployment still remain open; M02
is not wholly passed. Next: bounded support/discovery integration prerequisites.

### Discovery prerequisite (2026-10-21)

Added bounded release-pinned signed bootstrap/steward validation with endpoint,
scope, expiry and capacity delegation; revision floors and authenticated-fork
freezes; shared crypto/metadata accounting. Browser protocol fixtures cover this
layer. It is not yet wired into the desktop or an actual rendezvous daemon.
Next: authenticated, quota-limited loopback rendezvous and browser support links,
then LAN/Internet candidate diagnostics. No public deployment or extra router port
has been configured. Existing manual P2P flow and the v86 guest are preserved.

### Rendezvous RAM state prerequisite (2026-10-21)

Added the independent native `steward/leases.py` component: bounded explicit public
scopes, owned leases, expiry/renewal, opt-in random samples, intended signaling
routes, one-answer digest floors, and disconnect/restart disposal. All 31 state
tests pass. No socket or authentication facade is exposed. Transport proof and
signed lease output are still required before this can serve browsers; see
`steward/README.md`. The supplied M04 registry remains planned pending its actual
network-level acceptance cases.

### Authenticated loopback steward transport (2026-10-21)

The prior RAM-only prerequisite now has a root-delegated, loopback-only WebSocket
adapter with signed challenge/authentication, signed leases and sequenced requests,
intended offer/answer routes, socket/frame/time/rate/egress limits and generic
failure closure. Thirty-one state checks plus nineteen actual loopback checks
pass. Actual Chrome verifies the bootstrap chain, authenticates and verifies a
lease; forwarding tests still use fixture SDP. No desktop support client exists
yet, and TLS/LAN/WAN/M04 acceptance is incomplete. Next integrate one bounded
support-client manager per session with the existing PeerPool and prove real RTC
chat and separate move channels using automatically exchanged signals.

### Browser support client and real RTC module bridge (2026-10-21)

Added the optional shared-budget `sessionSupport` client. Actual Chrome tests
verify the full seed/service chain and live authentication, signed leases, renewal,
local invalid-request recovery, leave and canceled-auth cleanup. Two isolated
sessions/PeerPools inside one Chrome now exchange actual offers/answers through
the native steward and deliver real signed RTC chat; all resources return to zero.
19 network checks and 31 state checks pass. Product discovery controls, two-window
Chat/Rooms tests, renewal/reconnect management and WAN evidence remain next.

### Desktop public discovery integration (2026-10-21)

Optional Chat controls now discover sampled public peers and require explicit
invitation acceptance through the existing session PeerPool. Native signaling
supports real two-Chrome desktop chat and separate legal text moves; guests remain
unchanged and RTC survives stopping discovery. Jittered leases renew, pending work
and hints are bounded, and final disposal reaches zero. Twenty network and 31
state checks pass; manual peer Rooms and all 13 desktop groups also pass. A
loopback-only RAM-key demo is available via scripts/serve-discovery.py. Automatic
reconnect/seed refresh, glare, WSS/LAN/WAN and complete acceptance gates remain.

### Discovery-managed crossed offers (2026-10-21)

Resolved the reproduced simultaneous Invite race with deterministic verified
SID/key arbitration, preserving explicit consent. Expanded real two-Chrome tests
cover ordinary connection/disconnect, incoming-first orders, two real signed
offers held before delivery, conflicting-key injection and exactly one surviving
ready RTC link per browser. Existing room chat/moves, guests, renewal, support-stop
survival and disposal remain verified. Twenty network checks and 31 state checks
pass; failed before-fix evidence is retained. Manual-code glare and automatic
support recovery/seed refresh remain unfinished.

### Bounded discovery transport recovery (2026-10-21)

Added same-session recovery for transient steward loss, retaining signed authority
floors and the existing peer pool. One worker, jittered exponential delay and five
attempts per page lifetime bound reconnect work; fatal signatures/protocol/expiry
and Stop terminate it. Native listener/registry restart preserves RTC room chat,
legal Nf3, session keys, connection IDs and guests in two actual Chrome desktops.
Twenty-one grouped network checks and 31 state checks pass, including retry-limit,
refusal, cancellation and expired-authority cases. Signed seed refresh, admission
maintenance, multiple-steward failover, true process/failure-domain tests and
WSS/LAN/WAN remain unfinished; no full gate or deployment is claimed.

### Signed expected-operation refusals (2026-10-21)

Stale signaling and missing/unauthorized resource requests can now fail without
closing healthy source discovery. A dedicated signed error profile preserves exact
success schemas and binds refusals to nonce/sequence/operation. Refusals consume
quota; invalid protocol/crypto/replay remains fatal. Two-Chrome tests prove stale
invitation acceptance preserves existing RTC/guest state. Native transport fault,
quota and invalid error-frame tests pass. Twenty-six network groups and 31 state
checks pass; a cached UI error masking recovery was also fixed. Seed refresh,
admission maintenance, multiple stewards and WSS/LAN/WAN remain unfinished.

### Signed bootstrap refresh (2026-10-21)

Optional same-origin bundle refresh is integrated into Chat and bounded automatic
maintenance, retaining original pins and revision floors. Real Chrome tests adopt
new seed/service revisions while preserving RTC/guest/session, reject rollback and
malformed/redirected/oversized/stalled data, enforce learned scope revocation, and
cancel valid late reads. Native descriptor renewal is locked, monotonic and capped
by existing delegation. Twenty-seven network groups and 31 state checks pass.
Admission renewal, persistent publisher revision/root-policy reload, multi-steward
failover and WSS/LAN/WAN remain unfinished. No gate/deployment promotion is claimed.

### Same-connection admission maintenance (2026-10-21)

Discovery can now renew admission without replacing its identity, socket nonce,
peer pool, leases or quota. Fresh issuer proofs remain key/account-bound and cannot
extend stale membership/delegation; browser validation and jittered scheduling are
integrated. Two real Chrome desktops survive actual shortened admission deadlines;
fixture-issuer native tests cover fresh/old/expired certificates and negative
transfer/replay/downgrade cases. Twenty-eight network groups and 37 state checks
pass. This does not renew peer-room membership or peer certificates. Persistent
publisher/root-policy state, WSS/LAN/WAN, failover and other original gates remain.

### Durable publisher revisions (2026-10-21)

Added explicit private SQLite publication state and a provisioned loopback daemon.
Descriptors commit before return; restart reuses exact signed bytes and monotonic
floors, while unsafe/corrupt/missing/forked state fails closed. Twenty-four actual
persistence/process tests, 28 network groups and 37 RAM-state cases pass. Live
browsers accept a higher descriptor before a reopened-state restart and preserve
RTC/guest state. Root-policy reload/migration, peer/room upkeep, deployment UID/key
custody, multiple stewards and WSS/LAN/WAN remain unfinished.

### Signed root-policy reload (2026-10-21)

The provisioned daemon now verifies and applies newer signed seed policy while
running. Scope/capacity/expiry changes replace RAM admissions, preserve durable
floors and global rate limits, and publish the new bundle before closing old
controls. Reconnecting browsers verify the source before reauthenticating; removed
scopes stop while existing RTC links survive. Seven focused policy groups pass,
including actual Chrome traffic. See evidence/root-policy-reload.md for daemon
watch verification, receipt scope and failure behavior. Peer/room upkeep, policy
migration, multiple stewards and WSS/LAN/WAN remain unfinished; no gate promotion
or public deployment is claimed.

### Peer certificate upkeep (2026-10-21)

Signed handshake negotiation now enables same-key/account/session certificate
updates over existing RTC links. Current proofs are separate from the original
signed signaling transcript; new room invitations use them. Automatic upkeep
preserves link identity and replay sequence, rejects expired/non-advancing or
transferred authority, and uses existing shared control budgets. Local equal-expiry
issuer refreshes send no redundant update. Older peers retain original expiry.
See evidence/peer-identity-maintenance.md for focused actual Chrome evidence and
regression results. Room membership/descriptor/origin admission renewal and all
remaining distributed/public deployment gates still require work.

### Two-peer room upkeep (2026-10-21)

The current desktop opts into signed codi-room-renew/1 through its shared pool.
Controller-only chained descriptors and four same-stream grants extend live room
authority after a matched peer ack. Existing sends quiesce before the ack; replay
floors, local counters, chat history, legal moves and PGN persist. Identity and
policy changes, expired revival and scope/stream replacement are rejected. Signed
forks and ambiguous acknowledgments close the room while direct RTC remains
usable. Default 300-second grants renew automatically within original certificate
bounds. See evidence/room-renewal.md for current real-browser/adversarial evidence
and limits. Distributed membership/routing, private crypto, multisteward failover
and public WSS/LAN/WAN deployment gates remain unfinished.

### Release-pinned steward failover (2026-10-21)

SupportClient now accepts a bounded descriptor set and a version 2 same-origin
bundle while retaining existing single-service configuration. One active socket
and the same revision-floor directory survive retryable handoffs; selection avoids
recently failed keys and prefers different declared domains among ties. Product
lease requirements, issuer policy and release endpoints remain pinned. Fresh
nonces/leases replace stale hints/routes without replaying unknown signaling, and
ready RTC links survive. Separate native process SIGKILL, new RTC establishment
through the alternate, root retirement/rollback, learned root-only revocation and
fatal protocol rejection are exercised in evidence/steward-failover.md. This is
standby failover on one host, not replicated/sharded discovery or distributed HA.
Routed/private networking and public WSS/LAN/WAN gates remain unfinished.

### Optional private guest Internet relay (2026-10-21)

Real Chromium/v86 ping, DNS and HTTP content verification now pass through a
private SSH tunnel to box-webhost's QEMU/libslirp service. Default static guests
retain loopback-only networking. Focused packet-policy and actual four-QEMU
lifecycle checks cover malformed/private/multicast traffic, denied web access,
capacity and cleanup. See evidence/guest-internet.md. This is home-host egress,
not visitor-local Internet; public deployment/access control remains unfinished.

### Four-room/eight-context concurrency (2026-10-21)

The new scripts/multiroom-check.py passes with eight independent real Chromium
sessions, four accepted two-peer rooms and eight authenticated RTC links forming
a connected cycle. Eight expected remote chat markers arrive exactly once with
zero unintended-room deliveries; four separate e4/e5 games and all guest/session
identities survive redraw. Every tracked network budget clears on disposal.
See evidence/four-room-browser.md for recipient accounting, source hashes and the
initial corrected harness failure. This strengthens concurrency evidence only;
multi-party/routed groups, forwarding/repair, WAN and public gates remain open.

### Isolated issuer and certified concurrency (2026-10-21)

Connected previews now isolate public/state directories by explicit instance label
or alternate port, preserving legacy 8098 paths. Fresh 8115 issuer tests pass
actual login, bad-password, stable-account/fresh-key, renewal, logout and private
path checks. The complete eight-context/four-room connected-cycle run also passes
with all eight identities development-server certified, 8/8 remote chat deliveries
and zero unintended-room deliveries. See evidence/connected-instance-isolation.md
and evidence/four-room-browser.md. Temporary test service stopped; no default
signin/backend change, official authority or public/WAN/routed-group gate claim.

### Room chat reordering (2026-10-21)

Fixed a verified-event loss: PublicRooms no longer discards chat simply because
the replay gate reports a sequence gap. Bounded verified reordering delivers once
in arrival order, with a persistent warning in the room view/export. Chess gaps
still freeze the legal prefix. All 123 protocol fixtures and actual two-browser
chat/PGN/guest regression pass; see evidence/room-chat-reordering.md. No repair,
forwarding, multi-party or WAN gate is promoted by this change.

### Inactive history disclosure (2026-10-21)

Valid messages discarded while no view is open now mark that bookmark's history
as incomplete without allocating a hot history/subscription. Direct and room chat
views disclose it; public-room exports combine inactive, eviction and sequence-gap
warnings. Invalid records cannot mark history. All 125 protocol fixtures and the
actual RTC close-view/send/reopen regression pass. See evidence/inactive-history.md.
This reports missing content honestly; repair/routing/private/WAN gates remain open.

### Pending crossed-offer convergence (2026-10-21)

The shared pool now picks one pending path deterministically by signed session
order after confirming full identity binding. Existing established entries retain
priority. Actual two-browser crossed offers pass in both answer orders, exchange
messages on one matching RTC connection, reject a later duplicate and release all
tracked reservations. The three-browser pool/room regression and 125 protocol
cases also pass. See evidence/pending-offer-convergence.md for the reproduced
zero-ready-link failure and scope: this is pool API evidence, not simultaneous
manual UI, issuer-backed glare, partition recovery, WAN or routed-group proof.

### Issuer-backed crossed offers (2026-10-21)

The glare fixture now uses target runtime identity configuration and asserts
actual local/remote trust modes. Forward and reverse crossed-offer tests pass
through an isolated real development issuer, including matching RTC path,
bidirectional delivery, established duplicate preservation and complete cleanup.
A mismatched trust-mode expectation correctly fails without local substitution.
Receipts and limitations: evidence/pending-offer-convergence.md. No manual-UI,
official/public, routing or WAN claim is added.

### Same-origin HTTPS/WSS proof (2026-10-21)

Disposable discovery accepts explicit external origin/endpoint while keeping
backends loopback-only. A local Caddy 2.11.4 TLS terminator and two actual Chrome
sessions pass WSS discovery/consent, bidirectional RTC, RTC survival after support
stop, foreign-Origin 403, private-path 404 and complete cleanup. Explicit test
certificate trust is confined to the check; no system CA/live hosting/router
change. See evidence/tls-discovery.md and tls-discovery-result.json. Temporary
services stopped. This adds local TLS evidence, not public PKI/WAN/official issuer
or routed-group proof.

### HTTPS issuer proof (2026-10-21)

Connected previews now accept a validated external origin while the issuer backend
remains loopback-only. Actual Chromium through local Caddy HTTPS passes login,
wrong password, stable-account/fresh-session, certificate upkeep, logout, v86 boot
and private-path checks. Wrong Host/Origin receive 403; an initial empty-200
unknown-host proxy response prompted an explicit fallback 403 template. Receipt
source/proxy hashes and limits: evidence/tls-identity.md. No global trust or live
hosting change; temporary services stopped. Public/official/WAN/routed/private
and combined issuer/WSS gates remain open.

### Combined certified HTTPS/WSS preview (2026-10-21)

New serve-connected-discovery.py stages one isolated development issuer and an
independently scoped RAM steward behind the same Caddy HTTPS origin. Actual
issuer-certified Chrome sessions pass WSS discovery/consent, bidirectional RTC,
separate room chat and legal e4/e5/Nf3 (last after support stop), guest continuity
and complete cleanup. The same backend passes login/renewal/logout/Host/Origin
checks. See evidence/combined-tls-preview.md and combined-tls-result.json. Only
loopback test processes were started and stopped; no public/official/WAN/routing
or production-isolation gate is promoted.

### Combined delegation-expiry isolation (2026-10-21)

A fresh 45-second signed delegation expires in an actual two-browser HTTPS/WSS
run. At expiry+32 seconds (after a later publication tick), discovery is closed
and its connections are released, while issuer config and same-key/session
renewals remain available. Established RTC chat and legal Nf3 still arrive, guest
objects survive, and final disposal clears budgets. See
evidence/combined-delegation-expiry.md and combined-tls-expiry-result.json. This
is bounded local expiry evidence, not process-crash/soak/public/WAN/routing proof.

### Separate issuer/steward processes (2026-10-21)

Combined preview now launches the existing native provisioned steward CLI with
private key/provision/ledger state and atomic public bundle publication. Issuer
and steward have separate processes, still one development UID and loopback-only
backends. A verified steward SIGKILL leaves issuer renewal, identical RTC links,
chat/legal Nf3 and guests working; all budgets release afterward. Normal parent
SIGTERM reaps a live child. See evidence/combined-process-isolation.md. No
automatic restart/privilege separation/public/WAN/routing claim; rerun earlier
expiry proof on this new composition before treating its scope as current.

### Bounded steward supervision and live WSS recovery (2026-10-21)

The development supervisor allows three native worker restart attempts with
1/2/4-second backoff and the same private provision/key/publisher state. Actual
certified Chrome sessions recover WSS discovery and fresh sampling after a verified
SIGKILL, preserve service/RTC/session identity, deliver chat/legal Nf3 and clear
budgets. Further native kills prove lifetime exhaustion at three while the issuer
remains available. Normal shutdown cancels supervision and leaves no worker.
See evidence/combined-worker-supervision.md. Expiry/backoff, production privilege
isolation, public/WAN/routing/private gates remain unproven or unfinished.

### Expiry/backoff restart race (2026-10-21)

Actual native fault injection reproduced a replacement-worker launch after a
signed grant expired during backoff (native validation still refused authority).
The supervisor now rechecks expiry after sleeping. The same boundary test proves
no replacement PID and continued issuer availability; current-source certified
HTTPS/WSS browser recovery also passes. See evidence/steward-expiry-backoff.md.
Read-only hosting preflight confirms a clean ksu.codes source working tree and
existing routes to preserve; no deployment/config change was made. Public artifact,
CSP/path validation and managed release work remain before hosting integration.

### Public-only static artifact and /desktop/ CSP proof (2026-10-21)

New export-desktop.py packages the explicit public allowlists and runtime notices,
verifies input/copied runtime hashes, refuses existing destinations, and writes an
exact release manifest. The 133-file/12.8 MB artifact reproduces byte-identical
manifest hashes; corrupted-copy refusal is tested. Actual guest/desktop and
two-browser RTC/room/PGN checks pass under /desktop/ with a scoped CSP; private,
traversal, listing and outside-prefix requests are rejected. See
evidence/public-desktop-artifact.md and desktop-artifact-result.json. Existing
ksu.codes app/CSP were read only; no public deployment or default-backend change.
Connected/official/public/WAN/routing/private gates remain unfinished.

### ksu.codes route/CSP candidate (2026-10-21)

An isolated history-preserving clone/desktop-preview branch now contains the exact
public artifact, one /desktop mount and README notes. A separate parent-generator
patch adds only the desktop CSP; all other eight-site rendered output is unchanged
and the full candidate adapts successfully. Actual site/FastAPI+Caddy guest, desktop
and two-browser RTC/PGN checks pass. Existing homepage/guides/presentation bytes
match both Git and the live release's public-file hashes. No staging/commit/push,
remote source edit or deployment occurred. See evidence/ksu-desktop-candidate.md
and site-candidate-result.json. Managed release/public/WAN/routing gates remain.

### Live static ksu.codes/desktop preview (2026-10-21)

The reviewed site candidate is now committed/pushed/pulled as d6ccfc4 and deployed
via the normal controller to release 20261021T125622370238Z-279f978f. Scoped CSP
source was hash-guarded/backed up, generated, validated and reloaded under the
controller lock. Live HTTPS Chrome passes all 13 desktop/guest groups and actual
two-browser RTC/room/PGN checks; all 133 file hashes and existing content/policies
verify. All eight production smoke sites pass. A new visible public guest is ready.
See evidence/ksu-desktop-deployment.md and ksu-desktop-deployment-result.json.
This is local/unvalidated identity and guest-loopback static hosting, with no new
router ports or public issuer/relay. External fetch did not prove outside-LAN
reachability; WAN/TURN, connected official identity, routing/private/repair and
other original gates remain open. The full goal is not complete.

### Origin account-disable adapter (2026-10-21)

New origin_service.lifecycle preserves the reference issuer API while adding
private disabled/generation state, checks on registered issuance/renewal, and
re-enable without old-token revival. A local owned-state operator CLI adds no web
admin/signin route. All 42 reference regressions plus nine lifecycle cases pass;
actual Chrome/operator/API disable-enable and ordinary identity regression pass.
See evidence/origin-account-lifecycle.md. New connected preview launches use the
adapter; older processes and the public static site remain unchanged. Detached
certificates retain their original validity; full lifecycle/public S04 remains open.

### Fail-closed origin policy state (2026-10-21)

Fixed a reproduced generation-zero revival on missing policy rows. Registered
issuance now checks account existence, explicit policy and renewal generation;
new-account policy rows are atomic. Startup metadata/trigger checks reject broken
hardened state. Populated legacy state needs explicit owned-state migration that
preserves disabled flags/generations. All 60 native cases and actual lifecycle/
identity browser regressions pass. See evidence/origin-policy-state-integrity.md.
Public preview unchanged; detached expiry, full rollback/rotation/recovery/load/
independent review and public issuer gates remain open.

### Origin database backpressure (2026-10-21)

Reproduced the inherited ten-second account write wait/generic 500. Adapter account
transactions now use a two-second SQLite bound and BUSY/LOCKED -> 429, preserving
reference validation/Argon2/slot/throttle/registration behavior. All 62 native cases,
actual Chrome contention/lifecycle and ordinary identity regression pass; measured
lock refusal is ~2 seconds and login recovers after unlock. Native parallel calls
verify excess-slot refusal and independent anonymous entry in the reserved-lock
case. See evidence/origin-database-backpressure.md. Public site unchanged; full
HTTP load/timeouts, production entry/review and remaining S04 gates remain open.

### Stored Argon2 profile bounds (2026-10-21)

Added bounded canonical Argon2id-v19 envelope/metadata checks before verifier
work, using the existing maintained parser/provider. Unsupported/excessive stored
parameters fail closed; supported weaker hashes still verify and rehash normally.
All 65 native cases (including reference regressions and safe verifier-spy cases)
and actual browser lifecycle/contention/identity checks pass. See
evidence/origin-stored-hash-profile.md. No high-memory unsafe hashes were executed,
public site/accounts unchanged, and broader resource/S04/WAN/routing gates remain.

### Local operator password reset (2026-10-21)

Added atomic password replacement plus session-generation revocation, preserving
account identity and disabled status. Secrets enter via prompt/stdin. Fixed a
reproduced in-flight login race by carrying the generation captured during
password authentication into initial issuance. All 71 native cases and actual
Chrome reset/ordinary identity regressions pass. See
evidence/origin-password-reset.md. Public accounts remain off; detached certificate
expiry and the remaining production/S04/network gates remain open.

### Bounded development issuer HTTP (2026-10-21)

Connected preview now has eight request workers, bounded admission and five-second
socket I/O timeouts. Actual socket checks prove concurrent progress, saturation
503, idle-header timeout and recovery. All 71 native cases plus ordinary and
lifecycle/contention Chrome regressions pass. See evidence/origin-bounded-http.md.
This is not a production transport approval; proxy/total-deadline/load/review and
combined discovery integration remain open. Public static site unchanged.

### Combined bounded transport integration (2026-10-21)

Fixed the combined supervisor's independent single-threaded HTTP construction.
Actual two-Chrome HTTPS/WSS + issuer + separate chat/chess + steward SIGKILL/
restart checks pass with guest/session preservation. Combined eight-worker
saturation/refusal/recovery also passes. Repaired TLS fixture config generation
and validated fresh generated configs. See evidence/origin-bounded-combined.md.
Loopback host candidates only; remaining production/WAN/routing gates stay open.

### Development HTTP framing (2026-10-21)

Reproduced duplicate Host acceptance and added pre-WSGI rejection of ambiguous
headers/unsupported framing in the shared handler. Nine malformed socket cases
and existing admission checks pass. Actual HTTPS identity and two-Chrome WSS/RTC
chat/chess/v86 regressions pass. See evidence/origin-http-framing.md for receipts
and the retained missing-fixture-CA test invocation failure. Public deployment and
remaining production/WAN/routing gates unchanged.

### Explicit ICE relay policy (2026-10-21)

PeerLink now honors configured all/relay policy and rejects invalid values before
opening RTC. Actual Chrome verifies relay/no-TURN exposes no direct candidates;
full protocol and two-browser chat/chess/PGN regressions pass on a fresh current
server. See evidence/ice-transport-policy.md, including retained stale-server
fixture failures. No TURN deployment or WAN connectivity is claimed.

### Actual forced TURN/TCP peer delivery (2026-10-21)

Added a disposable authenticated loopback Coturn fixture and --expect-relay browser
oracle. Actual unauthenticated Allocate gets 401; two Chrome sessions select
relay/relay and pass signed chat, separate chess/chat, legal PGN and lifecycle
checks. Package extracted project-locally, no system service or router change;
fixture stops and removes credentials. See evidence/turn-loopback.md. This is
one-host TURN/TCP evidence, not TURN/TLS or WAN proof.

### Actual TURN/TLS peer delivery (2026-10-21)

Extended the local authenticated Coturn fixture to TLS. Actual Chrome selects
relay/relay with localRelayProtocol=tls and passes separate chat/chess/PGN and
lifecycle checks. Normal TLS trust rejects the self-signed fixture; explicit
fixture CA/SPKI is confined to tests. Plain TCP regression also passes. Fixtures
stop and remove credential configs. See evidence/turn-tls-loopback.md. Public
443 routing/certificates/auth/abuse policy and WAN proof remain open.

### Separate lab and active system (2026-10-21)

User requested two independent directories. desktop-lab contains static frontend/
local-v86 assets, local identity helpers and a static server. It retains proportion
controls; Chat/Rooms and backend service code are excluded. active-system is the
functional target with full-viewport desktop, guest Internet relay, shared peer
networking and optional issuer/steward source. Its app/index have no proportion
controller, presets, comparison controls or preview scaling. Windows now clamp
to the real viewport, including browser resizing.

Root sources remain the preserved pre-split baseline. Future functional work
belongs in active-system; sizing experiments belong in desktop-lab. Both have
README launch instructions and copied runtime. Active has its own .venv and
requirements lock; no old accounts, signing keys or service state were copied.
Run lab at 127.0.0.1:8131 and active at 127.0.0.1:8130. Public hosting unchanged.
Local runtime ping_group_range 1000..1000 permits relay ICMP, not persisted.

All 13 lab browser/guest checks pass. Active actual guest ping 1.1.1.1 (2/2), DNS
and HTTP pass. A first active room native-click case exposed offscreen controls;
fitWindow fixes this and the actual two-browser chat/chess/PGN regression passes.
The failed pre-fix log is retained in active-system/.build/checks. Additional
responsive/interface checks prove both guests boot and controller separation:
.build/checks/split-desktop-result.json. Product-specific receipts are stored in
each directory's .build/checks. Both local previews are left running for review.

### Active system: combined identity/discovery/guest Internet (2026-10-21)

Changes confined to active-system. Optional public-config composition connects
separate loopback issuer and guest relay behind one HTTPS origin. Actual Chrome
identity, two-browser WSS/RTC chat/chess, and issuer-backed v86 ping/DNS/HTTP all
pass. Nine real HTTP config failure/fragmentation cases and relay regression pass.
Default lab/active previews are preserved; temporary combined fixture is stopped.
See active-system/evidence/combined-identity-internet.md. Production/WAN/multiparty
and independent-review requirements remain open.

### Active system shared TLS listener (2026-10-21)

Fixed absent-SNI routing in the interrupted shared-port fixture. Actual active-
desktop Chrome sessions load HTTPS and use TURN/TLS through one loopback TCP
18443 listener; selected relay/relay and tls protocol plus chat/chess/PGN pass.
Unknown SNI is rejected; standalone TLS relay regression also passes. Project-local
fixtures stop and remove credentials. See active-system/evidence/shared-tls-port.md.
Public 443, trust, WAN, relay policy and multiparty admission/routing remain open.

### Active system expiring TURN credential foundation (2026-10-21)

Implemented Coturn's documented REST credential profile using standard-library
HMAC, native secret bounds, capped lifetime and authorization deadline. Actual
Chrome/Coturn rejects expired/altered credentials then passes fresh relay/relay
TLS chat/chess/PGN through shared listener. Six native bounds cases pass. This is
fixture interoperability, not public authorized issuance or instant allocation
revocation. See active-system/evidence/turn-expiring-credentials.md. Remaining
production/WAN/multiparty requirements stay open.

### Active-system authenticated session TURN policy (2026-10-21)

Optional native TurnPolicy now supplies temporary credentials only in successful
session/renewal replies, never public config. Client validates endpoints/expiry,
refuses missing/expired credentials and renews before TURN expiry. Actual issuer+
Coturn+shared-TLS Chrome chat/chess/PGN and renewal continuity pass; all 76 native
issuer cases and complete browser protocol suite pass. Default launchers/public
sign-in remain unchanged. See active-system/evidence/session-turn-issuance.md.
Production secret/abuse/deployment/WAN/multiparty gates remain open.

### Active-system private TURN launcher configuration (2026-10-21)

Added explicit paired secret-file/TURN-URL options to both development launchers.
Loader rejects unsafe permissions, public-tree placement, symlinks/hardlinks,
special files and invalid/big token content before staging/startup. Nineteen
native checks and actual signed HTTP issuance against both subprocess launchers
pass; workers reap and TURN secret fixture is removed. See
active-system/evidence/turn-private-file-launchers.md. User's public-prototype
boundary is recorded in AGENTS.md: no active backend or host ping at /desktop/.
No live-site changes; remaining public/WAN/multiparty requirements stay open.

### Full local stack verified — 2026-10-22

Same two Chrome contexts now combine real identity, discovery, relay/relay TLS,
guest ping/DNS/HTTP and steward restart/issuer renewal. Cleanup verified. See
active-system/evidence/full-system-local.md. /hidden/ is the authorized external
preview path; /desktop/ remains unchanged. Connected subpath support and its
proof/endpoint tests precede deployment; remaining full-goal gates stay open.

### Configurable hidden/root mount verified — 2026-10-22

Active-system now supports --base-path /hidden with root as the default. Full
external proof-path binding is retained; client renew/logout, scoped steward
endpoint, metadata refresh and guest relay/cookie paths match the mount. Both
complete local stacks, including browser identity regression, pass. All 81 native
and 143 protocol cases plus guest/steward regressions pass. See
active-system/evidence/configurable-mount.md for retained failures and receipts.
User confirms final site is domain-root; /hidden/ is temporary external testing,
and /desktop/ stays live. Next: isolated managed external preview deployment and
outside-network evidence. No live-site changes yet; full goal remains active.

### Private runtime/release preparation — 2026-10-22

Native connected launchers support a locked private external runtime, and an
allowlisted checksummed connected artifact can run with its release mounted
read-only. Real launcher restart/exclusion checks and full exported-release
browser integration provide local execution evidence. See
active-system/evidence/immutable-connected-release.md. /desktop/ remains the
unchanged backend-free public prototype; no native external deployment yet.
Continue managed external /hidden/ setup, runtime/role ownership, discovery
lifetime and public TURN/guest policy, then independent-network verification.
Production identity, multiparty routing, private groups and repair remain open.

### Stable provisioned development discovery — 2026-10-22

Explicit operator root issuance/renewal/export now supports stable discovery
identity and publisher floors across restart, bounded signed authority and real
expiry/restoration without losing issuer sessions. Actual two-browser renewal
preserves VM/RTC/chat/chess; exported-release checks enforce read-only operator/
service execution and verify package integrity afterward. Details and retained
failed checks: active-system/evidence/provisioned-discovery.md. /desktop/ remains
unchanged and /hidden/ is not deployed. Continue managed UID/root custody and
public proxy/relay preparation, then external/WAN and full production/multiparty/
private-group/repair requirements. No overall completion is claimed.

### Separate local issuer/steward accounts — 2026-10-22

The standalone issuer reads only operator-pinned public policy and signed
metadata from an independently owned steward. Actual systemd DynamicUser UIDs
and 32 native file-access probes per layout prove private keys/accounts/ledger
are separated. Both /hidden/ and root layouts pass real Chromium identity,
v86 boot, WSS discovery, RTC chat and separate legal chess moves. Registered
accounts survive native issuer restart; login remains usable with discovery
stopped. Signed public-bundle renewal and immutable release verification pass.
See active-system/evidence/isolated-service-roles.md for reproducible commands,
retained failures and scope. Public /desktop/ bytes remain unchanged.

Next deployment work remains persistent service/root ownership, independently
owned guest egress with an explicit ping policy, public TURN on existing 443,
managed /hidden/ routing and rollback, then independent-network evidence.
Production identity review, multiparty routing, private groups and history repair
remain part of the full objective. No graphical game interface is introduced.

### Dedicated guest service identity verified — 2026-10-22

Local issuer, steward and guest relay now run as three locked persistent service
identities. Both root and /hidden pass 57 native file-access probes, actual socket
permission/capability checks, complete issuer restart, real two-browser RTC
chat/chess and both v86 guests' ping/DNS/HTTP. QEMU runs under the guest UID without
raw-socket capabilities or the developer's group. Temporary adjacent-group ping
permission is restored after each test; no permanent network setting is written.
Account provisioning rejects unsafe existing identities; package profiles 1..4
remain verifiable. Full existing TURN/TLS/recovery compatibility also passes.
See active-system/evidence/managed-guest-role.md. /desktop/ remains unchanged;
/hidden/ is not deployed. Continue managed permanent units/state and external
proxy/relay/rollback work, plus remaining full-goal requirements above.

### Persistent private backends installed — 2026-10-22

The profile-5 package includes the release verifier and explicit root operator.
Real installed-unit/browser tests pass at both /hidden/ and root, including state
preservation, root/ledger refusal checks and startup assertions. KSU commit 517179c
was pushed/pulled Git-first without changing public/app trees. Its pinned native
release/venv are installed on box-webhost, where separate locked issuer/steward
roles now run on loopback. Actual signed API and private UID/process checks pass.
Guest remains stopped; native units are not boot-enabled. No public route, proxy,
router, firewall or ping policy changed. All eight sites and unchanged /desktop/
pass verification; /hidden/ is still 404. Operator authority expires after its
explicit 24-hour grant and must be renewed manually. See
active-system/evidence/persistent-service-operator.md. Continue native recovery/
upgrade/rollback and public relay/proxy policy before external browser/WAN tests;
retain all remaining production/multiparty/private-group/repair requirements.

### Private checkpoint and recovery verified — 2026-10-22

Profile-6 root controller adds exact private snapshots, verification, independently
fenced root epochs, credential quarantine and resumable recovery. Actual root /
/hidden / old-role-new-controller runs preserve issuer/root identities, recover
the same account after fresh credential reset, rotate scoped discovery authority
above live revision floors, and resume after an interrupted real namespace move.
Real browser v86/RTC chat/chess/guest Internet and full TURN compatibility pass.
Git-first commit 6b99ae4 is synced to box-webhost. It has a verified root-only local
checkpoint; private issuer/steward resumed on their original binaries with keys
unchanged. Config version 2 requires the new controller. Public /desktop/ and all
eight sites remain healthy and unchanged; /hidden/ is still unpublished. Continue
code upgrade/rollback, encrypted/off-host custody and public preview policies;
the remaining full production/network/group requirements stay active.


## Current direction: peer-first channels, one to 8,000 participants — 2026-10-24

This entry supersedes earlier scale assumptions, not the recorded evidence of
historical releases. The user explicitly wants self-organizing P2P gossip with
smart routing within each island and between hierarchy layers, server fallback,
and eventual correctness rather than perfect real-time delivery. A few seconds
of delay is acceptable. Most participants may be readers or relays, not speakers.
The user requested a PLAN for an 8,000-person/agent channel test; 8,000-node
operation is not implemented or verified by the current eight-browser tests.

The current release goal remains a verified /hidden/ integration of public
groups/history and the working desktop, followed by the authorized homepage ->
/blog/ and desktop -> domain-root cutover when ready. Preserve /desktop/. Do not
claim the fixed-star prototype is the final routing architecture.

### Channel semantics and chess roles

- The smallest channel is one person keeping notes: zero peer connections or
  relay work required. Anonymous notes/files stay in browser RAM unless explicitly
  downloaded; registered users may explicitly save to their private server folder.
  A same-channel solo mode is still to be implemented; the current Text editor
  already supports local notes and registered file saves.
- A match has exactly two authorized player seats, occupied by humans, agents,
  or one of each. Audience size is independent of player-seat count. Spectators
  may read the signed move record and participate in ordinary chat; a spectator
  signature or proof of work never authorizes a chess move.
- Moves and conversation remain distinct lanes, with separate authorization,
  replay state and priorities. Chat is never interpreted as a move or command.
  Multiple rounds have explicit game/round IDs and position/ply dependencies.
- A large channel is one logical conversation spread over cooperating islands,
  not a collection of unrelated chat rooms. Routing responsibility may move
  without transferring player keys, account ownership or channel permissions.
- Private-group encryption remains subject to the separate reviewed key gate.
  Public chat/relay transport must not be mislabeled as private encryption.

### Routing, resources and fallback

One session owns the shared peer pool, identity, queues and resource accounting;
applications own subscriptions/views, not independent hidden networks. Each node
keeps a bounded neighbor set and partial membership/directory information.
Membership gossip, demand-based forwarding, redundant bridges and periodic
anti-entropy repair missing data. Joins, graceful departures, crashes and island
splits/merges must reorganize routes without a permanent per-channel forwarder.
Established authorization and valid original messages survive routing changes.

The supplied mesh-policy.json already proposes island targets around256 members,
split above320/merge below128 with hysteresis. These are design/test parameters,
not measured Chrome capacity. At8,000 members, roughly32 islands is a useful test
shape, not a requirement to connect every browser to256 or8,000 other browsers.
Per-island and per-layer routing roles must fit the same shared device budget.

Resource policy MUST be configurable. The discussed128MiB is a proposed shared
browser allowance, not an automatic128MiB allocation for every joined channel or
hidden routing level. Inactive membership is a small record; active features and
caches take bounded leases only when used. Per-channel/island quotas may not
bypass the device-wide total. Metadata accounting is a conservative model, not
actual measured browser heap. Record actual heap/process memory, queue bytes,
CPU, crypto backlog and upload/download alongside accounting counters. The
current32MiB prototype setting is not the intended permanent product ceiling.
Validated configurable limits are still work to implement, not deployed settings.

Server fallback must carry the same authorized, deduplicated channel events and
return to healthy peer routes with hysteresis. Public TURN is an existing RTC
transport relay; a full WSS application fallback for environments where RTC fails
is a separate feature to implement/test. Preserve original author signatures,
permissions, message IDs and queue limits across paths. Keep ingress on80/443
where possible. Scale/admission limits for fallback must be measured separately
from P2P; a home server cannot promise unlimited broadcast fanout.

The four simultaneous Linux Internet wires are a different, server-side preview
resource cap. They are not a four-account/chat limit. Strict-policy2 anonymous
clients should allocate no Linux Internet wire. Registered relay admission
failure must leave private files and browser chat usable. Larger wire capacities
need coordinated configuration, cgroup/FD/process/churn/quota and traffic tests;
no cap was increased during the native16 integration.

### Incremental synchronization, checkpoints and branch handling

The user requests chunked catch-up from the last hash/checkpoint a participant
has verified. Do not send an entire graph for every change. Specify channel ID,
membership epoch, known heads/frontier, requested missing content hashes and
bounded paged chunk manifests. Chunks are content-addressed, verified before
application, resumable and idempotent. Sender and receiver bound chunk bytes,
concurrent requests, decompressed bytes, retained caches and retry deadlines.

Concurrent valid branches may have different heads. A content hash does not by
itself establish recency, authorization, completeness or a globally winning head.
Exchange missing data in both directions and define the merge/checkpoint rule
before marking shared state confirmed. If an old base was pruned, request an
explicit verified snapshot plus its tail; do not fabricate missing history.

The user's clarification is exact: valid updates that MISSED the winning batch
remain pending and can be carried into the head/next batch, preserving original
IDs/signatures and applying exactly once. Invalid branches are always rejected.
Re-check author permissions, epochs and dependencies against the current head.
Do not rewrite an original signed operation to pretend it had a different parent.
Chat can normally retain its original event. A chess operation whose position or
turn was superseded cannot be silently replayed as a new move; its dependencies
must be satisfied or the authorized player must submit a new operation.

UI states distinguish local signature/permission verification, pending propagation,
missing dependencies, and a confirmed checkpoint. A configurable number of gossip
rounds may be a minimum stabilization interval; merely waiting rounds is not
proof of convergence. Specify the required acknowledgements/evidence and failure
assumptions. Signed invalid/unauthorized content never becomes valid through time,
relay votes, inclusion in a later batch, or stronger proof of work. Chess forks
need player-authorized conflict handling, not audience voting.

Required branch tests: concurrent valid chat branches merge; valid missed updates
are reincluded once; duplicate/alternate-path copies stay single; missing parent
arrives after child; transfer interruption resumes; pruned base requests a trusted
snapshot; corrupted hash/signature and wrong-channel/epoch/role stay rejected;
invalid branch cannot return inside a later valid envelope; revoked authors cannot
resurrect live privileges. Attribute corrupt forwarding to the delivering route
without falsely blaming the claimed original author. Retain replay protection
when evicting caches and changing transports.

### Light client-paid proof of work

The user requests light proof of work paid by the client's browser. Plan a
bounded, cancellable Web Worker puzzle for admission/rate control, with cheap
verification and difficulty capped by local policy. Bind challenges/stamps to
identity, scope/epoch, nonce and expiry, with replay protection. Avoid binding to
a rapidly changing head that invalidates work whenever a chat message arrives.
Do not perform unlimited background work or a fresh puzzle for every gossip hop.
Solo notes/local reads should not need network admission work. Measure actual
physical-phone costs and cancellation behavior; synthetic timing is not phone
proof. Registered policies, per-key/account quotas and authenticated membership
remain enforced. PoW does not grant seats, prove message correctness, establish
independent identities, or substitute for the checkpoint/merge protocol.

### Staged scale and fault test plan

| Stage | Participants | Evidence required |
| --- | --- | --- |
| Solo | 1 human/agent | Local notes; zero peers; explicit save/export; close/reopen behavior |
| Match | 2 players plus audience | Human/human, human/agent and agent/agent; separate chat/move lanes; spectators cannot move |
| Small mesh | 8, then32 | Actual browser/RTC conformance; bounded neighbors; no permanent controller dependency |
| Island | 128 and256 | Join/leave, partial views, resource plateaus, signed chunk repair, split/merge behavior |
| Multiple islands | 1,000 | Redundant bridges, partitions, churn, fallback and P2P restoration |
| Worst planned channel | 8,000 | Independent identities and real transports; declared workload/active fraction; bounded recovery and overload |

Keep topology simulation, protocol-agent tests, real-browser tests and full
browser/Linux desktop tests explicitly separate. Eight thousand JS objects or
logical identities are not evidence for eight thousand real transports. Agents
must use real identity/signature/authorization/replay/PoW paths. Retain a measured
real-browser subset on multiple Internet connections, including mobile behavior.
An8,000-agent networking test alone does not prove8,000 cold v86/voice downloads
or complete browser desktops can load concurrently from the home uplink.

Parameterize total subscribers, active-speaker fraction, messages per speaker,
UTF8 payload bytes, game cadence and duration. Proposed workloads:

- Mostly-reading steady channel:8,000 members,1% speaking every10seconds gives
  8messages/second;256-byte payload means2KiB/second per full reader before overhead.
- Busy steady channel:10% speaking every10seconds gives80messages/second and
  20KiB/second of raw payload per full reader before overhead.
- Everyone-sends burst:8,000 unique256-byte messages is2,048,000 raw bytes per
  full reader ONCE, not per second. Allow bounded catch-up and report latency.
- Stress/overload only: everyone sends every second. This is about2MB/second per
  full reader before signatures/headers/retransmissions. Require explicit admission
  backpressure and bounded queues; never silently redefine this as normal traffic
  or claim full delivery of messages that were not admitted.

Batch small deltas and compress where useful. Do not accumulate a full batching
delay independently at every hop. A few seconds is an acceptable soft latency
target; correctness, eventual convergence when data is available, bounded memory
and honest incomplete/pending states are hard requirements. Record per-reader
AND aggregate network costs so broadcast replication is not hidden.

Inject sparse and sustained churn, sudden bridge/island losses, asymmetric links,
delayed/reordered/duplicate updates, damaged chunks, malicious branches, expired
or revoked grants, audience move attempts, CPU-heavy clients, background/suspend,
NAT/UDP blocking, TURN/WSS fallback, server loss/restart and restoration. Test
valid updates rejected from a selected batch being reincluded in the next head;
invalid branches must stay rejected through the same sequence. Server failure
must not silently invent new identity authority or claim unsaved RAM is durable.

Acceptance records include participant roles and real transport denominator,
unique admitted events, receipts/checkpoints, missing/recovered/rejected events,
convergence roots/frontiers, exactly-once application, policy/role negatives,
resource plateaus and cleanup. Report inability to recover expired/unavailable
data. No8k capacity claim until the actual staged tests pass at stated workloads.

Primary design references (not adopted dependencies or claims of implementation):
[GossipSub mesh/security specification](https://raw.githubusercontent.com/libp2p/specs/master/pubsub/gossipsub/gossipsub-v1.1.md),
[Automerge heads/have/need synchronization](https://automerge.org/automerge/automerge/sync/struct.Message.html), and
[Tor client-puzzle admission design](https://spec.torproject.org/dos-spec/overview.html).
Automerge is a reference for incremental synchronization, not an automatic chess
merge rule. PoW algorithm/parameters and checkpoint confirmation rules still need
explicit specification, review and measurements before implementation.


### Bounded routing during sudden channel growth — user clarification 2026-10-24

A channel is one logical scope regardless of how many smaller routing islands
carry it. Most channels are expected to stay small. Small peer groups should
exchange content directly without sending it through the main server or unrelated
peers; some may never use either for content. Identity/bootstrap/optional TURN or
server recovery dependencies must be described separately from message routing.
Server fallback remains available within an explicit capacity budget, not an
unlimited guarantee that the home server absorbs every failed peer path.

Do not scale client memory or peer degree linearly with channel membership.
128MiB remains a provisional shared per-desktop-tab networking accounting cap,
not a claim that an8k-member channel requires more memory. Avoid choosing a larger
"8k minimum" without measurement. Workload/message rate, retained history,
signature work and forwarding role determine resource pressure. The current UI
32..1024MiB development range is not a physical-memory safety guarantee. Actual
JS heap, WebRTC native buffers, Linux and voice memory need separate measurement.

Plan a tunable bounded neighbor set shared across channels, partial membership
views, several independent inter-island bridges and replacement candidates,
content-addressed recent-cache limits, chunked/resumable historical reads, bounded
verification work and transmit queues, and backpressure. Island size and bridge
counts are parameters for the staged tests rather than fixed production promises.
An island must not imply a full mesh inside it, a single indispensable bridge,
or connections to every island. Split/merge and replace failed bridges gradually
with hysteresis and randomized retry so a join surge does not cause mass churn.

On budget or capacity exhaustion: stop admitting extra relay work, prune obsolete
cache data while preserving durable replay/security floors, slow historical
catch-up, refuse or defer new work explicitly and protect already admitted chat.
Never silently drop admitted durable work or call unavailable history complete.
Churn, mass joins, a hot sender and complete server fallback saturation must each
have bounded queues/concurrency and an honest retryable UI. Broadcast still costs
a copy of each selected message per recipient; islands reduce connections and
redundant transmissions, not the necessary content bytes for readers.

Demonstrate sudden1/8/32 to1k/8k growth and shrink under the same bounded per-client
limits. Record memory plateaus, neighbor/bridge counts, signature queue depth,
unique delivery, catch-up lag and recovery after loss. An8k logical-channel test
must prove cross-island convergence, not eight disconnected subrooms sharing a
name. Keep the1-person/small-group path simple and avoid paying8k topology costs
for a two-person chat. Full scalable gossip remains future work, not currentR8.


## Active goal corrected by user — 2026-10-24 UTC

The user explicitly rejected treating the /hidden/ milestone as completion and
requested a rewritten goal covering the root/blog swap and other outstanding
changes. The active goal now includes the real domain-root cutover, required
mount/authority/publisher migration, remaining app/security regressions, scalable
P2P islands/gossip and fallback, chunked checkpoint synchronization, browser-paid
light PoW, player/audience separation and staged8k tests. Read the current goal
and initial requirement ledger before continuing. Existing passing /hidden/
checks remain milestone evidence, not proof of this whole goal.

This supersedes earlier agent-authored completion/deferment notes that excluded
the root/blog cutover or treated the requested networking work as planning-only.
Move the existing homepage to /blog/ and the active desktop to the domain root
when the migration is verified. Preserve /desktop/ byte-for-byte, other sites,
account IDs, keys, realm, UUID folders, permissions, saved files and monotonic
floors. Keep the current homepage live until the tested cutover transaction.
Do not weaken the goal to whatever subset currently passes. New marketplace/
payment apps are not prerequisites. The rewritten goal is ACTIVE.

Finish the requested active-system upgrade, including the root/blog swap and outstanding changes. The verified /hidden/ release is an intermediate milestone.

1. Audit earlier requests, served_apps_public/CONTRIBUTING.md, supplied v0.1–v0.3 plans, ROADMAP.md and live/code evidence into a requirement ledger: completed, partial, required, explicitly deferred. Finish required changes; do not silently turn implementation into planning. New marketplace/payment apps are not prerequisites.

2. Move the current homepage to https://ksu.codes/blog/ and publish the actual active desktop at https://ksu.codes/. Preserve blog content/guides/links, all /desktop/ sizing-prototype bytes and other sites. Root must be the real configurable mount, without an internal /hidden/ dependency or cosmetic proxy/base-tag move.

3. Implement managed frontend/API/WebSocket/cache, native/file/guest mount and signed discovery/root/publisher endpoint migration. Preserve keys, realm, account IDs, private UUID folders, permissions, documents, usage and monotonic authority/publisher/replay floors. Test interruption recovery and rollback in the private VM first; never restore old user data or reset ledgers. Use Git-first immutable releases and hosting controller/locks/pins. Prefer80/443; report new router ports before changes.

4. Finish remaining app work and retain Files→Text→edit/save→Files→authorized durable server operation→Text result. Verify xterm.js/nano, independent PTYs, multiple windows per independent workspace, task/minimize/roll-up/focus, mobile touch/menu/keyboard behavior, draggable tap-toggle on-device voice, dependency bundling and disposal. Reopen/account/workspace changes must not leak resources/sessions/workers or revive stale operations.

5. Preserve authoritative logins/permissions, registered private disk folders/per-user apps and isolated service accounts. Anonymous users retain browser-local files/chat, with no server folder or Linux Internet. Registered egress follows policy; private/LAN/special destinations require explicit exceptions. Capacity refusal must leave unrelated desktop/files/chat usable.

6. Implement shared P2P beyond fixed3–8-member stars: bounded partial meshes/islands/layers carrying one channel, self-organization on joins/leaves, redundant bridges, partition recovery, bounded server fallback and return to P2P. Small groups need no unrelated peers/main-server message routing. Bound memory/neighbors/queues through sudden growth, with variable shared per-tab budgets;128MiB is provisional accounting, not per-member/per-layer reserved RAM.

7. Implement resumable chunked hash/checkpoint sync and explicit convergence/conflict rules. Reinclude valid missed operations once with original IDs/signatures and rechecked permissions/dependencies; always reject invalid branches. Show pending/incomplete/verified/confirmed honestly. Add bounded cancellable browser-paid light PoW for admission/rate control, not permission/correctness. Preserve separate chess/chat channels, two authorized human/agent players, spectator chat, legal SAN/PGN and no historical replay as live moves.

8. Retain lazy verified public caches/persistence requests and honest maintenance countdown/reconnect/website-control locks. Test/document loss, restart, reload, eviction and browser/OS failure; never claim unsaved RAM was saved or browser Reload/Close can be prevented.

9. Run staged solo→small mesh→islands→8,000-participant channel tests at stated mostly-reading/burst loads, with real identities/signatures/authorization/transports. Separate simulation, agent load, browsers and full v86 desktops. Measure resource plateaus, bandwidth, convergence, overload, churn, partitions, invalid branches, cleanup and fallback saturation. Verify separate public networks with ordinary TLS.

Complete only after root desktop and /blog/ work live, /desktop/ and other sites are preserved, required implementation/tests and rollback pass, and the handoff is accurate.
