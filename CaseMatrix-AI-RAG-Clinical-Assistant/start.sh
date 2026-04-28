#!/bin/bash
# CaseMatrix AI - Quick Start Script
# This script sets up and runs the application

echo "🏥 CaseMatrix AI - Clinical Case Intelligence Tool"
echo "=================================================="
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python 3 found"
echo ""

# Navigate to backend
echo "📦 Installing dependencies..."
cd backend

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Install dependencies
pip install -r requirements.txt

echo ""
echo "✅ Dependencies installed successfully!"
echo ""
echo "🚀 Starting CaseMatrix AI Backend Server..."
echo ""
echo "The server will start on: http://127.0.0.1:5000"
echo ""
echo "🌐 Frontend: Open frontend/templates/index.html in your browser"
echo ""
echo "📝 API Documentation:"
echo "   - POST http://127.0.0.1:5000/query - Clinical case search"
echo "   - GET http://127.0.0.1:5000/api/health - Server health check"
echo "   - GET http://127.0.0.1:5000/api/cases/stats - Database statistics"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python app.py
