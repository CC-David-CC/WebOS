# Craft workspace build inputs

Run a fork's own Cargo command from the parent with the organized shared font
checkout explicitly selected:

```sh
python3 scripts/craft_cargo.py deckcraft -- metadata --format-version 1 --no-deps --locked --offline
python3 scripts/craft_cargo.py --cargo /path/to/toolchain/bin/cargo gridcraft -- check --locked
```

The command selects a fork from `scope.json`, changes to its workspace, and sets
`CRAFT_FONTS_DIR` to `assets/craft-fonts`. It forwards Cargo arguments and its exit
status. It does not install Rust, select browser targets, fetch dependencies on
its own, or declare the font set compatible. The fork owns its build recipe.
Cargo commands can fetch dependencies unless the caller requests `--offline`.
An explicit Cargo binary's directory is prepended to PATH; caller toolchain and
Cargo configuration otherwise remain in force.

DeckCraft and FigCraft have a sibling `../craft-fonts` development default in
their Cargo configuration. This parent command supplies the assembly path
without duplicating fonts under `apps/` or editing upstream layout defaults.

## Checked at the selected component revisions

All 17 workspaces passed `cargo metadata --no-deps --locked --offline` at the
initial reviewed pins. DeckCraft now consumes the public craft-web-host crate
from `libraries/craft-libs` at the parent-selected commit; initialize that sibling
component before building. Its only lockfile change is that crate source.
Its full native CI and release/browser checks are recorded in
[host-save qualification](DECKCRAFT-HOST-SAVE.md). The metadata command reads
workspace declarations; it does not resolve the
complete dependency graph, compile code, run build scripts or prove browser
support. DesignCraft's unused `designcraft-testkit` declaration and FigCraft's
unused `figcraft-tools` declaration reference missing directories. They did not
block these metadata checks; complete build qualification remains open.

The shared fonts checkout at `9ffb3a717e081a817470c5efe68fe314ca16c987`
merges the upstream Latin catalogue from
`37827adc41fd165f9a9234ac40f94dbad353aa69` while retaining the WebOS math font.
Both branches' added tests remain. The selected revision passes formatting,
Clippy with all targets/features and warnings denied, 42 workspace tests, and
its `embed` and `embed-latin` feature tests. All 66 font manifest entries match
their declared SHA-256 values and have licence files; none is an LFS pointer.
The existing 15 font payloads and the main and Chinese manifests are unchanged.
Upstream licence whitespace is retained byte-for-byte.

The prior font pin lacked the Latin manifest: DeckCraft's required generator
reported missing Inter even though the generator process returned zero. Its
`cargo::error` directive was a failure. With the selected fonts, the unchanged
generator produces three wasm faces and 57 native faces with no Cargo error.
WordCraft's unchanged generator produces byte-identical required-font input for
both wasm32 and native with the old and new font revisions, preserving its
existing math face. This input equivalence is not a new WordCraft browser test.

The following actual compiler checks pass for the selected DeckCraft source:

```sh
CRAFT_FONTS_REQUIRED=1 python3 scripts/craft_cargo.py deckcraft -- check --locked --offline -p deckcraft-fonts --target wasm32-unknown-unknown
CRAFT_FONTS_REQUIRED=1 python3 scripts/craft_cargo.py deckcraft -- check --locked --offline -p deckcraft-web --target wasm32-unknown-unknown
```

They ran with Rust 1.95, networking disabled, original source hidden, and output
outside source. The first attempt lacked cached `cpal` registry metadata; a
separate `cargo fetch --locked --target wasm32-unknown-unknown` obtained pinned
public inputs before the successful offline checks. Source and lockfiles stayed
unchanged. On a fresh machine an offline check needs those inputs populated first.

`cargo check` does not link/package the browser application or run it. DeckCraft
still needs its full browser artifact, browser launch, complete asset graph,
desktop lifecycle, durable save acknowledgement and shared-operation acceptance.
The other Craft apps also require actual builds and integration; their metadata
checks alone do not establish support.

## PdfCraft's selected browser build

Use `apps/pdfcraft/webos/build.py` and its pinned nightly for the hosted browser
build. This recipe checks exact source pins; the generic `craft_cargo.py` helper
above does not select each app's accepted browser font/translation version.
PdfCraft's build must use the following clean inputs:

| Input | Required source |
|---|---|
| Fonts | `e5f6cc5577fab9534095a6dfe2d409b2d9f72b1d`, declared in `apps/pdfcraft/webos/craft-fonts.rev` |
| Translations | `866aff71dd63d8369eb100b9c432b5af1400c22a`, declared in `apps/pdfcraft/craft-i18n.rev` |
| OCR models | The two exact files/hashes, licence texts and generated attribution declared in PdfCraft's `ATTRIBUTION.toml`; prepare with its `cargo xtask models DIRECTORY` and verify before packaging |

Both exact source commits are preserved in the existing verified local bare
origins under these tags, without changing the parent-selected shared checkouts:

- `webos-input-pdfcraft-fonts-e5f6cc55` in `craft-fonts.git`.
- `webos-input-pdfcraft-i18n-866aff71` in `craft-i18n.git`.

For another clean assembly, explicitly fetch these input tags from its verified
origin when needed, then create clean detached input worktrees outside source.
Do not switch the shared working checkouts to PdfCraft's pins and thereby change
WordCraft's inputs. For example, after choosing a new external input directory:

```sh
git -C assets/craft-fonts fetch origin tag webos-input-pdfcraft-fonts-e5f6cc55
git -C assets/craft-i18n fetch origin tag webos-input-pdfcraft-i18n-866aff71
git -C assets/craft-fonts worktree add --detach "$CRAFT_INPUTS/craft-fonts" e5f6cc5577fab9534095a6dfe2d409b2d9f72b1d
git -C assets/craft-i18n worktree add --detach "$CRAFT_INPUTS/craft-i18n" 866aff71dd63d8369eb100b9c432b5af1400c22a
```

These are required versioned source/runtime inputs, not intermediate compiler
builds. The accepted release was built offline with the original KSU.CODES path
hidden. Its actual selected source, complete asset hashes and qualification are
in [the PdfCraft report](../deploy/PDFCRAFT.md); do not infer that another Craft
app is qualified by this recipe.

## Local input audit, November 2026

The [Craft matrix](CRAFT-INTEGRATION-MATRIX.md) links each source workspace.
All 17 locked Rust dependency graphs passed
`cargo fetch --locked --offline --target wasm32-unknown-unknown` on the laptop
after recovering missing public dependencies for 13 workspaces. The check uses
the active GridCraft and DeckCraft integration trees and each other app's
selected checkout. The lockfile hashes stayed the same.

| Input | Local location and verification |
|---|---|
| Cargo dependency sources | `../.webos-migration/run-20261114-02/toolchain/cargo/` relative to the parent checkout. Select it with `CARGO_HOME`. |
| Office build toolchain | `../.webos-migration/run-20261114-02/toolchain/rustup/`, with the `nightly-2026-11-16` Rust toolchain and `wasm32-unknown-unknown` target. Select it with `RUSTUP_HOME`. |
| SolidCraft toolchain | The same SDK has SolidCraft's exact Rust 1.99.1 pin with Clippy, rustfmt and the `wasm32-unknown-unknown` target. SolidCraft's locked WASM dependencies also resolve offline with this compiler. |
| WASM packaging CLI | Sixteen locks select `wasm-bindgen` 0.2.129. The existing CLI is under `../.webos-migration/run-20261114-04/wordcraft-development-cache-r1/tools/trunk/wasm-bindgen-0.2.129/`. MaterialCraft selects 0.2.130. Its verified CLI and SHA-256 receipt are under `wasm-bindgen-0.2.130/` in the private round directory below. |
| Shared fonts | `assets/craft-fonts/` and its local bare origin contain both `e5f6cc5577fab9534095a6dfe2d409b2d9f72b1d` (WordCraft, PdfCraft, GridCraft) and `9ffb3a717e081a817470c5efe68fe314ca16c987` (DeckCraft). Each browser recipe selects its own revision. |
| Shared translations | `assets/craft-i18n/` and its local bare origin contain `e56d26244bbac099bfd42e23fb12f78a4be418a7` (WordCraft, PhotoCraft), `866aff71dd63d8369eb100b9c432b5af1400c22a` (PdfCraft) and `3cb11a36a58c5eabfd3a768448b55fdf086885bf` (TextureCraft). |
| PdfCraft OCR models and notices | `../.webos-migration/pdfcraft-nightly-20261117-7barkpzk/build-inputs/models/`. Both OCR models match the hashes in PdfCraft's `ATTRIBUTION.toml`. |
| DeckCraft native test SDK | `alsa-sdk/sysroot/` inside the private round directory. The extracted `libasound2-dev` package matches the installed ALSA runtime and its package-index checksum. It supplies the header and pkg-config files needed for the full Linux test suite. |
| Locked WebOS assembly inputs | `python3 scripts/verify_artifacts.py --inputs-only` verified 87 files totaling 87,172,057 bytes. |

The private round directory is
`../.webos-migration/craft-office-20261117T234813Z-8a43bc/` relative to
the parent checkout. `craft-input-audit.json` records all app revisions and
lock hashes. `craft-input-population.jsonl` records the fetch and offline
recheck results for the 13 populated workspaces.

The parent-selected and current checkout commits for all 124 components
are present in their independent local bare origins.
`local-source-recoverability.json` records that check. The Runtime and
Desktop integration branch tips also have local refs there.

Rechecking the current assembly at parent `116d7c9ff946` verified that all
124 selected commits have matching trees in the local bare origins and that
all 6,230 locked asset and reference files still match their expected bytes.
The 17 Craft checkouts have every tracked path and their `Cargo.lock` hashes
match the dependency audit. All 17 resolve
and fetch locked sources offline for both `wasm32-unknown-unknown` and
`x86_64-unknown-linux-gnu`. The Linux additions use the same shared Cargo cache.
Full offline metadata included the browser crates for DesignCraft, FigCraft
and PhotoCraft. Neither missing path declaration (`designcraft-testkit` or
`figcraft-tools`) participates in the resolved graph. See
`craft-current-linux-wasm-resolution.json` and
`craft-three-workspace-resolution.json` in the private round directory.
`source-build-input-recheck.json` records the current parent, child commits,
lock hashes and asset verification.

The current disk audit rechecked the 124 component trees against their local
bare origins and hashed all 6,230 locked artifact files. Every tracked path
in the 17 Craft checkouts was present. Each organized checkout passed locked,
offline Cargo fetch for Linux and browser WASM, using SolidCraft's exact
toolchain for that app. See `current-disk-assembly-audit.json` in the private
round directory for the selected commits and lock hashes. Per-app build
scripts, generated assets and browser workflows still need qualification.

### AniCraft and LightCraft build preflight

Full locked and offline metadata for `wasm32-unknown-unknown` resolved at the
selected pins. AniCraft `4e2a2af303d8` resolved 334 packages and selected the
root `anicraft` target. LightCraft `09a3d20bd722` resolved 372 packages and
included `lightcraft-web`. The original lock hashes matched after both checks.
The private receipt is `next-graphics-inputs-20261118.json`.

Both upstream release workflows pin Craft Fonts at `b076417b5880`, which is
present in the organized local fonts repository. AniCraft's web build writes
under its checkout and generates the guide with the native CLI. Run it from
an isolated integration checkout. LightCraft's `cargo xtask web` publishes
the module worker and a separately licensed Chinese font from the pinned
manifest. Include those while qualifying the browser build.

The November 18 recheck at parent `2653ac7d7eb7` verified 36,575 tracked
paths in the 17 Craft checkouts and repeated the locked offline Linux and
WASM dependency fetches. All 124 component trees match their local bare
origins. The 6,230 hash-verified artifact files include 6,143 historical
reference files, 70 inputs declared in the committed lock and 17 additional
inputs recorded in the preserved working copy of that lock. The audit left
the working copy as found. All explicit font and translation revisions
resolve in their local origins. The 14 tracked Trunk recipes have their
HTML entrypoints, and all 17 statically declared copy inputs are present.

VectorCraft's upstream release recipe pins fonts at `b076417b5880`. All
three startup faces and their license files were verified at that revision.
The same pin omits 30 optional background faces listed by VectorCraft.
Its build script reports those omissions as warnings and excludes the
faces from the generated web font table. The browser package and actual
font requests still need qualification. TextureCraft and MaterialCraft
intentionally vendor only the Phosphor icon variants used by their apps.

PhotoCraft's browser entrypoints and sharded packaging script are in its own
repository under `apps/photocraft/`. The exact translation pin matches
`assets/craft-i18n`. Trunk 0.21.14 is in the shared SDK and its Binaryen optimizer is at
`../.webos-migration/run-20261114-04/build-tool-cache/trunk/wasm-opt-version_123/bin/wasm-opt`.
The browser and boot crates pass an offline WASM compiler check with HEIF.
The R730 build workspace also has the four additional pinned Git dependency
trees, the translation catalogue, Binaryen version 123 and a checksum-verified
portable Trunk 0.21.14. The laptop's Trunk binary requires a newer glibc than
the builder has. The official portable release passes its version check on
R730. The linked browser package at `e83591e0612a`, with the generated
eframe snippet copied by packaging commit `7876cdf484ae`, passed the signed
loopback account checks described in the [integration log](CRAFT-INTEGRATION-LOG.md#photocraft-signed-account-workflow).
See `photocraft-r730-inputs.json` in the private round directory and the
[Trunk release](https://github.com/trunk-rs/trunk/releases/tag/v0.21.14).

The static source check found no unresolved Git LFS pointers or dangling
tracked symlinks in the 17 Craft trees. GridCraft and DeckCraft each have
eight deliberate branding-file removals on their integration branches.
PdfCraft's vendored libraries omit fixtures for their standalone tests
and examples. TextureCraft and MaterialCraft's vendored Phosphor crates
contain their selected fonts and omit the unused Thin, Light and Bold
variants. The static check lists these in
`craft-static-source-inputs.json`; the browser builds still need to
exercise their selected asset graphs.

The offline check covers locked Cargo sources. Compiler and packaging
checks still need to exercise app-specific inputs such as generated assets,
media and worker packaging.
Build outputs belong outside the source repositories. See the
[WebOS-wide source matrix](APP-MATRIX.md) for older non-Craft rebuild gaps.
