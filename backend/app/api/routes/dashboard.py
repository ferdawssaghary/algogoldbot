"""Dashboard API routes"""

from fastapi import APIRouter, Depends, Request
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