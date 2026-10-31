// Complete the shared My files folder chooser after accepting a download name.
export async function chooseRoot(page){
 await page.waitForSelector('.codi-file-picker');
 await page.waitForFunction(()=>[...document.querySelectorAll('.codi-picker-bar button')].some(b=>b.textContent==='Use this folder'&&!b.disabled));
 await page.evaluate(()=>[...document.querySelectorAll('.codi-picker-bar button')].find(b=>b.textContent==='Use this folder').click());
 await page.waitForFunction(()=>!document.querySelector('.codi-file-picker'));
}
