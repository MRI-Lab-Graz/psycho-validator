#!/bin/bash
# Setup script for BIDS GUI Dataset Description

set -e

echo "=================================="
echo "BIDS GUI Setup Script"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  UV not found. Attempting to install UV..."
    pip install uv
fi

echo "✓ UV is available"

# Create virtual environment
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "✓ Virtual environment activated"

# Install dependencies using UV
echo ""
echo "Installing dependencies using UV..."
uv pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "=================================="
echo "✓ Setup complete!"
echo "=================================="
echo ""
echo "To run the application:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Run: python main.py"
echo ""
echo "To load a specific BIDS dataset:"
echo "  python main.py /path/to/BIDS"
echo ""
