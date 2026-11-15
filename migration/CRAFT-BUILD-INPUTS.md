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

The shared fonts checkout at `e5f6cc5577fab9534095a6dfe2d409b2d9f72b1d`
contains 15 manifest entries whose payload SHA-256 values match and whose
declared licence files exist. None is an unmaterialized LFS pointer. This checks
the present manifests, not every possible font a consumer needs.

There is a confirmed compatibility gap with the selected DeckCraft source:
`fonts/latin-manifest.txt` is absent, so its required font generator reports
missing Inter Regular/Bold (or Variable) for both wasm32 and native inputs.
The unchanged generator was compiled directly with Rust 1.95 and run with
network disabled and the original workspace hidden. Optional mode generated
one wasm face and 14 native faces; required mode emitted `cargo::error` and no
faces. The generator process itself returns zero, so its Cargo error directive
must be treated as failure. This is a build-input check, not a full Cargo build
or a browser test. Suppressing required fonts is not a fix.

Next: review a compatible shared-font revision and payload/licence provenance,
then build affected consumers before promoting that asset pin. Other Craft
apps still need their full assets, browser build and desktop/file integration.
