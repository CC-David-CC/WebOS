#!/usr/bin/env bash
# Run maintenance while the ordinary Stalwart service is stopped.
set -euo pipefail
umask 077
root=/srv/data/webos-mailcraft
service=webos-mailcraft.service
recovery=webos-mailcraft-maintenance.service
guard=mailcraft_maintenance
action=${1:?Specify setup, list, provision, bind, grant, revoke or apply}
shift
[[ $(id -u) == 0 && $(hostname -s) == box-webhost ]]
if [[ "$action" == list ]]; then
    exec python3 "$root/bin/policy.py" "$root/mailcraft-access.sqlite" list
fi
case "$action" in
    setup|bind|grant|revoke|apply|provision|upgrade-pilot) ;;
    *) printf 'Unknown MailCraft maintenance action\n' >&2; exit 1 ;;
esac
exec 8>"$root/operator/maintenance.lock"
flock -n 8
if systemctl is-active --quiet "$service" || [[ -n $(ss -lntH 'sport = :28880') ]]; then
    printf 'Stop the running MailCraft service before maintenance.\n' >&2
    exit 1
fi
if nft list table inet "$guard" >/dev/null 2>&1; then
    printf 'Unexpected existing MailCraft maintenance firewall table.\n' >&2
    exit 1
fi

nft -f - <<'NFT'
table inet mailcraft_maintenance {
    chain input {
        type filter hook input priority -30; policy accept;
        iifname != "lo" tcp dport 28880 drop
    }
}
NFT
cleanup() {
    systemctl stop "$recovery" 2>/dev/null || true
    rm -f -- "$root/secrets/recovery.json"
    nft delete table inet "$guard"
}
trap cleanup EXIT
openssl rand -hex 32 | jq -Rn '{username:"mailcraft-maintenance",secret:input}' > "$root/secrets/recovery.json"
chown webos-mailcraft:webos-mailcraft "$root/secrets/recovery.json"
systemd-run --quiet --unit="$recovery" --property=User=webos-mailcraft --property=UMask=0077 \
    --working-directory="$root" --setenv=STALWART_RECOVERY_MODE=1 --setenv=STALWART_RECOVERY_MODE_PORT=28880 \
    --setenv=STALWART_HOSTNAME=mail.ksu.codes --setenv=STALWART_PUBLIC_URL=https://ksu.codes \
    /bin/sh -c 'export STALWART_RECOVERY_ADMIN="$(jq -r ".username+\":\"+.secret" secrets/recovery.json)"; exec bin/stalwart --config config.json >logs/maintenance.log 2>&1'
ready=0
for _ in {1..220}; do
    if curl -sS --max-time 1 http://127.0.0.1:28880/jmap/session >/dev/null 2>&1; then ready=1; break; fi
    systemctl is-active --quiet "$recovery" || break
    sleep .25
done
(( ready ))
if [[ "$action" == setup ]]; then
    python3 "$root/bin/configure_service.py" "$root" "$root/secrets/recovery.json"
    runuser -u webos-mailcraft -- python3 "$root/bin/configure_relay.py" "$root/secrets/recovery.json" "$root/secrets/smtp2go"
else
    python3 "$root/bin/policy.py" "$root/mailcraft-access.sqlite" --recovery "$root/secrets/recovery.json" "$action" "$@"
fi
