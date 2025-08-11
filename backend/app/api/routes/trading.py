"""Trading API routes"""

from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.trading import BotSettings

router = APIRouter()

class TradingSettingsIn(BaseModel):
    risk_percentage: float = Field(2.0, ge=0.1, le=10.0)
    max_daily_trades: int = Field(10, ge=1, le=100)
    stop_loss_pips: int = Field(50, ge=5, le=1000)
    take_profit_pips: int = Field(100, ge=5, le=2000)
    max_spread: float = Field(5.0, ge=0.1, le=100.0)
    timeframe: str = Field("M15")
    enable_strategy: bool = Field(True)
    custom_tick_value: float | None = Field(None)
    custom_point: float | None = Field(None)

@router.get("/settings")
async def get_trading_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(BotSettings).where(BotSettings.user_id == current_user.id))
    s = result.scalar_one_or_none()
    return {
        "risk_percentage": float(s.risk_percentage) if s else 2.0,
        "max_daily_trades": s.max_daily_trades if s else 10,
        "stop_loss_pips": s.stop_loss_pips if s else 50,
        "take_profit_pips": s.take_profit_pips if s else 100,
        "max_spread": float(s.max_spread) if s and s.max_spread is not None else 5.0,
        "timeframe": s.timeframe if s else "M15",
        "enable_strategy": s.enable_strategy if s else True,
        "custom_tick_value": float(s.custom_tick_value) if s and s.custom_tick_value is not None else None,
        "custom_point": float(s.custom_point) if s and s.custom_point is not None else None,
    }

@router.post("/settings")
async def save_trading_settings(
    payload: TradingSettingsIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(BotSettings).where(BotSettings.user_id == current_user.id))
    s = result.scalar_one_or_none()
    if s is None:
        s = BotSettings(
            user_id=current_user.id,
            risk_percentage=payload.risk_percentage,
            max_daily_trades=payload.max_daily_trades,
            stop_loss_pips=payload.stop_loss_pips,
            take_profit_pips=payload.take_profit_pips,
            max_spread=payload.max_spread,
            timeframe=payload.timeframe,
            enable_strategy=payload.enable_strategy,
            custom_tick_value=payload.custom_tick_value,
            custom_point=payload.custom_point,
        )
        db.add(s)
    else:
        s.risk_percentage = payload.risk_percentage
        s.max_daily_trades = payload.max_daily_trades
        s.stop_loss_pips = payload.stop_loss_pips
        s.take_profit_pips = payload.take_profit_pips
        s.max_spread = payload.max_spread
        s.timeframe = payload.timeframe
        s.enable_strategy = payload.enable_strategy
        s.custom_tick_value = payload.custom_tick_value
        s.custom_point = payload.custom_point
    await db.commit()
    return {"success": True}

@router.get("/status")
async def get_trading_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current trading status"""
    return {
        "status": "stopped",
        "user_id": current_user.id,
        "message": "Trading is currently stopped"
    }

@router.post("/start")
async def start_trading(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    engine = getattr(request.app.state, "trading_engine", None)
    if not engine:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Trading engine unavailable")
    return await engine.start_trading(current_user.id, db)

@router.post("/stop")
async def stop_trading(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    engine = getattr(request.app.state, "trading_engine", None)
    if not engine:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Trading engine unavailable")
    return await engine.stop_trading(current_user.id, db)