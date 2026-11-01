# Fill in from the real repository before implementation

This is a review worksheet, not a request to expand the desktop API.

| Binding | What the integrator must record | Current status |
|---|---|---|
| Loader/registration | Existing app discovery path and build output convention | unbound |
| DOM helper | Actual host.ui.make signature and ownership expectations | user supplied; implementation uninspected |
| Focus | Existing app-active notifications or scoped DOM focus approach | unbound |
| Visibility | Existing minimize/hide notification; do not infer occlusion from page visibility | unbound |
| Disposal | Close callback ordering and any existing host abort signal | unbound |
| Files | Authorized open/read/write/save-as and conflict semantics | unbound |
| Mobile shell | Window dimensions, safe areas and native close behavior | unbound |
| Asset serving | Base path, MIME, caching, CSP, worker/WASM support | unbound |
| XR permissions | HTTPS and current Permissions-Policy; actual supported sessions/features | unbound |
| Engines | Exact dependency/asset version and lock hashes | unbound |
| Rive authorship | Available authorized authoring tool and verified asset contract | unbound |
| Test devices | Desktop, Android phone and Galaxy XR exact browser/build | unbound |

Review cost is expected. Do not guess a service name and then change the desktop to match it. When a host capability is absent, implement the smallest app-local standard-browser behavior that preserves the user goal, or report the exact blocker. Do not silently drop phone/XR/Rive/save requirements.
