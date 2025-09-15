#!/bin/bash

# Background Remover Pro - Main Script
# Enhanced version with quality options and transparency fixes

echo "======================================"
echo "🎨 BACKGROUND REMOVER PRO"
echo "======================================"
echo

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Show menu
echo "Choose an option:"
echo "1) Remove background of images in Input"
echo "2) Exit"
echo

read -p "Enter your choice (1-2): " choice

case $choice in
    1)
        echo
        echo "🚀 Starting standard processing..."
        echo
        python process_images_enhanced.py
        ;;
    2)
        echo "Exiting..."
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        ;;
esac

# Deactivate virtual environment
deactivate