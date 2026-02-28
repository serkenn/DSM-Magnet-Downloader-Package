#!/bin/sh
# start.sh
# DSMパッケージ起動スクリプト
set -eu

PKG_NAME="dsm-magnet-dl"
VAR_DIR="/var/packages/${PKG_NAME}/var"
PID_FILE="${VAR_DIR}/ui-http.pid"
LOG_FILE="${VAR_DIR}/package.log"
RUNTIME_CONF="${VAR_DIR}/runtime.conf"
UI_PORT="${UI_PORT:-18765}"
PY_BIN=""

mkdir -p "${VAR_DIR}"

if [ -f "${RUNTIME_CONF}" ]; then
  # shellcheck disable=SC1090
  . "${RUNTIME_CONF}"
fi

for CAND in \
  /var/packages/Python3/target/usr/local/bin/python3 \
  /usr/local/bin/python3 \
  /bin/python3 \
  /usr/bin/python3 \
  python3
do
  if [ -x "${CAND}" ]; then
    PY_BIN="${CAND}"
    break
  fi
  if command -v "${CAND}" >/dev/null 2>&1; then
    PY_BIN="$(command -v "${CAND}")"
    break
  fi
done

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

"${PY_BIN}" --version >>"${LOG_FILE}" 2>&1 || true
"${PY_BIN}" "$(dirname "$0")/ui_server.py" >>"${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"
sleep 1
if ! kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "UI server failed to start on port ${UI_PORT}. Check ${LOG_FILE}."
  exit 1
fi

echo "DSM Magnet Downloaderパッケージ起動完了"
