# Combined alias retest — scoped PASS

This isolated retest rebuilds CAD source
`282c0f5ec9709c6ecdbc4f497ebbcce951616442`, including the independently reviewed
function-aware substitution fix, exact reader, Scene disposal and AxisSymmetry.
Native kernel defaults and prerequisites remain unchanged.

| Actual source-matched check | Result |
|---|---|
| Core public AxisSymmetry corpus | PASS150/150 positive-page Workers terminated;17 genuine-output/lifetime controls |
| Signed desktop AxisSymmetry workflow | PASS16 rows, including normal Save/sync, account404 denial and fresh Files reopen |
| TypeScript no emit and fresh sketch/project/semantic/app builds | PASS |

`runtime-pins.json` binds the exact source/build assets and removed copied
stale files. `core-receipt.json`, `signed-receipt.json`, raw logs and `pins.json`
bind the actual runs. No failures occurred in this retest. The earlier20403
inspection-budget harness failure remains in the parent directory's evidence;
this retest reused the corrected serial capture without changing assertions.

It owns only this new directory. The existing signed Axis test/helper/lifecycle
code is reused with import depth, test source label and isolated port20404
adjusted. Existing tests and fixture20403 remain unchanged. Synthetic accounts
and keys must be created in the new fixture; no prior account state is copied.

R730 runtime: `/mnt/data10tb/codi-cad-combined-axis-alias-20261106-r2`.
Direct core fixture: `http://127.0.0.1:20648/`.
Signed fixture: `http://127.0.0.1:20404/`.
Runtime pins are generated from freshly compiled ordinary app entries and
all three production Workers. Only copied, unreferenced old Workers/private
helper files may be removed from this new dist. No shared cache is overwritten.

The freshly emitted app is SHA256
`c8b5e10f3f9dbbe4b123606f96291a098610a4f711d3acad749953e711d1d0a5`.
The new sketch Worker is SHA256
`c7b435b2360c521d279d4f6bfacf761365c84934b2e9f0d3e8c5e3ee4593297b`;
the project Worker is SHA256
`7236c461672b662cf9d860439c99a3962784012f88245c248a771158f7287286`.
Semantic Worker SHA remains
`6e23b9cb4d35d37f20271ccc6efbbd00bfd940837d75d0f2b2b4fbe9f020df0f`.
The copied old `sketch-solver.cdcd797902e88e23b4a6.js` and
`project-validator.4e6eefb39455fd9062b4.js` were removed from this NEW dist only.
Both normal app entries were checked for current refs and no `webosTest`.

Run the exact CAD source's `test/headless-axis-symmetry/browser.cjs` and its
existing fault helper first, then the actual signed16-row workflow in this
directory. Public commands author all geometry; native/model access is a
read-only oracle. Independent reflected coordinates, live-axis dimensions,
duplicate/no-op, refusals, exact travel, genuine Open/Close cancellation,
normal My files Save/sync, foreign-account denial and fresh Files reopen remain
the required assertions. Asset SHA checks preceded signed authoring and fresh
reopen. The native saved document contains exactly the intended two symmetry
rows plus live-axis X0/Y10 requirements. No native/formula authoring seed,
private geometry writer or fabricated successful Worker result was used.

## Build and test reproduction

Create a fresh CAD checkout at the exact source above. Copy reviewed native
prerequisites from `/mnt/data10tb/codi-cad-combined-axis-20261106-r1/.build` and
its dist into the NEW worktree using plain copies. Reuse its locked dependencies
as read-only inputs. With R730 Node
`/mnt/data10tb/codi-3mf-qualification-SrUmue/node/bin/node`, run in order:

```sh
node node_modules/typescript/bin/tsc --noEmit
node node_modules/webpack/bin/webpack.js --config build/webpack.headless-sketch-worker.cjs
node node_modules/webpack/bin/webpack.js --config test/headless-line-relations/webpack.project.cjs
node node_modules/webpack/bin/webpack.js --config build/webpack.prism-semantic-worker.cjs
cp modules/workbenches/modeler/features/extrude/rectangleProfileRequest.mjs .build/prism-assets/rectangleProfileRequest.mjs
node node_modules/webpack/bin/webpack.js --config test/combined-axis/webpack.app.cjs
```

The project wrapper emits inside this worktree, avoiding shared dependency-cache
writes. The ordinary app wrapper enables the reviewed numeric/Manifold inputs
and excludes the private helper entry. Preserve all currently referenced
Workers; prune only unreferenced copied Workers from this NEW dist.

Serve using `test/enclosure-history/serve-craft-detach-fixture.py` with
`--root dist --port 20648`, and forward that private
loopback port. Run the exact source's Axis browser test with private URL/CDP,
`CODI_SOURCE` and receipt paths. The actual local driver files were byte copies
of that exact CAD source; their hashes are in `pins.json`. Another machine can
run directly from its CAD checkout after installing the locked test dependencies.

The signed adapter source is desktop10910b2d6 plus this new test directory,
with unchanged host code matching adapter708deffa5. R730 source is
`/mnt/data10tb/codi-axis-alias-signed-desktop-20261106`; catalog is
`/mnt/data10tb/codi-axis-alias-signed-apps-20261106`; fresh private state is
`/mnt/data10tb/codi-axis-alias-signed-tmp-20261106`. Reuse code/dependencies only;
never copy the older fixture's account/key state.

Stage this new dist using the already-qualified parent directory's explicit
asset inventory procedure. Retain the native Manifold receipt only after its
raw JS/WASM hashes match. Build a new jsketcher app catalog, adding unchanged
canonical Files/Text bundles. `fixture-catalog.json` records every asset and
`pins.json` binds its catalog/bundle hashes. No new kernel profile is claimed.

Start a fresh strict-CSP signed fixture with the same gateway/SDK/Caddy code
paths documented in the parent directory, using NEW port20404 and NEW TMPDIR.
Run this directory's `signed.test.mjs` with private URL/CDP and mandatory exact
app/sketch/project SHA variables. Test-account cookies stay only in memory.
The test closes only its own browser contexts and disconnects from shared CDP.

Raw build/core/signed logs and receipts are also retained at
`/mnt/data10tb/codi-axis-alias-evidence-20261106`. Fixtures20403 and20404 are
separate and retained unchanged. No source packaging, source promotion or
public deployment occurred. This is the requested bounded regression after the
substitution correction; overall CAD1 and unrelated engine/UI gates remain open.
