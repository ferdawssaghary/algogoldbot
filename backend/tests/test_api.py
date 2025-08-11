import asyncio
import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient

from backend.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data

@pytest.mark.asyncio
async def test_dashboard():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Without auth returns 401 for protected; health is open
        # Directly test public health already; here we can just check protected returns 401
        r = await ac.get("/api/dashboard/")
        assert r.status_code in (401, 403)

@pytest.mark.asyncio
async def test_ws_connect():
    # Use blocking client for websocket
    with TestClient(app) as client:
        with client.websocket_connect("/ws/1") as ws:
            # send ping and expect no exceptions
            ws.send_text("ping")
            # we might not get immediate messages, so just pass
            pass