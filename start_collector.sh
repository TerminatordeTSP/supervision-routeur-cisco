#!/bin/bash

# Create the run flag if it doesn't exist
touch run.flag

# Set the Python environment
source .env/bin/activate

# Install any required dependencies
pip install -r requirements.txt

# Start the collector
python collect_metrics.py

echo "Collector started. View the dashboard at http://localhost:8000"
