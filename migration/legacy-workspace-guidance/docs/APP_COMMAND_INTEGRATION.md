# Application commands and new editor integration

A first in-page prototype exists in source for Calculator; a remote-agent interface and adapters for the other apps do not yet exist. The desktop's existing application host, per-window lifecycle and signed-in My files service remain the integration boundary. A command adapter for an app should advertise the operations that app actually supports, accept structured inputs, return structured success or failure, and act only within the invoking user's authorization and selected app instance. Adapters must handle cancellation and window closure, avoid converting arbitrary documents into shell commands, and use file versions/conflict handling already provided by the desktop. Agent invocation requires a separately reviewed transport and authorization; a browser-side API alone does not grant an external agent access. Do not advertise commands that are not implemented and tested.

Candidate work, not yet integrated or live:

- **FreeCAD-Web:** browser WebAssembly port of FreeCAD; assess browser support, asset size, licensing/source distribution, window cleanup and My files bridging before adding it. Preserve its own runtime.
- **Graphite:** browser 2D vector/raster editor; review its document API, third-party connections, source/license and desktop file integration.
- **SolidCraft:** browser parametric CAD with a documented browser command API; its native MCP server is a separate executable and does not automatically connect to browser sessions. Verify the web API, per-user sessions and save/reopen before exposing commands.
- **OpenZCAD:** browser parametric CAD with command history and B-rep kernel. Assess offline project format and isolate/remove optional provider integrations before connecting My files.
- **OpenGPEX:** browser image editor with WebGPU and plugin commands. Review GPL source distribution, browser/GPU support, startup, lifecycle and project format; leave AI provider configuration empty and its provider/cloud bridges unavailable until the user supplies an approved backend; record deferred features. Local editing and any independently supported on-device tools do not require a provider.
- **OpenGEX:** 3D scene interchange format, distinct from OpenGPEX. Review importer/exporter availability, licensing and mapping to an actual consumer; format support is not yet implemented.

The separate glTF-Transform shared tool supports a narrow browser-safe API (GLB read/write, dedup and weld). It blocks URL fetches and expects apps to supply authorized file bytes. This is not an OpenGEX importer, a standalone editor, a general texture pipeline or an agent interface.

## Calculator prototype

`window.codiDesktopCommands.list()` discovers commands for the active account’s open windows; `execute({windowId, command, args})` invokes one of them. The initial `calculate` command accepts an expression and optional angle unit, updates its calculator window, and returns the result and Ans used. It validates inputs and removes the registration when that window closes. The registry rechecks the account, window and session after asynchronous handlers finish. Local desktop and emulated-phone tests cover two windows, discovery, calculation, invalid inputs, closing and switching accounts; a unit test covers stale async results. This is an in-page JavaScript API only. It is not a remote network endpoint or an authorization boundary against scripts already executing in the same page. It is not yet deployed.
