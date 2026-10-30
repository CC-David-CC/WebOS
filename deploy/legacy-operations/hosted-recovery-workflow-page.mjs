// Appended to the existing owned client/app fixture; no product code is patched.
window.recoveryViews=[];window.recoveryHTTP=[];window.recoveryChecks=[];
const observedRecoveryFetch=window.fetch;
window.fetch=async(url,options)=>{
  let op;try{op=JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation;}catch{}
  const response=await observedRecoveryFetch(url,options);if(op)recoveryHTTP.push({op,status:response.status});return response;
};
const recoveryCheck=(name,ok)=>{if(!ok)throw Error(name);recoveryChecks.push(name);};
const recoveryView=()=>{const v=view();recoveryViews.push(v);return v;};
const recoveryDestroy=()=>{for(const v of recoveryViews)v.destroy();recoveryViews.length=0;};
window.recoveryPrepare=async password=>{
  const s=await session('register',password);await activate(s);const a=recoveryView();window.recoveryA=a;
  await until(()=>!a.el.querySelector('[data-hosted-create]').disabled);click(a,'create');await idle();window.recoveryNode=a.w.hostedRoomId;
  const native=window.fetch;window.fetch=(url,options)=>{
    let op;try{op=JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation;}catch{}
    if(op==='accept')return Promise.reject(new TypeError('Owned outage before original proposal dispatch'));
    return native(url,options);
  };
  input(a,'[data-hosted-draft]','Keep this exact original after reload');click(a,'send');await idle();window.fetch=native;
  const state=client.snapshot(recoveryNode).selected;
  recoveryCheck('the actual bundled app retains an unaccepted signed proposal and its draft',state.pending&&!state.pendingAccepted&&state.count===0&&a.el.querySelector('[data-hosted-draft]').value==='Keep this exact original after reload');
  click(a,'save-proposal');
  return {node:recoveryNode,subject:s.public.sub,sid:s.public.sid};
};
window.recoveryCloseForReload=async()=>{
  recoveryDestroy();const old=currentSession;await client.close();const budget=sessionBudget(old).snapshot();
  recoveryCheck('closing original app/client resources before reload releases every tracked lease',Object.entries(budget).every(([k,v])=>k==='closed'||!v));return {budget};
};
window.recoveryFresh=async(password,prior)=>{
  const s=await session('signin',password);await activate(s);const a=recoveryView(),b=recoveryView();window.recoveryA=a;window.recoveryB=b;window.recoveryNode=prior.node;
  input(b,'[data-hosted-draft]','Other window draft stays independent');
  recoveryCheck('fresh sign-in restores the account bookmark without retaining its old signing session or pending text',s.public.sub===prior.subject&&s.public.sid!==prior.sid&&!client.snapshot(prior.node).selected.pending&&a.el.querySelector('[data-hosted-draft]').value==='');
  return {freshSID:s.public.sid};
};
window.recoveryImported=async()=>{
  await until(()=>client.snapshot(recoveryNode).selected.pending&&!recoveryA.el.querySelector('[data-hosted-reauthorize]').disabled);
  const state=client.snapshot(recoveryNode).selected;
  recoveryCheck('native file selection verifies the saved original locally without accepting or transmitting its text',state.count===1&&state.pending&&state.pendingExpired&&recoveryA.el.querySelector('[data-hosted-draft]').value==='Keep this exact original after reload'&&!recoveryHTTP.some(r=>r.op==='recover'));
  return {state};
};
window.recoverySubmit=async()=>{
  const native=window.fetch;let lost=false;
  window.fetch=async(url,options)=>{
    let op;try{op=JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation;}catch{}
    const response=await native(url,options);
    if(op==='recover'&&!lost){lost=true;await response.arrayBuffer();throw new TypeError('Owned fixture discarded actual committed recovery response');}
    return response;
  };
  click(recoveryA,'reauthorize');await idle();window.fetch=native;
  recoveryCheck('a lost committed recovery response keeps the original proposal and draft visibly pending',lost&&client.snapshot(recoveryNode).selected.pending&&recoveryA.el.querySelector('[data-hosted-draft]').value==='Keep this exact original after reload');
  click(recoveryA,'retry');await idle();const state=client.snapshot(recoveryNode).selected;
  recoveryCheck('explicit app resubmission checks fresh permission and confirms the old original exactly once',state.count===2&&!state.pending&&state.records.some(r=>r.recovered&&r.text==='Keep this exact original after reload')&&recoveryHTTP.filter(r=>r.op==='recover').length===1);
  recoveryCheck('only the submitting window clears its confirmed draft',recoveryA.el.querySelector('[data-hosted-draft]').value===''&&recoveryB.el.querySelector('[data-hosted-draft]').value==='Other window draft stays independent');
  click(recoveryA,'join');await idle();input(recoveryA,'[data-hosted-draft]','Fresh session starts its own sequence');click(recoveryA,'send');await idle();
  const final=client.snapshot(recoveryNode).selected;
  recoveryCheck('the new signing session starts its own stream instead of inheriting the old sequence',final.count===3&&final.records.find(r=>r.text==='Fresh session starts its own sequence')?.sequence===1);
  const before=sessionBudget(currentSession).snapshot();
  for(let n=0;n<12;n++){const v=recoveryView();await Promise.resolve();v.destroy();recoveryViews.pop();}
  recoveryCheck('twelve recovery-enabled app reopen cycles release observers and preserve shared resources',JSON.stringify(sessionBudget(currentSession).snapshot())===JSON.stringify(before)&&client.snapshot().views===2);
  return {count:final.count};
};
window.recoveryHoldFile=()=>{
  const v=recoveryView();window.recoveryHeldView=v;window.recoveryReadHeld=false;const native=File.prototype.text;
  File.prototype.text=function(){const file=this;return new Promise(resolve=>{window.recoveryReadHeld=true;window.recoveryReleaseRead=async()=>{File.prototype.text=native;resolve(await native.call(file));};});};
  window.recoveryHTTPBeforeHold=recoveryHTTP.length;return true;
};
window.recoveryCancelFile=async()=>{
  await until(()=>recoveryReadHeld);recoveryHeldView.destroy();recoveryViews.pop();await recoveryReleaseRead();await new Promise(resolve=>setTimeout(resolve,50));
  recoveryCheck('closing an app during native file reading cannot revive an import or dispatch a stale operation',recoveryHTTP.length===recoveryHTTPBeforeHold&&!client.snapshot(recoveryNode).selected.pending&&client.snapshot().views===2&&!recoveryHeldView.w.hostedRoomId);return true;
};
window.recoveryAnonymous=async()=>{
  recoveryDestroy();const old=currentSession;await activate(await session('anonymous'));const a=recoveryView();window.recoveryA=a;
  recoveryCheck('account change releases the prior account resources',Object.entries(sessionBudget(old).snapshot()).every(([k,v])=>k==='closed'||!v));return true;
};
window.recoveryForeignRefused=async()=>{
  await until(()=>recoveryA.w.hostedError?.includes('original proposal account'));
  recoveryCheck('an anonymous session cannot import another account proposal or create its bookmark',client.snapshot().rooms.length===0&&client.snapshot().busy===0&&recoveryA.el.querySelector('[data-hosted-draft]').value==='');
  recoveryDestroy();const s=currentSession;await client.close();const budget=sessionBudget(s).snapshot();
  recoveryCheck('final app/client close releases every observer, crypto job and storage lease',Object.entries(budget).every(([k,v])=>k==='closed'||!v));
  return {checks:recoveryChecks,budget};
};
