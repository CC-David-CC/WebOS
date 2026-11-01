# Dependencies, licenses and missing assets

No npm modules, browser binaries, WASM engine files, game art, fonts, audio or `.riv` assets are bundled. This is a design handoff. The implementation agent must bind versions, licenses and provenance before release.

| Family | Intended dependency role | Version status |
|---|---|---|
| Phaser | 2D scenes/rendering/input; Arcade Physics where needed | Unbound; choose one tested major/release |
| Three.js | Rendering + WebXR + canvas textures | Unbound |
| Rapier JS/WASM | Physics in the seven Three apps | Unbound; snapshot fingerprint required |
| Babylon.js | 3D games + WebXR + animations | Unbound |
| Havok web runtime | Pocket Golf only | Unbound; license/source review gate |
| Rive web runtime | All apps' specified character/UI integrations | Unbound; asset/runtime pair must be tested |
| chess.js | Chess rules, not AI | Unbound; BSD-2-Clause project [S19] |

Use the project's actual lockfile and locally served content-hashed assets. Match each WASM binary to its JS loader. No floating `@latest` CDN URL is part of a release. Record license notices and source origins for every bundled dependency; the external source register is guidance, not a completed legal inventory.

Rive's web runtime is MIT [S17]. Its authoring products and individual artwork/fonts are separate. Babylon's documentation describes the Havok web runtime as MIT-distributed [S11,S20]; this does not establish public source access to the full native Havok implementation. Do not advertise “all internals fully source-available” without checking that requirement.

Create an asset manifest per implemented game: relative path, purpose, author/source, license, original-versus-third-party, content hash and maximum dimensions/size. Use original names/themes. Falling Blocks and Tabletop Bot Arena are genre descriptions, not licensed Tetris/BattleBots products. Avoid copied branding, music and art.

Artboard properties in RIVE.md are **requested authoring contracts**, not built-in Rive properties. The implementer must create/inspect assets that actually expose them. Do not invent a `.riv` by renaming JSON. No claim is made that Rive authoring tools are installed or authorized in the integration environment.
