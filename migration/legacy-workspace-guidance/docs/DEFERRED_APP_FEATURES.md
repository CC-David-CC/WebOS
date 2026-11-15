# Deferred app features

Keep this list when removing or disabling third-party account or cloud-service
integrations. My files and the signed-in desktop account are the local workflow.
Do not assume an external feature works with the desktop account. These features
must remain unavailable in the student workflow until an internal, server-backed
replacement exists and has its own privacy, cost, rate-limit, abuse-control and
availability policies. Do not route requests through a user's personal
provider account or silently send their work to a third party.

The live rebuilt StitchFoundry editor uses local mode and the desktop account.
Its browser build removes the provider transport and credential store, removes
its MakerFoundry startup-link importer and blocks eight identified account or
provider commands. Its iframe policy separately restricts direct cross-origin
connections. The File bridge, local file workflow and identified command
restrictions passed local and live phone-sized checks. These checks do not prove
that every provider entry point or same-origin request has been audited; the
broader network and dependency review remains open. See
`apps/system/embroidery-studio/README.md` and `SIMPLIFIED_HANDOFF.md` for the
build and test evidence.

This is a partial inventory. A hidden sign-in button is not proof that the
underlying feature or its network request has been removed. Before calling an
integration disabled, inspect the pinned browser app, verify that its controls
are inaccessible, and confirm it does not send work to the provider. Keep
unverified or provider-dependent features unavailable in the student workflow.

| App | Feature | Status / reason |
| --- | --- | --- |
| Excalidraw | Reusable shape library, including local library creation and import/export | The unintegrated library surface is hidden because it does not use My files or account-backed persistence. In a local investigation, forcing the hidden controls visible and adding a rectangle made the same shape appear in a second window. The package uses a shared in-page state store, so a My files integration must explicitly handle multiple windows and prove account isolation and cleanup; cross-account persistence has not been tested. Restore with a reviewed account-file workflow. |
| Excalidraw | Browse or publish public shape libraries | The upstream library links to an external service. It is unavailable pending a reviewed integration and appropriate user disclosure. |
| Circuit Simulator (CircuitJS) | Import from Dropbox | The live Circuit Simulator removes the File-menu and command-palette entries and Dropbox startup import; My files is the supported workflow. No desktop-integrated cloud import replacement exists. |
| Electronics Design (designElectronics) | Upstream AI assistant | The upstream desktop assistant uses external local CLI tools; the WebAssembly build does not enable its network-backed agent support. No desktop-integrated replacement exists. |
| Electronics Design (designElectronics) | GitHub connection, commits, and project history | The embedded account and history controls are hidden; provide integrated project history before restoring them. |
| Embroidery Studio (StitchFoundry) | Open a MakerFoundry design from a startup link | The rebuilt live editor removes this importer. Desktop and phone-sized startup-link checks observed no MakerFoundry request; the iframe policy is a separate restriction. |
| Embroidery Studio (StitchFoundry) | Design from prompt | Upstream documentation says this uses an Anthropic API key. The identified browser command is blocked in the rebuilt live editor; no internal replacement exists. |
| Embroidery Studio (StitchFoundry) | Redraw image | Upstream documentation says this uses an Anthropic API key. The identified browser command is blocked in the rebuilt live editor; no internal replacement exists. |
| Embroidery Studio (StitchFoundry) | Ask about embroidery | The identified browser command is blocked in the rebuilt live editor. No internal replacement exists; other provider entry points remain under review. |
| Embroidery Studio (StitchFoundry) | Check My Sew-out and report a sew-out | Patched browser source removes the identified menu entries and blocks both command IDs. With a stitched design open, desktop and phone-sized account tests found the commands absent, rejected direct attempts with photo/send arguments, and observed no iframe requests during those attempts. No internal replacement exists; other routes remain under review. |
| Embroidery Studio (StitchFoundry) | Foundry Account and credits | The rebuilt live browser removes its provider credential store and blocks the identified account command. The pinned patched source gates the account chip on that disabled command. Direct command attempts were rejected without observed iframe requests in local desktop and phone-sized tests. Use the desktop account; other entry points remain under review. |
| Embroidery Studio (StitchFoundry) | Publish to MakerFoundry; Send to StitchShop | Patched browser source removes the identified File-menu entries and StitchShop jobs-panel button and blocks both command IDs. With a stitched design open, local desktop and phone-sized tests found the commands absent, rejected direct send attempts and observed no iframe requests during those attempts. No integrated replacement exists; other routes remain under review. |

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
