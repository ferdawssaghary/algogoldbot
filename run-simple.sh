#!/bin/bash

echo "🏆 Gold Trading Bot - Simple Demo"
echo "================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if we can run the frontend
if [ -d "frontend" ]; then
    print_status "Setting up minimal frontend demo..."
    cd frontend
    
    # Check if Node.js is available
    if command -v npm &> /dev/null; then
        print_status "Installing frontend dependencies..."
        npm install --silent
        
        print_status "Starting frontend in development mode..."
        print_success "Frontend will be available at: http://localhost:3000"
        print_success "This is a functional demo with:"
        echo "  ✅ Responsive React interface"
        echo "  ✅ Bilingual support (English/Farsi)"
        echo "  ✅ Modern Material-UI design"
        echo "  ✅ Trading dashboard mockup"
        echo "  ✅ Authentication interface"
        echo "  ✅ Real-time WebSocket placeholder"
        echo ""
        echo "🔐 Default Login: admin / admin123"
        echo ""
        npm start
    else
        echo "Node.js not found. Please install Node.js to run the frontend demo."
    fi
else
    echo "Frontend directory not found."
fi