# Learning and Strategy games

All seven games open from **Games → Learning & Strategy** on ksu.codes. In each game, **Game files → Save** creates an editable round. Opening the file from **Files → Documents** resumes the game.

| Game | Live source | Native file ending | Desktop and phone |
|---|---|---|---|
| Fraction Farm | [`5558c9adcdbc`](https://github.com/CC-David-CC/fraction-farm/commit/5558c9adcdbc8eb3ce2cd67669a9bb3859610a6a) | `.fraction-farm.json` | [Hosted desktop](learning-games-hosted/fraction-farm.png) · [Phone](https://github.com/CC-David-CC/fraction-farm/blob/5558c9adcdbc8eb3ce2cd67669a9bb3859610a6a/docs/phone.png) |
| Market Math | [`2c2e56476c60`](https://github.com/CC-David-CC/market-math/commit/2c2e56476c604c99f546e9c8f264fe42fd879882) | `.market-math.json` | [Hosted desktop](learning-games-hosted/market-math.png) · [Phone](https://github.com/CC-David-CC/market-math/blob/2c2e56476c604c99f546e9c8f264fe42fd879882/docs/phone.png) |
| Math Path | [`bae89640abef`](https://github.com/CC-David-CC/math-path/commit/bae89640abef45d0a7d65d704d754ed9d40e1a68) | `.math-path.json` | [Hosted desktop](learning-games-hosted/math-path.png) · [Phone](https://github.com/CC-David-CC/math-path/blob/bae89640abef45d0a7d65d704d754ed9d40e1a68/docs/phone.png) |
| Pocket Conquest | [`823a51dbe621`](https://github.com/CC-David-CC/pocket-conquest/commit/823a51dbe62121f39c2af2f09cb052acb3b85abd) | `.pocket-conquest.json` | [Hosted desktop](learning-games-hosted/pocket-conquest.png) · [Phone](https://github.com/CC-David-CC/pocket-conquest/blob/823a51dbe62121f39c2af2f09cb052acb3b85abd/docs/phone.png) |
| Rule Detective | [`0a6c3dde341e`](https://github.com/CC-David-CC/rule-detective/commit/0a6c3dde341e48e7c9e82116d86d810d96c8dac9) | `.rule-detective.json` | [Hosted desktop](learning-games-hosted/rule-detective.png) · [Phone](https://github.com/CC-David-CC/rule-detective/blob/0a6c3dde341e48e7c9e82116d86d810d96c8dac9/docs/phone.png) |
| Tile Islands | [`c297890852df`](https://github.com/CC-David-CC/tile-islands/commit/c297890852dfcd77b412d6a8e92549d1ae3a4592) | `.tile-islands.json` | [Hosted desktop](learning-games-hosted/tile-islands.png) · [Phone](https://github.com/CC-David-CC/tile-islands/blob/c297890852dfcd77b412d6a8e92549d1ae3a4592/docs/phone.png) |
| Word Weaver | [`c3fc00c1e8ee`](https://github.com/CC-David-CC/word-weaver/commit/c3fc00c1e8eec75a7ab0ca20a172b806e70caf8d) | `.word-weaver.json` | [Hosted desktop](learning-games-hosted/word-weaver.png) · [Phone](https://github.com/CC-David-CC/word-weaver/blob/c3fc00c1e8eec75a7ab0ca20a172b806e70caf8d/docs/phone.png) |

The hosted test started a fresh Anon browser, played each game, saved it, closed its window, reopened it from Files, and made another move. It verified that the saved bytes changed with that move. Registering promoted all seven files. A second browser signed into the account, reopened all seven rounds from the server, and saved further progress. Anon issued zero private file requests. The browser reported zero page errors.

Anonymous rounds also passed the same save, reopen, and continue checks at 390 × 844, 1920 × 1080 and 3840 × 2160. On the phone-sized viewport the browser sent touch input for game moves. Physical touchscreen verification remains open. Rule Detective's phone layout now keeps the hypothesis and footer actions accessible. [Hosted phone screenshot](learning-games-hosted/rule-detective-phone.png)

The seven games passed 67 native tests, alongside five shared-core tests, two cross-game compatibility tests, four Files association tests, and 14 Desktop tests.

| Release | Revision |
|---|---|
| Production viewer | `e803ec855d4727e55b0a7f2f7c9429b11753008892179e9d8fa726186cf131a9` |
| [WebOS release/learning-games](https://github.com/CC-David-CC/WebOS/tree/d28ca9bd28dc80f2a74c610ca593715541a93df1) | `d28ca9bd28dc80f2a74c610ca593715541a93df1` |
| [Desktop](https://github.com/CC-David-CC/desktop/commit/e6d8cebefc6bc3ccaf438330b19632a5f52cc823) | `e6d8cebefc6bc3ccaf438330b19632a5f52cc823` |
| [Learning game core](https://github.com/CC-David-CC/learning-game-core/commit/a1f3db3987fa0a89aad6eab359d90c9f49f24454) | `a1f3db3987fa0a89aad6eab359d90c9f49f24454` |
| [WebOS main at release](https://github.com/CC-David-CC/WebOS/tree/3f541eb6e5561a56ed57a5a393088253d670c42f) | `3f541eb6e5561a56ed57a5a393088253d670c42f` retained the previous seven game pins. The integration is published on the release branch. |

Rebuild from the pinned WebOS checkout with its npm workspace dependencies and initialized app submodules. Run the standard viewer workflow with `--learning-games enabled`. The native suites run with `npm run test:planned-games`.
