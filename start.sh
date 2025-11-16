#!/bin/bash
# Startup script for Home Departure Board

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the Flask server
echo "Starting Home Departure Board server..."
echo "Dashboard will be available at: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py

