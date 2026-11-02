# Application commands and new editor integration

This is planned work, not an implemented agent interface. The desktop's existing application host, per-window lifecycle and signed-in My files service remain the integration boundary. A command adapter for an app should advertise the operations that app actually supports, accept structured inputs, return structured success or failure, and act only within the invoking user's authorization and selected app instance. Adapters must handle cancellation and window closure, avoid converting arbitrary documents into shell commands, and use file versions/conflict handling already provided by the desktop. Agent invocation requires a separately reviewed transport and authorization; a browser-side API alone does not grant an external agent access. Do not advertise commands that are not implemented and tested.

Candidate work, not yet integrated or live:

- **FreeCAD-Web:** browser WebAssembly port of FreeCAD; assess browser support, asset size, licensing/source distribution, window cleanup and My files bridging before adding it. Preserve its own runtime.
- **Graphite:** browser 2D vector/raster editor; review its document API, third-party connections, source/license and desktop file integration.
- **SolidCraft:** browser parametric CAD with a documented browser command API; its native MCP server is a separate executable and does not automatically connect to browser sessions. Verify the web API, per-user sessions and save/reopen before exposing commands.
- **OpenZCAD:** browser parametric CAD with command history and B-rep kernel. Assess offline project format and isolate/remove optional provider integrations before connecting My files.
- **OpenGPEX:** browser image editor with WebGPU and plugin commands. Review GPL source distribution, browser/GPU support, startup, lifecycle and project format; disable optional provider/cloud bridges until explicitly supported and record deferred features.
- **OpenGEX:** 3D scene interchange format, distinct from OpenGPEX. Review importer/exporter availability, licensing and mapping to an actual consumer; format support is not yet implemented.

The separate glTF-Transform shared tool supports a narrow browser-safe API (GLB read/write, dedup and weld). It blocks URL fetches and expects apps to supply authorized file bytes. This is not an OpenGEX importer, a standalone editor, a general texture pipeline or an agent interface.
