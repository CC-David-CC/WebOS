# Clockwork Room

Solve the room and open its exit.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The gear, chime, pendulum and lock all registered as solved and the exit opened at all four sizes. The phone layout puts the mechanism list below the scene. At 1080p the maximized window’s 3D canvas measured 1,422 CSS pixels high.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical-device input and performance remain to be checked.
