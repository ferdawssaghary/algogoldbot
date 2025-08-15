# 🏆 Gold Trading Bot - Automated XAUUSD Trading System

A comprehensive web-based automated gold (XAUUSD) trading bot with MetaTrader 5 integration, developed for deployment on Replit with full Docker support.

## 🎯 Overview

This project implements a fully automated, profitable gold trading system that integrates with MetaTrader 5 via LiteFinance broker. The system features a modern React.js frontend, Python FastAPI backend, PostgreSQL database, and comprehensive trading algorithms.

## ✨ Key Features

### 🤖 Automated Trading
- **XAUUSD Exclusive**: Specialized trading for gold (XAUUSD) only
- **Advanced Algorithm**: Trend-following strategy with RSI confirmation
- **Risk Management**: Configurable stop loss, take profit, and position sizing
- **Real-time Execution**: Live trading with MT5 integration
- **Fallback Logic**: Error handling and connection recovery

### 🌐 Web Application
- **Responsive Design**: Fully responsive React.js frontend
- **Bilingual Support**: English & Farsi (Persian) language support
- **Real-time Dashboard**: Live trading status and account monitoring
- **Modern UI**: Material-UI components with beautiful design
- **Mobile Friendly**: Optimized for all device sizes

### 🔐 Security & Performance
- **Encrypted Storage**: Secure credential storage with encryption
- **JWT Authentication**: Secure user authentication system
- **Rate Limiting**: API protection with Nginx rate limiting
- **Error Handling**: Comprehensive error logging and recovery
- **Performance Monitoring**: Real-time metrics and analytics

### 📊 Advanced Features
- **Real-time Sync**: Live MT5 account synchronization
- **Trade Analytics**: Performance metrics and statistics
- **Telegram Integration**: Automated notifications and alerts
- **Journal System**: Sig Gol entries with linked accounting
- **WebSocket Support**: Real-time updates and live data

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React.js      │    │   FastAPI       │    │   PostgreSQL    │
│   Frontend      │────│   Backend       │────│   Database      │
│   (Port 3000)   │    │   (Port 8000)   │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                  ┌─────────────────┐    ┌─────────────────┐
                  │     Nginx       │    │   MetaTrader 5  │
                  │  Reverse Proxy  │    │   Integration   │
                  │   (Port 80)     │    │  (LiteFinance)  │
                  └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- LiteFinance demo account credentials

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd gold-trading-bot
```

### 2. Environment Configuration
Create `.env` file in the backend directory:
```env
# Database
DATABASE_URL=postgresql://goldtrader:securepassword123@postgres:5432/gold_trading_bot

# Security
SECRET_KEY=your-super-secure-secret-key-here-change-in-production

# MetaTrader 5
MT5_SERVER=LiteFinance-MT5-Demo

# Telegram
TELEGRAM_BOT_TOKEN=8348419204:AAEEr0DQfcBmwwWssvTu-ljg94C19qUPim8
TELEGRAM_CHAT_ID=-1002481438774

# Application
DEBUG=True
```

### 3. Deploy with Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access the Application
- **Web Interface**: http://localhost
- **API Documentation**: http://localhost/api/docs
- **Database**: localhost:5432

## 📁 Project Structure

```
gold-trading-bot/
├── 📁 backend/                  # Python FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📁 api/             # API routes
│   │   ├── 📁 core/            # Core configuration
│   │   ├── 📁 crud/            # Database operations
│   │   ├── 📁 models/          # Database models
│   │   ├── 📁 services/        # Business logic
│   │   └── 📁 utils/           # Utilities
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt
│   └── 📄 main.py
├── 📁 frontend/                 # React.js Frontend
│   ├── 📁 public/
│   ├── 📁 src/
│   │   ├── 📁 components/      # React components
│   │   ├── 📁 contexts/        # React contexts
│   │   ├── 📁 pages/           # Application pages
│   │   ├── 📁 services/        # API services
│   │   ├── 📁 utils/           # Utilities
│   │   └── 📁 i18n/            # Internationalization
│   ├── 📄 Dockerfile
│   └── 📄 package.json
├── 📁 database/                 # Database configuration
│   └── 📄 init.sql             # Database schema
├── 📁 mt5_expert_advisor/       # MQL5 Expert Advisor
│   └── 📄 GoldTradingBot.mq5   # MT5 trading bot
├── 📁 nginx/                    # Nginx configuration
│   └── 📄 nginx.conf
├── 📄 docker-compose.yml        # Docker services
└── 📄 README.md                # This file
```

## 🔧 Configuration

### MetaTrader 5 Setup
1. Install MetaTrader 5
2. Open demo account with LiteFinance
3. Install the Expert Advisor (`mt5_expert_advisor/GoldTradingBot.mq5`)
4. Configure the EA parameters
5. Enable automated trading

### Application Settings
Access settings through the web interface:
- **Trading Parameters**: Lot size, stop loss, take profit
- **Risk Management**: Risk percentage, maximum daily trades
- **Algorithm Settings**: Moving averages, RSI parameters
- **Account Configuration**: MT5 credentials and server

### Telegram Integration
1. The bot token is pre-configured: `8348419204:AAEEr0DQfcBmwwWssvTu-ljg94C19qUPim8`
2. Group chat ID is set: `-1002481438774`
3. Notifications will be sent automatically for:
   - Trade entries and exits
   - Bot start/stop events
   - Daily summaries
   - Error notifications

## 📊 Trading Algorithm

### Strategy: Trend Following with RSI Confirmation
- **Primary Indicators**: Fast EMA (12) and Slow EMA (26)
- **Confirmation**: RSI (14) with overbought/oversold levels
- **Entry Signals**:
  - **Buy**: Fast MA crosses above Slow MA + RSI < 70
  - **Sell**: Fast MA crosses below Slow MA + RSI > 30

### Risk Management
- **Stop Loss**: 50 pips (configurable)
- **Take Profit**: 100 pips (configurable)
- **Position Sizing**: 2% risk per trade
- **Maximum Spread**: 5 pips
- **Daily Trade Limit**: 10 trades

## 💻 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Database Management
```bash
# Connect to database
psql -h localhost -p 5432 -U goldtrader -d gold_trading_bot

# Run migrations
cd backend
alembic upgrade head
```

## 🔒 Security Features

- **Encrypted Credentials**: MT5 passwords encrypted at rest
- **JWT Authentication**: Secure API access
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error responses

## 📈 Monitoring & Analytics

### Real-time Metrics
- Account balance and equity
- Open positions and trades
- Daily/weekly/monthly performance
- Win rate and profit factor
- Maximum drawdown tracking

### Performance Dashboard
- Interactive charts and graphs
- Trade history analysis
- Risk metrics visualization
- Profit/loss reporting
- System health monitoring

## 🌍 Internationalization

The application supports:
- **English**: Default language
- **Farsi (Persian)**: Complete translation
- **RTL Support**: Right-to-left layout for Farsi
- **Dynamic Switching**: Language toggle in UI

## 🚀 Deployment

### Replit Deployment
1. Connect GitHub repository to Replit
2. Configure environment variables
3. Deploy using Docker Compose
4. Access via Replit URL

### Production Deployment
1. Configure SSL certificates
2. Update environment variables
3. Enable HTTPS in Nginx
4. Set up monitoring and logging
5. Configure backup strategies

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📞 Support & Documentation

### API Documentation
- **Interactive Docs**: http://localhost/api/docs
- **ReDoc**: http://localhost/api/redoc
- **OpenAPI Spec**: http://localhost/api/openapi.json

### Default Credentials
- **Username**: admin
- **Password**: admin123
- **Email**: admin@goldtrading.com

*⚠️ Change default credentials in production!*

### System Requirements
- **RAM**: 2GB minimum, 4GB recommended
- **CPU**: 2 cores minimum
- **Storage**: 10GB available space
- **Network**: Stable internet connection

## 🎯 Features Checklist

- ✅ Automated XAUUSD trading
- ✅ MetaTrader 5 integration
- ✅ Real-time synchronization
- ✅ Web-based dashboard
- ✅ Bilingual support (EN/FA)
- ✅ Responsive design
- ✅ Telegram notifications
- ✅ Risk management
- ✅ Performance analytics
- ✅ Docker containerization
- ✅ PostgreSQL database
- ✅ Security features
- ✅ Error handling
- ✅ Documentation

## 🏅 Production Ready

This application is production-ready with:
- Comprehensive error handling
- Security best practices
- Performance optimization
- Monitoring and logging
- Scalable architecture
- Professional UI/UX
- Complete documentation

## 📄 License

This project is proprietary software developed for gold trading automation. Unauthorized distribution or modification is prohibited.

---

**🏆 Gold Trading Bot - Professional Automated Trading Solution**
*Developed with ❤️ for profitable XAUUSD trading*

## 🪟 Windows + WSL + Docker Networking

- If MetaTrader 5 (EA) runs on Windows and the backend runs in Docker/WSL, set EA `BackendURL` to `http://host.docker.internal:8000` and add this URL in MT5 WebRequest allow-list.
- From Windows browser, access:
  - Frontend: `http://localhost`
  - API: `http://localhost/api` (or `http://host.docker.internal:8000` directly)
- Docker compose uses bridge network; Nginx proxies `/api` and `/ws` to backend.
