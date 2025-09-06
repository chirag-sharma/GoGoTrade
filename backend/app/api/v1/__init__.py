"""
API v1 router initialization
Includes all v1 API endpoints
"""

from fastapi import APIRouter
from .api import apiRouter
from .ai_enhanced import router as ai_enhanced_router
from .trade_prediction import router as trade_prediction_router
from .advanced_strategies import router as advanced_strategies_router
from .real_time_data import router as real_time_data_router

# Create the main v1 router
router = APIRouter(prefix="/v1")

# Include the main API router (which includes all strategies, trading-data, and charts endpoints)
router.include_router(apiRouter)

# Include the enhanced AI analysis router
router.include_router(ai_enhanced_router)

# Include the trade prediction router
router.include_router(trade_prediction_router)

# Include the advanced strategies router
router.include_router(advanced_strategies_router)

# Include the real-time data router
router.include_router(real_time_data_router)

# Health check endpoint for v1 API
@router.get("/status")
async def api_status():
    """API v1 status endpoint"""
    return {
        "status": "healthy",
        "version": "1.0",
        "api_endpoints": [
            # Structured API endpoints
            "/v1/status",
            "/v1/strategies/strategies",
            "/v1/strategies/backtest", 
            "/v1/strategies/signals/{symbol}",
            "/v1/trading-data/market-data/{symbol}",
            "/v1/trading-data/ohlcv/{symbol}",
            "/v1/trading-data/instruments",
            "/v1/charts/chart-data/{symbol}",
            
            # Enhanced AI Analysis endpoints
            "/v1/ai-enhanced/technical-analysis",
            "/v1/ai-enhanced/trend-analysis", 
            "/v1/ai-enhanced/risk-assessment",
            "/v1/ai-enhanced/sentiment-analysis",
            "/v1/ai-enhanced/strategy-recommendation",
            "/v1/ai-enhanced/prompt-categories",
            "/v1/ai-enhanced/reload-prompts",
            "/v1/ai-enhanced/health",
            
            # Real-Time Data endpoints
            "/v1/real-time/subscribe",
            "/v1/real-time/unsubscribe", 
            "/v1/real-time/price/{symbol}",
            "/v1/real-time/prices",
            "/v1/real-time/signals",
            "/v1/real-time/signals/{symbol}",
            "/v1/real-time/status",
            "/v1/real-time/ws",  # WebSocket endpoint
            "/v1/real-time/test/generate-sample-data",
            "/v1/charts/indicators/{symbol}"
        ]
    }
