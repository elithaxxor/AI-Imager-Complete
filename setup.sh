#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required libraries
pip install -r requirements.txt

# Find the main Streamlit app (edit this if your entry file is different)
APP_FILE="app.py"
if [ ! -f "$APP_FILE" ]; then
  # Try to find the most likely Streamlit file
  APP_FILE=$(ls *.py | grep -i streamlit | head -n 1)
  if [ -z "$APP_FILE" ]; then
    echo "Could not find the main Streamlit app file. Please update setup.sh with the correct filename."
    exit 1
  fi
fi

# Run the Streamlit app
streamlit run "$APP_FILE"
