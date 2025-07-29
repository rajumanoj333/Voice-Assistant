#!/bin/bash

# Voice Assistant with Supabase - Setup Script
# This script automates the setup process

set -e  # Exit on any error

echo "🚀 Voice Assistant with Supabase - Automated Setup"
echo "=================================================="

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    if ! python3 -m venv venv 2>/dev/null; then
        echo "❌ Failed to create virtual environment."
        echo "On Ubuntu/Debian systems, you may need to install python3-venv:"
        echo "  sudo apt install python3-venv"
        echo ""
        echo "Alternative: Install packages system-wide (not recommended for development):"
        echo "  pip3 install --break-system-packages -r requirements.txt"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "The .env file should already exist with Supabase credentials."
    echo "Please ensure the .env file is present and contains:"
    echo "  - SUPABASE_URL"
    echo "  - SUPABASE_KEY"
    echo "  - OPENAI_API_KEY (add your key)"
    echo "  - GOOGLE_APPLICATION_CREDENTIALS (add your path)"
    exit 1
else
    echo "✅ .env file found"
fi

# Run setup verification
echo "🧪 Running setup verification..."
python setup_verification.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with your OpenAI API key and Google Cloud credentials"
echo "2. Run the Supabase schema in your Supabase dashboard (supabase_schema.sql)"
echo "3. Start the application:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "Visit http://localhost:8000/docs for the API documentation"