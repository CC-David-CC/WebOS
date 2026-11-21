# FieldCraft

Open a cantilever analysis from account Files, solve the load and mode steps, and save the editable model with its results.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Opened the exact desktop-saved account file and preserved its revision. The panels left only a strip of the model in view, and the test could not reach Solve. | [Phone](phone.png) |
| 820 × 1,180 | Emulated touch | Used the visible Solve and Save controls. The project included both computed steps. The result panels crowded the model. | [Tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Solved both steps, viewed the stress contour, and saved the native analysis. | [1080p](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Solved and saved the same model with the full-size viewport and readable results panels. | [4K](4k.png) |

Each completed solve produced the same `results.bin` checksum. The account files retained the original mesh, load and constraints. A fresh phone browser reopened the exact desktop file through Files. The open preserved the stored solver results and revision. The phone did not produce a new analysis. In a separate phone attempt, interacting with command search produced a WASM `unreachable` page error. Touch-only Solve, readable compact results and editing on a physical phone remain open.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
