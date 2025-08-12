#!/usr/bin/env python3
"""
Simple WebSocket test script to check if the MT5 WebSocket endpoint is working
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Test the MT5 WebSocket connection"""
    uri = "ws://localhost:8000/ws/mt5?secret=g4dV6pG9qW2z8K1rY7tB3nM5xC0hL2sD"
    
    try:
        print(f"Attempting to connect to: {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Send a test message
            test_message = {"type": "get_balance"}
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent message: {test_message}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for response")
                
    except websockets.exceptions.InvalidURI:
        print("❌ Invalid WebSocket URI")
    except websockets.exceptions.ConnectionClosed:
        print("❌ WebSocket connection closed unexpectedly")
    except ConnectionRefusedError:
        print("❌ Connection refused - backend server is not running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())