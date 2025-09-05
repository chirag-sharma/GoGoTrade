"""
WebSocket Service for Real-time Trading Data
Provides live market data and AI signals via WebSocket connections
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from fastapi import WebSocket, WebSocketDisconnect
import socketio
from .market_data import MarketDataService
from .ai_trading import AITradingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and real-time data streaming"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, List[str]] = {}  # client_id: [symbols]
        self.market_service = MarketDataService()
        self.ai_service = AITradingService()
        self.is_streaming = False
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.connections[client_id] = websocket
        self.subscriptions[client_id] = []
        logger.info(f"WebSocket client {client_id} connected")
        
        # Send initial connection confirmation
        await self.send_to_client(client_id, {
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.connections:
            del self.connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        logger.info(f"WebSocket client {client_id} disconnected")
    
    async def send_to_client(self, client_id: str, data: Dict[str, Any]):
        """Send data to specific client"""
        if client_id in self.connections:
            try:
                await self.connections[client_id].send_text(json.dumps(data))
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast data to all connected clients"""
        disconnected_clients = []
        for client_id, websocket in self.connections.items():
            try:
                await websocket.send_text(json.dumps(data))
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def subscribe_symbols(self, client_id: str, symbols: List[str]):
        """Subscribe client to specific symbols"""
        if client_id in self.subscriptions:
            self.subscriptions[client_id] = symbols
            await self.send_to_client(client_id, {
                "type": "subscription",
                "status": "success",
                "symbols": symbols,
                "timestamp": datetime.now().isoformat()
            })
            logger.info(f"Client {client_id} subscribed to symbols: {symbols}")
    
    async def handle_message(self, client_id: str, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                symbols = data.get("symbols", [])
                await self.subscribe_symbols(client_id, symbols)
            
            elif message_type == "get_market_data":
                symbols = data.get("symbols", ["NIFTY", "SENSEX"])
                market_data = await self.get_market_data(symbols)
                await self.send_to_client(client_id, {
                    "type": "market_data",
                    "data": market_data,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "get_signals":
                symbols = data.get("symbols", ["RELIANCE.NS"])
                signals = await self.get_trading_signals(symbols)
                await self.send_to_client(client_id, {
                    "type": "trading_signals",
                    "data": signals,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "ping":
                await self.send_to_client(client_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
                
        except json.JSONDecodeError:
            await self.send_to_client(client_id, {
                "type": "error",
                "message": "Invalid JSON format",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self.send_to_client(client_id, {
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    async def get_market_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get market data for specified symbols"""
        try:
            market_data = []
            for symbol in symbols:
                data = self.market_service.get_real_time_data(symbol)
                if data:
                    market_data.append({
                        "symbol": symbol,
                        "price": data.get("price", 0),
                        "change": data.get("change", 0),
                        "changePercent": data.get("changePercent", 0),
                        "volume": data.get("volume", 0),
                        "high": data.get("high", 0),
                        "low": data.get("low", 0),
                        "open": data.get("open", 0),
                        "timestamp": datetime.now().isoformat()
                    })
            return market_data
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return []
    
    async def get_trading_signals(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get AI trading signals for specified symbols"""
        try:
            all_signals = []
            for symbol in symbols:
                signals = self.ai_service.get_trading_signals(symbol)
                if signals:
                    all_signals.extend(signals)
            return all_signals
        except Exception as e:
            logger.error(f"Error getting trading signals: {e}")
            return []
    
    async def start_real_time_stream(self):
        """Start real-time data streaming to all connected clients"""
        if self.is_streaming:
            return
            
        self.is_streaming = True
        logger.info("Starting real-time data stream")
        
        try:
            while self.is_streaming and self.connections:
                # Get all subscribed symbols
                all_symbols = set()
                for symbols in self.subscriptions.values():
                    all_symbols.update(symbols)
                
                if all_symbols:
                    # Fetch market data
                    market_data = await self.get_market_data(list(all_symbols))
                    if market_data:
                        await self.broadcast({
                            "type": "market_data_stream",
                            "data": market_data,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    # Fetch AI signals every 30 seconds
                    if datetime.now().second % 30 == 0:
                        signals = await self.get_trading_signals(list(all_symbols))
                        if signals:
                            await self.broadcast({
                                "type": "signals_stream",
                                "data": signals,
                                "timestamp": datetime.now().isoformat()
                            })
                
                # Stream every 5 seconds
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"Error in real-time stream: {e}")
        finally:
            self.is_streaming = False
            logger.info("Real-time data stream stopped")
    
    def stop_real_time_stream(self):
        """Stop real-time data streaming"""
        self.is_streaming = False
        logger.info("Stopping real-time data stream")

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
