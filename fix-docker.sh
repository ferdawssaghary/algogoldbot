#!/bin/bash

# Gold Trading Bot - Docker Fix Script
# Fixes common Docker issues and provides alternatives

set -e

echo "🔧 Gold Trading Bot - Docker Fix Script"
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

# Check Docker status
check_docker_status() {
    print_status "Checking Docker status..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        return 1
    fi
    
    print_success "Docker is running"
    return 0
}

# Clean Docker system
clean_docker() {
    print_status "Cleaning Docker system..."
    
    # Stop all containers
    print_status "Stopping all containers..."
    docker-compose down 2>/dev/null || true
    
    # Remove unused containers, networks, images
    print_status "Removing unused Docker resources..."
    docker system prune -f
    
    # Remove all images related to the project
    print_status "Removing project images..."
    docker images | grep algogoldbot | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
    
    print_success "Docker system cleaned"
}

# Fix frontend npm issues
fix_frontend() {
    print_status "Fixing frontend npm issues..."
    
    cd frontend
    
    # Remove node_modules and package-lock
    rm -rf node_modules package-lock.json 2>/dev/null || true
    
    # Reinstall dependencies
    print_status "Reinstalling npm dependencies..."
    npm install
    
    cd ..
    print_success "Frontend dependencies fixed"
}

# Rebuild with no cache
rebuild_docker() {
    print_status "Rebuilding Docker images without cache..."
    
    # Build without cache
    docker-compose build --no-cache --parallel
    
    print_success "Docker images rebuilt"
}

# Test individual services
test_services() {
    print_status "Testing individual Docker services..."
    
    # Test backend build
    print_status "Testing backend build..."
    cd backend
    if docker build -t test-backend .; then
        print_success "Backend builds successfully"
        docker rmi test-backend 2>/dev/null || true
    else
        print_error "Backend build failed"
    fi
    cd ..
    
    # Test frontend build
    print_status "Testing frontend build..."
    cd frontend
    if docker build -t test-frontend .; then
        print_success "Frontend builds successfully"
        docker rmi test-frontend 2>/dev/null || true
    else
        print_error "Frontend build failed"
    fi
    cd ..
}

# Show alternatives
show_alternatives() {
    echo ""
    print_warning "If Docker continues to fail, use these alternatives:"
    echo ""
    echo "🚀 **Development Setup (No Docker):**"
    echo "   ./dev-setup.sh"
    echo ""
    echo "☁️  **Replit Deployment:**"
    echo "   1. Push code to GitHub"
    echo "   2. Import to Replit from GitHub"
    echo "   3. Replit will auto-configure"
    echo ""
    echo "🐳 **Manual Docker Commands:**"
    echo "   # Backend only"
    echo "   cd backend && docker build -t gold-backend ."
    echo "   docker run -p 8000:8000 gold-backend"
    echo ""
    echo "   # Frontend only"
    echo "   cd frontend && docker build -t gold-frontend ."
    echo "   docker run -p 3000:3000 gold-frontend"
    echo ""
}

# Main menu
main_menu() {
    echo ""
    echo "🔧 What would you like to do?"
    echo ""
    echo "1) Clean Docker system and rebuild"
    echo "2) Fix frontend npm issues"
    echo "3) Test individual services"
    echo "4) Complete reset and rebuild"
    echo "5) Show alternatives to Docker"
    echo "6) Exit"
    echo ""
    read -p "Choose an option (1-6): " choice
    
    case $choice in
        1)
            clean_docker
            rebuild_docker
            print_success "Try running: docker-compose up -d"
            ;;
        2)
            fix_frontend
            print_success "Try building again: docker-compose build frontend"
            ;;
        3)
            test_services
            ;;
        4)
            clean_docker
            fix_frontend
            rebuild_docker
            print_success "Complete reset done. Try: docker-compose up -d"
            ;;
        5)
            show_alternatives
            ;;
        6)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid option"
            main_menu
            ;;
    esac
}

# Main execution
main() {
    if check_docker_status; then
        main_menu
    else
        print_error "Docker is not available. Please:"
        echo ""
        echo "1. Install Docker Desktop (Windows/Mac)"
        echo "2. Install docker.io (Linux): sudo apt install docker.io"
        echo "3. Start Docker service: sudo systemctl start docker"
        echo "4. Or use development setup: ./dev-setup.sh"
        echo ""
        show_alternatives
    fi
}

# Run main function
main "$@"