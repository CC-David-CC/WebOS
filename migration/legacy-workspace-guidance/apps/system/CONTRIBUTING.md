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
