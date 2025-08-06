"""Dashboard API routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard data"""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "account_balance": 10000.0,
        "equity": 10000.0,
        "profit": 0.0,
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