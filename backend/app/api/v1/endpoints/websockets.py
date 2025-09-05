"""
WebSocket endpoints for real-time trading data
Provides WebSocket connections for live market data and AI signals
"""

import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ....services.websocket_service import websocket_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time trading data"""
    client_id = str(uuid.uuid4())
    
    try:
        await websocket_manager.connect(websocket, client_id)
        
        # Start real-time streaming if this is the first client
        if len(websocket_manager.connections) == 1:
            import asyncio
            # Start streaming in background
            asyncio.create_task(websocket_manager.start_real_time_stream())
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                await websocket_manager.handle_message(client_id, data)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket communication: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        websocket_manager.disconnect(client_id)
        
        # Stop streaming if no clients remaining
        if not websocket_manager.connections:
            websocket_manager.stop_real_time_stream()

@router.websocket("/ws/market-data")
async def market_data_websocket(websocket: WebSocket):
    """Dedicated WebSocket for market data streaming"""
    client_id = f"market_{uuid.uuid4()}"
    
    try:
        await websocket_manager.connect(websocket, client_id)
        
        # Auto-subscribe to major indices
        default_symbols = ["NIFTY", "SENSEX", "RELIANCE.NS", "TCS.NS", "INFY.NS"]
        await websocket_manager.subscribe_symbols(client_id, default_symbols)
        
        # Keep connection alive
        while True:
            try:
                # Send periodic ping to keep connection alive
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Market data WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"Market data WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Market data WebSocket error for client {client_id}: {e}")
    finally:
        websocket_manager.disconnect(client_id)

@router.websocket("/ws/trading-signals")
async def trading_signals_websocket(websocket: WebSocket):
    """Dedicated WebSocket for AI trading signals"""
    client_id = f"signals_{uuid.uuid4()}"
    
    try:
        await websocket_manager.connect(websocket, client_id)
        
        # Keep connection alive and handle signal requests
        while True:
            try:
                data = await websocket.receive_text()
                await websocket_manager.handle_message(client_id, data)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Trading signals WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"Trading signals WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Trading signals WebSocket error for client {client_id}: {e}")
    finally:
        websocket_manager.disconnect(client_id)
