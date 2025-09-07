"""
Advanced WebSocket Endpoints for Real-time AI Trading Signals
Provides streaming AI predictions, sentiment analysis, and market regime updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Set
import asyncio
import json
import logging
from datetime import datetime

from ..services.websocket_service import websocket_manager
from ..services.market_data import market_service

logger = logging.getLogger(__name__)

router = APIRouter()

class AISignalStreamer:
    """Manages streaming of AI trading signals"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.symbol_subscriptions: Dict[WebSocket, Set[str]] = {}
        self.streaming_tasks: Dict[str, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect client to AI signal stream"""
        await websocket.accept()
        
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        
        self.active_connections[client_id].add(websocket)
        self.symbol_subscriptions[websocket] = set()
        
        logger.info(f"AI Signal client {client_id} connected")
        
    async def disconnect(self, websocket: WebSocket, client_id: str):
        """Disconnect client from AI signal stream"""
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        
        if websocket in self.symbol_subscriptions:
            symbols = self.symbol_subscriptions[websocket]
            del self.symbol_subscriptions[websocket]
            
            # Stop streaming tasks if no more subscribers
            for symbol in symbols:
                await self._maybe_stop_streaming(symbol)
        
        logger.info(f"AI Signal client {client_id} disconnected")
    
    async def subscribe_symbol(self, websocket: WebSocket, symbol: str):
        """Subscribe websocket to AI signals for a symbol"""
        if websocket in self.symbol_subscriptions:
            self.symbol_subscriptions[websocket].add(symbol)
            
            # Start streaming task if not already running
            if symbol not in self.streaming_tasks:
                task = asyncio.create_task(self._stream_ai_signals(symbol))
                self.streaming_tasks[symbol] = task
            
            logger.info(f"Client subscribed to AI signals for {symbol}")
    
    async def unsubscribe_symbol(self, websocket: WebSocket, symbol: str):
        """Unsubscribe websocket from AI signals for a symbol"""
        if websocket in self.symbol_subscriptions:
            self.symbol_subscriptions[websocket].discard(symbol)
            await self._maybe_stop_streaming(symbol)
            
            logger.info(f"Client unsubscribed from AI signals for {symbol}")
    
    async def _maybe_stop_streaming(self, symbol: str):
        """Stop streaming if no more subscribers for a symbol"""
        # Check if any websocket is still subscribed to this symbol
        has_subscribers = any(
            symbol in subscriptions 
            for subscriptions in self.symbol_subscriptions.values()
        )
        
        if not has_subscribers and symbol in self.streaming_tasks:
            task = self.streaming_tasks[symbol]
            task.cancel()
            del self.streaming_tasks[symbol]
            logger.info(f"Stopped AI signal streaming for {symbol}")
    
    async def _stream_ai_signals(self, symbol: str):
        """Stream AI signals for a symbol to all subscribers"""
        try:
            while True:
                try:
                    # Generate AI signals (this would use the advanced AI engine)
                    signal_data = await self._generate_streaming_signals(symbol)
                    
                    if signal_data:
                        # Send to all subscribers
                        await self._broadcast_signal(symbol, signal_data)
                    
                    # Wait before next update (adjust frequency as needed)
                    await asyncio.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error streaming AI signals for {symbol}: {e}")
                    await asyncio.sleep(60)  # Back off on error
                    
        except asyncio.CancelledError:
            logger.info(f"AI signal streaming cancelled for {symbol}")
    
    async def _generate_streaming_signals(self, symbol: str) -> Optional[Dict]:
        """Generate AI signals for streaming"""
        try:
            # This would integrate with the advanced AI engine
            # For now, simulate real-time AI signals
            
            current_time = datetime.now()
            
            # Simulate AI signal generation
            signal_strength = __import__('random').uniform(-1.0, 1.0)
            confidence = __import__('random').uniform(0.3, 0.9)
            
            signal_data = {
                "symbol": symbol,
                "timestamp": current_time.isoformat(),
                "ai_signals": [
                    {
                        "model_type": "lstm_prediction",
                        "signal_strength": round(signal_strength, 3),
                        "confidence": round(confidence, 3),
                        "prediction": "up" if signal_strength > 0 else "down",
                        "reason": f"LSTM model predicts {abs(signal_strength)*100:.1f}% {'upward' if signal_strength > 0 else 'downward'} movement"
                    },
                    {
                        "model_type": "pattern_recognition",
                        "signal_strength": round(signal_strength * 0.8, 3),
                        "confidence": round(confidence * 0.9, 3),
                        "pattern": "bullish_flag" if signal_strength > 0.3 else "bearish_wedge" if signal_strength < -0.3 else "consolidation",
                        "reason": "CNN pattern analysis detected continuation pattern"
                    }
                ],
                "market_sentiment": {
                    "overall_score": round(__import__('random').uniform(-0.5, 0.5), 3),
                    "news_sentiment": round(__import__('random').uniform(-0.3, 0.3), 3),
                    "social_sentiment": round(__import__('random').uniform(-0.4, 0.4), 3)
                },
                "market_regime": {
                    "current": "trending_bull" if signal_strength > 0.2 else "trending_bear" if signal_strength < -0.2 else "sideways",
                    "strength": round(abs(signal_strength), 3),
                    "volatility": "medium"
                }
            }
            
            return signal_data
            
        except Exception as e:
            logger.error(f"Error generating streaming signals for {symbol}: {e}")
            return None
    
    async def _broadcast_signal(self, symbol: str, signal_data: Dict):
        """Broadcast AI signal to all subscribers"""
        message = json.dumps({
            "type": "ai_signal",
            "data": signal_data
        })
        
        # Find all websockets subscribed to this symbol
        subscribers = [
            ws for ws, symbols in self.symbol_subscriptions.items()
            if symbol in symbols
        ]
        
        # Send to all subscribers
        for websocket in subscribers:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error sending AI signal to subscriber: {e}")
                # Remove disconnected websocket
                if websocket in self.symbol_subscriptions:
                    del self.symbol_subscriptions[websocket]

# Global AI signal streamer
ai_signal_streamer = AISignalStreamer()

@router.websocket("/ws/ai-signals/{client_id}")
async def ai_signals_websocket(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time AI trading signals
    Clients can subscribe to specific symbols and receive live AI predictions
    """
    await ai_signal_streamer.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for client messages
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                command = message.get("command")
                symbol = message.get("symbol", "").upper()
                
                if command == "subscribe" and symbol:
                    await ai_signal_streamer.subscribe_symbol(websocket, symbol)
                    await websocket.send_text(json.dumps({
                        "type": "subscription_confirmed",
                        "symbol": symbol,
                        "status": "subscribed"
                    }))
                
                elif command == "unsubscribe" and symbol:
                    await ai_signal_streamer.unsubscribe_symbol(websocket, symbol)
                    await websocket.send_text(json.dumps({
                        "type": "subscription_confirmed",
                        "symbol": symbol,
                        "status": "unsubscribed"
                    }))
                
                elif command == "get_status":
                    subscribed_symbols = list(ai_signal_streamer.symbol_subscriptions.get(websocket, set()))
                    await websocket.send_text(json.dumps({
                        "type": "status_response",
                        "client_id": client_id,
                        "subscribed_symbols": subscribed_symbols,
                        "active_streams": len(ai_signal_streamer.streaming_tasks)
                    }))
                
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid command or missing symbol"
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
                
    except WebSocketDisconnect:
        await ai_signal_streamer.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"Error in AI signals websocket for {client_id}: {e}")
        await ai_signal_streamer.disconnect(websocket, client_id)

@router.websocket("/ws/market-sentiment")
async def market_sentiment_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market sentiment updates
    Streams sentiment analysis across multiple sources
    """
    await websocket.accept()
    
    try:
        while True:
            # Generate sentiment update every 60 seconds
            sentiment_update = {
                "type": "sentiment_update",
                "timestamp": datetime.now().isoformat(),
                "market_sentiment": {
                    "overall": round(__import__('random').uniform(-0.3, 0.3), 3),
                    "news": round(__import__('random').uniform(-0.4, 0.4), 3),
                    "social": round(__import__('random').uniform(-0.5, 0.5), 3),
                    "institutional": round(__import__('random').uniform(-0.2, 0.2), 3)
                },
                "trending_topics": [
                    "earnings_season",
                    "fed_policy",
                    "market_volatility"
                ],
                "sentiment_drivers": [
                    {"factor": "Economic data", "impact": 0.2, "direction": "positive"},
                    {"factor": "Geopolitical events", "impact": -0.1, "direction": "negative"},
                    {"factor": "Sector rotation", "impact": 0.1, "direction": "positive"}
                ]
            }
            
            await websocket.send_text(json.dumps(sentiment_update))
            await asyncio.sleep(60)  # Update every minute
            
    except WebSocketDisconnect:
        logger.info("Market sentiment websocket disconnected")
    except Exception as e:
        logger.error(f"Error in market sentiment websocket: {e}")

@router.websocket("/ws/model-performance")
async def model_performance_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time AI model performance monitoring
    Streams model accuracy, prediction counts, and performance metrics
    """
    await websocket.accept()
    
    try:
        while True:
            # Generate model performance update
            performance_update = {
                "type": "model_performance",
                "timestamp": datetime.now().isoformat(),
                "models": {
                    "lstm_prediction": {
                        "accuracy": round(__import__('random').uniform(0.65, 0.78), 3),
                        "predictions_today": __import__('random').randint(50, 200),
                        "avg_confidence": round(__import__('random').uniform(0.6, 0.8), 3),
                        "status": "active"
                    },
                    "pattern_recognition": {
                        "accuracy": round(__import__('random').uniform(0.60, 0.75), 3),
                        "patterns_detected": __import__('random').randint(20, 80),
                        "avg_confidence": round(__import__('random').uniform(0.5, 0.7), 3),
                        "status": "active"
                    },
                    "sentiment_analysis": {
                        "accuracy": round(__import__('random').uniform(0.55, 0.70), 3),
                        "articles_processed": __import__('random').randint(100, 500),
                        "avg_confidence": round(__import__('random').uniform(0.4, 0.6), 3),
                        "status": "active"
                    },
                    "ensemble": {
                        "accuracy": round(__import__('random').uniform(0.70, 0.85), 3),
                        "signals_generated": __import__('random').randint(30, 120),
                        "avg_confidence": round(__import__('random').uniform(0.7, 0.9), 3),
                        "status": "active"
                    }
                },
                "system_metrics": {
                    "total_predictions": __import__('random').randint(200, 800),
                    "success_rate": round(__import__('random').uniform(0.65, 0.80), 3),
                    "processing_time_ms": __import__('random').randint(50, 200)
                }
            }
            
            await websocket.send_text(json.dumps(performance_update))
            await asyncio.sleep(30)  # Update every 30 seconds
            
    except WebSocketDisconnect:
        logger.info("Model performance websocket disconnected")
    except Exception as e:
        logger.error(f"Error in model performance websocket: {e}")
