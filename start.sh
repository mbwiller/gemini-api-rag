#!/bin/bash

# YouTube Channel RAG Tool - Start Script
# This script starts the Flask server

set -e

echo "================================================"
echo "YouTube Channel RAG Tool - Starting Server"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run: ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found"
    echo "Please create .env file with your API keys"
    exit 1
fi

# Check environment variables
if ! grep -q "APIFY_API_TOKEN=.\+" .env; then
    echo "Warning: APIFY_API_TOKEN not set in .env"
fi

if ! grep -q "GOOGLE_API_KEY=.\+" .env; then
    echo "Warning: GOOGLE_API_KEY not set in .env"
fi

# Start the server
echo "Starting Flask server..."
echo "Server will be available at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python backend/app.py
