# Sky Courier

Resume the flight, toggle firing, confirm route progress advances and pause.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The phone needs scrolling between the scene and its firing controls. On 4K the actual game canvas stays about 327 × 491 pixels and the surrounding stage grows substantially.

Tested in Chromium using a disposable account on ksu.codes release `8d93a81d687eb85f012d0dde801c2a27a69e3d7adc49bae91a4c69c790f91be3`. Physical-device input and performance remain to be checked.
