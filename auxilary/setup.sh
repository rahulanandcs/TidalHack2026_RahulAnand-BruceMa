#!/bin/bash

# Resume Parser - Quick Setup Script

echo "========================================="
echo "Resume Parser - Quick Setup"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================="
echo "✓ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate   (Mac/Linux)"
echo "   venv\\Scripts\\activate      (Windows)"
echo ""
echo "2. Test the parser:"
echo "   python test_parser.py"
echo ""
echo "3. Parse a resume:"
echo "   python resume_parser.py your_resume.pdf"
echo ""
echo "Happy parsing! 🚀"
