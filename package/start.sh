#!/bin/sh
# start.sh
# DSMパッケージ起動スクリプト
set -eu

PKG_NAME="dsm-magnet-dl"
VAR_DIR="/var/packages/${PKG_NAME}/var"
PID_FILE="${VAR_DIR}/ui-http.pid"
LOG_FILE="${VAR_DIR}/package.log"
UI_DIR="$(dirname "$0")/ui"
UI_PORT="${UI_PORT:-18765}"
PY_BIN="$(command -v python3 || true)"

mkdir -p "${VAR_DIR}"

# VPN接続
"$(dirname "$0")/mullvad_connect.sh"

# Local UI server for DSM "Open" button.
if [ -f "${PID_FILE}" ] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "UI server is already running on port ${UI_PORT}."
  exit 0
fi

if [ -z "${PY_BIN}" ]; then
  echo "python3 command is not available. Please install Python3 package on DSM."
  exit 1
fi

"${PY_BIN}" "$(dirname "$0")/ui_server.py" >>"${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"

echo "DSM Magnet Downloaderパッケージ起動完了"
