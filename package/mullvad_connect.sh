#!/bin/sh
# mullvad_connect.sh
# Mullvad WireGuard自動接続スクリプト
# 必要: Mullvadアカウント、WireGuard設定ファイル(mullvad-wg.conf)
set -eu

WG_CONF="${WG_CONF:-/usr/local/etc/mullvad-wg.conf}"
WG_BIN="${WG_BIN:-/usr/local/bin/wg-quick}"
REQUIRE_VPN="${REQUIRE_VPN:-0}"

warn_and_maybe_exit() {
  echo "$1"
  if [ "${REQUIRE_VPN}" = "1" ]; then
    exit 1
  fi
  exit 0
}

if [ ! -f "$WG_CONF" ]; then
  warn_and_maybe_exit "WireGuard設定ファイルが見つかりません: $WG_CONF"
fi

if [ ! -x "$WG_BIN" ]; then
  warn_and_maybe_exit "wg-quickコマンドが見つかりません: $WG_BIN"
fi

$WG_BIN up "$WG_CONF" || warn_and_maybe_exit "WireGuard接続に失敗しました: $WG_CONF"
echo "Mullvad VPN(WireGuard)に接続しました。"
