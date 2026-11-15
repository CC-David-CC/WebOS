> Original design reference from 2026-10-30. This describes intended behavior, not current implementation or qualification. The current app README is authoritative for status. Pseudocode and template JSON here are documentation, not build entries.

# Three.js + Rapier · physics to tabletop XR

Visible physical cause and effect, direct manipulation, small constructive challenges, then a tabletop robot-combat capstone.

**Status: design/pseudocode only; no game is implemented or browser-tested in this ZIP.**

| App | Single-player experience | Wave |
|---|---|---:|
| [Physics Playground](../../../apps/games/02-three-physics-xr/physics-playground/design/README.md) | Physics toy with challenge cards | 1 |
| [Marble Works](../../../apps/games/02-three-physics-xr/marble-works/design/README.md) | Build-and-run marble puzzle | 2 |
| [Stack & Balance](../../../apps/games/02-three-physics-xr/stack-balance/design/README.md) | Stability challenge | 2 |
| [Kinetic Relay](../../../apps/games/02-three-physics-xr/kinetic-relay/design/README.md) | Rube-Goldberg mechanism puzzle | 3 |
| [Sling Targets](../../../apps/games/02-three-physics-xr/sling-targets/design/README.md) | Physics aiming puzzle | 3 |
| [Gravity Pinball](../../../apps/games/02-three-physics-xr/gravity-pinball/design/README.md) | Single-player physical pinball | 3 |
| [Tabletop Bot Arena](../../../apps/games/02-three-physics-xr/tabletop-bot-arena/design/README.md) | Single-player BattleBots-style capstone | 4 |

## Engine boundary

Exactly one Rapier world per app instance; meters, fixed simulation ticks, explicit model-to-XR transforms and bounded entities.

Every child folder is an independent app. No category loader or inherited base class is required. All implement synchronous `mount(host)` and app-owned `dispose()` when built. Phone controls are mandatory. Every child also implements its own XR flow; read its XR.md.

Rive is specified in each child folder, not added as an optional afterthought. Read [engine guidance](ENGINE-GUIDES.md), [Rive composition](RIVE-COMPOSITION.md), [integration handoff](ORIGINAL-INSTRUCTIONS.md) and [common gates](ACCEPTANCE-COMMON.md).

Official reference IDs: S04, S05, S06, S07, S08, S12, S13 in [SOURCES.md](SOURCES.md). API choices still require dependency pinning and verification.
