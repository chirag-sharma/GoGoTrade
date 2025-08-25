#!/bin/bash

# GoGoTrade Backend Startup Script
echo "Starting GoGoTrade FastAPI Backend..."

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install fastapi uvicorn[standard] pydantic-settings python-dotenv

# Start the FastAPI server
echo "Starting server at http://127.0.0.1:8000"
echo "API Documentation available at http://127.0.0.1:8000/docs"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
