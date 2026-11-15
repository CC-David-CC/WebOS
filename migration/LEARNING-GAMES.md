# Preserved planned learning and strategy games

Seven source-only planned games now have independent repositories under `apps/`.
Their three shared validation/report/odds modules have one owner at
`libraries/learning-game-core/`. No Desktop view, renderer, audio, account storage
adapter or authorized host operation has been added. These are not enabled apps.

| Component | Directory | Mechanical baseline | Package commit |
|---|---|---|---|
| math-path | `apps/math-path/` | `b27ef75510b3d9a7f52b295a313e7d81c3b52fea` | `2a0c2812fb85dc7edb7280f0a30649637fbb8f4e` |
| fraction-farm | `apps/fraction-farm/` | `1aec8754434f7fd2dbbce8e15371b544199038a4` | `2dbcbbfe3fd6e47a9abc157c0d4f9152514167f5` |
| word-weaver | `apps/word-weaver/` | `2de30df8f6da2c825da7465db2fdd982ea105133` | `25504bbf142dee6e5c4817283691c96a95fe8031` |
| market-math | `apps/market-math/` | `0bf4867c5f5c4d5390c5ef145498dc4c75d58e96` | `e33b4409d4512d5ba44864d486cf68adc525e526` |
| rule-detective | `apps/rule-detective/` | `93fdb65fc646581eee1357398ade45050ee36ba0` | `3d9609c50b6f20360bc19e64d735a5c2464233b9` |
| pocket-conquest | `apps/pocket-conquest/` | `0adbf3df00585965868f33527656996ac1fda7b4` | `d3b63061c95661f71950ba114bd4a39dec8558ac` |
| tile-islands | `apps/tile-islands/` | `96612415765ef49649e7ced1becbe3cbee27a9fa` | `7d04e64b2bb1b6eb6950188f703d85201310899b` |
| learning-game-core | `libraries/learning-game-core/` | `516da45cc6eff3020d4004cb692e3e527bcad654` | `5ee756d48c55a91963e232c542fac171902f16c8` |

Each mechanical baseline preserves its original file blobs/modes and filtered
path history. Package declarations and public-import rewiring are separate commits.
The original full history, original grouped README/package metadata, commit maps
and exact tree checks remain in private recovery. The old aggregate package is
superseded metadata, not a grouped source owner in this assembly.

Run the preserved rules and cross-component tests from the parent:

```sh
npm ci --ignore-scripts
npm run test:planned-games
```

All57 original tests pass before and after separation. Individual model tests
remain with their game. Shared experience tests remain with the shared library.
Cross-game learning-report/save-version tests and the byte-identical historical
fixture belong to `tests/learning-games/` and use public package exports.
No assertions, game rules, snapshot versions or fixture contents were changed.

Math Path, Fraction Farm, Word Weaver, Market Math and Rule Detective use core-2
snapshots and reject their existing core-1 fixtures. No migration is implemented.
Pocket Conquest remains core-1; compatibility beyond its initial state is not
established. Complete compatibility review before enabling account saves.
Tile Islands and Pocket Conquest are distinct models with shared bounded odds.

These seven planned cores add to the28 previously registered game repositories.
Source organization and passing domain tests do not qualify rendering, UX,
window lifecycle, server persistence or human/agent Desktop operation.
