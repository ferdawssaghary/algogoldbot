#!/bin/bash

# Gold Trading Bot Deployment Script
# Automated deployment for Replit and local environments

set -e

echo "🏆 Gold Trading Bot - Deployment Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        print_status "See DOCKER_SETUP.md for installation instructions"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        print_status "See DOCKER_SETUP.md for installation instructions"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        print_status "Solutions:"
        print_status "  - Windows: Start Docker Desktop"
        print_status "  - Linux: sudo systemctl start docker"
        print_status "  - See DOCKER_SETUP.md for detailed instructions"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed and running"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f "backend/.env" ]; then
        print_status "Creating environment configuration..."
        
        cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://goldtrader:securepassword123@postgres:5432/gold_trading_bot

# Security Settings
SECRET_KEY=$(openssl rand -hex 32)

# MetaTrader 5 Settings
MT5_SERVER=LiteFinance-Demo
MT5_TIMEOUT=60000

# Telegram Configuration
TELEGRAM_BOT_TOKEN=8348419204:AAEEr0DQfcBmwwWssvTu-ljg94C19qUPim8
TELEGRAM_CHAT_ID=-1002481438774
TELEGRAM_ENABLED=true

# Application Settings
DEBUG=true
LOG_LEVEL=INFO

# Trading Settings
DEFAULT_SYMBOL=XAUUSD
DEFAULT_LOT_SIZE=0.01
DEFAULT_STOP_LOSS=50
DEFAULT_TAKE_PROFIT=100
MAX_SPREAD=5.0
RISK_PERCENTAGE=2.0
MAX_DAILY_TRADES=10

# CORS Settings
ALLOWED_HOSTS=http://localhost:3000,http://frontend:3000,*
EOF
        
        print_success "Environment file created at backend/.env"
    else
        print_warning "Environment file already exists at backend/.env"
    fi
}

# Setup SSL certificates for production
setup_ssl() {
    if [ ! -d "nginx/ssl" ]; then
        print_status "Setting up SSL certificates..."
        mkdir -p nginx/ssl
        
        # Generate self-signed certificates for development
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
            2>/dev/null
        
        print_success "SSL certificates generated in nginx/ssl/"
    else
        print_warning "SSL certificates already exist"
    fi
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Build images with error handling
    print_status "Building Docker images..."
    if ! docker-compose build --parallel; then
        print_error "Docker build failed. Common solutions:"
        print_status "1. Try: docker-compose build --no-cache"
        print_status "2. Try: docker system prune -a && docker-compose build"
        print_status "3. Use development setup: ./dev-setup.sh"
        print_status "4. Check DOCKER_SETUP.md for detailed troubleshooting"
        exit 1
    fi
    
    # Start services
    print_status "Starting services..."
    if ! docker-compose up -d; then
        print_error "Failed to start services. Try:"
        print_status "1. Check ports: docker-compose down && docker-compose up -d"
        print_status "2. Use development setup: ./dev-setup.sh"
        exit 1
    fi
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_services_health
}

# Check services health
check_services_health() {
    print_status "Checking services health..."
    
    # Check database
    if docker-compose exec -T postgres pg_isready -U goldtrader -d gold_trading_bot > /dev/null 2>&1; then
        print_success "Database is ready"
    else
        print_error "Database is not ready"
        return 1
    fi
    
    # Check backend
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend is ready"
    else
        print_warning "Backend may not be ready yet"
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is ready"
    else
        print_warning "Frontend may not be ready yet"
    fi
    
    # Check nginx
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_success "Nginx proxy is ready"
    else
        print_warning "Nginx proxy may not be ready yet"
    fi
}

# Display access information
display_access_info() {
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "===================================="
    echo ""
    echo "📱 Access URLs:"
    echo "  Web Application: http://localhost"
    echo "  API Documentation: http://localhost/api/docs"
    echo "  Database: localhost:5432"
    echo ""
    echo "🔐 Default Credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo "  Email: admin@goldtrading.com"
    echo ""
    echo "⚠️  Important Notes:"
    echo "  - Change default credentials in production"
    echo "  - Configure your MT5 account in the settings"
    echo "  - Update environment variables for production"
    echo ""
    echo "📚 Commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart services: docker-compose restart"
    echo ""
}

# Cleanup function
cleanup() {
    print_status "Cleaning up old containers and images..."
    docker-compose down --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Main deployment function
main() {
    echo "Starting deployment process..."
    echo ""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cleanup)
                cleanup
                exit 0
                ;;
            --ssl)
                setup_ssl
                exit 0
                ;;
            --env-only)
                create_env_file
                exit 0
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --cleanup     Clean up Docker containers and images"
                echo "  --ssl         Setup SSL certificates only"
                echo "  --env-only    Create environment file only"
                echo "  --help        Show this help message"
                echo ""
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
        shift
    done
    
    # Run deployment steps
    check_docker
    create_env_file
    setup_ssl
    deploy_services
    display_access_info
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"