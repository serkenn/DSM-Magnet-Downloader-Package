#!/bin/sh
# stop.sh
# DSMパッケージ停止スクリプト
set -eu

PKG_NAME="dsm-magnet-dl"
VAR_DIR="/var/packages/${PKG_NAME}/var"
PID_FILE="${VAR_DIR}/ui-http.pid"

# VPN切断
WG_BIN="/usr/local/bin/wg-quick"
WG_CONF="/usr/local/etc/mullvad-wg.conf"

if [ -x "$WG_BIN" ]; then
  $WG_BIN down "$WG_CONF" || true
fi

if [ -f "${PID_FILE}" ]; then
  PID="$(cat "${PID_FILE}")"
  if kill -0 "${PID}" 2>/dev/null; then
    kill "${PID}" || true
  fi
  rm -f "${PID_FILE}"
fi

echo "DSM Magnet Downloaderパッケージ停止完了"
