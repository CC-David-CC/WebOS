// Test-only instrumentation, installed after desktop startup in an owned page.
(() => {
  const native={setTimeout,clearTimeout,setInterval,clearInterval,Worker,ResizeObserver,add:EventTarget.prototype.addEventListener,remove:EventTarget.prototype.removeEventListener,fetch};
  const timers=new Map(),workers=new Set(),observers=new Set(),listeners=new Set(),requests=new Set();
  const appStack=stack=>/\/assets\/desktop\/apps\/|\/terminal\.js:/.test(stack);
  for(const [name,clear,repeat] of [['setTimeout','clearTimeout',false],['setInterval','clearInterval',true]]){
    window[name]=(fn,delay,...args)=>{
      const stack=new Error().stack;let id;
      const wrapped=typeof fn==='function'?function(...values){if(!repeat)timers.delete(id);return Reflect.apply(fn,this,values);}:fn;
      id=native[name].call(window,wrapped,delay,...args);timers.set(id,{repeat,app:appStack(stack)});return id;
    };
    window[clear]=id=>{timers.delete(id);native[clear].call(window,id);};
  }
  window.Worker=class extends native.Worker {
    constructor(...args){super(...args);this.probeRecord={ref:new WeakRef(this),stopped:false};workers.add(this.probeRecord);}
    terminate(){this.probeRecord.stopped=true;return super.terminate();}
  };
  window.ResizeObserver=class extends native.ResizeObserver {
    constructor(...args){super(...args);this.probeRecord={ref:new WeakRef(this),targets:new Map()};observers.add(this.probeRecord);}
    observe(target,...args){this.probeRecord.targets.set(target,new WeakRef(target));return super.observe(target,...args);}
    unobserve(target){this.probeRecord.targets.delete(target);return super.unobserve(target);}
    disconnect(){this.probeRecord.targets.clear();return super.disconnect();}
  };
  function capture(options){return typeof options==='boolean'?options:!!options?.capture;}
  EventTarget.prototype.addEventListener=function(type,callback,options){
    if(![window,document,visualViewport].includes(this)||!callback)return native.add.call(this,type,callback,options);
    let r=[...listeners].find(r=>r.target===this&&r.type===type&&r.callback===callback&&r.capture===capture(options));
    if(r||options?.signal?.aborted)return native.add.call(this,type,r?.wrapped||callback,options);
    r={target:this,type,callback,capture:capture(options)};
    r.wrapped=function(...args){if(options?.once)listeners.delete(r);return typeof callback==='function'?Reflect.apply(callback,this,args):callback.handleEvent(...args);};
    listeners.add(r);if(options?.signal)native.add.call(options.signal,'abort',()=>listeners.delete(r),{once:true});
    return native.add.call(this,type,r.wrapped,options);
  };
  EventTarget.prototype.removeEventListener=function(type,callback,options){
    const r=[...listeners].find(r=>r.target===this&&r.type===type&&r.callback===callback&&r.capture===capture(options));
    if(r)listeners.delete(r);return native.remove.call(this,type,r?.wrapped||callback,options);
  };
  window.fetch=async function(...args){const r={url:String(args[0]?.url||args[0]),app:appStack(new Error().stack)};requests.add(r);try{return await native.fetch.call(window,...args);}finally{requests.delete(r);}};
  window.appLifecycleProbe={snapshot(){
    let observed=0;for(const r of observers)if(r.ref.deref())observed+=r.targets.size;
    return {appTimers:[...timers.values()].filter(r=>r.app).length,intervals:[...timers.values()].filter(r=>r.repeat).length,globalListeners:listeners.size,workers:[...workers].filter(r=>!r.stopped&&r.ref.deref()).length,observerTargets:observed,appRequests:[...requests].filter(r=>r.app).length,terminals:terminalSessions.size,windows:[...surfaces.values()].reduce((n,d)=>n+d.windows.length,0),chatViews:desktopNetwork.appContext().views.size};
  }};
})();
