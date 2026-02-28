#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DIR="${ROOT_DIR}/package"
INFO_FILE="${PACKAGE_DIR}/INFO/package.info"
DIST_DIR="${ROOT_DIR}/dist"
TMP_DIR="${ROOT_DIR}/.tmp-spk-build"

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

mkdir -p "${DIST_DIR}"
output_file="${DIST_DIR}/${package_name}-${version}.spk"

# Build Synology SPK layout:
# - INFO        (metadata)
# - package.tgz (payload)
rm -rf "${TMP_DIR}"
mkdir -p "${TMP_DIR}"

cp "${INFO_FILE}" "${TMP_DIR}/INFO"
tar -C "${PACKAGE_DIR}" -czf "${TMP_DIR}/package.tgz" \
  --exclude "INFO" \
  --exclude "INFO/*" \
  --exclude "INFO/package.info" \
  .

rm -f "${output_file}"
tar -C "${TMP_DIR}" -cf "${output_file}" INFO package.tgz

echo "Built: ${output_file}"
