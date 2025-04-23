#!/bin/bash

# Optional: name of your conda env
CONDA_ENV_NAME="corelink-poc"

# Optional: number of seconds to wait before running test.py
WAIT_SECONDS=2

# Activate conda environment (adjust path if needed)
source ~/anaconda3/etc/profile.d/conda.sh
conda activate "$CONDA_ENV_NAME"

# Run sender script
echo "Starting sendertester.py..."
python sendertester.py &

# Wait before starting test.py
echo "Waiting $WAIT_SECONDS seconds for sender to initialize..."
sleep "$WAIT_SECONDS"

# Run test script
echo "Starting test.py..."
python test.py
