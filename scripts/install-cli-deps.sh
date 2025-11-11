#!/bin/bash
# Install Super-Agents CLI dependencies

echo "Installing Super-Agents CLI Dependencies..."
echo ""

# Detect Python
if command -v python3 &> /dev/null; then
    PIP_CMD="pip3"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PIP_CMD="pip"
    PYTHON_CMD="python"
else
    echo "Error: Python not found. Please install Python 3.7 or later."
    exit 1
fi

echo "Using: $PYTHON_CMD ($($PYTHON_CMD --version))"
echo ""

# Install requirements
echo "Installing dependencies from requirements-cli.txt..."
$PIP_CMD install -r requirements-cli.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Installation complete!"
    echo ""
    echo "You can now run:"
    echo "  python3 cli.py init"
    echo ""
else
    echo ""
    echo "✗ Installation failed."
    echo ""
    echo "Try manual installation:"
    echo "  $PIP_CMD install click rich questionary tabulate"
    exit 1
fi
