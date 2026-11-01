# Deferred app features

Keep this list when removing or disabling third-party account or cloud-service
integrations. My files and the signed-in desktop account are the local workflow.
Do not assume an external feature works with the desktop account. These features
must remain unavailable in the student workflow until an internal, server-backed
replacement exists and has its own privacy, cost, rate-limit, abuse-control and
availability policies. Do not route requests through a user's personal
provider account or silently send their work to a third party.

The pinned StitchFoundry WebAssembly contains provider URLs and account/AI
feature text. Its locally prepared page now adds `connect-src 'self'` and
`form-action 'none'`. Local desktop and phone-sized tests verified a blocked
third-party fetch and successful editor startup; this policy does not establish
that every account or AI control has been removed, or restrict same-origin
requests. The change is not live.

A separate local StitchFoundry rebuild removes its browser provider transport and credential store and rejects eight provider/account commands. Desktop and emulated-phone tests exercised those restrictions and the local file workflow. It is not live: packaging, remaining network-surface and licensing review are outstanding. The older shipped binary is not proven to match this source revision.

This is a partial inventory. A hidden sign-in button is not proof that the
underlying feature or its network request has been removed. Before calling an
integration disabled, inspect the pinned browser app, verify that its controls
are inaccessible, and confirm it does not send work to the provider. Keep
unverified or provider-dependent features unavailable in the student workflow.

| App | Feature | Status / reason |
| --- | --- | --- |
| Circuit Simulator (CircuitJS) | Import from Dropbox | The live Circuit Simulator removes the File-menu and command-palette entries and Dropbox startup import; My files is the supported workflow. No desktop-integrated cloud import replacement exists. |
| Electronics Design (designElectronics) | Upstream AI assistant | The upstream desktop assistant uses external local CLI tools; the WebAssembly build does not enable its network-backed agent support. No desktop-integrated replacement exists. |
| Electronics Design (designElectronics) | GitHub connection, commits, and project history | The embedded account and history controls are hidden; provide integrated project history before restoring them. |
| Embroidery Studio (StitchFoundry) | Design from prompt | Upstream documentation says this uses the user's Anthropic API key. No internal replacement exists. Keep unavailable; audit the pinned browser build to confirm the entry point and provider request are blocked. |
| Embroidery Studio (StitchFoundry) | Redraw image | Upstream documentation says this uses the user's Anthropic API key. No internal replacement exists. Keep unavailable; audit the pinned browser build to confirm the entry point and provider request are blocked. |
| Embroidery Studio (StitchFoundry) | Ask about embroidery | The pinned WebAssembly contains this feature’s name and upstream help text; its interactive entry points have not been fully audited. No internal replacement exists. Keep unavailable until its interface and replacement are reviewed. |
| Embroidery Studio (StitchFoundry) | Check My Sew-out | The bundled WebAssembly contains upstream feature text; the nearby candidate source sends a design and photos for AI analysis. The actual entry points require audit and no internal replacement exists. |
| Embroidery Studio (StitchFoundry) | Foundry Account and credits | The bundled WebAssembly contains account screens and provider text. Use the desktop account; upstream account entry points require removal. |
| Embroidery Studio (StitchFoundry) | Publish to MakerFoundry; Send to StitchShop | The bundled WebAssembly contains these feature names. Their actual entry points and network behavior need review; no integrated replacement exists. |

## Replacement gate

Before restoring a deferred feature, implement and review the service behind
the desktop's existing signed-in identity, enforce per-account request and
spending limits, disclose what user data leaves the browser, and provide clear
consent and failure paths. Keep the ordinary local editor usable when the
service is unavailable. Track provider and model choices separately from the
app bundle so they can be changed without coupling every application to a
provider account. Do not expose the feature while the service or its controls
are still under development.

Add entries when an app review confirms a feature is removed, disabled, or
unavailable due to a third-party dependency. Record the exact app and feature,
what the user sees, and what is needed to restore it; do not list ordinary
local capabilities as removed without evidence.
