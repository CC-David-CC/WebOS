# SolidCraft

Open a native `.sc` design from account Files, apply a 2 mm edge fillet, and save the editable design.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Tapped the edge, confirmed the fillet, and saved through the visible toolbar. The model tree took most of the available canvas width. | [Phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Tapped the edge and saved the added fillet. | [Tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Reopened the exact phone revision from account Files. Rounded a second edge and saved a copy. The original phone revision kept the same SHA-256 digest. | [1080p](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Rounded an edge and saved the editable design. | [4K](4k.png) |

Every saved archive retained the original sketch and extrusion and recorded the new fillet with its selected edge and 2 mm radius. Chromium reported zero page errors. The automated test used the Fillet keyboard shortcut on all four viewports. Touch-only command access, precision selection, and viewport changes during an edit still need testing on physical devices. Curvature preview responsiveness is tracked separately in the [fix queue](../FIX-QUEUE.md).

Tested in Chromium with a disposable account on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
