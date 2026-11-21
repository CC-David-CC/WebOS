# Expression Puppet

Change an expression slider, score the pose, and save it in an in-app slot.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1920 × 1080 | Mouse | Passed | [desktop](desktop.png) |
| 3840 × 2160 | Mouse | Passed | [4k](4k.png) |

The face becomes wide and flattened at 4K. On the phone the face fills the initial window and the sliders require scrolling.

A disposable account ran the workflow in Chromium at device scale 1 against ksu.codes release `8d93a81d687eb85f012d0dde801c2a27a69e3d7adc49bae91a4c69c790f91be3`. Physical-device behavior remains unverified.
