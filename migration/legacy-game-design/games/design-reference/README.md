# Game design reference

These are preserved requirements from the original 2026-10-30 planning package, not current runtime status or test evidence. Current implementations live only in `apps/games/`. Per-game plans are beside their implementation under `design/`; files named `*.pseudo.*` are explanatory documents, not apps.

All 28 original game folders have a current `index.mjs`. Their individual README files describe remaining work; this cleanup does not qualify games, Rive assets, phone behavior or XR.

Shared plans:

- [01-phaser-arcade.md](01-phaser-arcade.md)
- [02-three-physics-xr.md](02-three-physics-xr.md)
- [03-babylon-xr-games.md](03-babylon-xr-games.md)
- [04-rive-interactives.md](04-rive-interactives.md)
- [ACCEPTANCE-COMMON.md](ACCEPTANCE-COMMON.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [ASSET-STATUS.md](ASSET-STATUS.md)
- [DEPENDENCIES-AND-ASSETS.md](DEPENDENCIES-AND-ASSETS.md)
- [ENGINE-GUIDES.md](ENGINE-GUIDES.md)
- [INTEGRATION-BINDINGS.md](INTEGRATION-BINDINGS.md)
- [ORIGINAL-INSTRUCTIONS.md](ORIGINAL-INSTRUCTIONS.md)
- [PHONE-AND-INPUT.md](PHONE-AND-INPUT.md)
- [QUALITY-AND-PERFORMANCE.md](QUALITY-AND-PERFORMANCE.md)
- [RIVE-COMPOSITION.md](RIVE-COMPOSITION.md)
- [ROADMAP.md](ROADMAP.md)
- [SAVE-LOAD.md](SAVE-LOAD.md)
- [SOURCES.md](SOURCES.md)
- [XR-LIFECYCLE.md](XR-LIFECYCLE.md)

The old package catalog, status report, checksums and package validator were removed because they described a documentation bundle rather than the current desktop. Their exact originals remain in Git at Desktop commit `011f2fac19fbbfb7cd0396a81ef67a2f8e078c31`, under `apps/UNFINISHED-TO INTEGRATE-PARTIAL/game_tree/`.
