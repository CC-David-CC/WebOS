# PhotoCraft

A disposable account on ksu.codes created a layered project at 1920 × 1080. The editor placed a PNG as a smart object, saved the project, and independently verified the revision from Files. Three fresh browser sessions opened the same project from the account. The phone and tablet used emulated touch to launch Files and exercised the standard Files open operation. Viewing preserved the revision. At 3840 × 2160, the editor placed another layer and saved a new confirmed revision. The smart object was introduced through the native image-drop intake using a synthetic test image.

| Viewport | Observed workflow | Capture |
|---|---|---|
| Phone · 390 × 844 | Opened with the saved revision. The default properties and layers dock left a 34 CSS pixel strip of the page visible. The compact viewing task needs work. | [Phone](phone.png) |
| Tablet · 820 × 1180 | Opened with the saved revision. The entire page fit in the default view with the layers visible. | [Tablet](tablet.png) |
| Desktop · 1920 × 1080 | Created, edited, saved and reopened the layered project. | [Desktop](desktop.png) |
| 4K · 3840 × 2160 | Reopened, added another layer and verified the saved revision. | [4K](4k.png) |

Chromium used device scale 1 and software rendering. The screenshots show the default WebOS window on each viewport. Mobile editing, pinch zoom and physical hardware still need verification. The test ran against viewer release `8d93a81d687eb85f012d0dde801c2a27a69e3d7adc49bae91a4c69c790f91be3` and PhotoCraft `84acebca30a09c66ee578e203bf808d1ad29835b`. A request for an optional font manifest returned 404. The tested project rendered with the bundled interface and images.
