# LightCraft

Import a PNG, change its rating and save the native catalog with its linked original.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Saved a four-star catalog and its linked original. | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Saved a four-star catalog and its linked original. | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Reopened the exact phone catalog via Files, retrieved its original, and saved a five-star rating. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Saved a four-star catalog and its linked original. | [4k](4k.png) |

The review used a synthetic file-drop event to introduce the same PNG at each size and read back the saved catalog through the signed Files context. The confirmed catalog carried the fixture’s digest and the changed rating. The desktop verified the exact phone revision and retrieved the linked original in a fresh browser. The phone header overlaps the Search Photos field. Physical file picking, touch-only rating, RAW imports and phone development controls remain open.

Tested in Chromium with a disposable account on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
