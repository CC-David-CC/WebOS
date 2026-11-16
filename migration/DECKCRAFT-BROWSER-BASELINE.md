# DeckCraft source-built browser baseline

DeckCraft `772219838e2807f0d5b0270f8993421499717f58` builds and runs as a
standalone browser application with shared fonts
`9ffb3a717e081a817470c5efe68fe314ca16c987`. The tested source assembly was
`b8128e06086c5b3bff29ace94da95f3a846e24dd`; subsequent reporting changes do
not change those component inputs.

## Build and packaging actually exercised

Rust 1.95 compiled the release browser binary, using its unchanged Cargo.lock
(SHA-256 `62ae3ec99cad25f438b1b86cf8e88fa6ec350f6405725862cf33792cf4a195a9`).
The equivalent assembly command is:

```sh
CRAFT_FONTS_REQUIRED=1 CARGO_TARGET_DIR=/path/to/output/target python3 scripts/craft_cargo.py deckcraft -- build --release --jobs 4 --locked --offline -p deckcraft-web --target wasm32-unknown-unknown
wasm-bindgen --target web --out-dir /path/to/browser --out-name deckcraft --no-typescript /path/to/output/target/wasm32-unknown-unknown/release/deckcraft-web.wasm
```

Cargo dependencies were populated separately with a locked public fetch before
the offline build. Use the selected Rust toolchain and `wasm-bindgen` 0.2.129;
its Linux tool archive matched the official GitHub release SHA-256 digest.
The compiler and packager ran with network disabled and the original workspace
hidden. No dependency, lockfile or DeckCraft source changes were required.

Packaging retained the upstream canvas HTML and replaced its two Trunk links:
the Rust link became a module importing `./deckcraft.js` and awaiting its default
initializer; the icon link became `./deckcraft.ico`, copied from the selected
source. The generated JS, WASM and eframe snippet were retained together, along
with the upstream attribution, notice and two source licences. This produced
nine files, 49,282,200 bytes. The raw release WASM was 53,088,372 bytes with SHA-256
`d7c611fc03a27802de3463c8e53a56a18eb6695563d2b76ee5a4283773734b93`.
This is an explicit standalone test package. It has no `wasm-opt` pass and is
not claimed byte-equivalent to the upstream Trunk release pipeline.

## Real browser result

Chromium ran in an isolated network namespace with a disposable local static
server and fresh browser profile. `?blank&webgl` selected the blank deck and
WebGL2 path using SwiftShader. The real Rust UI rendered; its screenshot was
visually inspected and showed the inserted text shape and Inter font selection.

The application's existing `window.deckcraft` API inspected the live document,
inserted a rounded rectangle containing `WebOS rebuild smoke`, inspected that
shape, then undid the insertion through the same application's command path.
The slide shape total changed **2 → 3 → 2**. Five local asset requests succeeded;
there were zero page errors, console errors, failed asset requests or external
requests. The browser and server were closed after the test.

The first test launch failed before opening a browser because its Puppeteer
import used the old package directory layout. The import was corrected to the
installed 25.17.0 package export; app code and test assertions were unchanged.
Both attempt logs are retained privately.

## Still open

This is not desktop/account/agent acceptance. DeckCraft remains disabled in the
minimum launcher. It still needs synchronous mount/dispose integration, explicit
instance/document/resource targeting, authorized shared operations, durable
server save acknowledgement, Save As/export identity handling, cancellation,
lifecycle and multi-client persistence tests. The existing upstream host bridge
sends save bytes to the parent; sending bytes alone does not confirm a durable
account save. No platform agent authority was exercised by this standalone page
API test. Full feature coverage, production release notices and deployment are
separate gates. Original source and deployments remain unchanged.

The subsequent [host-save qualification](DECKCRAFT-HOST-SAVE.md) preserves the
premature-clean failure at this baseline and records the selected fork fix with
full native CI and real-browser acknowledgement/view regressions. Account and
Desktop integration remain separate.
