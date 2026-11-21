# Tabletop Bot Arena

Start practice, use a toy-robot action, drive briefly and pause.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed with incorrect cooldown message | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed with incorrect cooldown message | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed with incorrect cooldown message | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Passed with incorrect cooldown message | [4k](4k.png) |

One press deducted energy at each size and immediately displayed a cooldown message. The round still accepted drive and pause. The maximized canvas measured 1,560 pixels high at 1080p and 3,480 pixels high at 4K, placing controls below the viewport.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical-device input and performance remain to be checked.
