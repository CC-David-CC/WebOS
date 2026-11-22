# I-SUCCESS

Open **Apps → Learning → I-SUCCESS**. The browser runs the upstream Rust math curriculum with the native practice engine. Choose a grade, select a skill and check an answer. **Save as** creates a `.isuccess` document, which Files can reopen for another session.

| Production check | Result |
|---|---|
| Anon practice | Pre-K → Count up to 5. Entering 1 for three dots produced Wrong and counted one attempt. Saving in Documents and reopening the resulting file restored the same problem. The worked step filled 3. Checking again produced Correct and awarded zero unassisted points. The browser made zero private file requests. |
| Account practice | Creating an account promoted that file. The next problem accepted 5 without a hint and brought the score to one correct across two attempts. An independent fresh browser signed into the same account, reopened the saved file through Files, and read identical native bytes. |
| Compact and large screens | Anon opened and saved the selected Pre-K skill at 390 × 844 and 820 × 1180 with emulated touch, and at 1920 × 1080 and 3840 × 2160 with a mouse. Physical touchscreen certification remains open. |
| Build and pins | Rust 1.99.1 and wasm-bindgen 0.2.130. Nineteen content, engine and native-view tests passed. The normal WebOS build packaged the exact app revision. A fresh public fetch verified both Git mode 160000 pins. |
| Desktop reference suite | Eight passed. The same five stale fixture tests raise `drakonApps is not defined` on the prior Desktop commit and the release commit. |

| Artifact | Revision |
|---|---|
| [Native source and package recipe](https://github.com/CC-David-CC/i-success/tree/a2cc1582f55c33d642dbe8d7fec8b8d23678221b/apps/i-success-web) | `a2cc1582f55c33d642dbe8d7fec8b8d23678221b` |
| [Desktop menu and Files binding](https://github.com/CC-David-CC/desktop/tree/0d2d3aa1f16fc7a401707336d1c21e74ccd4c524) | `0d2d3aa1f16fc7a401707336d1c21e74ccd4c524` |
| [WebOS assembly](https://github.com/CC-David-CC/WebOS/tree/063c869823ea8a120be50fa7834f7779dae1d4c7) | `063c869823ea8a120be50fa7834f7779dae1d4c7` |
| Production viewer | `cf823755cfd9bfbd6d29fb6efa0d9e1ac8b6835ea58a9565f7eaaa60efdfdcb5` |
| Production app bundle | `ad9703d994018504dadb04785312ef2c611af3589f9cd81666a4c912ed199c40` |

At verification time, WebOS main did not have the new submodule. The published WebOS release branch and Desktop topic branch contain the integration. The app fork's main stayed at the upstream revision.

[Recorded practice](signed-practice.png) · [Phone](phone.png) · [Tablet](tablet.png) · [1080p](desktop.png) · [4K](4k.png) · [Machine-readable results](production.json)
