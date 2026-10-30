import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const b=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:120000});
const c=await b.createBrowserContext(),p=await c.newPage(),user='phonetest'+Date.now().toString().slice(-8),errors=[];
p.on('pageerror',error=>errors.push(error.message));
try{
  await p.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1});
  await p.goto('http://127.0.0.1:18139/');await p.waitForSelector('.login-toggle');await p.click('.login-toggle');
  await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');
  await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
  await p.click('.task[data-app="terminal"]');
  await p.waitForFunction(()=>{const t=document.querySelector('[data-serial-view]')?.terminal;if(!t)return false;let text='';for(let i=0;i<t.buffer.active.length;i++)text+=t.buffer.active.getLine(i)?.translateToString(true)+'\n';return text.includes('Built-in commands:')&&text.includes('------------------');},{timeout:120000,polling:500});
  const state=await p.evaluate(()=>{const win=document.querySelector('.window'),desktop=document.querySelector('.desktop'),view=win.getBoundingClientRect(),root=desktop.getBoundingClientRect(),t=win.querySelector('[data-serial-view]').terminal;let text='';for(let i=0;i<t.buffer.active.length;i++)text+=t.buffer.active.getLine(i)?.translateToString(true)+'\n';return {view:{x:view.x-root.x,y:view.y-root.y,width:view.width,height:view.height},desktop:{width:root.width,height:root.height},text};});
  assert.ok(state.view.x<=1&&state.view.width>=state.desktop.width-2);assert.ok(state.view.height>=state.desktop.height-state.view.y-2);
  assert.ok(!state.text.includes('built-in shell (ash)'));assert.ok(!state.text.includes("Enter 'help' for a list of built-in commands."));
  assert.ok(state.text.includes('help'));console.log('PASS real shell help output and fullscreen phone terminal');
  await p.click('.task[data-app="files"]');await p.waitForFunction(()=>document.querySelectorAll('.window').length>=2,{timeout:20000});
  const full=await p.evaluate(()=>{const d=document.querySelector('.desktop').getBoundingClientRect(),w=[...document.querySelectorAll('.window')].at(-1).getBoundingClientRect();return Math.abs(w.left-d.left)<2&&Math.abs(w.width-d.width)<2&&Math.abs(w.bottom-d.bottom)<2;});assert.ok(full,'Files must also start fullscreen on phone');
  assert.deepEqual(errors,[]);console.log('PASS second phone app also starts fullscreen');
}finally{await c.close();await b.disconnect();}
