# Python Notebook (JupyterLite + Pyodide)

## Production Files and Python verification

On November 22 the Programming menu opened the source-built browser Notebook. A fresh guest typed Python into a cell, ran it, and saved the notebook using Jupyter’s File menu. Opening that file in WebOS Files restored the editor with its output. The guest changed the expression, ran it again and saved. Python printed `42` on the first run and `91` after reopening. The browser made zero private Files requests during the guest workflow.

Creating a disposable account carried the same file into signed-in storage. The user changed the cell to `print(11 * 11)`, ran it and saved. An independent browser signed in, opened the file through Files and displayed `121`. Both signed-in browsers read identical 554-byte notebooks with SHA-256 `31d671fff11a1f16769ca10ec1e82cd5c512712ea2102e094e7caf146d8a73c6`. The deployed role test recorded zero uncaught page errors. [Signed-in notebook](files-account.png)

| Viewport | Verified interaction | Production screenshot |
|---|---|---|
| 390 × 844 | Tapped the visible cell, typed Python, tapped Run cell and used More controls to save the notebook. The editor had 324 CSS pixels of usable width. | [Phone](files-phone.png) |
| 820 × 1,180 | Tapped the cell and ran Python with keyboard input. | [Tablet](files-tablet.png) |
| 1,920 × 1,080 | Edited and ran Python using the desktop controls. | [Desktop](files-desktop.png) |
| 3,840 × 2,160 | Edited and ran Python with 3,436 CSS pixels of editor width. | [4K](files-4k.png) |

All four runs produced the expected output and had zero horizontal page overflow. Chromium emulated touch on the two smaller viewports. The physical tablet keyboard, native export/share sheet and interactive notebook widgets remain open hardware checks. Three simultaneous cold starts on a memory-constrained Surface exceeded the kernel startup timeout. A separate cold start on R730 reached the ready state in 16 seconds. Retain the loaded-device startup case for follow-up.

The hosted viewer SHA-256 is `4038d316e49e0e9715f3724cd6e9ea0563e6d8767d8f00c104e273ca09b6bb75`. Its Notebook bundle `ef4e1dc1093d4321b55f76e31b671b6b89e8f7f3c21dda4222a2746bfe0df7e9` contains 594 files, including the 592 declared runtime assets. The published WebOS release pins the new Notebook and Desktop commits. At verification, WebOS main still pinned Notebook `691c8fcd` and Desktop `d09cff32`. [WebOS release](https://github.com/CC-David-CC/WebOS/commit/a6a1530ec7ce3cf99d09196532b815a04d486e5b) · [Notebook source](https://github.com/CC-David-CC/notebook/commit/8d4b8a873d401411a61514a57fd04107375c4867) · [Desktop source](https://github.com/CC-David-CC/desktop/commit/b1f7a00ea9f8911beca97667c309cd91f7cf5db1)

The first deployment exposed an outdated hash in the server’s Jupyter Content Security Policy. We rolled that attempt back. The release operator now moves the existing Jupyter exception only between the old and new verified runtime directories. It checks the deployed document, wrapper and retired path. The desktop and wrapper retain the ordinary policy. Six Notebook reference tests and all four release policy tests passed.

The guest also saved separate .light.py and .percent.py documents, confirming the prompt about discarding output in a text copy. Both opened in Notebook through Files. The user ran a second calculation and saved the revised source in each format.

## Previous production review

Edit a Python cell, run it, and save the .ipynb with its computed output.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed after collapsing the sidebar through the app API. | [phone](phone.png), [Initial phone layout](phone-before.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed through the app picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The phone initially left its Jupyter file sidebar open in a 320-pixel iframe. The code editor extended beyond the frame and its center landed under the WebOS app rail. The compact controls were absent. The test used Jupyter’s shell API to collapse the sidebar, then tapped the cell, entered code, ran it, and saved output. The desktop opened the exact phone file from the notebook picker, verified the saved output, ran an edited cell and saved its new result. Files sent the .ipynb to CodeMirror. Tablet and 4K completed the task without the sidebar workaround.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. The test emulated touch and used Playwright key input for editing. The physical phone keyboard, fully touch-driven editing, and widgets remain unverified.
