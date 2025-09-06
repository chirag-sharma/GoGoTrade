"""
Real-time data API endpoints.
Provides REST and WebSocket APIs for live market data and trading signals.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services.real_time_data import real_time_data_service, get_real_time_service
from app.services.market_data_processor import MarketDataProcessor


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/real-time", tags=["Real-Time Data"])


# Pydantic models for request/response
class SubscriptionRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of trading symbols to subscribe")
    
class LivePriceResponse(BaseModel):
    symbol: str
    ltp: float = Field(..., description="Last traded price")
    change: float = Field(..., description="Price change from previous close")
    change_percent: float = Field(..., description="Percentage change")
    volume: int
    timestamp: str
    source: str

class SignalResponse(BaseModel):
    symbol: str
    signal_type: str = Field(..., description="BUY, SELL, or HOLD")
    confidence: float = Field(..., description="Signal confidence (0.0 to 1.0)")
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    reasoning: str
    timeframe: str
    generated_at: str

class MarketStatusResponse(BaseModel):
    is_market_open: bool
    market_session: str
    active_subscriptions: int
    data_sources_connected: int
    last_update: str


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.symbol_subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from symbol subscriptions
        for symbol, connections in self.symbol_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")
    
    async def subscribe_to_symbol(self, websocket: WebSocket, symbol: str):
        if symbol not in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol] = []
        
        if websocket not in self.symbol_subscriptions[symbol]:
            self.symbol_subscriptions[symbol].append(websocket)
            logger.info(f"Client subscribed to {symbol}")
    
    async def unsubscribe_from_symbol(self, websocket: WebSocket, symbol: str):
        if symbol in self.symbol_subscriptions and websocket in self.symbol_subscriptions[symbol]:
            self.symbol_subscriptions[symbol].remove(websocket)
            logger.info(f"Client unsubscribed from {symbol}")
    
    async def broadcast_price_update(self, symbol: str, data: Dict):
        if symbol in self.symbol_subscriptions:
            message = {
                "type": "price_update",
                "symbol": symbol,
                "data": data
            }
            
            disconnected = []
            for websocket in self.symbol_subscriptions[symbol]:
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    disconnected.append(websocket)
            
            # Remove disconnected clients
            for ws in disconnected:
                self.symbol_subscriptions[symbol].remove(ws)
                if ws in self.active_connections:
                    self.active_connections.remove(ws)
    
    async def broadcast_signal(self, signal: Dict):
        message = {
            "type": "trading_signal",
            "data": signal
        }
        
        disconnected = []
        for websocket in self.active_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for ws in disconnected:
            self.disconnect(ws)


# Global connection manager
manager = ConnectionManager()

# Initialize market data processor
market_processor = MarketDataProcessor()


@router.on_event("startup")
async def startup_event():
    """Initialize real-time services on startup."""
    await market_processor.initialize()
    
    # Add price update callback to broadcast to WebSocket clients
    async def price_update_callback(symbol: str, price_data: Dict):
        await manager.broadcast_price_update(symbol, price_data)
    
    real_time_data_service.add_price_callback(price_update_callback)


@router.post("/subscribe", response_model=dict)
async def subscribe_to_live_data(
    request: SubscriptionRequest,
    service = Depends(get_real_time_service)
):
    """
    Subscribe to live market data for specified symbols.
    
    Args:
        request: Subscription request with symbols list
        
    Returns:
        Subscription status and details
    """
    try:
        success = await service.subscribe_to_live_prices(request.symbols)
        
        if success:
            return {
                "status": "success",
                "message": f"Subscribed to {len(request.symbols)} symbols",
                "symbols": request.symbols,
                "active_subscriptions": len(service.active_subscriptions)
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to subscribe to live data")
            
    except Exception as e:
        logger.error(f"Subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unsubscribe", response_model=dict)
async def unsubscribe_from_live_data(
    request: SubscriptionRequest,
    service = Depends(get_real_time_service)
):
    """
    Unsubscribe from live market data for specified symbols.
    
    Args:
        request: Unsubscription request with symbols list
        
    Returns:
        Unsubscription status
    """
    try:
        success = await service.unsubscribe_from_live_prices(request.symbols)
        
        if success:
            return {
                "status": "success",
                "message": f"Unsubscribed from {len(request.symbols)} symbols",
                "symbols": request.symbols,
                "active_subscriptions": len(service.active_subscriptions)
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to unsubscribe from live data")
            
    except Exception as e:
        logger.error(f"Unsubscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price/{symbol}", response_model=LivePriceResponse)
async def get_live_price(
    symbol: str,
    service = Depends(get_real_time_service)
):
    """
    Get current live price for a symbol.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        Current price data
    """
    try:
        price_data = await service.get_live_price(symbol)
        
        if not price_data:
            raise HTTPException(status_code=404, detail=f"No live data found for {symbol}")
        
        return LivePriceResponse(**price_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting live price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices", response_model=List[LivePriceResponse])
async def get_all_live_prices(service = Depends(get_real_time_service)):
    """
    Get live prices for all subscribed symbols.
    
    Returns:
        List of current price data for all active subscriptions
    """
    try:
        prices = []
        
        for symbol in service.active_subscriptions:
            price_data = await service.get_live_price(symbol)
            if price_data:
                prices.append(LivePriceResponse(**price_data))
        
        return prices
        
    except Exception as e:
        logger.error(f"Error getting all live prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals", response_model=List[SignalResponse])
async def get_active_signals(symbol: Optional[str] = None):
    """
    Get active trading signals.
    
    Args:
        symbol: Optional symbol filter
        
    Returns:
        List of active trading signals
    """
    try:
        signals = await market_processor.get_active_signals(symbol)
        return [SignalResponse(**signal) for signal in signals]
        
    except Exception as e:
        logger.error(f"Error getting active signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/{symbol}", response_model=List[SignalResponse])
async def get_signals_for_symbol(symbol: str):
    """
    Get active trading signals for a specific symbol.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        List of active signals for the symbol
    """
    try:
        signals = await market_processor.get_active_signals(symbol)
        return [SignalResponse(**signal) for signal in signals]
        
    except Exception as e:
        logger.error(f"Error getting signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=MarketStatusResponse)
async def get_market_status(service = Depends(get_real_time_service)):
    """
    Get real-time market status and service health.
    
    Returns:
        Market status and service information
    """
    try:
        # Check if market is open (simplified check)
        current_hour = datetime.now().hour
        is_market_open = 9 <= current_hour <= 15  # Simplified market hours
        
        market_session = "Regular" if is_market_open else "Closed"
        if current_hour < 9:
            market_session = "Pre-Market"
        elif current_hour > 15:
            market_session = "After-Hours"
        
        return MarketStatusResponse(
            is_market_open=is_market_open,
            market_session=market_session,
            active_subscriptions=len(service.active_subscriptions),
            data_sources_connected=2,  # Mock value
            last_update=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time data streaming.
    
    Supports commands:
    - {"action": "subscribe", "symbol": "AAPL"}
    - {"action": "unsubscribe", "symbol": "AAPL"}
    - {"action": "get_price", "symbol": "AAPL"}
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            symbol = message.get("symbol")
            
            if action == "subscribe" and symbol:
                await manager.subscribe_to_symbol(websocket, symbol)
                
                # Subscribe to live data if not already subscribed
                async with get_real_time_service() as service:
                    if symbol not in service.active_subscriptions:
                        await service.subscribe_to_live_prices([symbol])
                
                # Send confirmation
                await websocket.send_text(json.dumps({
                    "type": "subscription_confirmed",
                    "symbol": symbol,
                    "status": "subscribed"
                }))
                
                # Send current price if available
                async with get_real_time_service() as service:
                    price_data = await service.get_live_price(symbol)
                    if price_data:
                        await websocket.send_text(json.dumps({
                            "type": "price_update",
                            "symbol": symbol,
                            "data": price_data
                        }))
            
            elif action == "unsubscribe" and symbol:
                await manager.unsubscribe_from_symbol(websocket, symbol)
                
                await websocket.send_text(json.dumps({
                    "type": "unsubscription_confirmed",
                    "symbol": symbol,
                    "status": "unsubscribed"
                }))
            
            elif action == "get_price" and symbol:
                async with get_real_time_service() as service:
                    price_data = await service.get_live_price(symbol)
                    
                    if price_data:
                        await websocket.send_text(json.dumps({
                            "type": "price_response",
                            "symbol": symbol,
                            "data": price_data
                        }))
                    else:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"No price data available for {symbol}"
                        }))
            
            elif action == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
            
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid action or missing symbol"
                }))
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


@router.post("/test/generate-sample-data")
async def generate_sample_data():
    """
    Generate sample market data for testing purposes.
    This endpoint is for development/testing only.
    """
    try:
        # Start the real-time service with sample data
        async with get_real_time_service() as service:
            sample_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
            await service.subscribe_to_live_prices(sample_symbols)
            
            return {
                "status": "success",
                "message": "Sample data generation started",
                "symbols": sample_symbols
            }
            
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
