# UI harness dispatch-before observation — retained failure

Frozen driver39811a3e3 on exact Desktop e2da/Coref714 phone fixture.
Untitled Save/cancel and first browser/server bytes passed. Existing-path Save
was asserted clean after checking only coordinator idle, which can be observed
before the iframe postMessage reaches the host. Immediate dirty=false failed.
This run does not establish a lost write or product defect.

Follow-up waits for inspected saved path/dirty=false and then idle. Assertions,
geometry and storage expectations remain unchanged. No product source change.
Do not relabel this failed run as qualification.
