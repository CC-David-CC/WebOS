import pathlib
import runpy
import tempfile
import zipfile

app = pathlib.Path(__file__).resolve().parents[1] / 'apps/system/circuit-lab'
audit = runpy.run_path(str(app / 'audit-builder.py'))['audit_app_sources']
names = ('index.mjs', 'netlist.mjs', 'worker.mjs', 'style.css', 'app.json')
with tempfile.TemporaryDirectory(prefix='circuit-source-bind-') as directory:
    root = pathlib.Path(directory)
    archive = root / 'source.zip'
    with zipfile.ZipFile(archive, 'w') as package:
        for name in names:
            (root / name).write_bytes((app / name).read_bytes())
            package.writestr('app/' + name, (app / name).read_bytes())
    audit(archive, root)
    (root / 'index.mjs').write_text('different source')
    try:
        audit(archive, root)
    except ValueError as error:
        assert 'index.mjs' in str(error)
    else:
        raise AssertionError('source mismatch passed audit')
print('PASS source archive app-input match and mismatch')
