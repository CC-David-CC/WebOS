# Marble Works

Rotate and place one track piece, release the marble and return to Edit track.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The clock advanced and the piece remained in place after returning to editing. The phone stacks the track and controls. The canvas stays 620 × 620 CSS pixels on both desktop and 4K.

Tested in Chromium using a disposable account on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical-device input and performance remain to be checked.
