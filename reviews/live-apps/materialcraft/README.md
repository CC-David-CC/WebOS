# MaterialCraft

Import a bitmap, add a Blend node and save the editable graph with its embedded original.

The current compact graph release passed five hosted checks. [Release results and screenshots](compact-graph.md)

## Earlier review

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Imported, added Blend and saved both nodes. The default graph view showed neither node, even with the cooked red bitmap visible in the 2D panel. | [Phone](phone.png) |
| 820 × 1,180 | Emulated touch | Imported, added Blend and saved both nodes. The graph showed the Bitmap node and connection, with the Blend node beyond its right edge. | [Tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Reopened the exact phone file through Files and saved a three-node copy. The original graph and embedded bitmap remained intact. | [1080p](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Imported, added Blend, viewed its connected red output and saved the two-node graph. | [4K](4k.png) |

Every archive contained the byte-identical PNG and the expected number of editable nodes in `package.sbs`. The phone and tablet used the visible device picker, Blend and Save buttons. A fresh desktop opened the exact phone revision and saved a copy. Focus the graph on compact launch and verify node manipulation and wiring on physical touch hardware.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.

## Hosted source and anonymous reproduction

The deployed component receipt identifies commit `a0c356d2899c84279816cc23fc76bc0d8199b1bc` and tree `43716b4a0db25de318ffd34dd24248cc21c08cd8`. A fetch into an empty repository recovered that exact commit from the published branch `webos/hosted-materialcraft`. [Hosted source](https://github.com/CC-David-CC/materialcraft/tree/a0c356d2899c84279816cc23fc76bc0d8199b1bc) · [Production receipt](https://ksu.codes/materialcraft/component-build.json)

In a fresh anonymous session on viewer `44df85457f82083dfb0cc7ba5b8a9add6a8b0ad79b0b2b904b79e5e34aca2de5`, opening MaterialCraft from Materials & Textures and importing the solid red PNG reproduced the missing node. The app window was 336 CSS pixels wide. The lower 2D preview displayed the image while the editable graph showed an empty grid. Chromium reported zero page errors and the guest made zero private file requests. [Anonymous phone screenshot](baseline-anon-390.png)
