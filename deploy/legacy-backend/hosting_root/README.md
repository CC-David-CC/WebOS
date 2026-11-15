# KSU root desktop hosting candidate

`common.py` is a reviewed candidate for the managed webhost generator, not a
standalone web server or a live Caddy edit. It derives from generator718934ce….
The hardware/cardboard dependency modules are unchanged copies of the currently
installed modules. No production authentication hashes are included.

An optional KSU-only `codi_mount = ""` selector generates root routes. With no
selector, every current generated production byte stays unchanged. Root mode
requires the existing enabled desktop profile and a coherent native asset graph.
The application, file and guest backends must actually be migrated to root first.

Blog, guides, static assets, robots, health, test-time and the `/desktop/` prototype
retain the website backend and their previous policies. Native root assets/API,
discovery, gateway and rendezvous have their own routes; no hidden-prefix rewrite
implements the root. `/hidden` entry paths redirect to root. Other domain blocks,
the shared ingress and the TURN certificate site remain byte-identical.

Use the hosting controller lock, validated manifest, pinned immutable source,
backups, generated Caddy validation/reload and all-site/prototype verification for
deployment or rollback. The candidate is not authorization to hand-edit derived
live Caddy. Read `evidence/root-hosting-cache.md` for measured scope and the
remaining coordinated production transaction.
