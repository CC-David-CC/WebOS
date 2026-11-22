# FieldCraft

Open a cantilever project from Files, tap **Solve**, and use **Analysis** to review the results. On a phone, **View** returns to the model and **Model** opens its tree. **Save** writes the editable `.fieldcraft` project with the computed results.

| Browser viewport | Verified workflow | Screenshot |
|---|---|---|
| 390 × 844, emulated touch | Opened Search and entered a query, solved the static load and mode steps, toggled the deformed shape in Analysis, saved and reopened through Files. | [Model](phone-workspace.png) · [Search](phone-search.png) · [Solved](phone.png) · [Analysis](phone-analysis.png) |
| 820 × 1,180, emulated touch | Used the full toolbar to solve both steps, save and reopen through Files. | [Tablet](tablet.png) |
| 1,920 × 1,080, mouse | Solved, saved and reopened using the full workspace. | [Desktop](desktop.png) |
| 3,840 × 2,160, mouse | Solved, saved and reopened using the full workspace. | [4K](4k.png) |

The saved files retained their original mesh, boundaries, loads and steps. In a separate phone edit, I changed the model units to inches, pounds-force and psi from command search, tapped Run, and saved. Both roles reopened their edited native file with that unit system. Every solve produced the same native solver result checksum as the earlier desktop reference, `02dba169b6eadb7bc950e3b38a9713d435d3cf465d8866a8a9bae848bc8d72f2`. Anon used Files in the same browser tab and made zero private file server requests. Signed-in phone edits reopened from account Files in a fresh desktop browser.

Before this fix, opening Search at an internal canvas width of 336 pixels crashed the browser engine. A Rust regression test now checks popup bounds at six widths including zero and a viewport with a nonzero origin. The physical phone check is still open. Tap **Search**, enter “solve” with the on-screen keyboard, close Search, and tap a face of the beam. Check that the keyboard closes and the selected face matches your touch.

The narrow Search fix is also [upstream PR #1029](https://github.com/tangency-labs/fieldcraft/pull/1029).

Verified production viewer `4bbd86251ee6473815d74053f484f5ba7d53bc0fddb1c6d15476c320a1974d4d`. The WebOS release branch pins this component at `b89311fca381752d871c2cd874128e79228b7e6b`. [FieldCraft source](https://github.com/CC-David-CC/fieldcraft/commit/b89311fca381752d871c2cd874128e79228b7e6b) · [Combined WebOS release](https://github.com/CC-David-CC/WebOS/commit/ecc15c44851996e6b9a3b5fe6f1ddf5b3d95e0b9)
