#!/bin/sh
# Starts all Apptainer instances by calling the start scripts in each odda_* directory.

SCRIPT_DIR=$(dirname "$0")

echo "Starting DIA-NN instances..."
sh "${SCRIPT_DIR}/odda_diann/start_diann_instances.sh"

echo "Starting MaxQuant instances..."
sh "${SCRIPT_DIR}/odda_maxquant/start_maxquant_instances.sh"

echo "Starting ThermoFisher instances..."
sh "${SCRIPT_DIR}/odda_thermofisher/start_thermofisher_instance.sh"

echo "All instances started."
