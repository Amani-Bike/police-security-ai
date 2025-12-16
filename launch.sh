#!/bin/bash

# Cross-platform launcher script for Police Security AI Platform
echo "============================================"
echo "SafetyNet - Police Security AI Platform"
echo "============================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    if command_exists "python3"; then
        python3 -m pip install -r requirements.txt
    elif command_exists "python"; then
        python -m pip install -r requirements.txt
    else
        echo "Error: Python is not installed or not in PATH."
        exit 1
    fi
else
    echo "Warning: requirements.txt not found"
fi

# Initialize the database
echo ""
echo "Initializing database..."
if [ -f "init_db.py" ]; then
    if command_exists "python3"; then
        python3 init_db.py
    elif command_exists "python"; then
        python init_db.py
    fi
else
    echo "Warning: init_db.py not found"
fi

# Start the server
echo ""
echo "Starting the server..."
echo "Visit http://localhost:8000 in your browser"
echo "Press Ctrl+C to stop the server"
echo ""

if command_exists "python3"; then
    exec python3 -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
elif command_exists "python"; then
    exec python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
else
    echo "Error: Python is not available"
    exit 1
fi