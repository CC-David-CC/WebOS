#!/usr/bin/env bash
set -euo pipefail
umask 077

case ${1:-} in
    preview | seed | reset) operation=$1 ;;
    *) echo 'Use preview, seed, or reset. Preview and reset accept --cleanup-files.' >&2; exit 64 ;;
esac
shift
args=()
if (( $# )); then
    if [[ "$operation" == seed || $# != 1 || "$1" != --cleanup-files ]]; then
        echo 'Only preview and reset accept --cleanup-files.' >&2
        exit 64
    fi
    args+=("$1")
fi
base=${WEBOS_TEST_ROOT:?Set the installation root for this test site}
driver=/usr/local/libexec/webos-ksu-test-maintenance/reset-test-accounts.py
database="$base/private/account-state/identity/accounts.sqlite3"
packages=${WEBOS_TEST_RESET_PACKAGES:-}
if (( ${#args[@]} )) && [[ -n "$packages" ]]; then
    if [[ ! "$packages" =~ ^/srv/webos-guest-network/releases/[0-9a-f]{64}/packages$ || ! -d "$packages" || -L "$packages" ]]; then
        echo 'Expected the installed WebOS backend packages.' >&2
        exit 78
    fi
    exec "$base/environment/bin/python" -I -B -c \
        'import runpy, sys; sys.path.insert(0, sys.argv[1]); sys.argv = sys.argv[2:]; runpy.run_path(sys.argv[0], run_name="__main__")' \
        "$packages" "$driver" "$operation" "$database" "${args[@]}"
fi
exec "$base/environment/bin/python" -I -B "$driver" "$operation" "$database" "${args[@]}"
