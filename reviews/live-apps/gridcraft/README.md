# GridCraft

Enter and calculate a formula, save the workbook to My files, then change the result after reopening the phone workbook from Files on desktop.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Edit and account save passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Edit and account save passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Edit and account save passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Edit and account save passed | [4k](4k.png) |

At phone width the Save icon overlaps the theme control. A tap in that area switched theme. Ctrl+S opened the account save dialog. The worksheet and formula remained usable with an emulated keyboard.

The browser used a disposable account and a fresh context at each size. Physical-device input, software keyboard and GPU performance still need hardware testing.

Desktop release `e5ee6f304c8fc82927f0e93c49bb0982871df3320e81a76fd0b320e611e366e7`. Tested app bundle `19f180ef9fbd71d8248f14fee0f2faca0617ef32d008ab304922050e77a14b68`.
