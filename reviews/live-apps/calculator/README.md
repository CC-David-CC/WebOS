# Calculator

Choose **Apps → System Tools → Calculator**. The graphing calculator can save expressions, results and plotted functions together as a `.calc.json` session. Open the session from Files to continue editing.

| Live test | Result |
|---|---|
| Guest session | Evaluated `6*7`, plotted `x^2+37` and saved. Files reopened the graph. A second edit evaluated `12*12` and saved to the same file. There were zero private file requests. |
| Create account | The new account retained the guest file. The signed-in user evaluated `13*13` and saved the updated session. |
| Fresh sign-in | A new browser profile opened the account file through Files and restored its three graph traces. Its 1,618 bytes matched the saved SHA-256. |
| Layout | Arithmetic, plotting and workspace fit passed at 390 × 844, 820 × 1180, 1920 × 1080 and 3840 × 2160 CSS pixels. The smaller two sizes used Chromium touch emulation. Physical touch and Safari remain open. |

Viewer `3bdb5bf26626224479a36484acc01fdc86161bbcd5bb7e4ebc43f96a92fb8739`, Calculator bundle `3a0440640d2fd5016ad62e6a4b3a56c4a26f1cd23b651e95faa1e41440a0e9b9`. The source build passed 42 graphing tests, two legacy arithmetic test files and four desktop file-launch tests. [Calculator source](https://github.com/CC-David-CC/calculator/commit/552d3b0767f309aaffc5ee4d06b176c922f90869) · [Desktop source](https://github.com/CC-David-CC/desktop/commit/91b8b6ba913a314fc866e80edd0b7f8223cb8999) · [WebOS integration](https://github.com/CC-David-CC/WebOS/commit/7bc22be8003ddc91052264a15533ad8a06783d03)

[Phone](phone.png) · [Tablet](tablet.png) · [1080p](desktop.png) · [4K](4k.png)
