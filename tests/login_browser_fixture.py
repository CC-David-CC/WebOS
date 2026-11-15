"""Actual loopback account authority for the Login component browser acceptance test."""
import argparse
import json
from pathlib import Path
from wsgiref.simple_server import make_server
from webos_accounts import AccountsService, Config
from webos_accounts.http_server import BoundedServer, QuietHandler

parser = argparse.ArgumentParser()
parser.add_argument('--public-root', type=Path, required=True)
parser.add_argument('--state-root', type=Path, required=True)
args = parser.parse_args()
server = make_server('127.0.0.1', 0, lambda env, start: (), server_class=BoundedServer, handler_class=QuietHandler)
origin = 'http://127.0.0.1:' + str(server.server_port)
service = AccountsService(Config(args.state_root, args.public_root, origin=origin, rate_per_minute=1000))
server.set_app(service)
print(json.dumps({'origin': origin}), flush=True)
try:
    server.serve_forever()
finally:
    server.server_close()
