#!/usr/bin/env python3
"""Loopback-only cookie/slow/failed download server for the Gecko tests."""
import asyncio
from aiohttp import web

async def index(request):
    if request.query.get('stream')=='1':
        return web.Response(text='<style>body{margin:0}a{display:block;width:250px;height:80px;background:white;font:22px sans-serif}</style><a href="/stream-big">STREAM WITHOUT LENGTH</a>',content_type='text/html')
    html=('<!doctype html><style>body{margin:0}a{display:block;width:250px;'
          'height:80px;background:white;font:22px sans-serif}</style>'
          '<a href="/file">COOKIE DOWNLOAD</a>'
          '<a href="/big">OVERSIZED DOWNLOAD</a>'
          '<a href="/zero">EMPTY DOWNLOAD</a>'
          '<a href="/abort">INTERRUPTED DOWNLOAD</a>')
    response=web.Response(text=html,content_type='text/html')
    response.set_cookie('codi_fixture','authenticated',httponly=True,samesite='Lax')
    return response

async def file(request):
    if request.cookies.get('codi_fixture')!='authenticated':
        return web.Response(status=403,text='Cookie missing')
    data=b'authenticated-cookie-download-'+b'Z'*65536
    response=web.StreamResponse(headers={'Content-Type':'application/octet-stream','Content-Disposition':'attachment; filename="cookie-result.bin"','Content-Length':str(len(data))})
    await response.prepare(request);await response.write(data[:32768]);await asyncio.sleep(1.5);await response.write(data[32768:]);await response.write_eof()
    return response

async def big(request):
    response=web.StreamResponse(headers={'Content-Type':'application/octet-stream','Content-Disposition':'attachment; filename="oversize.bin"','Content-Length':str(128*1024*1024+1)})
    await response.prepare(request)
    try:await response.write(b'begin');await asyncio.sleep(3)
    except ConnectionResetError:pass
    return response

async def zero(request):
    return web.Response(body=b'',headers={'Content-Type':'application/octet-stream','Content-Disposition':'attachment; filename="empty.bin"'})

async def interrupted(request):
    response=web.StreamResponse(headers={'Content-Type':'application/octet-stream','Content-Disposition':'attachment; filename="incomplete.bin"','Content-Length':'10000'})
    await response.prepare(request);await response.write(b'partial');request.transport.close();return response

async def stream_big(request):
    response=web.StreamResponse(headers={'Content-Type':'application/octet-stream','Content-Disposition':'attachment; filename="stream-big.bin"'})
    await response.prepare(request);chunk=b'x'*65536
    try:
        for _ in range(2064):await response.write(chunk)
        await response.write_eof()
    except (ConnectionResetError,asyncio.CancelledError):pass
    return response

app=web.Application();app.router.add_get('/',index);app.router.add_get('/file',file);app.router.add_get('/big',big);app.router.add_get('/zero',zero);app.router.add_get('/abort',interrupted);app.router.add_get('/stream-big',stream_big)
web.run_app(app,host='127.0.0.1',port=18777,print=None)
