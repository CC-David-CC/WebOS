# Fabrication projects in Files

Verified on ksu.codes in viewer `8670315110a000ae578b6cef32e5c582c9a533c8e06786e580de8ca9f76b5c03`. Files opens `.kiri` in Fabrication Studio and `.meshproj` in Mesh Editor.

| App | Anon | Signed in |
|---|---|---|
| Fabrication Studio (Kiri:Moto) | [Reopened workspace](kiri-moto-anon-native.png) | [Reopened workspace](kiri-moto-signed-native.png) |
| Mesh Editor (Mesh:Tool) | [Reopened workspace](mesh-tool-anon-native.png) | [Reopened workspace](mesh-tool-signed-native.png) |

All four Chromium tests opened the app from 3D Printing, added a cube with the native File menu, saved the workspace to Documents, closed the original session or window, and opened the saved copy through Files. The native model dimensions and file SHA-256 matched. Each reopened editor accepted a second cube. Each test saved that edit to a separate project and verified that the original bytes stayed intact. Signed-in tests synced and signed in again from a fresh browser context. Anon made zero private file requests. [Release receipt](release.json)

The deployed Grid Tools and Desktop commits were fetched independently and verified against the WebOS submodule pins. WebOS main has the previous pins at the time of this check. [WebOS release commit](https://github.com/CC-David-CC/WebOS/commit/7f607b6e69e28e9b012424f0a1974339cce257f5)

The compact Kiri:Moto menu and Mesh:Tool canvas each have a separate open row. On a physical phone, open File in Kiri:Moto, tap the build plate to dismiss it, then slice and preview a small cube. In Mesh:Tool, open a saved project and try selecting, rotating and zooming the mesh with your finger. Please report the device and browser alongside what happened. [Fix queue](../FIX-QUEUE.md)
