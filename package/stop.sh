#!/bin/sh
# stop.sh
# DSMパッケージ停止スクリプト
set -eu

# VPN切断
WG_BIN="/usr/local/bin/wg-quick"
WG_CONF="/usr/local/etc/mullvad-wg.conf"

if [ -x "$WG_BIN" ]; then
  $WG_BIN down "$WG_CONF" || true
fi

echo "DSM Magnet Downloaderパッケージ停止完了"
