# Lantern Leap

Open the platform game and verify that its playfield renders before starting the level.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Failed · blank playfield | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Failed · blank playfield | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Failed · blank playfield | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Failed · blank playfield | [4k](4k.png) |

The scene stayed blank for 30 seconds at every size. The canvas was present in the DOM with a 900 × 360 backing buffer and was hidden according to Chromium. The game toolbar and controls rendered. The gameplay input and save checks remain open.

Tested in Chromium using a disposable account on ksu.codes release `8d93a81d687eb85f012d0dde801c2a27a69e3d7adc49bae91a4c69c790f91be3`. Physical-device input and performance remain to be checked.
