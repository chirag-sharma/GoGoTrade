#!/bin/bash

# GoGoTrade System Startup Script
# This script helps you start the GoGoTrade system properly

echo "🚀 GoGoTrade System Startup"
echo "=========================="

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   cd backend && ./startup.sh"
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "   $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No virtual environment detected. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        echo "🔄 Activating virtual environment..."
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    fi
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"

# Check if database needs initialization
echo "🗄️  Checking database..."
if [ ! -f "gogotrade.db" ]; then
    echo "   Initializing database..."
    python scripts/init_db.py
    echo "✅ Database initialized"
else
    echo "✅ Database found"
fi

# Start the server
echo ""
echo "🌐 Starting GoGoTrade server..."
echo "   Server will be available at: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Start with auto-reload for development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
