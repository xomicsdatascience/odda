#!/usr/bin/env bash
# Builds the Salmon Apptainer image from salmon.def.
# The Salmon version is taken from the first positional argument, then the
# SALMON_VERSION environment variable, then the SALMON_VERSION default declared
# in salmon.def. The self-contained `salmon` binary in this directory is
# embedded into the image via the def file's %files section.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEF_FILE="${SCRIPT_DIR}/salmon.def"

if [[ ! -f "$DEF_FILE" ]]; then
    echo "Error: Definition file not found: ${DEF_FILE}" >&2
    exit 1
fi

# Determine the Salmon version: explicit arg > env var > default in salmon.def.
version="${1:-${SALMON_VERSION:-}}"
if [[ -z "$version" ]]; then
    version="$(grep -oP 'SALMON_VERSION\s*=\s*\K[0-9][0-9A-Za-z.\-]*' "$DEF_FILE" | head -1)"
fi

if [[ -z "$version" ]]; then
    echo "Error: Could not determine Salmon version. Pass it as the first argument, set SALMON_VERSION, or declare it in ${DEF_FILE}." >&2
    exit 1
fi

echo "Salmon version: ${version}"

if [[ ! -f "${SCRIPT_DIR}/salmon" ]]; then
    echo "Error: Salmon binary not found at ${SCRIPT_DIR}/salmon (required by %files in salmon.def)." >&2
    exit 1
fi

output="${SCRIPT_DIR}/salmon_v${version}.sif"
if [[ -f "$output" ]]; then
    echo "Skipping ${version}: ${output} already exists"
    exit 0
fi

echo "Building image for Salmon ${version}..."
# %files paths in the def are resolved relative to the build working directory,
# so run the build from the directory that contains the salmon binary.
cd "${SCRIPT_DIR}"
if apptainer build \
    --build-arg "SALMON_VERSION=${version}" \
    "$output" \
    "$DEF_FILE" > /dev/null; then
    echo "Built: ${output}"
else
    echo "Error: Build failed for Salmon ${version}" >&2
    exit 1
fi

echo "Done."
