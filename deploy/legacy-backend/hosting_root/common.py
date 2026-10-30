"""Manifest validation and deterministic deployment configuration generation."""
from pathlib import Path
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'sites.toml'
DOMAIN_RE = re.compile(r'(?=.{1,190}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,62}$')
SLUG_RE = re.compile(r'[a-z][a-z0-9-]{0,24}$')

def validate(data):
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported manifest schema')
    if 'codi_shared_ingress' in data and type(data['codi_shared_ingress']) is not bool:
        raise ValueError('codi_shared_ingress must be boolean')
    if data.get('codi_shared_ingress') and not any(s['domain']=='ksu.codes' and s['enabled'] and s.get('codi_preview') and s.get('codi_turn_certificate') for s in data['sites']):
        raise ValueError('Shared ingress requires the enabled KSU preview/certificate profile')
    seen = {k: set() for k in ['domain', 'slug', 'port', 'service', 'user']}
    for s in data['sites']:
        if not DOMAIN_RE.fullmatch(s['domain']) or not SLUG_RE.fullmatch(s['slug']):
            raise ValueError('Invalid domain or slug')
        if s['service'] != f"web-{s['slug']}.service" or s['user'] != f"site-{s['slug']}":
            raise ValueError('Service/account must match the validated slug')
        if type(s['port']) is not int or not 8011 <= s['port'] <= 8999:
            raise ValueError('Application port must be in 8011..8999')
        if type(s['workers']) is not int or not 1 <= s['workers'] <= 4:
            raise ValueError('Workers must be in 1..4; measure before increasing')
        if type(s['enabled']) is not bool:
            raise ValueError('enabled must be boolean')
        if 'codi_files' in s and (type(s['codi_files']) is not bool or s['domain']!='ksu.codes' or s['codi_files'] and (not s['enabled'] or not s.get('codi_preview',False))):
            raise ValueError('codi_files requires a boolean on enabled KSU preview only')
        if 'codi_speech' in s and (not isinstance(s['codi_speech'],str) or not re.fullmatch('[0-9a-f]{64}',s['codi_speech']) or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_preview',False)):
            raise ValueError('codi_speech requires a SHA256 on enabled KSU preview only')
        if 'codi_frontend' in s and (not isinstance(s['codi_frontend'],str) or not re.fullmatch('[0-9a-f]{64}',s['codi_frontend']) or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_preview',False)):
            raise ValueError('codi_frontend requires a SHA256 on enabled KSU preview only')
        if 'codi_turn_certificate' in s and (type(s['codi_turn_certificate']) is not bool or s['domain']!='ksu.codes' or s['codi_turn_certificate'] and not s['enabled']):
            raise ValueError('codi_turn_certificate must be boolean on enabled ksu.codes only')
        if 'codi_preview' in s and (type(s['codi_preview']) is not bool or s['domain']!='ksu.codes'):
            raise ValueError('codi_preview must be a boolean on ksu.codes only')
        if 'codi_mount' in s and (type(s['codi_mount']) is not str or s['codi_mount'] not in ('','/hidden') or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_preview',False)):
            raise ValueError('codi_mount requires root or /hidden on the enabled KSU desktop only')
        if s.get('codi_mount','/hidden')=='' and s.get('codi_frontend'):
            raise ValueError('Root desktop requires its coherent native asset graph')
        if 'hardware_studio' in s and (type(s['hardware_studio']) is not bool or s['domain'] != 'hardware.ksu.codes'):
            raise ValueError('hardware_studio must be boolean on its exact hostname')
        if 'cardboard_studio' in s and (type(s['cardboard_studio']) is not bool or s['domain'] != 'cardboard.ksu.codes'):
            raise ValueError('cardboard_studio must be a boolean on its exact hostname')
        for k in seen:
            if s[k] in seen[k]:
                raise ValueError(f'Duplicate {k}: {s[k]}')
            seen[k].add(s[k])
    return data

def load(path=MANIFEST):
    return validate(tomllib.loads(path.read_text()))

def dump(data):
    validate(data)
    lines = ['schema_version = 1', *(['codi_shared_ingress = '+str(data['codi_shared_ingress']).lower()] if 'codi_shared_ingress' in data else []), '']
    for s in data['sites']:
        lines.append('[[sites]]')
        for key in ['domain','slug','port','service','user','workers','enabled','theme','description','accent']:
            v = s[key]
            text = str(v).lower() if isinstance(v, bool) else str(v) if isinstance(v, int) else json.dumps(v, ensure_ascii=False)
            lines.append(f'{key} = {text}')
        if 'codi_preview' in s: lines.append('codi_preview = '+str(s['codi_preview']).lower())
        if 'codi_mount' in s: lines.append('codi_mount = '+json.dumps(s['codi_mount']))
        if 'codi_files' in s: lines.append('codi_files = '+str(s['codi_files']).lower())
        if 'codi_frontend' in s: lines.append('codi_frontend = '+json.dumps(s['codi_frontend']))
        if 'codi_speech' in s: lines.append('codi_speech = '+json.dumps(s['codi_speech']))
        if 'codi_turn_certificate' in s: lines.append('codi_turn_certificate = '+str(s['codi_turn_certificate']).lower())
        if 'hardware_studio' in s: lines.append('hardware_studio = '+str(s['hardware_studio']).lower())
        if 'cardboard_studio' in s: lines.append('cardboard_studio = '+str(s['cardboard_studio']).lower())
        lines.append('')
    return '\n'.join(lines)

def unit(s):
    if s.get('hardware_studio'):
        from hardware_hosting import unit as hardware_unit
        return hardware_unit(s)
    if s.get('cardboard_studio'):
        from cardboard_hosting import unit as cardboard_unit
        return cardboard_unit(s)
    base = f"/srv/webapps/{s['domain']}/current"
    return f'''[Unit]
Description=Independent FastAPI site: {s['domain']}
After=network.target
StartLimitIntervalSec=60
StartLimitBurst=5

[Service]
Type=simple
User={s['user']}
Group={s['user']}
WorkingDirectory={base}
EnvironmentFile=/etc/webapps/{s['slug']}.env
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONDONTWRITEBYTECODE=1
ExecStart={base}/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port {s['port']} --workers ${{WEB_WORKERS}} --proxy-headers --forwarded-allow-ips 127.0.0.1 --timeout-keep-alive 10 --timeout-graceful-shutdown 20 --no-server-header --no-access-log
Restart=on-failure
RestartSec=3
TimeoutStopSec=30
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
CapabilityBoundingSet=
AmbientCapabilities=
UMask=0027
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''


def connected_preview(s):
    # Only the validated KSU flag can activate these fixed loopback targets.
    if s.get('codi_mount','/hidden')=='':
        return connected_root(s)
    return [
        '\t@codi_preview path /hidden /hidden/*',
        '\theader @codi_preview >Cache-Control "no-store"',
        '\theader @codi_preview >Content-Security-Policy "default-src \'none\'; script-src \'self\' \'wasm-unsafe-eval\'; connect-src \'self\' wss://ksu.codes; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:; font-src \'self\'; worker-src \'self\' blob:; base-uri \'none\'; frame-ancestors \'none\'; form-action \'none\'"',
        '\thandle /hidden {', '\t\tredir * /hidden/ 308', '\t}',
        '\thandle /hidden/rendezvous {', '\t\treverse_proxy 127.0.0.1:8119', '\t}',
        *(['\thandle /hidden/gateway/* {', '\t\turi strip_prefix /hidden', '\t\trequest_body {', '\t\t\tmax_size 12MiB', '\t\t}', '\t\treverse_proxy 127.0.0.1:8140', '\t}'] if s.get('codi_files') else []),
        '\thandle_path /hidden/* {',
        '\t\trequest_body {', '\t\t\tmax_size 64KiB', '\t\t}',
        '\t\troute {',
        *(['\t\t\t@codi_frontend path /app.js /style.css /terminal.js /assets/terminal-initramfs.cpio.gz /desktop-apps.js /networking.js', '\t\t\thandle @codi_frontend {', '\t\t\t\troot * /srv/codi-connected/frontends/'+s['codi_frontend'], '\t\t\t\tfile_server', '\t\t\t}'] if s.get('codi_frontend') else []),
        *(['\t\t\thandle_path /assets/speech/* {','\t\t\t\troot * /srv/codi-connected/speech/'+s['codi_speech'],'\t\t\t\tfile_server','\t\t\t}'] if s.get('codi_speech') else []),
        '\t\t\t@codi_identity path /api/* /discovery.json /.well-known/codi-issuer.json',
        '\t\t\treverse_proxy @codi_identity 127.0.0.1:8118',
        '\t\t\treverse_proxy 127.0.0.1:8132', '\t\t}', '\t}',
    ]

WEBSITE_PATHS = '/blog /blog/* /posts /posts/* /static /static/* /robots.txt /healthz /test-time /test-time/* /desktop /desktop/*'
DESKTOP_CSP = "default-src 'none'; script-src 'self' 'wasm-unsafe-eval'; connect-src 'self' wss://ksu.codes; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; worker-src 'self' blob:; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"

def connected_root(s):
    # The native backends must already be configured at the actual root mount.
    # Reserved website routes retain their existing paths, backend and policy.
    return [
        '\t@codi_root {', '\t\tnot path '+WEBSITE_PATHS+' /hidden /hidden/*', '\t}',
        '\theader @codi_root >Cache-Control "no-store"',
        '\theader @codi_root >Content-Security-Policy "'+DESKTOP_CSP+'"',
        '\t@codi_website path '+WEBSITE_PATHS,
        '\thandle @codi_website {', '\t\treverse_proxy 127.0.0.1:'+str(s['port'])+' {',
        '\t\t\ttransport http {', '\t\t\t\tkeepalive 4s', '\t\t\t}', '\t\t}', '\t}',
        '\t@codi_old_preview path /hidden /hidden/*',
        '\thandle @codi_old_preview {', '\t\tredir * / 308', '\t}',
        '\thandle /rendezvous {', '\t\treverse_proxy 127.0.0.1:8119', '\t}',
        *(['\thandle /gateway/* {', '\t\trequest_body {', '\t\t\tmax_size 12MiB', '\t\t}', '\t\treverse_proxy 127.0.0.1:8140', '\t}'] if s.get('codi_files') else []),
        *(['\thandle_path /assets/speech/* {', '\t\troot * /srv/codi-connected/speech/'+s['codi_speech'], '\t\tfile_server', '\t}'] if s.get('codi_speech') else []),
        '\t@codi_identity path /api/* /discovery.json /.well-known/codi-issuer.json',
        '\thandle @codi_identity {', '\t\trequest_body {', '\t\t\tmax_size 64KiB', '\t\t}', '\t\treverse_proxy 127.0.0.1:8118', '\t}',
        '\thandle {', '\t\trequest_body {', '\t\t\tmax_size 64KiB', '\t\t}', '\t\treverse_proxy 127.0.0.1:8132', '\t}',
    ]

def caddy(data, mode):
    validate(data)
    if mode not in ['prepare','production']:
        raise ValueError('Invalid mode')
    lines = [f'# webhost-sites mode: {mode}', '{', '\tadmin unix//run/caddy/admin.sock', *(['\thttp_port 8080', '\thttps_port 8443', '\tdefault_bind 127.0.0.1'] if data.get('codi_shared_ingress') and mode=='production' else []), '\tservers {', '\t\tprotocols h1 h2', *(['\t\tlistener_wrappers {', '\t\t\tproxy_protocol {', '\t\t\t\ttimeout 1s', '\t\t\t\tallow 127.0.0.1/32', '\t\t\t\tfallback_policy reject', '\t\t\t}', '\t\t\ttls', '\t\t}'] if data.get('codi_shared_ingress') and mode=='production' else []), '\t}', '}', '', '(site_defaults) {', '\tencode zstd gzip', '\theader ?Cache-Control "no-cache, max-age=0, must-revalidate"', '\theader {', '\t\tX-Content-Type-Options nosniff', '\t\tReferrer-Policy no-referrer', '\t\tContent-Security-Policy "default-src \'none\'; style-src \'self\'; img-src \'self\'; base-uri \'none\'; frame-ancestors \'none\'; form-action \'none\'"', '\t}', '}', '']
    for s in data['sites']:
        if not s['enabled']:
            continue
        address = 'http://'+s['domain'] if mode=='prepare' else s['domain']
        lines += [address+' {']
        if mode=='prepare': lines += ['\tbind 127.0.0.1']
        if s['domain'] == 'ksu.codes':
            lines += ['\t@test_time path /test-time/*', '\theader @test_time >Content-Security-Policy "default-src \'none\'; script-src \'self\'; connect-src \'self\'; style-src \'self\'; img-src \'self\' data:; base-uri \'none\'; frame-ancestors \'none\'; form-action \'none\'"']
        if s['domain'] == 'ksu.codes':
            lines += ['\t@desktop path /desktop/*', '\theader @desktop >Content-Security-Policy "default-src \'none\'; script-src \'self\' \'wasm-unsafe-eval\'; connect-src \'self\'; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:; font-src \'self\'; worker-src \'self\' blob:; base-uri \'none\'; frame-ancestors \'none\'; form-action \'none\'"']
        lines += ['\timport site_defaults', '\tlog {', f"\t\toutput file /var/log/caddy/{s['slug']}.json {{", '\t\t\troll_size 10MiB', '\t\t\troll_keep 3', '\t\t\troll_keep_for 168h', '\t\t}', '\t\tformat json', '\t}']
        if s.get('hardware_studio'):
            # Never retain the server-issued workspace token in access logs.
            lines[-2:-1] = ['\t\tformat filter {', '\t\t\twrap json', '\t\t\tfields {', '\t\t\t\trequest>headers>X-Workspace-Token delete', '\t\t\t}', '\t\t}']
            from hardware_hosting import caddy_lines
            lines += caddy_lines(s)
        if s.get('cardboard_studio'):
            from cardboard_hosting import caddy_lines
            lines += caddy_lines(s)
        upstream = [f"\treverse_proxy 127.0.0.1:{s['port']} {{", '\t\ttransport http {', '\t\t\tkeepalive 4s', '\t\t}', '\t}']
        if s.get('codi_preview',False):
            lines += connected_preview(s)
            upstream = [] if s.get('codi_mount','/hidden')=='' else ['\thandle {']+['\t'+line for line in upstream]+['\t}']
        lines += upstream+['}', '']
    if any(s.get('codi_turn_certificate',False) for s in data['sites']):
        lines += [('http://' if mode=='prepare' else '')+'turn.ksu.codes {']
        if mode=='prepare': lines += ['\tbind 127.0.0.1']
        lines += ['\timport site_defaults', '\trespond \"Not found\" 404', '}', '']
    lines += [':8080 {' if data.get('codi_shared_ingress') and mode=='production' else ':80 {']
    if mode=='prepare': lines += ['\tbind 127.0.0.1']
    lines += ['\trespond "Not found" 404', '}', '']
    return '\n'.join(lines)
