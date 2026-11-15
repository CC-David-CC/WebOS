# Games source layout

These five groups contain the canonical game sources. The first four preserve the original design categories:

- `01-phaser-arcade` — arcade games.
- `02-three-physics-xr` — physics games with XR intended for later.
- `03-babylon-xr-games` — world games with XR intended for later.
- `04-rive-interactives` — interactive games.
- `05-core-learning-strategy` — core learning and strategy work in development.

The original names describe the source groups and their design goals. They do not promise that every preview currently uses that engine, has final Rive artwork, or supports XR; see each app's README for its actual capabilities and remaining work.

`catalog.json` maps the existing stable app IDs to these source groups. The public-app builder uses this map; changing a folder must not change the ID, saved-game format, or Files routing. Run `node --test tests/game-preview-registry.test.mjs` and `node tests/game-menu-groups.test.mjs` (with its isolated preview running) after catalog or menu changes.

## Original planning package

All 28 original designs now have an app entry under the first four groups. This is source integration, not proof that every game or XR path is finished. Each app retains its original requirements under `design/`; shared requirements are in [the game design reference](../../docs/games/design-reference/README.md). The obsolete unfinished staging tree has been removed. There is one implementation directory per game.
