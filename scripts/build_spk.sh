#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DIR="${ROOT_DIR}/package"
INFO_FILE="${PACKAGE_DIR}/INFO/package.info"
DIST_DIR="${ROOT_DIR}/dist"
TMP_DIR="${ROOT_DIR}/.tmp-spk-build"
SPK_META_DIR="${ROOT_DIR}/spk"

if [[ ! -f "${INFO_FILE}" ]]; then
  echo "Missing package info: ${INFO_FILE}" >&2
  exit 1
fi

package_name="$(sed -nE 's/^package="([^"]+)"/\1/p' "${INFO_FILE}")"
version="$(sed -nE 's/^version="([^"]+)"/\1/p' "${INFO_FILE}")"

if [[ -z "${package_name}" || -z "${version}" ]]; then
  echo "Failed to parse package/version from ${INFO_FILE}" >&2
  exit 1
fi

required_meta_files=(
  "${SPK_META_DIR}/scripts/start-stop-status"
  "${SPK_META_DIR}/conf/privilege"
  "${SPK_META_DIR}/PACKAGE_ICON.PNG"
  "${SPK_META_DIR}/PACKAGE_ICON_256.PNG"
)

for f in "${required_meta_files[@]}"; do
  if [[ ! -f "${f}" ]]; then
    echo "Missing required SPK metadata file: ${f}" >&2
    exit 1
  fi
done

mkdir -p "${DIST_DIR}"
output_file="${DIST_DIR}/${package_name}-${version}.spk"

# Build Synology SPK layout:
# - INFO        (metadata)
# - package.tgz (payload)
rm -rf "${TMP_DIR}"
mkdir -p "${TMP_DIR}"

cp "${INFO_FILE}" "${TMP_DIR}/INFO"
cp -R "${SPK_META_DIR}/scripts" "${TMP_DIR}/scripts"
cp -R "${SPK_META_DIR}/conf" "${TMP_DIR}/conf"
cp "${SPK_META_DIR}/PACKAGE_ICON.PNG" "${TMP_DIR}/PACKAGE_ICON.PNG"
cp "${SPK_META_DIR}/PACKAGE_ICON_256.PNG" "${TMP_DIR}/PACKAGE_ICON_256.PNG"

if [[ -f "${ROOT_DIR}/LICENSE" ]]; then
  cp "${ROOT_DIR}/LICENSE" "${TMP_DIR}/LICENSE"
fi

PAYLOAD_DIR="${TMP_DIR}/payload"
cp -R "${PACKAGE_DIR}" "${PAYLOAD_DIR}"
chmod 755 "${PAYLOAD_DIR}/start.sh" "${PAYLOAD_DIR}/stop.sh" "${PAYLOAD_DIR}/mullvad_connect.sh" || true
chmod 644 "${PAYLOAD_DIR}/magnet_fetcher.py" || true

tar -C "${PAYLOAD_DIR}" -czf "${TMP_DIR}/package.tgz" \
  --exclude "INFO" \
  --exclude "INFO/*" \
  --exclude "INFO/package.info" \
  .

rm -f "${output_file}"
tar -C "${TMP_DIR}" -czf "${output_file}" \
  INFO \
  package.tgz \
  scripts \
  conf \
  PACKAGE_ICON.PNG \
  PACKAGE_ICON_256.PNG \
  $( [[ -f "${TMP_DIR}/LICENSE" ]] && echo LICENSE )

echo "Built: ${output_file}"
