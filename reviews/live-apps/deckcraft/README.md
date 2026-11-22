# DeckCraft

## 22 November 2026 · Edit slides and notes on a phone

A 390 × 844 browser opened a 336-pixel DeckCraft editing window. The same slide grew from **48 × 27 to 280 × 157 pixels**. On narrow windows, tap **Slides** for thumbnails and tap a thumbnail to return to editing. Tap **Notes** to show or hide speaker notes. The two buttons are 44 logical pixels tall. The full desktop editing layout starts as before.

| Browser viewport | Editing result on ksu.codes |
|---|---|
| 390 × 844, emulated touch | Opened the slide list, selected a slide, toggled notes, entered a title and a speaker note, and saved a PPTX. Closing and reopening from Files preserved both fields. |
| 820 × 1,180, emulated touch | The slide measured 474 × 267 in a 766-pixel editor. Thumbnails remained visible alongside the slide and notes accepted text. |
| 1,920 × 1,080, mouse | The slide measured 630 × 355 in a 922-pixel editor. A fresh signed-in session reopened the phone revision and saved another speaker note. |
| 3,840 × 2,160, mouse | The slide measured 1,214 × 683 in a 1,882-pixel editor. Notes remained editable. All three wider windows retained the 236-pixel thumbnail pane. |

[Original phone layout](phone-before.png) · [Phone title and notes](phone-edit-and-notes.png) · [Thumbnails on demand](phone-slide-list.png) · [Desktop reopened from Files](desktop-reopened.png)

The Anon session made zero private Files requests. Creating an account promoted identical bytes. The signed-in phone changed the title to *Route update*. A fresh desktop login reopened the same 24,872-byte revision and saved the additional note. Independent Office Open XML checks read the slide title and notes directly from the PPTX archives. The cargo UI suite passed 538 tests, including the new compact-navigation regression. Four existing screenshot/long-soak tests were ignored. All 41 WebOS adapter tests passed.

The directly tested production viewer was `44df85457f82083dfb0cc7ba5b8a9add6a8b0ad79b0b2b904b79e5e34aca2de5`. The normal WebOS viewer reproduced the native build’s 236 payloads byte for byte. [DeckCraft source](https://github.com/CC-David-CC/deckcraft/commit/5a3c26a37576ce08b7d8943eb652b284c011c2ac) · [WebOS assembly](https://github.com/CC-David-CC/WebOS/commit/0f4275c11c0af803de5c3642ad5e8701f4b58473)

**Remaining checks.** Try text entry with a physical phone keyboard in portrait and landscape. The phone screenshot also shows the document name overlapping quick-access icons in the top row. The Save control remained usable in this test.

## Earlier review

Enter a speaker note, save the presentation to My files, then reopen the same phone revision on desktop and append to the note.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Edit and account save passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Edit and account save passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Edit and account save passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Edit and account save passed | [4k](4k.png) |

On the phone the thumbnail pane takes about 236 pixels of a 336-pixel editor. The slide itself measured 48 × 27 pixels at 5% zoom. The notes field accepted text, but the displayed slide is too small for comfortable editing.

The browser used a disposable account and a fresh context at each size. Physical-device input, software keyboard and GPU performance still need hardware testing.

Desktop release `e5ee6f304c8fc82927f0e93c49bb0982871df3320e81a76fd0b320e611e366e7`. Tested app bundle `f4e98b143687a132b83ac8233954fdd01e2dc2b6ec91966a0612cd18bedec16f`.
