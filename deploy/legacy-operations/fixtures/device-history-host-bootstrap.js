// Test-only minimal window manager; real desktop-apps.js/app loader/API2 run.
const make=(tag,classes='',text='')=>{const n=document.createElement(tag);n.className=classes;n.textContent=text;return n;};
const textButton=(text,handler,classes='')=>{const b=make('button',classes,text);b.type='button';b.addEventListener('click',handler);return b;};
let currentSession={public:{kind:'registered',sub:'registered-a',sid:'fresh-session-a'}},identityConfig={identity:{issuer:location.origin}},guestState='fixture-only',guestMessage='No v86 in this test';
function signedInSubject(){return currentSession?.public.kind==='registered'?currentSession.public.sub:null;}
for(const name of ['feedback','sendTerminalBytes','sendTerminal','attachTerminalRenderer','resizeTerminal','setScreenKeyboardEnabled','applyScreenKeyboardPolicy'])window[name]=()=>{};
window.terminalSession=()=>null;
window.hostFixture={disabled:false,networkStarts:0,mounts:0,active:0,timerTicks:0,inputEvents:0,liveScopes:[],facades:[],routedMounts:0,windows:[],next:1};
const terminalSessions=new Map(),surfaces=new Map(),fixtureChatViews=new Map();
const desktopNetwork={appContext:()=>({disabled:hostFixture.disabled,views:fixtureChatViews,routedRooms:{},routedContent:()=>{hostFixture.routedMounts++;if(hostFixture.decoratorFail)throw Error('Room extension temporarily unavailable');return make('p','fixture-routed','Owned room extension');}}),initialize:async(session,config,{signal}={})=>{
  hostFixture.networkStarts++;
  if(hostFixture.holdNetwork)await new Promise(resolve=>hostFixture.finishNetwork=resolve);
  signal?.throwIfAborted();if(currentSession!==session)throw Error('Account changed in network hook');return true;
}};
