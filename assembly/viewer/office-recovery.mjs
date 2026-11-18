/** Compose app-owned codecs/journals with the current account's Desktop. */
export function createOfficeRecovery(app, name, {createDraftStore, createDraftJournal}) {
  const key = app + 'DraftId';
  const sourceKey = app + 'RecoverySourceId';
  return {
    name,
    journal(host, context, valid) {
      const sourceId = host.w[key] || null;
      host.w[sourceKey] = sourceId;
      return createDraftJournal({
        store: createDraftStore({issuer: location.origin, accountId: context.owner}),
        sourceId, valid,
        onIdentity(id) {
          if (!valid()) return;
          host.w[key] = id;
          host.desktop.saveLayout();
        }
      });
    },
    async restore({desktops, accountId, valid}) {
      try {
        const records = await createDraftStore({issuer: location.origin, accountId}).list();
        const desktop = desktops[0];
        if (!valid() || !desktop) return;
        const represented = new Set(desktops.flatMap(d => d.windows.flatMap(w => [w[key], w[sourceKey]])));
        for (const record of records) {
          if (!valid()) return;
          if (represented.has(record.id)) continue;
          const duplicate = record.path && desktops.some(d => d.windows.some(w =>
            w.launchContext?.storage === 'account' && w.launchContext.owner === accountId
            && w.launchContext.path === record.path));
          const w = desktop.launch(app, 'Recovered document — ' + name);
          if (!w) continue;
          w[key] = record.id;
          w[app + 'RecoveryAsCopy'] = !!duplicate;
          w.ownerSub = accountId;
          represented.add(record.id);
        }
        desktop.saveLayout();
      } catch (error) {
        if (valid()) console.error(name + ' recovery discovery unavailable:', error.message);
      }
    }
  };
}
