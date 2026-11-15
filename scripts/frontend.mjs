/** Parent composition only. Components own their views and domain implementations. */
import {createAccountsClient} from '@webos/accounts';
import {mount as mountLogin} from '@webos/login';
import {mount as mountDesktop, createDesktopController} from '@webos/desktop';
import {mount as mountFiles} from '@webos/files';
import {mount as mountCalculator} from '@webos/calculator';
import {mount as mountHelp} from '@webos/help';
import {mount as mountText} from '@webos/text';
import {UserFiles} from '@webos/storage';
import {mount as mountWordcraft} from '@webos/wordcraft';

export function mountAssembly(root, {wordcraftUrl = null} = {}) {
  const accounts = createAccountsClient(); let view, desktop, disposed = false, renewal;
  function showLogin() {
    clearTimeout(renewal); view?.dispose(); desktop?.dispose(); desktop = null;
    if (disposed) return;
    view = mountLogin({accounts, onAuthenticated: showDesktop}); root.replaceChildren(view.element);
  }
  async function showDesktop(session) {
    if (disposed || accounts.inspect().sessionId !== session.sessionId) return;
    const authority = Object.freeze({}), files = new UserFiles(accounts.createFileAuthority(), {workerUrl: new URL('./workers/storage-verify.mjs', import.meta.url)});
    let endingSession = false;
    const authorize = (candidate, request) => candidate === authority && accounts.inspect().sessionId === session.sessionId && !(endingSession && request?.desktopId && request.operation === 'open');
    const nextDesktop = createDesktopController({sessionId: session.sessionId, accountId: session.accountId, authorize,
      applications: [{id: 'calculator', title: 'Calculator', width: 420, height: 640, mount: host => mountCalculator({...host, authority, authorize})}, {id: 'help', title: 'Help', width: 620, height: 500, mount: host => mountHelp({...host, authority, authorize})}, {id: 'text', title: 'Text', width: 800, height: 620, mount: host => mountText({...host, files, authority, authorize})}, {id: 'files', title: 'Files', mount: host => mountFiles({...host, files, authority, authorize,
        openFile: async file => {
          if (/\.(txt|md|json|csv|log|js|mjs|css|html|py)$/i.test(file.path)) return desktop.execute({desktopId: desktop.inspect().desktopId, sessionId: session.sessionId, operation: 'open', args: {appId: 'text', resource: {path: file.path, sha256: file.sha256}}}, authority);
          if (!wordcraftUrl || !/\.(docx|docm|dotx|dotm|doc|odt|ott|rtf|txt|md)$/i.test(file.path)) throw Error('An editor is not connected for this file type. Use Download to retrieve it.');
          return desktop.execute({desktopId: desktop.inspect().desktopId, sessionId: session.sessionId, operation: 'open', args: {appId: 'wordcraft', resource: {path: file.path, sha256: file.sha256}}}, authority);
        }})}, ...(wordcraftUrl ? [{id: 'wordcraft', title: 'WordCraft', width: 1080, height: 760,
          mount: host => mountWordcraft({...host, files, authority, authorize, displayName: session.displayName, url: wordcraftUrl})}] : [])]});
    async function signOut() {
      if (endingSession) return; endingSession = true;
      try {
        while (desktop?.inspect().windows.length) {
          const state = desktop.inspect(), windowId = state.windows[0].id;
          const result = await desktop.execute({desktopId: state.desktopId, sessionId: session.sessionId, operation: 'close', args: {windowId}}, authority);
          if (result.status !== 'closed') throw Error('Sign out cancelled; a window is still open.');
        }
        await accounts.logout();
      } finally { endingSession = false; }
    }
    let nextView;
    try { nextView = mountDesktop({desktop: nextDesktop, authority, displayName: session.displayName, onSignOut: signOut}); }
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
