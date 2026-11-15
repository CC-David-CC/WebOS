'use strict';
const make=(tag,cls,text)=>{const n=document.createElement(tag);n.className=cls||'';n.textContent=text??'';return n;};
const textButton=(text,fn,cls)=>{const n=make('button',cls,text);n.type='button';n.addEventListener('click',fn);return n;};
let currentSession={public:{kind:'anonymous',sub:crypto.randomUUID(),sid:crypto.randomUUID(),name:'anon'}},identityConfig={identity:{issuer:location.origin}},guestState='ready',guestMessage='Owned fixture has no v86';
const surfaces=new Map(),fileGateway=null;
const signedInSubject=()=>currentSession.public.kind==='registered'?currentSession.public.sub:null;
const terminalSession=()=>null,sendTerminalBytes=()=>{},sendTerminal=()=>{},attachTerminalRenderer=()=>{},resizeTerminal=()=>{},setScreenKeyboardEnabled=()=>{},feedback=()=>{},applyScreenKeyboardPolicy=()=>{};
const desktopNetwork={appContext:()=>({disabled:true})};
window.confirm=()=>true;window.fixtureReady=false;
