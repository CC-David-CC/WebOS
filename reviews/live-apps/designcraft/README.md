# DesignCraft

Draw a Type-tool frame, enter text, and save the editable publication.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Passed after Fit Page in Window. | [phone](phone.png), [Before Fit Page](phone-initial.png) |
| 820 × 1,180 | Emulated touch and keyboard | Passed after Fit Page in Window. | [tablet](tablet.png), [Before Fit Page](tablet-initial.png) |
| 1,920 × 1,080 | Mouse and keyboard | Passed, including the exact phone project from Files. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Passed | [4k](4k.png) |

The first phone and tablet runs showed only a sliver of the page at the bottom of the workspace. Fit Page in Window moved it into the workspace. The phone page was then about 83 CSS pixels wide and the tablet page about 186 pixels. The test created text frames with emulated touch at both sizes and confirmed the authored text in each native archive. A fresh desktop opened the exact phone publication from Files, preserved its text, added another frame and saved the revised publication.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch placement, comfortable text editing on small displays, and print output remain to be checked.
