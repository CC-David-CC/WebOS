/** Parent composition only. Components own their views and domain implementations. */
import {createAccountsClient} from '@webos/accounts';
import {mount as mountLogin} from '@webos/login';
import {mount as mountDesktop, createDesktopController} from '@webos/desktop';
import {mount as mountFiles} from '@webos/files';
import {UserFiles} from '@webos/storage';

export function mountAssembly(root) {
  const accounts = createAccountsClient(); let view, desktop, disposed = false, renewal;
  function showLogin() {
    clearTimeout(renewal); view?.dispose(); desktop?.dispose(); desktop = null;
    if (disposed) return;
    view = mountLogin({accounts, onAuthenticated: showDesktop}); root.replaceChildren(view.element);
  }
  async function showDesktop(session) {
    if (disposed || accounts.inspect().sessionId !== session.sessionId) return;
    const authority = Object.freeze({}), files = new UserFiles(accounts.createFileAuthority(), {workerUrl: new URL('./workers/storage-verify.mjs', import.meta.url)});
    const authorize = candidate => candidate === authority && accounts.inspect().sessionId === session.sessionId;
    const nextDesktop = createDesktopController({sessionId: session.sessionId, accountId: session.accountId, authorize,
      applications: [{id: 'files', title: 'Files', mount: host => mountFiles({...host, files, authority, authorize,
        openFile: async () => { throw Error('An editor is not connected yet. Use Download to retrieve this account file.'); }})}]});
    let nextView;
    try { nextView = mountDesktop({desktop: nextDesktop, authority, displayName: session.displayName, onSignOut: () => accounts.logout()}); }
    catch (error) { nextDesktop.dispose(); throw error; }
    view?.dispose(); desktop?.dispose(); desktop = nextDesktop; view = nextView; root.replaceChildren(view.element);
    async function renew() {
      if (disposed || accounts.inspect().sessionId !== session.sessionId) return;
      try { await accounts.renew(); }
      catch { await accounts.logout().catch(() => {}); }
      if (!disposed && accounts.inspect().sessionId === session.sessionId) renewal = setTimeout(renew, 60000);
    }
    renewal = setTimeout(renew, 60000);
  }
  const unsubscribe = accounts.subscribe(state => { if (!disposed && desktop && state.phase !== 'authenticated') showLogin(); });
  showLogin();
  return Object.freeze({inspect: () => ({account: accounts.inspect(), desktop: desktop?.inspect() ?? null, disposed}),
    dispose() { if (disposed) return; disposed = true; clearTimeout(renewal); unsubscribe(); view?.dispose(); desktop?.dispose(); root.replaceChildren(); }});
}
