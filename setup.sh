#!/bin/bash

# YouTube Channel RAG Tool - Setup Script
# This script sets up the development environment

set -e

echo "================================================"
echo "YouTube Channel RAG Tool - Setup"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "Dependencies installed successfully"

# Check if .env file exists
echo ""
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your API keys:"
    echo "  - APIFY_API_TOKEN (get from: https://console.apify.com/account/integrations)"
    echo "  - GOOGLE_API_KEY (get from: https://aistudio.google.com/app/apikey)"
    echo ""
else
    echo ".env file found"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p temp_transcripts
mkdir -p backend/__pycache__
echo "Directories created"

# Run tests
echo ""
echo "Running basic tests..."
python3 -m py_compile backend/apify_service.py && echo "  ✓ apify_service.py"
python3 -m py_compile backend/gemini_service.py && echo "  ✓ gemini_service.py"
python3 -m py_compile backend/app.py && echo "  ✓ app.py"
python3 -m py_compile backend/utils.py && echo "  ✓ utils.py"

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: ./start.sh"
echo "3. Open: http://localhost:5000"
echo ""
