#!/usr/bin/env bash
# Runs the Apptainer build scripts for all MCP server packages (odda_diann, odda_maxquant, odda_thermofisher).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BUILD_SCRIPTS=(
    "${SCRIPT_DIR}/odda_diann/static/apptainer/build_images.sh"
    "${SCRIPT_DIR}/odda_maxquant/static/apptainer/build_images.sh"
    "${SCRIPT_DIR}/odda_thermofisher/static/apptainer/build_images.sh"
)

failed=0

for script in "${BUILD_SCRIPTS[@]}"; do
    if [[ ! -f "$script" ]]; then
        echo "Warning: Build script not found: ${script}" >&2
        failed=1
        continue
    fi

    echo "=== Running $(basename "$(dirname "$(dirname "$(dirname "$script")")")") ==="
    if bash "$script"; then
        echo ""
    else
        echo "Error: ${script} exited with status $?" >&2
        failed=1
        echo ""
    fi
done

if [[ $failed -ne 0 ]]; then
    echo "Some builds had warnings or errors."
    exit 1
fi

echo "All builds complete."
