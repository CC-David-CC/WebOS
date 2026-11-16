# DeckCraft Desktop and account-file integration

The selected fork has an optional WebOS Desktop view using Storage's public
UserFiles interface. The parent owns launcher/file associations and build
composition; DeckCraft owns its view, native document and account-resource
bindings. Human commands and native controls use the same editor domain.
Delegated command transport is explicitly unavailable; it cannot borrow the
human capability retained for UI controls.

## Verified behavior

A browser package built from the independent assembly clone passes actual Login,
Desktop, Files and DeckCraft tests with disposable signed server-backed accounts:

- Launch, edit and save a presentation, close it, then open it from Files.
- Close Files and continue saving from the editor.
- Open independent editor windows and discard one without changing the other.
- Retrieve saved content in a fresh browser context signed into the same account.
- Reject a stale save, retain its dirty edits and preserve the newer server file.
- Open the current server content again through Files after the conflict.

Calculator keyboard smoke and WordCraft startup also pass in the same assembled
build. There are zero page errors, external requests or guest-Linux requests.
The final screenshot was inspected. This is two browser contexts on one laptop,
not a physical second-machine acceptance test.

The app's eight required CI stages pass: 2,291 tests, zero failures and five
existing ignored. Fifteen account-domain/packaging tests pass. The parent-owned
adapter regression retains the reproduced startup-save failure: while initial
account reading was paused, the previous adapter dispatched a Storage write;
the guarded view sends failure before Storage, then completes the pending open.
These fake-Storage protocol tests remain distinct from real account acceptance.

## Build and run locally

Initialize selected submodules and provide Rust with the wasm32 target, Node and
wasm-bindgen matching Cargo.lock (currently 0.2.129). Cargo caches may be reused;
a successful cached build is not described as a cold rebuild.

```sh
python3 scripts/build_deckcraft.py --output /private/generated/deckcraft \
  --target-dir /private/cargo-target --offline
node scripts/build_development.mjs /private/generated/assembled \
  --wordcraft /private/generated/wordcraft --deckcraft /private/generated/deckcraft
```

Use explicit `--cargo`, `--wasm-bindgen` and `--node` paths when tools are outside
PATH. Output/staging destinations must be new and outside source. The command
requires clean selected DeckCraft, shared fonts and Craft core; compiles Cargo
release WASM; runs matching wasm-bindgen; preserves notices; uses the fork's
external-bootstrap packager; and records source/tool/asset commits and file
hashes in component-build.json. It neither runs wasm-opt nor claims Trunk output
equivalence. The existing server Content Security Policy is unchanged. The
parent checks exact selected source and every copied artifact digest.

The editor is enabled only when `--deckcraft` supplies its verified artifact.
Without it the existing minimum remains unchanged. Files associates named
.deckcraft/.pptx/.potx/.ppsx presentations with the enabled editor; existing Text
and WordCraft associations remain. No private module imports or source copies
are introduced into the parent.

```sh
WEBOS_TEST_OUTPUT=/private/new-test WEBOS_TEST_PYTHON=/path/to/python \
WEBOS_DECKCRAFT_SITE=/private/generated/deckcraft \
WEBOS_WORDCRAFT_SITE=/private/generated/wordcraft \
node tests/deckcraft_desktop_browser.mjs
python3 tests/test_assembly.py
python3 tests/test_deckcraft_build.py
```

The browser fixture creates only disposable local accounts/backend state and
closes its processes. It refuses a remote deployment origin. The adapter-only
regression accepts PUBLIC_ROOT RESULT_JSON ADAPTER_ROOT as command arguments.

## Remaining gates

Real Save As/export lifecycle, unknown-outcome reconciliation, authenticated
scoped agent operations, physical second-machine acceptance and broader suite
qualification remain open. Native exports are uncorrelated copies and cannot
silently become account saves. An unknown save blocks retry/close; it is never
reported as confirmed. Multiple dirty documents require native saves or explicit
reviewed discard; the view does not silently route background commands by focus.
Same-origin code is trusted, not sandboxed by Git ownership. No external Git
publication or deployment changed in this qualification.
