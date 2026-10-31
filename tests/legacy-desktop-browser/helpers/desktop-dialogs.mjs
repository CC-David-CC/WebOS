export async function installDesktopDialogAutoAnswer(page, initial = 'accept') {
  await page.evaluateOnNewDocument(choice => {
    window.__codiDialogAutoAnswer = choice;
    const showModal = HTMLDialogElement.prototype.showModal;
    HTMLDialogElement.prototype.showModal = function (...args) {
      const result = showModal.apply(this, args);
      if (this.classList.contains('codi-confirm-dialog')) {
        const dialog = this;
        setTimeout(() => {
          if (!dialog.open || !window.__codiDialogAutoAnswer) return;
          const buttons = dialog.querySelectorAll('.codi-confirm-actions button');
          const button = window.__codiDialogAutoAnswer === 'accept' ? buttons[buttons.length - 1] : buttons[0];
          button?.click();
        }, 10);
      }
      return result;
    };
  }, initial);
}

export async function setDesktopDialogAutoAnswer(page, choice) {
  await page.evaluate(value => { window.__codiDialogAutoAnswer = value; }, choice);
}

export async function answerDesktopDialog(page, accept) {
  await page.waitForSelector('.codi-confirm-dialog[open]');
  await page.evaluate(accept => {
    const dialog = document.querySelector('.codi-confirm-dialog[open]');
    const buttons = dialog?.querySelectorAll('.codi-confirm-actions button');
    const button = accept ? buttons?.[buttons.length - 1] : buttons?.[0];
    if (!button) throw new Error('Desktop confirmation has no action button.');
    button.click();
  }, accept);
}
