# AniCraft

Draw a rectangle, extend its timeline exposure with Insert Frame and save the editable animation.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Passed with keyboard after hiding default panels. | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Passed, including the exact phone project from Files. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Passed | [4k](4k.png) |

With the default panels visible, the phone test had only 52 CSS pixels of stage width. Hide Panels (F4) and Fit Stage widened it to 256 pixels. The phone test drew with emulated touch and used keyboard shortcuts for the tool, timeline and save. The fresh desktop reopened the exact phone project through Files, preserved the original shape, added a second shape and extended the exposure from two to three frames. Physical touch, phone editing without keyboard shortcuts and playback remain open. [Phone with default panels](phone-default-panels.png)

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
