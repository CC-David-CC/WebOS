# Falling Blocks

Resume, hard-drop one piece, confirm the score increased, then pause.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1920 × 1080 | Mouse | Passed | [desktop](desktop.png) |
| 3840 × 2160 | Mouse | Passed | [4k](4k.png) |

The playfield measured about 100 × 200 CSS pixels on phone and 103 × 207 on tablet. The desktop board expanded with the window.

A disposable account ran the workflow in Chromium at device scale 1 against ksu.codes release `8d93a81d687eb85f012d0dde801c2a27a69e3d7adc49bae91a4c69c790f91be3`. Physical-device input and performance remain unverified.
