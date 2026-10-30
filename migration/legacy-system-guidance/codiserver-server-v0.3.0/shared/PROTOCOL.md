# CodiServer peer identity protocol — codi-peer/1

**Status:** versioned application protocol + runnable reference, not an independently
reviewed authentication product. Production activation is a separate gate.
Both ZIPs carry this same document, schema bundle, limits, and public fixtures.
The browser is the application runtime. The authority certifies session keys; it
does not run desktops, guests, chat, or ordinary computation.

## 1. One model, two stages of authority

`Session = { public identity, private session key, private session token?, trust }`.
A public identity contains `sid`, `sub`, `kind`, `name`, public P-256 `key`, and
`certificate` (compact JWS string or null). Private fields never cross the peer,
VM, logging, public-config, or screenshot boundary. Every fresh browser entry
creates a new nonextractable signing key. A registered account has a stable
server `sub`, NOT a permanently reused browser signing key.

Local development has no authority. ANON creates a random identity in RAM;
`certificate: null`, `kind: anonymous`, `sub == sid`. Peers see **Local / not
server validated**, even though their actual packets have cryptographic signatures.
SIGNIN is disabled until a real service is configured. Do not fabricate successful
account registration, install a production key in fixtures, or mint a fake
"official" certificate to make GUI tests pass.

Connected deployment: ANON and SIGNIN BOTH call the identity service, prove
possession of the browser key, and receive a server-assigned identity plus a
short-lived certificate. ANON's subject and display name are random, not a claim
about a person; no password or durable account is created. SIGNIN auto-creates
an unused canonical username or verifies the existing password. The same UI,
PeerLink, VM controller and identity verifier are used afterward. No automatic
fallback from failed server verification to an unvalidated identity.

The local-development deployment profile exists to test an authority-free stage;
it is not a hidden per-user privilege flag. A production build must not expose
it as a way to bypass the server. Run isolated local tests on loopback only.

## 2. Cryptographic roles (do not confuse them)

* HTTPS authenticates the configured origin and protects passwords/HTTP requests.
* The authority signs a short-lived certificate binding account/session identity
  to a browser public key. Its private signing key stays on the service host.
* The browser signs connection descriptions, live key-possession handshakes,
  and every chat packet. It never receives the authority signing key.
* WebRTC DTLS protects the data channel in transit. Do not invent another
  encryption protocol or claim that a signature alone encrypts content.
* Public static assets can be pinned by an asset manifest/hash inventory. A
  signed release manifest is a later release gate, not proof that this source
  was already signed by David's real authority.

"Sign everything" means every authoritative application statement and peer
operation is authenticated in its own domain. Do not sign every HTML pixel or
send passwords to peers. Unknown peer messages never invoke code or host actions.

## 3. Encoding and key profile

Use ES256: ECDSA over P-256 with SHA-256. Web uses Web Crypto; Python uses
`cryptography`. No home-made elliptic-curve arithmetic or password hashing.
Compact JWS consists of base64url(protected-header) + '.' + base64url(payload) +
'.' + base64url(signature). ES256 signatures are exactly 64 bytes, r || s,
not ASN.1 DER. Python converts at its library boundary; the wire format is one
standard format. Verify the exact received signing input, never a reconstructed
JSON serialization. Noncanonical base64url and unsupported headers are rejected.

Header `alg` is fixed to `ES256`, not dynamically negotiated from input. Allowed
header fields: `alg`, `typ`, optionally `kid`. No `jku`, `x5u`, embedded authority
JWK, `crit`, or algorithm fallback. Never fetch a key URL supplied by a peer.
Public session keys have `kty: EC`, `crv: P-256`, 32-byte x and y; reject a
private `d`. Thumbprints use the RFC 7638 member ordering crv,kty,x,y.
Distinct JWS `typ` values prevent cross-protocol substitutions:

| Object | typ | Signed by |
|---|---|---|
| Server identity certificate | `codi-identity+jwt` | Authority |
| Account/session request proof | `codi-request+jws` | Browser session |
| Offer or answer | `codi-signal+jws` | Browser session |
| Hello or chat | `codi-peer+jws` | Browser session |

## 4. Server certificate

Claims: `v=1`, `iss` exact configured origin, `aud=codiserver-peers-v1`, `sub`,
`sid`, `kind` (anonymous or registered), `name`, `cnf.jwk`, `iat`, `nbf`, `exp`,
`jti`. `iat` is the most recent authority validation of this session key, not
proof that a human typed a password at that instant. Defaults: certificate
lifetime 900 s, HTTP challenge lifetime 60 s, session absolute lifetime 8 h.
Time fields are integer Unix seconds. The verifier allows at most 30 s for
future-clock skew, **no grace after exp**, and no lifetime exceeding 900 s.

The receiver verifies the configured authority key selected from a trusted,
bounded kid map, signature, exact issuer/audience, type/version, time window,
subject/session/display-name/kind binding, and exact public-key binding.
A certificate alone is public and copyable: the receiver must additionally
verify fresh signatures by its bound private key. A copied certificate without
that private key cannot authenticate a connection.

Trust roots come from a deployment configuration on the configured HTTPS origin
(or the explicit local test authority), never from a peer. A known-key endpoint
is useful for operations but is not a license to trust arbitrary self-published
keys. Key rotation needs an overlap window and an authenticated configuration
update before issuing with a new kid. No wildcard issuer/audience and no
"download unknown key from token" behavior.

**Expiry is not instant revocation.** A disconnected peer cannot discover a
new server-side ban or logout. An existing certificate can remain acceptable
until exp. UI labels say "last validated" and show expiry, not "online now" or
"safe forever." Without reliable client time, offline expiry checks are not a
strong guarantee against a malicious client. The server enforces its own clock
for all protected resources. Immediate revocation would require an online
status protocol; it is deliberately not promised by this minimal design.

## 5. Minimal authority HTTP contract

All POSTs: same configured Origin and Host; application/json; 64 KiB maximum;
no CORS wildcard, no logging of request bodies, credentials, tokens or SDP.
All API responses are no-store. The reference launcher is loopback-only.

| Endpoint | Input | Result |
|---|---|---|
| GET /config.json | none | Explicit deployment profile and public trust keys (development reference); production publishes reviewed static config |
| GET /.well-known/codi-issuer.json | none | Public issuer/kid/JWK metadata, not a new trust root |
| GET /healthz | none | Minimal health indicator |
| POST /api/v1/challenge | public key + exact target path | Random one-use nonce, 60 s expiry |
| POST /api/v1/anonymous | signed request envelope with empty request object | Random temporary identity, certificate, private session token |
| POST /api/v1/auth | signed envelope with username/password | Auto-register or authenticate, then same session result |
| POST /api/v1/renew | signed empty request + key-bound session token | Fresh certificate, same sid/key/sub |
| POST /api/v1/logout | signed empty request + key-bound session token | Delete that HTTP session |

Envelope: `{request: <exact compact JSON string>, proof: <JWS>}`.
The proof binds v, nonce, issuer/session sid, intended authority audience,
HTTP method, exact path, iat, exp, and SHA-256 of the **exact request string**.
The challenge records the public key and intended path. Consume once under a
lock, even on a failed verification. TLS carries passwords; neither passwords
nor request proofs are sent over P2P or stored in browser persistence.

A private, 256-bit random `session_token` returned only to the browser is kept
in RAM and sent as `Authorization: Codi <token>` on renew/logout. Server stores
its hash in RAM and requires a fresh signature by the same key AND matching
sid. The token alone is insufficient. This explicitly replaces a single ambient
cookie because multiple anonymous tabs must not overwrite each other's session.
Never put this token in localStorage, URLs, public identity, VM files, or logs.
XSS in this same-origin app can still act as the user; nonextractable keys do
not make hostile JavaScript harmless.

Username normalization: trim outer whitespace, lowercase ASCII, 3–32 characters,
letter first, then letters/digits/_/-. Reserve admin/root/owner/system as a naming
policy; NO username grants authority regardless. Passwords are not trimmed,
normalized or truncated: 15–128 characters and at most 512 UTF-8 bytes. Argon2id
reference policy is 64 MiB, t=3, p=1, random 16-byte salt, 32-byte hash. Benchmark
on box-webhost, bound concurrent hashing, and review current guidance before
public exposure. Account creation uses an atomic unique username constraint;
wrong password never overwrites, resets or silently creates a second account.
A typo in a previously unused name intentionally creates another account; the
UI warns about this tradeoff. No email recovery or MFA is claimed in this slice.

Anonymous issuance does not make people unique, prevent Sybil identities, or
hide visitor IPs from the HTTP/STUN/TURN operators. Rate and capacity limits
bound resource use; stronger abuse controls are a public-deployment gate.

## 6. Peer connection and signaling

MVP is one other browser per PeerLink, reliable ordered RTCDataChannel named
`codi-chat-v1`. No WebSocket chat, BroadcastChannel chat, localStorage bus,
public peer directory or hidden signaling service. Copy/paste signed offer and
answer strings through an existing trusted channel. No STUN/TURN endpoints
are contacted by the shipped configuration. Same-host/LAN connectivity still
has to be measured; Internet NAT traversal is not guaranteed.

Signaling payload: v, kind (offer|answer), random room, iat, exp<=iat+120,
reply_to (null for offer; SHA-256 of exact offer JWS for answer), sender public
identity including certificate, and full SDP. Signing SDP binds the DTLS
fingerprint and candidate data to the identity. The receiver verifies the
signature, identity and expiry before setRemoteDescription. The answer is bound
to a specific offer, not merely a username. Invitation material exposes ICE
candidate metadata to whoever receives it: do not log it or publish it broadly.

A signed invitation authenticates its signer, not the user's intended human
recipient. Compare the full key fingerprint/account subject through the trusted
invitation channel when that distinction matters. A local name can be copied.
Even a server-issued anonymous name is only a temporary pseudonym.

Connection ID = SHA-256(exact offer JWS + '\n' + exact answer JWS). After DTLS
opens, both endpoints send a signed `hello` on the actual data channel. The
first accepted sequence is 1; ordinary chat is enabled only after both hellos.

## 7. Peer packet rules

Signed payload: v=1, kind=hello|chat, link=connection ID, from=sender sid,
to=recipient sid, seq=positive safe integer, iat, exp<=iat+60, text. Hello uses
empty text; chat uses 1–8192 UTF-8 bytes. Wire packet <=32768 bytes. Signaling
JWS <=262144 bytes; SDP <=131072 characters. Outbound bufferedAmount cap 256 KiB;
UI retains at most 200 messages and 100,000 raw serial characters.

Exact per-direction sequence increment on an ordered reliable channel, with
serialized async verification, rejects replays and out-of-order packets.
The replay state advances only after every check. New connections use a new
connection ID; old packets are invalid there. No queues grow without bounds.
Unknown/binary/oversized message kinds fail closed. Text is rendered with
textContent; it is never evaluated, interpreted as markup or a command, or
injected into a terminal. Signatures provide attribution, not truthfulness.

Certificate validity is checked on every message and periodically while open.
At expiry, close the link and show stale identity; the desktop and browser-only
work may continue. Revalidate through the authority, then exchange a fresh
invitation. This deliberately avoids an extra in-band identity-update protocol
until it is actually needed. Session logout destroys peer links and guest state;
reload does not restore private session keys or message history.

## 8. What the server is NOT

No chat store/relay, peer-to-peer data relay, remote guest executor, Linux account
manager, shell endpoint, host filesystem endpoint, or inference daemon. Static
assets are public read-only bytes, never a mount of a home directory. Browser
VM execution happens on each visitor's CPU. Registered-account identity does
not itself authorize host operations.

Automatic discovery would need an additional rendezvous mechanism. It is not
provided by HTTP file serving or by WebRTC itself. Keep manual signaling while
the service's scope is strictly bootstrap + identity. If automatic invites are
later chosen, approve a separate RAM-only, TTL-bounded signaling component;
chat remains over the data channel. TURN, if needed, is an additional network
relay dependency, not something the minimal auth service magically implements.

## 9. Protocol change procedure

Shared files in both packages must have identical SHA-256 hashes. Edit the
protocol/schema/fixtures together, increment the version for incompatible wire
changes, add negative vectors first, and run Python plus WebCrypto checks.
Do not accept multiple conflicting wire formats merely to protect an old test.
This is a narrow reference profile: independent review, fuzzing and real-browser
interoperability are mandatory before calling it production authentication.
