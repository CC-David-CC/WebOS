# Snake Garden

Resume and steer up with the direction pad. Read the rendered head position to verify it moved up, then pause.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1920 × 1080 | Mouse | Passed | [desktop](desktop.png) |
| 3840 × 2160 | Mouse | Passed | [4k](4k.png) |

The board stayed 560 CSS pixels wide at both 1080p and 4K. At 4K, the direction pad is separated from the board by a large area.

A disposable account ran the workflow in Chromium at device scale 1 against ksu.codes release `8d93a81d687eb85f012d0dde801c2a27a69e3d7adc49bae91a4c69c790f91be3`. Physical-device input and performance remain unverified.
