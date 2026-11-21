# MaterialCraft

Import a bitmap, add a Blend node and save the editable graph with its embedded original.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Imported, added Blend and saved both nodes. The default graph view showed neither node, even with the cooked red bitmap visible in the 2D panel. | [Phone](phone.png) |
| 820 × 1,180 | Emulated touch | Imported, added Blend and saved both nodes. The graph showed the Bitmap node and connection, with the Blend node beyond its right edge. | [Tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Reopened the exact phone file through Files and saved a three-node copy. The original graph and embedded bitmap remained intact. | [1080p](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Imported, added Blend, viewed its connected red output and saved the two-node graph. | [4K](4k.png) |

Every archive contained the byte-identical PNG and the expected number of editable nodes in `package.sbs`. The phone and tablet used the visible device picker, Blend and Save buttons. A fresh desktop opened the exact phone revision and saved a copy. Focus the graph on compact launch and verify node manipulation and wiring on physical touch hardware.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
