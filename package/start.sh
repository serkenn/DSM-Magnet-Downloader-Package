#!/bin/sh
# start.sh
# DSMパッケージ起動スクリプト
set -eu

# VPN接続
"$(dirname "$0")/mullvad_connect.sh"

# Transmission起動（DSM標準サービス利用を推奨）
# /usr/local/bin/transmission-daemon -g /usr/local/etc/transmission &

echo "DSM Magnet Downloaderパッケージ起動完了"
