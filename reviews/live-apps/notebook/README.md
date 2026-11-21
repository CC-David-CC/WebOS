# Python Notebook (JupyterLite + Pyodide)

Edit a Python cell, run it, and save the .ipynb with its computed output.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed after collapsing the sidebar through the app API. | [phone](phone.png), [Initial phone layout](phone-before.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed through the app picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The phone initially left its Jupyter file sidebar open in a 320-pixel iframe. The code editor extended beyond the frame and its center landed under the WebOS app rail. The compact controls were absent. The test used Jupyter’s shell API to collapse the sidebar, then tapped the cell, entered code, ran it, and saved output. The desktop opened the exact phone file from the notebook picker, verified the saved output, ran an edited cell and saved its new result. Files sent the .ipynb to CodeMirror. Tablet and 4K completed the task without the sidebar workaround.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. The test emulated touch and used Playwright key input for editing. The physical phone keyboard, fully touch-driven editing, and widgets remain unverified.
