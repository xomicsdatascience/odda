#!/usr/bin/env bash
# Installs ODDA and its submodules into a virtual environment.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON="${PYTHON:-python3}"
VENV_DIR=".venv"

# Check Python version
if ! "$PYTHON" -c "import sys; assert sys.version_info >= (3, 11)" 2>/dev/null; then
    echo "Error: Python >= 3.11 is required." >&2
    exit 1
fi

# Check /data/ directories
DATA_DIRS=("/data/articles" "/data/datasets" "/data/quantified" "/data/supporting" "/data/code")
for dir in "${DATA_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "Warning: $dir already exists."
    else
        echo "Creating $dir..."
        mkdir -p "$dir" || { echo "Error: Failed to create $dir. You may need to run with sudo or create it manually." >&2; exit 1; }
    fi
done

# Ensure submodules are initialized
git submodule update --init --recursive

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# Get dotnet for MaxQuant:
mkdir -p odda_maxquant/static/apptainer/dotnet/
wget https://download.visualstudio.microsoft.com/download/pr/dd6ee0c0-6287-4fca-85d0-1023fc52444b/874148c23613c594fc8f711fc0330298/dotnet-sdk-8.0.302-linux-x64.tar.gz -P odda_maxquant/static/apptainer/
tar -xzf odda_maxquant/static/apptainer/dotnet-sdk-8.0.302-linux-x64.tar.gz -C odda_maxquant/static/apptainer/dotnet/
rm odda_maxquant/static/apptainer/dotnet-sdk-8.0.302-linux-x64.tar.gz

echo "Upgrading pip..."
pip install --upgrade pip

# Install submodules and local packages in editable mode
echo "Installing packages..."
pip install -e odda_utils
pip install -e odda_diann
pip install -e odda_maxquant
pip install -e odda_thermofisher
pip install -e request_visualization

echo ""
echo "Installation complete. Activate the environment with:"
echo "  source $VENV_DIR/bin/activate"
