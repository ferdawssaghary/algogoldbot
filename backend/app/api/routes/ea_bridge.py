from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, List

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

class EASettingsIn(BaseModel):
    enabled: bool
    shared_secret: str

class TickIn(BaseModel):
    symbol: str
    bid: float
    ask: float
    time: str

class AccountIn(BaseModel):
    balance: float
    equity: float
    profit: float
    margin: float | None = None

class TradeEventIn(BaseModel):
    ticket: int
    order: int | None = None
    symbol: str
    type: str
    volume: float
    price: float
    profit: float | None = None
    comment: str | None = None
    time: str | None = None

class InstructionOut(BaseModel):
    id: str
    action: str
    symbol: str
    side: str | None = None
    lot: float | None = None
    price: float | None = None
    sl: float | None = None
    tp: float | None = None
    comment: str | None = None

@router.get("/settings")
async def get_ea_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return {
        "enabled": settings.EA_BRIDGE_ENABLED,
        "shared_secret": settings.EA_SHARED_SECRET or ""
    }

@router.post("/settings")
async def save_ea_settings(
    payload: EASettingsIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    settings.EA_BRIDGE_ENABLED = payload.enabled
    settings.EA_SHARED_SECRET = payload.shared_secret
    return {"success": True}

# Webhook auth helper
def _require_secret(secret: str):
    if not settings.EA_BRIDGE_ENABLED:
        raise HTTPException(status_code=403, detail="EA bridge disabled")
    if not settings.EA_SHARED_SECRET or secret != settings.EA_SHARED_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")

@router.post("/tick")
async def ea_tick(request: Request, payload: TickIn):
    secret = request.headers.get("X-EA-SECRET") or request.query_params.get("secret")
    _require_secret(secret or "")
    # Optionally forward to websockets as live tick
    engine = getattr(request.app.state, "trading_engine", None)
    if engine:
        try:
            msg = {
                "type": "account_status",
                "tick": { "symbol": payload.symbol, "bid": payload.bid, "ask": payload.ask, "time": payload.time }
            }
            for _, clients in list(engine.user_websocket_clients.items()):
                for ws in list(clients):
                    try:
                        await ws.send_json(msg)
                    except Exception:
                        pass
        except Exception:
            pass
    return {"ok": True}

@router.post("/account")
async def ea_account(request: Request, payload: AccountIn):
    secret = request.headers.get("X-EA-SECRET") or request.query_params.get("secret")
    _require_secret(secret or "")
    # Could persist to DB if needed; for now notify websockets
    engine = getattr(request.app.state, "trading_engine", None)
    if engine:
        msg = {
            "type": "account_status",
            "balance": payload.balance,
            "equity": payload.equity,
            "profit": payload.profit,
        }
        for _, clients in list(engine.user_websocket_clients.items()):
            for ws in list(clients):
                try:
                    await ws.send_json(msg)
                except Exception:
                    pass
    return {"ok": True}

@router.post("/trade-event")
async def ea_trade_event(request: Request, payload: TradeEventIn):
    secret = request.headers.get("X-EA-SECRET") or request.query_params.get("secret")
    _require_secret(secret or "")
    # Notify telegram about entries/exits
    tg = getattr(request.app.state, "telegram_service", None)
    if tg:
        side = payload.type
        txt = f"EA {side} {payload.symbol} @ {payload.price:.2f} vol {payload.volume:.2f} ticket {payload.ticket}"
        await tg.send_notification(txt, "ea_trade")
    return {"ok": True}

@router.get("/instructions")
async def ea_instructions(request: Request):
    secret = request.headers.get("X-EA-SECRET") or request.query_params.get("secret")
    _require_secret(secret or "")
    queue: List[Dict[str, Any]] = getattr(request.app.state, "ea_instruction_queue", [])
    # Return and clear pending instructions
    if not queue:
        return {"instructions": []}
    items = list(queue)
    queue.clear()
    return {"instructions": items}