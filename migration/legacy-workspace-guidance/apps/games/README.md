# Games source layout

The four directories follow the original `UNFINISHED-TO INTEGRATE-PARTIAL/game_tree` groups. They contain the canonical source of the integrated game previews:

- `01-phaser-arcade` — arcade games.
- `02-three-physics-xr` — physics games with XR intended for later.
- `03-babylon-xr-games` — world games with XR intended for later.
- `04-rive-interactives` — interactive games.

The original names describe the source groups and their design goals. They do not promise that every preview currently uses that engine, has final Rive artwork, or supports XR; see each app's README for its actual capabilities and remaining work.

`catalog.json` maps the existing stable app IDs to these source groups. The public-app builder uses this map; changing a folder must not change the ID, saved-game format, or Files routing. Run `node --test tests/game-preview-registry.test.mjs` and `node tests/game-menu-groups.test.mjs` (with its isolated preview running) after catalog or menu changes.
