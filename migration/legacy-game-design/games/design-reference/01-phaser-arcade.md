> Original design reference from 2026-10-30. This describes intended behavior, not current implementation or qualification. The current app README is authoritative for status. Pseudocode and template JSON here are documentation, not build entries.

# Phaser · 2D arcade

Complete small games with precise rules, responsive touch controls, scenes, sprites, cameras and animation.

**Status: design/pseudocode only; no game is implemented or browser-tested in this ZIP.**

| App | Single-player experience | Wave |
|---|---|---:|
| `Falling Blocks` (original package reference) | Tetris-type falling-block puzzle | 1 |
| [Snake Garden](../../../apps/games/01-phaser-arcade/snake-garden/design/README.md) | Grid arcade | 2 |
| [Chess Study](../../../apps/games/01-phaser-arcade/chess-study/design/README.md) | Single-player chess versus local AI | 2 |
| [Solitaire Table](../../../apps/games/01-phaser-arcade/solitaire/design/README.md) | Klondike cards | 2 |
| [Sky Courier](../../../apps/games/01-phaser-arcade/sky-courier/design/README.md) | Side-scrolling arcade shooter | 2 |
| [Lantern Leap](../../../apps/games/01-phaser-arcade/lantern-leap/design/README.md) | Precision-friendly platformer | 3 |
| [Garden Defense](../../../apps/games/01-phaser-arcade/garden-defense/design/README.md) | Single-player tower defense | 3 |
| [Pocket Rally](../../../apps/games/01-phaser-arcade/pocket-rally/design/README.md) | Top-down single-player racing | 3 |

## Engine boundary

Choose the smallest per-game model: discrete board logic, Phaser Arcade Physics, or simple authored kinematics. Do not load Rapier or Babylon.

Every child folder is an independent app. No category loader or inherited base class is required. All implement synchronous `mount(host)` and app-owned `dispose()` when built. Phone controls are mandatory. These apps remain flat browser-window experiences, including when viewed in the headset browser.

Rive is specified in each child folder, not added as an optional afterthought. Read [engine guidance](ENGINE-GUIDES.md), [Rive composition](RIVE-COMPOSITION.md), [integration handoff](ORIGINAL-INSTRUCTIONS.md) and [common gates](ACCEPTANCE-COMMON.md).

Official reference IDs: S01, S02, S03 in [SOURCES.md](SOURCES.md). API choices still require dependency pinning and verification.
