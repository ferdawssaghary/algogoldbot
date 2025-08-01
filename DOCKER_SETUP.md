# 🐳 Docker Setup and Troubleshooting Guide

## 🚨 Quick Fix for Docker Issues

### **Issue: Docker daemon not running**
Error: `Cannot connect to the Docker daemon at unix:///var/run/docker.sock`

## 🛠️ **Solutions by Environment**

### **Option 1: Windows with WSL2 (Recommended)**

1. **Install Docker Desktop for Windows:**
   ```bash
   # Download from: https://www.docker.com/products/docker-desktop
   # Make sure WSL2 integration is enabled
   ```

2. **Start Docker Desktop:**
   - Open Docker Desktop application
   - Wait for it to fully start (green indicator)
   - Enable WSL2 integration in Settings

3. **Verify Docker is running:**
   ```bash
   docker --version
   docker-compose --version
   ```

### **Option 2: Linux/Ubuntu**

1. **Install Docker:**
   ```bash
   # Update package index
   sudo apt update
   
   # Install Docker
   sudo apt install docker.io docker-compose-plugin
   
   # Start Docker service
   sudo systemctl start docker
   sudo systemctl enable docker
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   
   # Logout and login again, then test
   docker --version
   ```

2. **Start Docker daemon:**
   ```bash
   sudo systemctl start docker
   ```

### **Option 3: Alternative - Use Docker without Compose**

If Docker Compose is problematic, run services individually:

```bash
# Create network
docker network create trading_network

# Run PostgreSQL
docker run -d \
  --name gold_trading_db \
  --network trading_network \
  -e POSTGRES_USER=goldtrader \
  -e POSTGRES_PASSWORD=securepassword123 \
  -e POSTGRES_DB=gold_trading_bot \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15

# Build and run backend
cd backend
docker build -t gold-trading-backend .
docker run -d \
  --name gold_trading_backend \
  --network trading_network \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://goldtrader:securepassword123@gold_trading_db:5432/gold_trading_bot \
  gold-trading-backend

# Build and run frontend
cd ../frontend
docker build -t gold-trading-frontend .
docker run -d \
  --name gold_trading_frontend \
  --network trading_network \
  -p 3000:3000 \
  gold-trading-frontend
```

## 🏃 **Quick Development Setup (Without Docker)**

If Docker continues to cause issues, you can run the application in development mode:

### **Backend Setup:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="sqlite:///./gold_trading.db"
export SECRET_KEY="your-secret-key"

# Run backend
uvicorn main:app --reload --port 8000
```

### **Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### **Database Setup (SQLite for development):**
The backend will automatically create SQLite database if PostgreSQL is not available.

## 🔄 **Alternative Deployment: Replit Direct**

Since you're targeting Replit, you can also deploy directly:

1. **Create new Repl from GitHub:**
   - Go to Replit.com
   - Click "Create Repl"
   - Choose "Import from GitHub"
   - Enter your repository URL

2. **Replit will automatically:**
   - Detect the project structure
   - Install dependencies
   - Start the application

3. **Configure environment variables in Replit:**
   - Go to Secrets tab
   - Add required environment variables

## 🐛 **Common Docker Issues and Fixes**

### **Issue: Permission denied**
```bash
sudo chmod 666 /var/run/docker.sock
# OR
sudo usermod -aG docker $USER
# Then logout and login
```

### **Issue: Docker Compose not found**
```bash
# Install Docker Compose
sudo apt install docker-compose-plugin
# OR
pip install docker-compose
```

### **Issue: Port already in use**
```bash
# Find and kill processes using ports
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5432

# Kill specific process
sudo kill -9 <PID>
```

### **Issue: Image build fails**
```bash
# Clean Docker system
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

## ✅ **Verification Commands**

Test if everything is working:

```bash
# Check Docker
docker --version
docker ps

# Check services
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost/health

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🆘 **If All Else Fails**

Contact me with:
1. Your operating system
2. Docker version output
3. Complete error messages
4. Output of `docker ps` and `docker images`

The application is designed to work in multiple environments, so we can find a solution that works for your setup!