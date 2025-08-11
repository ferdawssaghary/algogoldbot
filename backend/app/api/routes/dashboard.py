"""Dashboard API routes"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_dashboard_data(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard data"""
    mt5_service = getattr(request.app.state, "mt5_service", None)
    account_info = None
    if mt5_service:
        account_info = await mt5_service.get_account_info()
    
    balance = float(account_info.get("balance", 0.0)) if account_info else 0.0
    equity = float(account_info.get("equity", 0.0)) if account_info else 0.0
    profit = float(account_info.get("profit", 0.0)) if account_info else 0.0
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "account_balance": balance,
        "equity": equity,
        "profit": profit,
        "open_trades": 0,
        "total_trades": 0,
        "win_rate": 0.0
    }

@router.get("/performance")
async def get_performance_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics"""
    return {
        "user_id": current_user.id,
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate": 0.0,
        "total_profit": 0.0,
        "max_drawdown": 0.0
    }

@router.get("/price")
async def get_price_data(
    request: Request,
    symbol: str = Query("XAUUSD"),
    timeframe: str = Query("M15"),
    count: int = Query(200, ge=10, le=2000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get historical OHLC price data"""
    mt5_service = getattr(request.app.state, "mt5_service", None)
    if not mt5_service:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MT5 service unavailable")
    df = await mt5_service.get_price_data(symbol=symbol, timeframe=timeframe, count=count)
    if df is None or df.empty:
        return {"symbol": symbol, "timeframe": timeframe, "candles": []}
    candles = [
        {
            "time": idx.isoformat(),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]) ,
            "volume": int(row.get("tick_volume", 0)) if "tick_volume" in row else 0
        }
        for idx, row in df.iterrows()
    ]
    return {"symbol": symbol, "timeframe": timeframe, "candles": candles}