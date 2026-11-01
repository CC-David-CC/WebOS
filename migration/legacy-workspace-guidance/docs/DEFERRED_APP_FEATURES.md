# Deferred app features

Keep this list when removing or disabling third-party account or cloud-service
integrations. My files and the signed-in desktop account are the local workflow.
Do not assume an external feature works with the desktop account. These features
must remain unavailable in the student workflow until an internal, server-backed
replacement exists and has its own privacy, cost, rate-limit, abuse-control and
availability policies. Do not route requests through a user's personal
provider account or silently send their work to a third party.

This is a partial inventory. A hidden sign-in button is not proof that the
underlying feature or its network request has been removed. Before calling an
integration disabled, inspect the pinned browser app, verify that its controls
are inaccessible, and confirm it does not send work to the provider. Keep
unverified or provider-dependent features unavailable in the student workflow.

| App | Feature | Status / reason |
| --- | --- | --- |
| Electronics Design (designElectronics) | GitHub connection, commits, and project history | The embedded account and history controls are hidden; provide integrated project history before restoring them. |
| Embroidery Studio (StitchFoundry) | Design from prompt | Upstream documentation says this uses the user's Anthropic API key. No internal replacement exists. Keep unavailable; audit the pinned browser build to confirm the entry point and provider request are blocked. |
| Embroidery Studio (StitchFoundry) | Redraw image | Upstream documentation says this uses the user's Anthropic API key. No internal replacement exists. Keep unavailable; audit the pinned browser build to confirm the entry point and provider request are blocked. |
| Embroidery Studio (StitchFoundry, attribution tentative) | Ask about embroidery | Found in a separate upstream research checkout; presence in the pinned browser build is unverified. No internal replacement exists. Keep unavailable unless and until its source, network behavior and replacement are reviewed. |

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
