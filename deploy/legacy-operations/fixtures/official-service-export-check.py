#!/usr/bin/env python3
"""Exercise packaged launcher and reject package mutations with temporary state."""
import importlib.util,json,signal,socket,subprocess,sys,tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
from codiauth import jose
spec=importlib.util.spec_from_file_location('official_export',ROOT/'scripts/export-official-service.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
base=ROOT/'.build/official-services';base.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='check-',dir=base) as temp, tempfile.TemporaryDirectory(prefix='official-state-') as state_dir:
    package=Path(temp)/'package';assert module.export(package)['status']=='verified'
    state=Path(state_dir)/'state';command=[sys.executable,str(package/'scripts/official-admin.py'),'--state',str(state),'init'];subprocess.run(command,check=True,capture_output=True)
    key=ec.generate_private_key(ec.SECP256R1());policy={'mode':'server','issuer':'http://127.0.0.1:8091','authorityKeys':[{'kid':'fixture','jwk':jose.public_jwk(key)}]};policy_path=Path(state_dir)/'policy.json';policy_path.write_text(json.dumps(policy))
    with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    command=[sys.executable,str(package/'scripts/run-official-runtime.py'),'--database',str(state/'official.sqlite'),'--ledger',str(state/'access.sqlite'),'--issuer-policy',str(policy_path),'--port',str(port)]
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        line=process.stdout.readline();assert line,process.stderr.read();assert json.loads(line)['port']==port
        process.send_signal(signal.SIGTERM);process.wait(timeout=10);assert process.returncode==0
    finally:
        if process.poll() is None:process.kill();process.wait(timeout=5)
        process.stdout.close();process.stderr.close()
    (package/'steward/official_runtime.py').write_text('tampered')
    try:module.verify(package);raise AssertionError('Tampered package accepted')
    except ValueError:pass
print('PASS: private code-only package, actual packaged startup/shutdown, tamper rejection')
