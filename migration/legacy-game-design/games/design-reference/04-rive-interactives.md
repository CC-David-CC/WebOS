> Original design reference from 2026-10-30. This describes intended behavior, not current implementation or qualification. The current app README is authoritative for status. Pseudocode and template JSON here are documentation, not build entries.

# Rive · animated interfaces and small games

Character performance, data-bound controls, branching storytelling and playful interactions; real activities, not animation galleries.

**Status: design/pseudocode only; no game is implemented or browser-tested in this ZIP.**

| App | Single-player experience | Wave |
|---|---|---:|
| [Owl Companion](../../../apps/games/04-rive-interactives/owl-companion/design/README.md) | Interactive character toy | 1 |
| [Reactive Control Desk](../../../apps/games/04-rive-interactives/reactive-control-desk/design/README.md) | Animated interface challenge | 2 |
| [Rhythm Garden](../../../apps/games/04-rive-interactives/rhythm-garden/design/README.md) | Rhythm-tap game | 3 |
| [Story Cards](../../../apps/games/04-rive-interactives/story-cards/design/README.md) | Interactive animated story | 2 |
| [Expression Puppet](../../../apps/games/04-rive-interactives/expression-puppet/design/README.md) | Interactive character and pose toy | 2 |
| [Memory Garden](../../../apps/games/04-rive-interactives/memory-garden/design/README.md) | Animated memory puzzle | 3 |

## Engine boundary

No general physics engine. JavaScript owns goals, timing and saved state; Rive owns authored visual performance.

Every child folder is an independent app. No category loader or inherited base class is required. All implement synchronous `mount(host)` and app-owned `dispose()` when built. Phone controls are mandatory. These apps remain flat browser-window experiences, including when viewed in the headset browser.

Rive is specified in each child folder, not added as an optional afterthought. Read [engine guidance](ENGINE-GUIDES.md), [Rive composition](RIVE-COMPOSITION.md), [integration handoff](ORIGINAL-INSTRUCTIONS.md) and [common gates](ACCEPTANCE-COMMON.md).

Official reference IDs: S14, S15, S16, S17 in [SOURCES.md](SOURCES.md). API choices still require dependency pinning and verification.
