# PdfCraft

## 22 November 2026 · Open a PDF on a phone

A narrow PdfCraft window now opens the PDF in Read mode. Tap **Read → All tools → Organize pages** to rotate a page. The fit and zoom controls are on the right. Wider windows open with the full editing panel. The startup rule applies only when the window is 540 CSS pixels wide or narrower and the native workspace would otherwise open the default All tools panel.

| Browser viewport | Actual app width | Deployed result |
|---|---:|---|
| 390 × 844, emulated touch | 336 px | Page 1 was visible on launch. Its viewport was 287 px wide. Taps switched fit mode, zoomed in and out, opened the tools and rotated the page. |
| 820 × 1,180, emulated touch | 766 px | All tools and the PDF were visible together. Fit and zoom responded to touch. |
| 1,920 × 1,080, mouse | 922 px | Full editing controls were available. A new signed-in session reopened the phone revision and saved a further rotation. |
| 3,840 × 2,160, mouse | 1,882 px | All tools and the PDF were visible together. Fit and zoom responded to the mouse. |

[Phone on open](compact-reading.png) · [Same PDF after two taps on Zoom in](compact-zoom.png) · [Page tools on demand](compact-tools.png)

Anon saved a 90° rotation, reopened the file from Documents, rotated it again and saved it at 180°. Creating an account promoted identical bytes. The signed-in phone saved a 270° rotation. A fresh desktop login reopened that revision and saved the fourth turn. An independent PDF parser confirmed every rotation. Anon made zero private Files requests. Chromium reported zero page errors. A separate test opened the illustrated *Field notes* PDF from Files and captured the two reading screenshots.

Production viewer `a8c6e33a0c9c86b60d336578727e12d4e8346b1a636ab32f3851b9bb8af31d47` served WebOS bundle `a4bda86862e573143e9a9fab0ade6f0f4d5cc5c8b9bb364f4fd35ad8bdb05c7c`. The build reused 66 verified native engine assets. Adapter tests passed 11/11 and packaging checks passed 3/3. [PdfCraft adapter](https://github.com/CC-David-CC/pdfcraft/commit/1eab1a0327a9c37372b970ebbd09c7b0c8ae56d8) · [WebOS assembly](https://github.com/CC-David-CC/WebOS/commit/9df0ed2ef4d202f7d38b77919a0a21466e963104)

**Hardware check open.** On a physical phone, open an existing PDF from Files, use fit and zoom, then rotate and save a copy with the on-screen keyboard. Check the text size and whether the controls are comfortable to tap.

## Earlier review

Use Organize pages to rotate a page, save the PDF to My files, then reopen the phone revision on desktop and verify the saved rotation before rotating and saving again.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Edit and account save passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Edit and account save passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Edit and account save passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Edit and account save passed | [4k](4k.png) |

The phone defaults to the All tools panel across almost the entire editing area. Organize pages actions remain reachable, although the panel leaves only a sliver of the page area visible.

The browser used a disposable account and a fresh context at each size. Physical-device input, software keyboard and GPU performance still need hardware testing.

Desktop releases `e5ee6f304c8fc82927f0e93c49bb0982871df3320e81a76fd0b320e611e366e7`, `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Tested app bundle `77933e39f4981b21b25556f6cb05e0d651fcc8882548bb581f9b136dc0a592a0`.
