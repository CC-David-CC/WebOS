# CodiServer Server — minimal identity/bootstrap handoff v0.2.0

**Do not deploy on box-webhost yet.** This is a separate server-side plan plus
an executable **loopback-only reference** for contract tests. The web/ANON GUI
path works without starting it. No port forwarding, firewall, DNS, TLS, systemd,
sudo, or persistent public service was configured by this handoff.

The eventual server does only two jobs: distribute public static resources and
issue short-lived identities after anonymous registration or username/password
signup/signin. Desktop computation, Linux v86 execution, files inside the guest,
and P2P messages stay in browsers. Manual signed signaling keeps chat out of this
service. Automatic discovery, TURN and the future owner-files broker are separate
explicit decisions, not undocumented responsibilities of the login server.

## Optional local tests

Use an already authorized Python environment with dependencies in requirements.txt.
The code uses Python WSGI/SQLite plus `cryptography` and `argon2-cffi`; it does not
implement cryptographic primitives itself and needs no FastAPI, Docker, Redis,
Node server or database daemon. The dependency ranges are **not** a production
lockfile; lock hashes during the deployment gate.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
# ONLY when testing the later connected mode locally:
python3 -m codiauth.dev \
  --web-root ../codiserver-web-v0.2.0/public \
  --state-dir ./var --port 8098
# Open http://127.0.0.1:8098/ (not the web-only development port).
```

The reference serves an explicit public directory and intercepts config.json
with its **test authority** public key. The UI says Test server validated,
never Official server validated. Both ANON and SIGNIN now make real requests.
It stores registered password hashes + the issuer private key under ./var;
anonymous identities, one-use challenges and key-bound session tokens remain
only in RAM. Signing keys are generated on first local launch, not shipped.

**Do not point --web-root at your home folder or CodiServer project root.**
Use only the sibling web package's public/ directory. State and public trees
must be disjoint. This service has no host-files endpoint.

## Read first

AGENTS.md → shared/PROTOCOL.md → docs/01_SERVICE_PLAN.md →
docs/02_BUILD_TEST_LADDER.md → docs/03_TICKETS.md → evidence/STATUS.md.
The Python reference is not a hardened Internet server. Its public deployment
entry point is deliberately not implemented; complete S04 before adding one.

## Operational simplicity

One authority process, bounded worker threads/hashing and SQLite are enough for
the initial scale. Memory-held challenges/sessions mean **do not run multiple
independent WSGI workers** and expect them to share state. Restart invalidates
HTTP sessions/challenges but not registered accounts or already issued offline
certificates. If scale later demands another topology, change the state model
rather than layering inconsistent local caches over it.
