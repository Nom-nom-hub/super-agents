#!/bin/bash

# Script to format all markdown files in the project using mdformat

set -e  # Exit on any error

echo "Formatting all markdown files in the project..."

# Find and format all markdown files
find . -name "*.md" -exec python3 -m mdformat {} \;

echo "All markdown files have been formatted successfully!"