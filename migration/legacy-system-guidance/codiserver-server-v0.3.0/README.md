# CodiServer Server — identity + delegated P2P support plan v0.3.0

**Keep the origin small:** distribute static resources and issue identities. Do not
make it the global chat, presence, game or per-user settings database. Some of
David's peers can steward scoped directory/room/cache responsibilities independently.

This ZIP preserves the earlier loopback `codiauth` implementation and adds the
**steward/relay architecture, bounded protocol plan, capacity accounting and build
ladder**. A steward daemon or TURN service is NOT implemented/deployed by this release.
The multi-group browser runtime is a separate implementation task in the web ZIP.

Read `shared/MESH_SUPPORT_SERVICES.md`, `shared/MESH_ARCHITECTURE.md`,
`shared/MESH_WIRE.md`, `shared/MESH_SCALE.md`, then `docs/02_BUILD_TEST_LADDER.md`.
`docs/08_P2P_V03_DECISIONS.md` explains intentional changes to earlier suggestions.

## Local checks, no public service required

```sh
python3 -m unittest discover -s tests -v
python3 shared/capacity.py
python3 shared/capacity.py --online 1
python3 scripts/check_package.py --peer ../codiserver-web-v0.3.0
```

The retained authentication tests require the already installed/authorized
`cryptography` and `argon2-cffi` dependencies in requirements.txt. The new model
and capacity tests use only Python's standard library. Do not auto-install packages.

Optional existing loopback service for identity tests:

```sh
python3 -m codiauth.dev --web-root ../codiserver-web-v0.3.0/public \
    --state-dir ./var --port 8098
```

State/private keys must stay outside the public tree. Do not use a home directory
as web root. This does NOT grant owner host-files access, start rendezvous/TURN,
configure DNS/TLS/firewall or publish box-webhost to the Internet.

The shared contracts/models are byte-identical in both ZIPs. The single combined
registry has 181 obligations / 27 gates / 66 tickets; all new production gates remain
planned. `evidence/STATUS.md` distinguishes executed tests from prior-run records
and from unimplemented private group crypto/discovery/load milestones.
