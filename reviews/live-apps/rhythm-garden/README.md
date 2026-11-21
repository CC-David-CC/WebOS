# Rhythm Garden

Start a phrase, tap a lane to receive a timing judgment, then pause.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1920 × 1080 | Mouse | Passed | [desktop](desktop.png) |
| 3840 × 2160 | Mouse | Passed | [4k](4k.png) |

On the 4K check the playfield reached about 3,054 CSS pixels tall, exceeding the 2,160-pixel viewport. The desktop field also exceeded its viewport height.

A disposable account ran the workflow in Chromium at device scale 1 against ksu.codes release `8d93a81d687eb85f012d0dde801c2a27a69e3d7adc49bae91a4c69c790f91be3`. Physical-device behavior remains unverified.
