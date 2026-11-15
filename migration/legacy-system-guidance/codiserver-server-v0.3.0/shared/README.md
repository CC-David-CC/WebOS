# Shared contract boundary
These files are intentionally identical in the server and web ZIPs. This is a
necessary distribution boundary, not two competing internal state models.
`PROTOCOL.md` is normative for this handoff; `schemas.json` describes wire shapes;
`fixtures.json` contains a Python-signed **public** test certificate with a fixed
explicit test clock. It contains no issuer or browser private key.
Run `scripts/check_package.py --peer <other-package-root>` to detect drift.
