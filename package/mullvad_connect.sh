#!/bin/sh
# mullvad_connect.sh
# Mullvad WireGuard自動接続スクリプト
# 必要: Mullvadアカウント、WireGuard設定ファイル(mullvad-wg.conf)

WG_CONF="/usr/local/etc/mullvad-wg.conf"
WG_BIN="/usr/local/bin/wg-quick"

if [ ! -f "$WG_CONF" ]; then
  echo "WireGuard設定ファイルが見つかりません: $WG_CONF"
  exit 1
fi

if [ ! -x "$WG_BIN" ]; then
  echo "wg-quickコマンドが見つかりません: $WG_BIN"
  exit 1
fi

sudo $WG_BIN up "$WG_CONF"
echo "Mullvad VPN(WireGuard)に接続しました。"
