import {beginSession,logoutSession} from './network/identity.mjs';
import {PeerPool} from './network/peer-pool.mjs';
import {Discovery} from './network/discovery.mjs';
const config=await (await fetch('/config.json')).json(),fixture=await (await fetch('/server-route-config.json')).json(),name=new URL(location.href).searchParams.get('name');
const session=await beginSession(config,'registered',name,'1!$?'),messages=[];let discovery;
const pool=new PeerPool(session,config,{onDeviceMember:()=>{},onMessage:(entry,msg)=>messages.push(msg.text)});
try{
 discovery=new Discovery(session,{...fixture.discovery,identity:config.identity,channelTransport:'server'},pool);discovery.onChannelPeer=()=>true;await discovery.start();await discovery.addChannel(fixture.tag,fixture.channel,fixture.genesis);window.routeFixture={session,pool,discovery,messages,async send(text){const p=pool.firstReady();if(!p)throw Error('No server-routed peer');await p.link.send(text);},async stats(){const p=pool.firstReady();return {peers:pool.list(),transport:p?(await p.link.stats()).transport:null,messages:[...messages]};},async close(){discovery.close();pool.close();await logoutSession(config,session).catch(()=>{});}};window.fixtureReady=true;
}catch(error){window.fixtureError=error.stack;throw error;}
