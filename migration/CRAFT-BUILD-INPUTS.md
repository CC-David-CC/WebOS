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

All 17 workspaces passed `cargo metadata --no-deps --locked --offline`, with
unchanged lockfiles. This reads workspace declarations; it does not resolve the
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
