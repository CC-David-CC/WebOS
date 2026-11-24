# WebOS source project

The November 24, 2026 source catalog contains 143 app repositories and eight platform services. The ksu.codes release manifest lists 130 launchers. The catalog identifies service owners and distinguishes live applications from planned interfaces. [App and server catalog](apps/README.md) · [Component and launcher matrix](apps/CATALOG.md) · [Live release manifest](https://ksu.codes/viewer-release.json)

Organized source for future WebOS development. Start with [START-HERE.md](START-HERE.md) and the [full app/component matrix](migration/APP-MATRIX.md), sorted by category with functional priorities, source locations, interfaces and build gaps. Applications are independent Git repositories pinned by this parent.

The existing Desktop/Workspace viewer is in platform/desktop/active-system/. The unsolicited replacement implementation and its parent builder/browser harnesses are removed. This repository does not claim a currently assembled replacement website or full beta parity. Neither website is changed by source organization.

## Build the core viewer from a checkout

Use Git with Git LFS, Node.js 24, Python 3.12 or later, and Rust 1.95 with
the `wasm32-unknown-unknown` target. WordCraft also uses Trunk 0.21.14 and the
`wasm-bindgen-cli` version in its `Cargo.lock`.

```sh
git clone --recurse-submodules https://github.com/CC-David-CC/WebOS.git
cd WebOS
git submodule status --recursive
npm ci --ignore-scripts --no-audit --no-fund
(cd apps/pohoda && npm ci --ignore-scripts --no-audit --no-fund)
webos_build_dir=$(mktemp -d "${TMPDIR:-/tmp}/webos-build.XXXXXXXX")
```

Keep full submodule history. The backend packager uses the Accounts revision
`c53a2f64b287b1f59bd90cdcd355766c5d713e63`, an ancestor of the selected
Accounts commit. The WordCraft build also uses earlier shared-library revisions.

Follow the **Complete browser assets** instructions in
[WordCraft's WebOS build guide](https://github.com/CC-David-CC/wordcraft/blob/edeb4a090cd301cd7d4405e20af795007b37b69b/webos/README.md#complete-browser-assets). Use
`$webos_build_dir/wordcraft` as its site output. The Git submodules under
`assets/` provide the fonts and translations. Select the exact revisions in
`apps/wordcraft/webos/craft-fonts.rev` and `apps/wordcraft/craft-i18n.rev` in
separate detached checkouts. Prepare the two bare providers from
`libraries/egui` and `libraries/craft-libs` with every revision for their
respective upstream URLs listed in WordCraft's `Cargo.lock`. Keep the providers
and compiler cache outside the assembly.

```sh
node scripts/build_viewer.mjs \
  --output "$webos_build_dir/viewer" --wordcraft-site "$webos_build_dir/wordcraft"
python3 scripts/package_viewer_backend.py \
  --output "$webos_build_dir/backend" --archive "$webos_build_dir/backend.tar.gz"
```

The default viewer assembles Calculator, Files, Text, WordCraft, Help, Weather
and Weather Maps. Additional applications supply their own separately built
inputs through the viewer build's app-specific flags. The build receipts in the
output directories identify the component revisions and files.
