# 830c asset transition — isolated research, not an operator

Inputs: exact parent 3ad and corrected target 830c. The target keeps every old
path and preserves the old global apps.json; four old files differ (cache
manifest, offline worker, desktop loader and unserved patch), with 84 added
paths. Generator SHA-256 `e06fc8aa018ff048138fb2585ddb34ab9c6f1b061fb0022b06b14dca7df55928`;
route-table SHA-256 `32ad4a8b79bfa3886f5a16b29e6b55e04d17268230ba449c967a344283a720c1`.
The guard builder produces SHA-256
`7fba2e37df11c41cc06db58150a14c74e3aa575208eb913827f6cdb3f7a7c956`.
The derived render-inventory builder produces SHA-256
`49e99fe32497149ee6f89d840f36afc152e4176414dd6978a0f72457b24d37d3`.

`generator.test.py` binds both original and e7 main families, confirms exact
old and gated Caddy bytes, non-beta equality and unknown selector rejection.
`caddy.test.py` tests all 166 asset routes, exact shell queries, retained old
overlays, backend routing and maintenance denial on real loopback Caddy.
The isolated baseline fixture is not the whole live site; browser/account
compatibility is a separate test.

`asset-floor.py` reuses the existing FloorJournal with separate asset journal
and asset floor names. Every lock check verifies that the original OPFS floor is
still the exact e7a5/3ad record. It gates before a new asset floor is durable;
a pre-floor interruption may restore 3ad, and a post-floor interruption returns
to the gate then forward to 830c. A finalized recovery with unavailable 830c
leaves the gate selected. Five SIGKILL model tests cover those outer phases.
`asset-router.py` binds only pinned 3ad, gate and 830c snapshots for the exact
old/e7 main families to the existing transaction and inventory. It rejects
unreviewed endpoints and old-route restoration after asset floor.
`controller.test.py` uses the pinned copied managed controller and real
loopback Caddy against e7 for SIGKILL at outer gated/floor/forward stages and
inside the Caddy reload before and after asset floor. It checks a 503 gate,
correct recovered endpoint and unchanged original floor. The test translates
production hostnames/paths to loopback; timer, service checks, signed health,
backup and main health use fixture callbacks. Forking with its HTTP fixture
thread causes Python's documented warning; no deadlock was observed.

The generated guard rejects a pending asset journal and after the asset floor
accepts only 830c with its exact beta route block. The current live fb27 guard
and bc9 recovery successor do **not** understand that floor. A protected,
reviewed combined successor/guard installation and quiescence fence is required
before asset transition. The snippets here do not establish supported entrypoint
fencing, privileged custody, actual backend/signed health, production ingress,
old-client persistence, or release safety. No live changes were made.

Example tests, with verified input trees and Caddy:

```
python3 -B research/main-qualified-release/beta-asset-830c/generator.test.py OLD NEW
python3 -B research/main-qualified-release/beta-asset-830c/router.test.py OLD NEW
python3 -B research/main-qualified-release/beta-asset-830c/guard.test.py OLD NEW
python3 -B research/main-qualified-release/beta-asset-830c/asset-floor.test.py
CODI_ASSET_KILL=inner-after python3 -B research/main-qualified-release/beta-asset-830c/controller.test.py OLD NEW CADDY
```
