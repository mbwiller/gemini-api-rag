#!/bin/bash

# YouTube Channel RAG Backend - Start Script

echo "========================================="
echo "YouTube Channel RAG Backend"
echo "========================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your API keys before continuing."
    echo "Press Enter when ready..."
    read
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Testing service connections..."
python backend/test_services.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Starting Flask server..."
    echo "Server will be available at: http://localhost:5000"
    echo ""
    python backend/app.py
else
    echo ""
    echo "❌ Service tests failed. Please fix the issues and try again."
    exit 1
fi
