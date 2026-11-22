# SketchCraft touch modeling

On a phone or tablet, SketchCraft gives the 3D view the full app width. Tap Browser, Inspector or Workspace in the header to open that panel. Laptop and desktop layouts keep their side panels. The rectangle tool now uses the second tap to locate its opposite corner even when the pointer never moves between taps.

Each check launched SketchCraft from CAD, drew a rectangle, applied Push / Pull at exactly three meters, and used File → Save. Each saved project had six editable faces. Files reopened it byte-for-byte and showed six faces in the Inspector. Adding another rectangle and saving again produced a seven-face native project. Both signed-in tests reopened from a separate browser context. Anon used browser storage exclusively for the project.

| Viewport | Session | Canvas in CSS pixels | Measured height | Faces after the next edit |
|---|---|---:|---:|---:|
| phone | anon | 336 × 656 | 3 m | 7 |
| phone | signed | 336 × 674 | 3 m | 7 |
| tablet | anon | 766 × 992 | 3 m | 7 |
| desktop | anon | 1326 × 909 | 3 m | 7 |
| 4k | signed | 3246 × 2004 | 3 m | 7 |

The earlier 390-pixel phone left zero horizontal pixels for the 3D scene. The 820-pixel tablet left 246. This release also passed the editor's 282 JavaScript tests. The native Rust/WebAssembly engine matches the previous qualified release. The SketchCraft interface and pointer handling were built from the published source.

The physical phone check remains open. Under CAD → SketchCraft, tap two corners with the Rectangle tool, tap Push / Pull and the face, then enter 3m using the on-screen keyboard. Check that Save and reopen through Files preserve the solid.

Production viewer `b13979e5071d` uses WebOS branch `release/sketchcraft-compact-solid` and component branch `webos/compact-touch-solid`. At verification WebOS main still pinned SketchCraft at f40e10b06079.

[Phone](compact-phone.png) · [Tablet](compact-tablet.png) · [1080p](compact-desktop.png) · [4K](compact-4k.png) · [Verification data](compact-solid.json) · [SketchCraft source](https://github.com/CC-David-CC/sketchcraft/commit/4f20b296ee65685f230a2ed375e1eeacb0bf3253) · [WebOS source](https://github.com/CC-David-CC/WebOS/commit/900bf8a5ae71908343c8c73c345b3ab753f90557)
