#!/bin/bash

# Gold Trading Bot - Development Setup (No Docker Required)
# Quick setup for development without Docker dependencies

set -e

echo "🏆 Gold Trading Bot - Development Setup"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python installation
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python ${python_version} is installed"
}

# Check Node.js installation
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 16+ first."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    node_version=$(node --version)
    npm_version=$(npm --version)
    print_success "Node.js ${node_version} and npm ${npm_version} are installed"
}

# Setup backend
setup_backend() {
    print_status "Setting up Python backend..."
    
    cd backend
    
    # Create virtual environment
    print_status "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    
    # Use simplified requirements for better compatibility
    if [ -f "requirements-simple.txt" ]; then
        print_status "Using simplified requirements for compatibility..."
        pip install -r requirements-simple.txt
    elif [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    else
        pip install -r requirements.txt
    fi
    
    # Create environment file
    if [ ! -f ".env" ]; then
        print_status "Creating backend environment file..."
        cat > .env << EOF
# Development Configuration
DATABASE_URL=sqlite:///./gold_trading.db
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "dev-secret-key-change-in-production")
DEBUG=true
LOG_LEVEL=INFO

# MetaTrader 5 Settings
MT5_SERVER=LiteFinance-Demo
MT5_TIMEOUT=60000

# Telegram Configuration
TELEGRAM_BOT_TOKEN=8348419204:AAEEr0DQfcBmwwWssvTu-ljg94C19qUPim8
TELEGRAM_CHAT_ID=-1002481438774
TELEGRAM_ENABLED=true

# Trading Settings
DEFAULT_SYMBOL=XAUUSD
DEFAULT_LOT_SIZE=0.01
DEFAULT_STOP_LOSS=50
DEFAULT_TAKE_PROFIT=100
MAX_SPREAD=5.0
RISK_PERCENTAGE=2.0
MAX_DAILY_TRADES=10

# CORS Settings
ALLOWED_HOSTS=http://localhost:3000,*
EOF
        print_success "Backend environment file created"
    else
        print_warning "Backend environment file already exists"
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up React frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create environment file
    if [ ! -f ".env" ]; then
        print_status "Creating frontend environment file..."
        cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
GENERATE_SOURCEMAP=false
EOF
        print_success "Frontend environment file created"
    else
        print_warning "Frontend environment file already exists"
    fi
    
    cd ..
    print_success "Frontend setup completed"
}

# Create start scripts
create_start_scripts() {
    print_status "Creating startup scripts..."
    
    # Backend start script
    cat > start-backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Gold Trading Bot Backend..."
cd backend

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Start the backend
echo "Backend starting at http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF

    # Frontend start script
    cat > start-frontend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Gold Trading Bot Frontend..."
cd frontend
echo "Frontend starting at http://localhost:3000"
npm start
EOF

    # Make scripts executable
    chmod +x start-backend.sh start-frontend.sh
    
    print_success "Startup scripts created"
}

# Display instructions
display_instructions() {
    echo ""
    echo "🎉 Development setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "📱 **Next Steps:**"
    echo ""
    echo "1. **Start the Backend:**"
    echo "   ./start-backend.sh"
    echo "   OR manually:"
    echo "   cd backend && source venv/bin/activate && uvicorn main:app --reload"
    echo ""
    echo "2. **Start the Frontend (in another terminal):**"
    echo "   ./start-frontend.sh"
    echo "   OR manually:"
    echo "   cd frontend && npm start"
    echo ""
    echo "3. **Access the Application:**"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "🔐 **Default Login:**"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "⚠️  **Development Notes:**"
    echo "   - Using SQLite database (no PostgreSQL required)"
    echo "   - MetaTrader 5 integration requires MT5 installation"
    echo "   - Telegram notifications are pre-configured"
    echo ""
    echo "📚 **Useful Commands:**"
    echo "   Backend logs: tail -f backend/logs/app.log"
    echo "   Stop services: Ctrl+C in each terminal"
    echo ""
}

# Main setup function
main() {
    print_status "Starting development environment setup..."
    echo ""
    
    check_python
    check_node
    setup_backend
    setup_frontend
    create_start_scripts
    display_instructions
}

# Handle script interruption
trap 'print_error "Setup interrupted"; exit 1' INT TERM

# Run main function
main "$@"