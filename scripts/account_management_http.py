"""Public one-time password recovery for users who cannot enter the signed-in desktop."""

import asyncio
from html import escape
from urllib.parse import urlsplit

from aiohttp import web
from webos_accounts.management import ManagementError

PATH = "/api/accounts/reset"
FORM = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reset your WebOS password</title><main><h1>Reset your WebOS password</h1>
{feedback}
<form method="post"><p><label>One-time code <input name="code" required maxlength="43" autocomplete="one-time-code"></label></p>
<p id="password-rules">Use 4–32 characters without control characters.</p>
<p><label>New password <input type="password" name="password" required aria-describedby="password-rules" autocomplete="new-password"></label></p>
<p><label>Confirm password <input type="password" name="repeat" required autocomplete="new-password"></label></p>
<button>Reset password</button></form></main></html>"""
HEADERS = {
    "Cache-Control": "no-store",
    "Referrer-Policy": "same-origin",
    "Content-Security-Policy": "default-src 'none'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'",
}


def reset_form(error=None):
    feedback = f'<p role="alert">{escape(error)}</p>' if error else ""
    return web.Response(
        text=FORM.format(feedback=feedback),
        content_type="text/html",
        status=400 if error else 200,
        headers=HEADERS,
    )


def install(app, management, origin):
    async def form(request):
        if request.headers.getall("Host", []) != [urlsplit(origin).netloc]:
            raise web.HTTPForbidden()
        if request.method == "GET":
            return reset_form()
        if (
            request.headers.getall("Origin", []) != [origin]
            or request.content_type != "application/x-www-form-urlencoded"
            or request.content_length is None
            or not 0 < request.content_length <= 2048
            or request.headers.get("Content-Encoding")
            or request.headers.get("Transfer-Encoding")
        ):
            raise web.HTTPForbidden()
        values = await request.post()
        if (
            set(values) != {"code", "password", "repeat"}
            or len(values) != 3
            or values["password"] != values["repeat"]
        ):
            return reset_form("Provide the code and matching passwords.")
        try:
            await asyncio.to_thread(
                management.redeem, values["code"], values["password"]
            )
        except ManagementError as exc:
            return reset_form(str(exc))
        return web.Response(
            text="Password reset. Open WebOS and sign in with your new password.",
            headers=HEADERS,
        )

    app.router.add_get(PATH, form, allow_head=False)
    app.router.add_post(PATH, form)
