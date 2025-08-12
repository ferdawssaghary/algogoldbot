#!/usr/bin/env python3
"""
Very simple test server for WebSocket connection
"""

import asyncio
import json
import websockets
from datetime import datetime
import random

# Mock data
MOCK_DATA = {
    'balance': 500.0,
    'equity': 500.0,
    'profit': 0.0,
    'currency': 'USD',
    'bid': 2000.0,
    'ask': 2000.1
}

async def handler(websocket, path):
    """Simple WebSocket handler"""
    print(f"Client connected: {websocket.remote_address}")
    
    try:
        # Send initial data
        data = {
            "type": "account_status",
            "balance": MOCK_DATA['balance'],
            "equity": MOCK_DATA['equity'],
            "profit": MOCK_DATA['profit'],
            "currency": MOCK_DATA['currency']
        }
        await websocket.send(json.dumps(data))
        print("Sent initial data")
        
        # Handle messages
        async for message in websocket:
            print(f"Received: {message}")
            
            # Send tick data
            tick_data = {
                "type": "account_status",
                "tick": {
                    "symbol": "XAUUSD",
                    "bid": MOCK_DATA['bid'] + random.uniform(-1, 1),
                    "ask": MOCK_DATA['ask'] + random.uniform(-1, 1),
                    "time": datetime.now().isoformat()
                }
            }
            await websocket.send(json.dumps(tick_data))
            print("Sent tick data")
            
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    print("Starting test server on ws://localhost:8001")
    
    # Start server
    server = await websockets.serve(handler, "localhost", 8001)
    print("Server started!")
    print("Test with: ws://localhost:8001")
    
    # Keep running
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")