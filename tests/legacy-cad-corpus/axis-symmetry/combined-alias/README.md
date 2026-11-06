# Combined alias retest — in progress

This isolated retest rebuilds CAD source
`282c0f5ec9709c6ecdbc4f497ebbcce951616442`, including the independently reviewed
function-aware substitution fix, exact reader, Scene disposal and AxisSymmetry.
Native kernel defaults and prerequisites remain unchanged.

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

Run the exact CAD source's `test/headless-axis-symmetry/browser.cjs` and its
existing fault helper first, then the actual signed16-row workflow in this
directory. Public commands author all geometry; native/model access is a
read-only oracle. Independent reflected coordinates, live-axis dimensions,
duplicate/no-op, refusals, exact travel, genuine Open/Close cancellation,
normal My files Save/sync, foreign-account denial and fresh Files reopen remain
the required assertions. Asset SHA checks precede signed authoring.

No completion claim, source promotion or public deployment is made until the
actual source-matched results and any failures are recorded here.
