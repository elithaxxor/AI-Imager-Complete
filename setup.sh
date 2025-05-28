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

# Load environment variables if using .env (optional, adjust path as needed)
if [ -f "./project_files/.env" ]; then
  export $(grep -v '^#' ./project_files/.env | xargs)
elif [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Automatically initialize and update the SQLAlchemy database
echo "Initializing the database..."
python3 database.py

# If you want to also initialize the alternate/project_files database, uncomment:
# python3 project_files/database.py

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
