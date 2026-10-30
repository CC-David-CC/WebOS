# Building a desktop app

Place an app in `apps/system/<id>/index.mjs` and export a synchronous
`mount(host)` returning `{element, dispose()}`. The element must have the
`window-content` class. Release timers, listeners and workers on disposal;
keep per-window state on the window or in the mounted view. `host.signal` is
aborted on disposal.

Register a new app in the explicit app builder list and desktop menu. App code
is trusted same-origin code, not a sandbox. Use the shared host's account and
storage interfaces; a folder or hidden menu item is not a security boundary.
The build process bundles declared imports and hashes output. Node and npm are
build tools, not visitor requirements. Downloaded dependencies and generated
output stay outside Git.

An app may declare its own pinned `package.json` and lockfile in its folder;
run `npm ci --prefix apps/system/<id> --ignore-scripts` before building. The
builder resolves that app's `node_modules` first and bundles dependencies only
into that app. `app.json` may declare an `inject` array of app-local JavaScript
files for build-time shims. Dependency licenses are included in each bundle.

An `app.json` can also declare packaged workers and assets. A reviewed
`patches` entry may replace one exact string in an app-local dependency only
when its complete SHA-256 matches; use this sparingly and explain the reason.
The PDF viewer uses this to prohibit PDF.js's dynamic fallback worker. The
builder permits small embedded PNG/SVG CSS data URLs but rejects external URLs.
Document Editor delegates PDF preview to the independent PDF Viewer via the
host; apps communicate through host services, not each other's private state.
