"""Check the shipped patched source no longer exposes Dropbox import paths."""
from pathlib import Path
from zipfile import ZipFile

archive = Path(__file__).resolve().parents[1] / 'apps/system/circuitjs/node_modules/circuitjs-build/corresponding-source.zip'
with ZipFile(archive) as z:
    command = z.read('integration/CommandManager.ts').decode()
    menus = z.read('integration/Menus.ts').decode()
    palette = z.read('integration/CommandPaletteRegistry.ts').decode()
    simulator = z.read('integration/CirSim.ts').decode()
    packaged_index = z.read('desktop-integration/index.mjs')
    packaged_manifest = z.read('desktop-integration/app.json')
    packaged_readme = z.read('desktop-integration/README.md')
root = archive.parents[2]
assert packaged_index == (root / 'index.mjs').read_bytes()
assert packaged_manifest == (root / 'app.json').read_bytes()
assert packaged_readme == (root / 'README.md').read_bytes()
assert 'codiCircuitOpen: true' in command
assert 'Import From Dropbox...' not in menus
assert 'file:importfromdropbox' not in palette
assert "await import('./ImportFromDropboxDialog')" not in simulator
assert 'doImportDropboxLink(this.startCircuitLink' not in simulator
print('PASS packaged source removes Dropbox entry, command and startup import')
