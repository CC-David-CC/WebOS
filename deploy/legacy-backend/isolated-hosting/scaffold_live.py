"""Copy-once starter. Refuses to overwrite existing site source."""
from pathlib import Path
import html
import json
import re
from common import ROOT

STYLE = '''/* Local assets only; no build pipeline. */
:root{color-scheme:light;--paper:#f5f3ed;--ink:#172321;--muted:#52635f;--accent:#185b4d}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.6}main{max-width:980px;margin:auto;padding:clamp(1.5rem,6vw,5rem)}header{display:flex;justify-content:space-between;align-items:center;gap:1rem;border-bottom:1px solid #ced5d0;padding-bottom:1.25rem}.badge{font-size:.75rem;text-transform:uppercase;letter-spacing:.12em;color:var(--accent);border:1px solid currentColor;border-radius:2rem;padding:.25rem .8rem}.number{font-family:ui-monospace,monospace;font-size:.8rem;color:var(--muted)}h1{font-size:clamp(2.6rem,9vw,6.4rem);font-weight:650;line-height:1.03;letter-spacing:-.065em;overflow-wrap:anywhere;margin:5rem 0 1.4rem}h2{font-size:1.2rem;margin:0 0 .7rem}.lead{font-size:clamp(1.2rem,3vw,1.65rem);max-width:680px;line-height:1.45}.note{margin-top:4rem;border-top:3px solid var(--accent);padding:1.6rem 0;max-width:680px}.note p{color:var(--muted);margin:.5rem 0}.disclaimer{font-weight:600}footer{border-top:1px solid #ced5d0;margin-top:4rem;padding-top:1rem;font-size:.8rem;color:var(--muted)}code{font-family:ui-monospace,monospace;font-size:.75rem;overflow-wrap:anywhere}@media(max-width:480px){h1{margin-top:3rem}header{align-items:flex-start}.badge{max-width:12rem}.note{margin-top:2.5rem}}
'''

def scaffold(s, root=ROOT):
    path = root/'sites'/s['domain']
    if path.exists():
        raise FileExistsError(f'Refusing to overwrite {path}')
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',s['accent']): raise ValueError('Invalid accent')
    for folder in ['app','public/static','tests']:
        (path/folder).mkdir(parents=True, exist_ok=True)
    (path/'app/__init__.py').write_text('')
    (path/'app/main.py').write_text(f'''from pathlib import Path
from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles

DOMAIN = {s['domain']!r}
PUBLIC = Path(__file__).resolve().parents[1] / "public"
app = FastAPI(debug=False, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=[DOMAIN], www_redirect=False)

@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
async def homepage():
    return FileResponse(PUBLIC / "index.html")

@app.api_route("/robots.txt", methods=["GET", "HEAD"], include_in_schema=False)
async def robots():
    return FileResponse(PUBLIC / "robots.txt", media_type="text/plain")

@app.get("/healthz", include_in_schema=False)
async def health():
    return JSONResponse({{"status": "ok", "site": DOMAIN}}, headers={{"Cache-Control": "no-store"}})

app.mount("/static", StaticFiles(directory=PUBLIC / "static", follow_symlink=False), name="static")
''')
    domain, theme, desc = [html.escape(s[k]) for k in ['domain','theme','description']]
    disclaimer = '<p class="disclaimer">An independent peer-learning project. Not an official Kennesaw State University website.</p>' if s['domain']=='ksu.codes' else ''
    marker = f"site:{s['domain']}:starter-v1"
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{desc}"><title>{domain} — In progress</title><link rel="icon" href="/static/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/static/style.css"></head>
<body><main><header><span class="badge">Work in progress</span><span class="number">{theme}</span></header>
<h1>{domain}</h1><p class="lead">{desc}</p>
<section class="note" aria-labelledby="status"><h2 id="status">A beginning, with more to come.</h2><p>This is an early placeholder. Content and services are still being developed; no service, download, quotation, or transaction is offered here yet.</p>{disclaimer}</section>
<footer><p>Independent project · Initial site preparation</p><code>{marker}</code></footer></main></body></html>
'''
    (path/'public/index.html').write_text(page, encoding='utf-8')
    (path/'public/robots.txt').write_text('User-agent: *\nDisallow: /\n')
    (path/'public/static/style.css').write_text(STYLE+f'\n:root{{--accent:{s["accent"]};}}\n')
    (path/'public/static/favicon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{s["accent"]}"/><path d="M17 17h30v6H23v18h24v6H17z" fill="#f5f3ed"/></svg>\n')
    (path/'requirements.in').write_text('fastapi\nuvicorn\n')
    (path/'tests/contract.json').write_text(json.dumps(dict(domain=s['domain'],marker=marker,port=s['port']),indent=2)+'\n')

INITIAL = [
('python.coach','python-coach','Python, in practice','A place taking shape for practical Python learning and coaching.','#215e51'),
('code.contractors','code-contractors','Software & collaboration','An early home for software projects and thoughtful contracting.','#71412d'),
('ksu.codes','ksu-codes','Learn with peers','Independent peer learning and computing resources, in development.','#4b477b'),
('arpa.net.ai','arpa-net-ai','AI & systems','A place for independent experiments in AI, software, and systems.','#245777'),
('plastic.download','plastic-download','Ideas into objects','A future collection of fabrication notes and downloadable designs.','#925018'),
('official.bid','official-bid','Requests & quotations','A future home for independent project requests and quotations.','#5b5630'),
('does.trade','does-trade','Projects & services','A project exploring useful connections between projects, services, and trade.','#386777')]

if __name__=='__main__':
    from common import MANIFEST, dump
    if MANIFEST.exists(): raise SystemExit('Manifest already exists; use webctl add for new sites.')
    data={'schema_version':1,'sites':[]}
    for index,(domain,slug,theme,description,accent) in enumerate(INITIAL):
        s=dict(domain=domain,slug=slug,port=8011+index,service=f'web-{slug}.service',user=f'site-{slug}',workers=1,enabled=True,theme=theme,description=description,accent=accent)
        data['sites'].append(s)
        scaffold(s)
    MANIFEST.write_text(dump(data), encoding='utf-8')
