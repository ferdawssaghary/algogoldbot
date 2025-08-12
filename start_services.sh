#!/bin/bash

echo "🚀 Starting Gold Trading Bot Services in WSL..."

# Check if Docker is running
echo "📋 Checking Docker status..."
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo ""
    echo "🔧 To fix this:"
    echo "1. Open Docker Desktop on Windows"
    echo "2. Make sure WSL integration is enabled in Docker Desktop settings"
    echo "3. Wait for Docker to start completely"
    echo "4. Run this script again"
    echo ""
    echo "💡 You can also try:"
    echo "   docker --version"
    echo "   docker ps"
    exit 1
fi

echo "✅ Docker is running!"

# Check if containers are already running
echo "📋 Checking existing containers..."
if docker ps --format "table {{.Names}}" | grep -q "gold_trading"; then
    echo "⚠️  Some containers are already running. Stopping them first..."
    docker-compose down
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
echo "=================="

# Check backend
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ Backend (port 8000): Running"
else
    echo "❌ Backend (port 8000): Not responding"
fi

# Check frontend
if curl -s http://localhost:3000 >/dev/null; then
    echo "✅ Frontend (port 3000): Running"
else
    echo "❌ Frontend (port 3000): Not responding"
fi

# Check database
if docker exec gold_trading_db pg_isready -U goldtrader >/dev/null 2>&1; then
    echo "✅ Database: Running"
else
    echo "❌ Database: Not responding"
fi

echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"