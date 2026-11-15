> v0.3 note: this document describes the preserved v0.2 baseline.
> For planned multi-group work and intentional changes, read
> `08_P2P_V03_DECISIONS.md` and `../shared/MESH_ARCHITECTURE.md`.

# Minimal box-webhost plan — not an instruction to deploy now

## Initial topology

Public HTTPS static server: reviewed web public/ directory, BIOS/WASM/guest
images and later models as immutable resources. Private loopback/Unix-socket
authority: anonymous issuance, automatic signup/signin, renewal/logout, public
issuer metadata. SQLite holds only registered accounts; issuer private key lives
outside public files. Anonymous sessions/challenges/token hashes are bounded RAM.

No Linux desktop sessions, v86 instances, VM disk overlays, peer message history,
chat service, compute job broker or owner-files broker belongs in this service.
The reference loopback WSGI handler also serves small assets just to simplify
local tests. At deployment, Caddy serves assets/ranges directly; the Python
service must not buffer multi-gigabyte images into RAM.

## What "initial resources and login/signup" necessarily includes

A public bootstrap document/config; a trusted authority-key distribution path;
a one-use key-possession challenge; anonymous issuance; combined signup/signin;
certificate renewal and logout. Those are the lifecycle of the same identity
service, not separate application backends. P2P message signatures are made by
browsers; the server does not sign each message on demand.

The browser holds the session private key and an in-RAM opaque, key-bound HTTP
session token. The same certificate object works for local-service tests and the
later official deployment; the configured trust root and UI authority label
are different. The development entry point deliberately rejects official mode.

## Durable data

accounts(username UNIQUE, subject UNIQUE, password_hash, created).
Issuer key: PEM/PKCS8 P-256, generated locally, file 0600 in directory 0700.
Account password hashes use Argon2id; never reversible password encryption.
HTTP tokens are random and stored as SHA-256 digests in RAM, bound to sid/key.
No anonymous account table or durable chat/SDP table. No source-controlled keys.

Service restarts lose anonymous session state and active HTTP sessions. Accounts
and issuer identity survive. Offline peer certificates are still verifiable until
expiry; restart is not cryptographic revocation. Recovery/key rotation/revocation
are explicit public-release gates, not automatic inventions in the GUI.

## Public deployment checklist (S04)

Use a dedicated unprivileged service user unable to read David's home. Read-only
code/public assets, private state directory, explicit configured origin, HTTPS,
trusted proxy routing, request/body/time/concurrency limits and no credential
logging. One process with bounded threads; the current RAM state is NOT shared
across multi-process workers. Pin dependency hashes and record versions/SBOM.
Fuzz parsing and test original Host/Origin handling through the actual proxy.
Do not trust arbitrary X-Forwarded-For or X-Forwarded-Host from the Internet.

Review account lifecycle: disable state checked on every renewal, recovery,
password change invalidating active HTTP sessions, retention/deletion policy,
registration/rate abuse limits, stale certificate window, clock behavior, key
rotation, backup/restore and compromise response. Owner access requires stronger
reauthentication and preferably a second factor in its own later gate.

The reference includes a per-IP/per-name fixed window, two concurrent password
hash slots, and session/challenge capacities. These are testable bounds, not a
complete Internet abuse defense. Anonymous certificates do not prevent Sybils.
The single-threaded WSGI development server is not a production server.

## No deployment facts are assumed

box-webhost has externally reachable ports per David's description, but this
handoff does not know or change its DNS name, interfaces, existing services,
TLS setup, SSH identity or firewall. Inspect that host with permission only when
S04 is selected. Do not replace a service already using 80/443. Reuse its reverse
proxy only after confirming ownership and routing. No tunnels are created.

## Optional rendezvous (a separate later decision)

The MVP uses manual signed signaling and needs no signaling backend. Automatic
peer invitations would add a minimal RAM-only, 120-second mailbox for signed
SDP, random unguessable invitation IDs, bounded size/rate and explicit acceptance.
That would be new service scope; don't smuggle it into /auth or use username
lookup as a globally enumerable chat directory. Never relay message bodies
through it. Universal connectivity may also require independently configured
STUN/TURN. These are documented network dependencies, not login/signup logic.
