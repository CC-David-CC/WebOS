# Pocket Rally

Open the race, hold Gas until the speed increases and pause.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Blank on launch. Drove after retry. | [Launch](phone.png), [Retry](phone-recovered.png) |
| 820 × 1,180 | Emulated touch | Blank on launch. Drove after retry. | [Launch](tablet.png), [Retry](tablet-recovered.png) |
| 1,920 × 1,080 | Mouse | Blank on launch. Drove after retry. | [Launch](desktop.png), [Retry](desktop-recovered.png) |
| 3,840 × 2,160 | Mouse | Blank on launch. Drove after retry. | [Launch](4k.png), [Retry](4k-recovered.png) |

The playfield stayed blank for 35 seconds on normal launch at all four sizes. A retry that let the window resize and used Resume rendered the track and completed the driving check at all four sizes. The 4K canvas briefly measured 0 × 0 before layout caught up.

Tested in Chromium using a disposable account on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical-device input and performance remain to be checked.
