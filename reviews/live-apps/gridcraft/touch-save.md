# GridCraft touch Save

On a 390 × 844 phone, the previous toolbar drew the Save icon on top of the theme button. Tapping the icon switched the workbook to dark mode and left the workbook unsaved. The compact toolbar now has a labeled Save button. AutoSave, More and the theme switch have separate positions. Undo and Redo are available in More. Wider windows keep the full toolbar.

| Live workflow | Result |
|---|---|
| Phone, Anon and signed in | Entered `=7*6` in A1, tapped Save, named an XLSX workbook and verified its stored formula. The theme stayed put. Tapping the separate theme control switched it without opening Save. |
| Files | Reopened the saved XLSX from Files, read 42, replaced the formula with `=9*6`, saved again, and confirmed the new workbook revision stored the new formula. Signed-in sessions reopened from a fresh browser context. |
| Other sizes | Repeated the native workbook edit, save and Files reopen on an 820-pixel tablet, 1080p desktop and 4K desktop. |
| Browser-local storage | The Anon tests completed with zero requests to private user files. |

The tests used Chromium with emulated touch. On a physical phone, tap Office → GridCraft, enter a formula, tap Save, and reopen the workbook from Files. Tap the theme control separately to confirm its hit area on your device.

Both source pins were fetched independently from GitHub release branches and verified in the parent tree. At the time of review, WebOS main still pinned GridCraft at `fd80ce897bce`. The deployed release uses `webos/compact-touch-save` through the WebOS `release/gridcraft-compact-touch` branch.

[Before](touch-save-before.png) · [Phone](touch-save-phone.png) · [Desktop](touch-save-desktop.png) · [Release checks](touch-save-receipt.json) · [GridCraft source](https://github.com/CC-David-CC/gridcraft/commit/757b11dce199db8b953363ad847cf45a36cd2687) · [WebOS release](https://github.com/CC-David-CC/WebOS/commit/90117b1714c73ab1993919c4edfe8af2669d99ff)
