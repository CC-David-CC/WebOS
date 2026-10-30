"""Shared TLS passthrough for websites/ACME and the isolated TURN relay."""
import re
from pathlib import Path

LISTENER_WRAPPERS = [
    '\t\tlistener_wrappers {', '\t\t\tproxy_protocol {', '\t\t\t\ttimeout 1s',
    '\t\t\t\tallow 127.0.0.1/32', '\t\t\t\tfallback_policy reject',
    '\t\t\t}', '\t\t\ttls', '\t\t}',
]
GLOBAL_OPTIONS = ['\thttp_port 8080', '\thttps_port 8443', '\tdefault_bind 127.0.0.1']


def haproxy(*, http_bind='[::]:80 v4v6', tls_bind='[::]:443 v4v6',
            http_backend=8080, tls_backend=8443, turn_backend=13479,
            stats='/run/codi-shared-ingress/stats.sock'):
    for value in [http_bind, tls_bind]:
        if not re.fullmatch(r'[a-fA-F0-9:.\[\],]+(?: v4v6)?', value):
            raise ValueError('Explicit IP bind required')
    for port in [http_backend, tls_backend, turn_backend]:
        if type(port) is not int or not 1024 <= port <= 65535:
            raise ValueError('Unprivileged fixed backend port required')
    if not re.fullmatch(r'/run/(?:user/[0-9]+/)?[a-zA-Z0-9._/-]+', str(stats)) or '..' in Path(stats).parts:
        raise ValueError('Private runtime stats socket required')
    return f'''global
 maxconn 1024
 nbthread 2
 stats socket {stats} mode 600 level admin
defaults
 mode tcp
 timeout connect 5s
 timeout client 1h
 timeout server 1h
 timeout client-fin 10s
 timeout server-fin 10s
frontend web_http
 bind {http_bind}
 default_backend web_plain
frontend shared_tls
 bind {tls_bind}
 tcp-request inspect-delay 5s
 tcp-request content accept if {{ req.ssl_hello_type 1 }}
 acl turn_name req.ssl_sni -i turn.ksu.codes
 use_backend web_tls if {{ req.ssl_alpn acme-tls/1 }}
 use_backend turn_tls if turn_name
 default_backend web_tls
backend web_plain
 server web 127.0.0.1:{http_backend} send-proxy-v2
backend web_tls
 server web 127.0.0.1:{tls_backend} send-proxy-v2
backend turn_tls
 server turn 127.0.0.1:{turn_backend}
'''


def service(binary, config, *, instance='codi-shared-ingress'):
    if len(instance)>31 or not re.fullmatch(r'codi-shared-ingress(?:-[a-z0-9-]+)?', instance):
        raise ValueError('Managed ingress instance required')
    for value in [binary, config]:
        if not re.fullmatch(r'/[a-zA-Z0-9._/-]+', str(value)) or '..' in Path(value).parts:
            raise ValueError('Canonical protected executable/config path required')
    return f'''[Unit]
Description=Codi shared website and TURN TLS ingress
Requires=caddy.service webhost-firewall.service
After=caddy.service webhost-firewall.service

[Service]
Type=exec
DynamicUser=yes
User={instance}
RuntimeDirectory={instance}
RuntimeDirectoryMode=0700
ExecStart={binary} -db -f {config}
Restart=on-failure
RestartSec=2s
TimeoutStopSec=10s
NoNewPrivileges=yes
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
RestrictNamespaces=yes
RestrictSUIDSGID=yes
LockPersonality=yes
UMask=0077
MemoryMax=128M
TasksMax=32
LimitNOFILE=8192
'''


def caddy_dependency():
    # Caddy is already boot-enabled. Its ordinary start also starts ingress,
    # preserving website availability after reboot; native roles stay disabled.
    return '[Unit]\nWants=codi-shared-ingress.service\nBefore=codi-shared-ingress.service\n'
