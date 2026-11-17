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
