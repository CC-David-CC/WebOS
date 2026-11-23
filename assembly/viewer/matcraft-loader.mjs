import init, {
  replace_script, run_script, script_saved, script_snapshot, take_file_request, workspace_ready,
} from './engine.js';

try {
  await init({module_or_path:new URL('./engine_bg.wasm', import.meta.url)});
  window.matcraftWorkspace = Object.freeze({
    ready:workspace_ready,
    replace:replace_script,
    snapshot:script_snapshot,
    saved:script_saved,
    run:run_script,
    request:take_file_request,
  });
} catch {
  const status = document.getElementById('matcraft_loading');
  status.dataset.startError = '';
  status.textContent = 'Could not start the MatCraft engine.';
}
