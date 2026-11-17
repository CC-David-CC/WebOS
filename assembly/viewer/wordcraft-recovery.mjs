/** Compose WordCraft's public recovery API with account-owned Desktop windows. */
import {createDraftStore, createDraftJournal} from '@webos/wordcraft/recovery';

export function wordcraftRecovery(host, context, valid) {
  host.w.wordcraftRecoverySourceId = host.w.wordcraftDraftId || null;
  return createDraftJournal({store:createDraftStore({issuer:location.origin,accountId:context.owner}),
    sourceId:host.w.wordcraftDraftId || null, valid,
    onIdentity(id) {if(!valid())return;host.w.wordcraftDraftId=id;host.desktop.saveLayout();}});
}

export async function restoreWordcraftRecovery({desktops,accountId,valid}) {
  try {
    const records=await createDraftStore({issuer:location.origin,accountId}).list();if(!valid())return;
    const represented=new Set(desktops.flatMap(d=>d.windows.flatMap(w=>[w.wordcraftDraftId,w.wordcraftRecoverySourceId])));
    const desktop=desktops[0];if(!desktop)return;
    for(const record of records){
      if(!valid())return;if(represented.has(record.id))continue;
      // Orphaned drafts are recovered as separate unsaved copies when another
      // view already owns their account resource. Never create competing saves.
      const duplicate=record.path&&desktops.some(d=>d.windows.some(w=>w.launchContext?.storage==='account'&&w.launchContext.owner===accountId&&w.launchContext.path===record.path));
      const w=desktop.launch('wordcraft','Recovered document — WordCraft');if(!w)continue;
      w.wordcraftDraftId=record.id;w.wordcraftRecoveryAsCopy=!!duplicate;w.ownerSub=accountId;represented.add(record.id);
    }
    desktop.saveLayout();
  }catch(error){if(valid())console.error('WordCraft recovery discovery unavailable:',error.message);}
}
