#!/usr/bin/env python3
"""
Simple HTTP and WebSocket server for testing MT5 connection
"""

import asyncio
import json
import websockets
from datetime import datetime
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Mock MT5 data
MOCK_ACCOUNT = {
    'balance': 500.0,
    'equity': 500.0,
    'profit': 0.0,
    'currency': 'USD'
}

MOCK_TICK = {
    'symbol': 'XAUUSD',
    'bid': 2000.0 + random.uniform(-10, 10),
    'ask': 2000.0 + random.uniform(-10, 10),
    'time': datetime.now().isoformat()
}

# HTTP handler for health check
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "database": "connected",
                    "mt5": True,
                    "trading_engine": True,
                    "telegram": True
                }
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_http_server():
    """Start HTTP server in a separate thread"""
    server = HTTPServer(('localhost', 8001), HealthHandler)
    print("🌐 HTTP server running on http://localhost:8001")
    server.serve_forever()

async def handle_websocket(websocket, path):
    """Handle WebSocket connections"""
    print(f"🔌 Client connected from {websocket.remote_address}")
    
    try:
        # Send initial account info
        account_info = {
            "type": "account_status",
            "balance": MOCK_ACCOUNT['balance'],
            "equity": MOCK_ACCOUNT['equity'],
            "profit": MOCK_ACCOUNT['profit'],
            "currency": MOCK_ACCOUNT['currency']
        }
        await websocket.send(json.dumps(account_info))
        print("📤 Sent initial account info")
        
        # Keep connection alive and handle messages
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"📥 Received: {data}")
                
                if data.get("type") == "get_balance":
                    account_info = {
                        "type": "account_status",
                        "balance": MOCK_ACCOUNT['balance'],
                        "equity": MOCK_ACCOUNT['equity'],
                        "profit": MOCK_ACCOUNT['profit'],
                        "currency": MOCK_ACCOUNT['currency']
                    }
                    await websocket.send(json.dumps(account_info))
                    print("📤 Sent account info")
                
                elif data.get("type") == "get_tick":
                    # Update mock tick with new random prices
                    MOCK_TICK['bid'] = 2000.0 + random.uniform(-10, 10)
                    MOCK_TICK['ask'] = MOCK_TICK['bid'] + random.uniform(0.1, 1.0)
                    MOCK_TICK['time'] = datetime.now().isoformat()
                    
                    tick_data = {
                        "type": "account_status",
                        "tick": {
                            "symbol": MOCK_TICK['symbol'],
                            "bid": round(MOCK_TICK['bid'], 2),
                            "ask": round(MOCK_TICK['ask'], 2),
                            "time": MOCK_TICK['time']
                        }
                    }
                    await websocket.send(json.dumps(tick_data))
                    print("📤 Sent tick data")
                
                elif data.get("type") == "place_order":
                    # Mock order placement
                    order_result = {
                        "type": "order_result",
                        "success": True,
                        "ticket": random.randint(100000, 999999),
                        "message": "Order placed successfully (mock)"
                    }
                    await websocket.send(json.dumps(order_result))
                    print("📤 Sent order result")
                
            except json.JSONDecodeError:
                print("❌ Invalid JSON received")
                continue
                
    except websockets.exceptions.ConnectionClosed:
        print("🔌 Client disconnected")
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Start the servers"""
    print("🚀 Starting MT5 WebSocket server...")
    print("📍 WebSocket: ws://localhost:8001/ws/mt5")
    print("📍 HTTP: http://localhost:8001/health")
    print("🔑 Secret key: g4dV6pG9qW2z8K1rY7tB3nM5xC0hL2sD")
    print("")
    
    # Start HTTP server in a separate thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # Start WebSocket server
    async with websockets.serve(handle_websocket, "localhost", 8001):
        print("✅ WebSocket server is running!")
        print("📊 Mock data:")
        print(f"   Account Balance: ${MOCK_ACCOUNT['balance']}")
        print(f"   Current Bid: ${MOCK_TICK['bid']:.2f}")
        print(f"   Current Ask: ${MOCK_TICK['ask']:.2f}")
        print("")
        print("🌐 Test the connection in your browser:")
        print("   http://localhost:3000")
        print("")
        print("⏹️  Press Ctrl+C to stop the server")
        
        # Keep the server running
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")