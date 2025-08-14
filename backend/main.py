#!/usr/bin/env python3
"""
Gold Trading Bot - Main FastAPI Application
XAUUSD Automated Trading System with MetaTrader 5 Integration
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports
from app.core.config import settings
from app.core.database import get_db, init_db
from app.core.security import get_current_user
from app.models.user import User
from app.api.routes import auth, trading, dashboard, mt5_config, telegram_bot
from app.api.routes import ea_bridge
from app.services.trading_engine import TradingEngine
from app.services.mt5_service import MT5Service
from app.services.telegram_service import TelegramService
from app.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Global services
trading_engine: Optional[TradingEngine] = None
mt5_service: Optional[MT5Service] = None
telegram_service: Optional[TelegramService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global trading_engine, mt5_service, telegram_service
    
    try:
        # Initialize database
        if str(settings.DATABASE_URL).startswith("postgres"):
            await init_db()
        else:
            logger.warning(f"Skipping DB init for non-Postgres DATABASE_URL: {settings.DATABASE_URL}")
        logger.info("Database initialized successfully")
        
        # Initialize services
        mt5_service = MT5Service()
        
        # Auto-connect to MT5 if credentials are configured
        if settings.MT5_LOGIN and settings.MT5_PASSWORD:
            logger.info(f"Attempting to connect to MT5 account: {settings.MT5_LOGIN}")
            connection_success = await mt5_service.connect_account(
                login=settings.MT5_LOGIN,
                password=settings.MT5_PASSWORD,
                server=settings.MT5_SERVER
            )
            if connection_success:
                logger.info("Successfully connected to MT5 account")
            else:
                logger.error("Failed to connect to MT5 account. Trading functionality will be limited.")
        else:
            logger.warning("No MT5 credentials configured. Please configure MT5 credentials for full functionality.")
        
        telegram_service = TelegramService(mt5_service)
        trading_engine = TradingEngine(mt5_service, telegram_service)
        
        # Expose services via app state for routers
        app.state.mt5_service = mt5_service
        app.state.trading_engine = trading_engine
        app.state.telegram_service = telegram_service
        app.state.ea_instruction_queue = []  # simple global queue for EA instructions
        
        # Start background services
        asyncio.create_task(trading_engine.start())
        asyncio.create_task(telegram_service.start())
        
        logger.info("All services started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Cleanup on shutdown
        if trading_engine:
            await trading_engine.stop()
        if telegram_service:
            await telegram_service.stop()
        if mt5_service:
            await mt5_service.disconnect()
        
        logger.info("Application shutdown completed")

# Create FastAPI application
app = FastAPI(
    title="Gold Trading Bot API",
    description="Automated XAUUSD Trading System with MetaTrader 5 Integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "mt5": mt5_service.is_connected() if mt5_service else False,
            "trading_engine": trading_engine.is_running() if trading_engine else False,
            "telegram": telegram_service.is_connected() if telegram_service else False
        }
    }

# API Status endpoint
@app.get("/api/status")
async def api_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get API and trading bot status"""
    try:
        bot_status = {
            "is_active": False,
            "total_trades": 0,
            "open_trades": 0,
            "daily_profit": 0.0,
            "account_balance": 0.0,
            "account_equity": 0.0
        }
        
        if trading_engine:
            bot_status = await trading_engine.get_status(current_user.id, db)
        
        return {
            "success": True,
            "data": {
                "user_id": current_user.id,
                "username": current_user.username,
                "bot_status": bot_status,
                "mt5_connected": mt5_service.is_connected() if mt5_service else False,
                "services_running": {
                    "trading_engine": trading_engine.is_running() if trading_engine else False,
                    "telegram_bot": telegram_service.is_connected() if telegram_service else False
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API status"
        )

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(mt5_config.router, prefix="/api/mt5", tags=["MT5 Configuration"])
app.include_router(telegram_bot.router, prefix="/api/telegram", tags=["Telegram"])
app.include_router(ea_bridge.router, prefix="/api/ea", tags=["EA Bridge"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "Internal server error", "detail": str(exc)}
    )

# Trading control endpoints
@app.post("/api/trading/start")
async def start_trading(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start the trading bot"""
    try:
        if not trading_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Trading engine not initialized"
            )
        
        result = await trading_engine.start_trading(current_user.id, db)
        
        if result["success"]:
            # Send notification
            background_tasks.add_task(
                telegram_service.send_notification,
                f"🤖 Trading bot started for user {current_user.username}",
                "bot_start"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error starting trading: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start trading: {str(e)}"
        )

@app.post("/api/trading/stop")
async def stop_trading(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop the trading bot"""
    try:
        if not trading_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Trading engine not initialized"
            )
        
        result = await trading_engine.stop_trading(current_user.id, db)
        
        if result["success"]:
            # Send notification
            background_tasks.add_task(
                telegram_service.send_notification,
                f"🛑 Trading bot stopped for user {current_user.username}",
                "bot_stop"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error stopping trading: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop trading: {str(e)}"
        )

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time trading updates"""
    await websocket.accept()
    
    try:
        if trading_engine:
            await trading_engine.add_websocket_client(user_id, websocket)
            
            # Keep connection alive
            while True:
                await websocket.receive_text()
                
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        if trading_engine:
            await trading_engine.remove_websocket_client(user_id, websocket)

# MT5 WebSocket endpoint for direct MT5 connection
@app.websocket("/ws/mt5")
async def mt5_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for direct MT5 connection"""
    await websocket.accept()
    
    # Get secret from query parameters
    secret = websocket.query_params.get("secret")
    expected_secret = "g4dV6pG9qW2z8K1rY7tB3nM5xC0hL2sD"
    
    if secret != expected_secret:
        await websocket.close(code=4001, reason="Invalid secret")
        return
    
    try:
        logger.info("MT5 WebSocket client connected")
        
        # Send initial account info
        if mt5_service and mt5_service.current_account:
            account_info = {
                "type": "account_status",
                "balance": mt5_service.current_account.get('balance', 0),
                "equity": mt5_service.current_account.get('equity', 0),
                "profit": mt5_service.current_account.get('profit', 0),
                "currency": mt5_service.current_account.get('currency', 'USD')
            }
            await websocket.send_json(account_info)
        
        # Keep connection alive and handle MT5 data
        while True:
            try:
                # Receive any messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "get_balance":
                    if mt5_service and mt5_service.current_account:
                        account_info = {
                            "type": "account_status",
                            "balance": mt5_service.current_account.get('balance', 0),
                            "equity": mt5_service.current_account.get('equity', 0),
                            "profit": mt5_service.current_account.get('profit', 0),
                            "currency": mt5_service.current_account.get('currency', 'USD')
                        }
                        await websocket.send_json(account_info)
                
                elif message.get("type") == "get_tick":
                    symbol = message.get("symbol", "XAUUSD")
                    if mt5_service:
                        tick = await mt5_service.get_market_data(symbol)
                        if tick:
                            tick_data = {
                                "type": "account_status",
                                "tick": {
                                    "symbol": symbol,
                                    "bid": tick.get('bid', 0),
                                    "ask": tick.get('ask', 0),
                                    "time": tick.get('time', '')
                                }
                            }
                            await websocket.send_json(tick_data)
                
                elif message.get("type") == "place_order":
                    # Handle order placement
                    order_result = await mt5_service.place_order(
                        symbol=message.get("symbol", "XAUUSD"),
                        order_type=message.get("order_type", "BUY"),
                        volume=message.get("volume", 0.01),
                        price=message.get("price", 0),
                        sl=message.get("sl", 0),
                        tp=message.get("tp", 0),
                        comment=message.get("comment", "")
                    )
                    await websocket.send_json({
                        "type": "order_result",
                        "success": order_result.get("success", False),
                        "ticket": order_result.get("ticket", 0),
                        "message": order_result.get("message", "")
                    })
                    
            except json.JSONDecodeError:
                # Keep connection alive with ping/pong
                continue
                
    except Exception as e:
        logger.error(f"MT5 WebSocket error: {e}")
    finally:
        logger.info("MT5 WebSocket client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )