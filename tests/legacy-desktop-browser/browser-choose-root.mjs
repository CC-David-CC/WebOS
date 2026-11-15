// Complete the shared My files folder chooser after accepting a download name.
export async function chooseRoot(page){
 await page.waitForSelector('.codi-file-picker');
 await page.waitForFunction(()=>[...document.querySelectorAll('.codi-picker-bar button')].some(b=>b.textContent==='Use this folder'&&!b.disabled));
 await page.evaluate(()=>[...document.querySelectorAll('.codi-picker-bar button')].find(b=>b.textContent==='Use this folder').click());
 await page.waitForFunction(()=>!document.querySelector('.codi-file-picker'));
}
export async function chooseFolder(page,name){
 await page.waitForSelector('[aria-label="Open folder '+name+'"]');
 await page.click('[aria-label="Open folder '+name+'"]');
 await page.waitForFunction(n=>document.querySelector('.codi-picker-location')?.textContent==='My files: /'+n,{},name);
 await chooseRoot(page);
}
