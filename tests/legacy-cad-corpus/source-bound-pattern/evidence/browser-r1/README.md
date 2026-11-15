# Preserved first browser-only followup: wrong physical-module expectation

This run accepted all17 recipe commands wholly inside the actual served browser
module using its default real registry. The test then incorrectly required a
separate `/examples/source-bound-pattern.mjs` resource URL. The actual app-builder
compiles that input into outer `index.mjs`; its source marker, exported function
and pinned215627-byte outer bundle are present. The original failure stays FAIL;
its later native measurement/Save oracles were not reached. No product changed.
The corrected driver verifies the real outer bundle bytes and compiled export,
records the input source hash separately (not as byte-identical compiled output),
and writes the17-command trace before subsequent checks. Native geometry and
saved-intent oracles remain unchanged. Own context/targets cleanup passed.
`driver.before.mjs` is the exact failed test source, retained for hash audit;
its relative imports reflect the original test directory, not this evidence path.
