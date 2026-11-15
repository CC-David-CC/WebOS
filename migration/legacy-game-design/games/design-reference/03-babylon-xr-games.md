> Original design reference from 2026-10-30. This describes intended behavior, not current implementation or qualification. The current app README is authoritative for status. Pseudocode and template JSON here are documentation, not build entries.

# Babylon.js · complete 3D and XR games

Small authored worlds with objectives, camera modes, animated actors, spatial audio, interactive environments and an ending.

**Status: design/pseudocode only; no game is implemented or browser-tested in this ZIP.**

| App | Single-player experience | Wave |
|---|---|---:|
| [Clockwork Room](../../../apps/games/03-babylon-xr-games/clockwork-room/design/README.md) | Small escape-room puzzle | 1 |
| [Crystal Defense](../../../apps/games/03-babylon-xr-games/crystal-defense/design/README.md) | 3D tabletop tower defense | 2 |
| [Drone Circuit](../../../apps/games/03-babylon-xr-games/drone-circuit/design/README.md) | Single-player 3D time trial | 2 |
| [Pocket Golf](../../../apps/games/03-babylon-xr-games/pocket-golf/design/README.md) | 3D miniature golf | 3 |
| [Target Garden](../../../apps/games/03-babylon-xr-games/target-garden/design/README.md) | Stationary 3D target challenge | 3 |
| [Orbital Courier](../../../apps/games/03-babylon-xr-games/orbital-courier/design/README.md) | 3D navigation and collection | 3 |
| [Clockwork Quest](../../../apps/games/03-babylon-xr-games/clockwork-quest/design/README.md) | Small third-person adventure | 4 |

## Engine boundary

Use explicit game kinematics unless a game needs rigid bodies. Pocket Golf selects the Babylon Havok plugin; do not load Havok into the other games merely because it exists.

Every child folder is an independent app. No category loader or inherited base class is required. All implement synchronous `mount(host)` and app-owned `dispose()` when built. Phone controls are mandatory. Every child also implements its own XR flow; read its XR.md.

Rive is specified in each child folder, not added as an optional afterthought. Read [engine guidance](ENGINE-GUIDES.md), [Rive composition](RIVE-COMPOSITION.md), [integration handoff](ORIGINAL-INSTRUCTIONS.md) and [common gates](ACCEPTANCE-COMMON.md).

Official reference IDs: S09, S10, S11, S12, S13 in [SOURCES.md](SOURCES.md). API choices still require dependency pinning and verification.
