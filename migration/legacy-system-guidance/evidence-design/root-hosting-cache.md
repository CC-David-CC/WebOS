# Root routing and cache migration — 2026-10-24 UTC

Production remains at `/hidden/`; the homepage and `/desktop/` are unchanged.
This phase implements and verifies routing/cache candidates for the root/blog
cutover. The full goal remains active, including later distributed networking.

The new managed generator is `hosting_root/common.py`, SHA
`c3181a47ed0b9489bf2b6093ce2f54e62bab089560eb57eec86c6f0ec0c290e7`.
An enabled KSU-only `codi_mount = ""` flag selects root. Missing selector renders
every existing Caddy byte unchanged. Other domain blocks, shared ingress and TURN
certificate site remain byte-identical. Root reserves `/blog`, `/posts`, `/static`,
`/robots.txt`, `/healthz`, `/test-time` and `/desktop` for the actual website.
Native root API/discovery, guest assets, file gateway, speech and WebSocket routes
use their actual root paths. Hidden entry URLs redirect; there is no root→hidden
rewrite. Existing CSP and body-size boundaries remain scoped to their handlers.

Generated candidate `.build/hosting/root-mount-r1-candidate` has manifest SHA
`f583f6f43f5b03d1e48afd71567f0c508373a7073c1bfc5add1dd75a591bee12`, production
Caddy SHA `4cf23397bd3d1885e8f2c386072633c9ffec36459811753bce68866b50252bb5` and
prepare Caddy SHA `97b26b7ab35c24688a8dc7d4be0c0877a5cd14d2d59d8e5e6befd830a14622f9`.
Hardware/cardboard modules remain the current34bea543…/9aff2ac2… sources.

`root-hosting-result.json` passes17 actual Caddy checks against the real FastAPI
blog/prototype source and tagged native-port stubs. They cover root paths, GET/HEAD
redirects, strict blog vs desktop/prototype CSP, all133prototype files over HTTP,
all three guides, retained website paths, speech static selection, nine other
domain roots, preserved hardware authentication, actual WebSocket upgrade,
64KiB API and12MiB file limits, and invalid root-selector refusal. An independently
generated fixture user replaces only the private hardware auth import for tests;
no production account/hash was read or copied. The first harness attempted to
adapt that unavailable import and selected a static directory instead of a file;
both failures are retained. Candidate production bytes were not weakened.

The mount-aware public cache client retires only the opposite owned desktop
worker and `codi-public-v1|<opposite-mount>|*` caches, after a bounded, uncached,
non-redirected config response confirms this page's actual server mount. Exact
script/scope matching preserves foreign workers. Prototype caches, unrelated
caches, localStorage and IndexedDB are untouched. Offline/mismatched/oversized
metadata defers retirement. The inverse operation supports rollback to hidden.

Root entry navigation is network-first while online: a restored blog or newer
entry document comes from the authoritative server. Only the exact verified
desktop index is cached; other server HTML is returned uncached. Network failure
or5xx can use the verified recovery shell, whose UI does not claim RAM was saved.
Other public assets remain verified cache-first; API/config/private files never
enter the public cache. Hidden entry caching retains its earlier policy.

Final native16 candidate `.build/releases/connected-root-cache-r2` has manifest
`c23b1b73df68ffb25da810a7db73074d09297f0ccc06c459e8bc9c0430ca30c1`,327files.
Versioned cache client:
`assets/desktop/device-cache-v2/23df9ee07327b089a5d491684921e9a72d14a661f35692d8a4d7981d2b7eb44c.mjs`.
Worker SHA `891592f66fe8a63a66b259702d834773380c7df65e4c312f25c6b7e1ea57ef4e`;
public cache id `1bf66d10b93fcb51e1e2131fd54e4d794da7bea95a4679b0fdc7e265b4d85036`.
All53native/security files,24network modules, seven app bundles and the Linux
image are unchanged. Old public assets are retained except mutable entry/cache/
graph metadata. R1/8d9384dd… was tested and superseded by R2's root entry behavior.

`mount-cache-browser-result.json` passes17 actual Chrome worker/CacheStorage
checks using authentic old/new workers in an owned localhost fixture. It covers
warm hidden→root, root→hidden, authoritative blog navigation after rollback,
uncached foreign HTML, repeated calls, stale-page guard, offline/oversize refusal,
foreign-worker preservation and actual private/prototype sentinel contents in
CacheStorage/localStorage/IndexedDB. Identity metadata is a fixture context stub,
not a live account/VM claim. It exercises the real cache client and worker bytes.

The final candidate was code-upgraded in the retained VM at its actual root mount.
`root-cache-r2-native-vm-result.json` passes11 real Chrome/v86 cache checks,
including persist's actual boolean decision, lazy app loading, corrupt-cache
repair, honest offline reload/RAM loss, fresh Linux on return and clear/rebuild.
No VM snapshot or private-file caching is claimed.

`root-caddy-native-vm-result.json` then tests the generated Caddy routes with real
native VM backends and the real blog/prototype FastAPI backend, using the fixture
certificate's exact SPKI. It passes38 xterm/PTY/nano/touch/IME checks and19 durable
document composition/authorization/lifecycle checks at HTTPS root. Blog, guide and
prototype metadata bytes match the real source. The blog backend uses an owned
loopback SSH reverse forward; no host filesystem or private service state is
shared with the VM. Fixture changes adapt only host matching, an explicit static
IP certificate, logging/static locations and the blog's expected Host header.
These are fixture TLS tests, not public/default-trust/WAN evidence.

Initial combined-fixture failures retained in root-caddy-native-vm-before-* logs:
fixture hostname remapping also altered the blog Host header, and IP-literal
Chrome through QEMU had no SNI for default certificate selection. The fixture now
preserves the blog header and selects its sole tagged certificate explicitly;
public production TLS policy is unchanged. Every failed and successful run
restored the original Python fixture ingress and removed the Caddy test unit.
The blog process and owned SSH forward are stopped. Cleanup preserves native PIDs
and config; the final VM is healthy at root, root/fence12, native candidatec23…,
with no pending native or fixture route journal. See root-phase3-final-state.

The deployable offline mount operator is the exact cycle-tested five-file code,
manifest `6e4ebb33e945ea8712dd72c56f5a9928a955af5b340ceaff6ef0221112ebe0dc`.
`stage-root-cutover.py` can only validate/install these Git-first immutable files;
it never activates services or routes. Installation receipts are recorded below.

Source/proof commit `8f605fa2bbd37f9525d71354e26a0e2d16046c07` was fast-forwarded
into the clean webhost checkout under the hosting lock. All373 declared native,
operator and proof files matched. Phase3 proof manifest is
`7abe4b45301674b6fd7a610387994e9971250b90d433868c0374ee58f4b751c4`.

The plan and actual inactive install both pass. Installed candidates are
`/srv/codi-connected/releases/native16-c23b1b73df68ffb2` and
`/srv/codi-connected/mount-operators/6e4ebb33e945ea8712dd72c56f5a9928a955af5b340ceaff6ef0221112ebe0dc`.
Root receipt:
`/srv/codi-connected/root-cutover-install-1792835854213111621-result.json`.
The installer verified all133prototype files and unchanged native PIDs,
config, hosting, website release and homepage. Neither candidate was activated.

`validate-root-cutover.py` then passed both generated Caddy configurations through
the actual production Caddy validator as its runtime user, using the private
hardware authentication import in place on the server. Only temporary validation
files were created and removed; no live configuration was changed. Log hashes,
not adapted private authentication data, are retained. The installed mount tool
also prepared a readonly root plan against the real native/file/guest system:
24metadata files, prospective root3. It signs prospective public plan bytes but
does not commit them; the actual authority stays at root2. Native PIDs, managed
config, hosting, external fence and authority revision/token remain unchanged.
See root-cutover-{plan,install,validation}-result.json and
root-phase3-source-sync-result.json. No production restart or notice was issued.

The installation/validation follow-up is frozen at private Git
`9531506c9ed3254d6946df2cbc0f9d296e0e9b78`, package
`tools/codiserver/root-mount-r3-staged`, eight declared files, proof manifest
`93a10812d53b89e3785e66ecc9e53507bb70980d16a0a61137a262d2290e8128`.
The clean webhost checkout was fast-forwarded and verified under the hosting
lock; config and native PIDs stayed unchanged. That source-only follow-up does
not activate the installed candidates. Receipt:
`root-phase3-staged-source-sync-result.json`.

Still required before public cutover: a tested coordinated deployment journal
covering website release, native code, signed mount operation and managed hosting;
forward-revision rollback/recovery across those phases; production Caddy validation
with its private import kept on-server; truthful maintenance notice; real public
root/blog/all-site/prototype and independent-WAN acceptance. The P2P/islands,
checkpoint/PoW/chess-audience/8k work remains required. Do not mark the goal done.
