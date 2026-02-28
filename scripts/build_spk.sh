#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DIR="${ROOT_DIR}/package"
INFO_FILE="${PACKAGE_DIR}/INFO/package.info"
DIST_DIR="${ROOT_DIR}/dist"

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

rm -f "${output_file}"
tar -C "${ROOT_DIR}" -czf "${output_file}" package

echo "Built: ${output_file}"
