# Geometry engine comparison

The user requested that the unified jSketcher retain both its existing OCCT
path and the newer surfacing/native BREP/mesh path, compare them, and find
flaws. This is a test plan and preliminary findings, not a claim of engine
interchangeability or manufacturing safety.

Compare the same explicitly defined inputs in Chromium with each engine,
recording the engine version, settings and tolerance. Keep source models and
results per engine. An unsupported operation is **unsupported**, not a
failed geometry result; do not silently switch engines or claim matching
accuracy. Preserve both representations in the user's My files project and
make conversion explicit and testable.

| Case | Independent checks | Current evidence |
| --- | --- | --- |
| Box 10 × 20 × 30 | Extents 10, 20, 30; volume 6,000; closed solid; repeat after save/reopen. | Newer surfacing branch's existing `BOX` modeler operation is an explicit native-engine stub. The surfacing editor has different primitives; compare only once exposed through a suitable common harness. |
| Overlapping axis-aligned boxes | Union, intersection and subtraction volumes from independent analytical box-overlap calculations; nonempty boundaries, watertightness and input preservation. | Not yet compared. |
| Circular/cylindrical geometry | Known radius/height and analytic volume; record mesh approximation tolerance and scale. | Not yet compared. |
| Closed spline extrusion | Curve endpoints, closed contour, extrusion height, volume and solid validity; compare transformed and reversed contours. | Baseline OCCT path produced a 10-unit extrusion, reported volume 7,200 and shape validity in a scripted Chromium case. The other engine has not yet been checked against the same input. |
| Tiny and large scales | Error and failure reporting at several scales; no silent disappearing geometry. | Not yet compared. |
| Disjoint, touching and degenerate inputs | Explicit result or actionable error; verify no crash, stale output or silent omission. | Not yet compared. |
| Edit, references and project recovery | Multiple windows, versioned My files save/sync/reopen; downstream references after edit/undo/redo; old project compatibility. | OCCT stable-ID research and separate local spline/history checks are partial. No combined engine persistence test yet. |
| Performance | Time, peak memory, cancellation and UI responsiveness for repeatable workloads; report device/browser. | Not yet measured. |

The upstream `surfacing-refactor` branch replaces core OCC operations with
native-path stubs in its current modeler, so a textual merge alone would remove
working behavior. Its mesh boolean code currently refers to `/manifold.wasm`,
which needs an app-owned, prefix-safe resource path and CSP qualification.
The upstream surface scene is stored separately from the existing desktop
project snapshot; it must be included and restored through the host before a
user can rely on Save. Treat all initial results as focused evidence and retain
the full validation follow-up in `JSKETCHER_UPSTREAM_WORK.md`.
