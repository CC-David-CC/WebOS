/** Composition uses Text's public local-recovery API, never account secrets. */
import {createDraftStore, createDraftJournal} from '@webos/text/recovery';

export function textRecovery(host, context, valid) {
  host.w.textRecoverySourceId = host.w.textDraftId || null;
  return createDraftJournal({store: createDraftStore({issuer: location.origin, accountId: context.owner}),
    sourceId: host.w.textDraftId || null, valid,
    onIdentity(id) { if (!valid()) return; host.w.textDraftId = id; host.desktop.saveLayout(); }});
}

export async function restoreTextRecovery({desktops, accountId, valid}) {
  try {
    const records = await createDraftStore({issuer: location.origin, accountId}).list();
    if (!valid()) return;
    const represented = new Set(desktops.flatMap(d => d.windows.flatMap(w => [w.textDraftId, w.textRecoverySourceId])));
    const desktop = desktops[0]; if (!desktop) return;
    for (const record of records) {
      if (!valid()) return;
      if (represented.has(record.id)) continue;
      const w = desktop.launch('text', 'Text Editor'); w.textDraftId = record.id; w.ownerSub = accountId;
      represented.add(record.id);
    }
    desktop.saveLayout();
  } catch (error) {
    // Existing Text windows report their own storage failure. Do not claim
    // that no drafts exist when discovery itself failed.
    if (valid()) console.error('Text recovery discovery unavailable:', error.message);
  }
}
