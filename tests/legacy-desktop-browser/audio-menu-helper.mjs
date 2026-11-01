// Drive the embedded editor through the same File menu available to users.
export async function audioMenu(page, label, index=0) {
 const frames=await page.$$('.audio-editor-frame');
 const frame=await frames[index]?.contentFrame();
 if(!frame)throw Error('Audio Editor frame is unavailable');
 const file=await frame.waitForSelector('.pk_hdr > .pk_btn > button');
 await file.click();
 await frame.waitForFunction(label=>{const b=[...document.querySelectorAll('.pk_hdr .pk_menu .pk_opt')].find(x=>x.textContent.trim()===label);if(!b)return false;const r=b.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return b===hit||b.contains(hit)},{timeout:10000},label);
 const handle=await frame.evaluateHandle(label=>[...document.querySelectorAll('.pk_hdr .pk_menu .pk_opt')].find(x=>x.textContent.trim()===label),label);
 try{const element=handle.asElement();if(!element)throw Error('Missing Audio Editor menu action: '+label);await element.click();}finally{await handle.dispose();}
}
