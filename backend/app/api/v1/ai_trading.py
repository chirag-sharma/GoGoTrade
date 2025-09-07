"""
AI Trading API Endpoints
Provides real-time market data and AI-powered trading signals
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging

from ...services.market_data import market_service, MarketData
from ...services.ai_trading import ai_engine, TradingSignal, SignalType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-trading", tags=["AI Trading"])

@router.get("/market-data", response_model=List[dict])
async def get_market_data(
    symbols: str = Query(..., description="Comma-separated list of symbols (e.g., NIFTY,SENSEX,RELIANCE.NS)")
):
    """
    Get real-time market data for specified symbols
    
    Example symbols:
    - NIFTY, SENSEX (Indian indices)
    - RELIANCE.NS, TCS.NS, INFY.NS (Indian stocks)
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        async with market_service:
            market_data = await market_service.get_market_data(symbol_list)
        
        # Convert to dict format for JSON response
        result = []
        for data in market_data:
            result.append({
                "symbol": data.symbol,
                "price": round(data.price, 2),
                "change": round(data.change, 2),
                "changePercent": round(data.change_percent, 2),
                "volume": data.volume,
                "high": round(data.high, 2),
                "low": round(data.low, 2),
                "open": round(data.open, 2),
                "timestamp": data.timestamp.isoformat()
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching market data: {str(e)}")

@router.get("/trading-signals", response_model=List[dict])
async def get_trading_signals(
    symbols: str = Query(..., description="Comma-separated list of symbols for signal generation")
):
    """
    Get AI-powered trading signals for specified symbols
    
    Returns signals with confidence scores, patterns, and recommendations
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        # Generate AI signals
        signals = await ai_engine.generate_trading_signals(symbol_list)
        
        # Convert to dict format for JSON response
        result = []
        for signal in signals:
            result.append({
                "symbol": signal.symbol,
                "signalType": signal.signal_type.value,
                "confidence": round(signal.confidence, 3),
                "price": round(signal.price, 2),
                "reason": signal.reason,
                "timestamp": signal.timestamp.isoformat(),
                "patternType": signal.pattern_type.value if signal.pattern_type else None,
                "targetPrice": round(signal.target_price, 2) if signal.target_price else None,
                "stopLoss": round(signal.stop_loss, 2) if signal.stop_loss else None
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Error generating trading signals: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating signals: {str(e)}")

@router.get("/historical-data/{symbol}", response_model=List[dict])
async def get_historical_data(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of historical data")
):
    """
    Get historical OHLC data for technical analysis
    
    Args:
        symbol: Stock symbol (e.g., RELIANCE.NS)
        days: Number of days of historical data (1-365)
    """
    try:
        symbol = symbol.upper()
        
        async with market_service:
            historical_data = await market_service.get_historical_data(symbol, days)
        
        # Convert to dict format for JSON response
        result = []
        for data in historical_data:
            result.append({
                "symbol": data.symbol,
                "timestamp": data.timestamp.isoformat(),
                "open": round(data.open, 2),
                "high": round(data.high, 2),
                "low": round(data.low, 2),
                "close": round(data.close, 2),
                "volume": data.volume
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

@router.get("/dashboard-data", response_model=dict)
async def get_dashboard_data(
    symbols: str = Query("NIFTY,SENSEX,RELIANCE.NS,TCS.NS,INFY.NS", description="Dashboard symbols")
):
    """
    Get comprehensive dashboard data including market data and AI signals
    
    This endpoint provides all data needed for the trading dashboard in a single call
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        async with market_service:
            # Fetch market data and AI signals in parallel
            market_data = await market_service.get_market_data(symbol_list)
        
        signals = await ai_engine.generate_trading_signals(symbol_list)
        
        # Format market data
        market_data_formatted = []
        for data in market_data:
            market_data_formatted.append({
                "symbol": data.symbol,
                "price": round(data.price, 2),
                "change": round(data.change, 2),
                "changePercent": round(data.change_percent, 2),
                "volume": data.volume,
                "high": round(data.high, 2),
                "low": round(data.low, 2),
                "open": round(data.open, 2),
                "timestamp": data.timestamp.isoformat()
            })
        
        # Format signals
        signals_formatted = []
        for signal in signals:
            signals_formatted.append({
                "symbol": signal.symbol,
                "signalType": signal.signal_type.value,
                "confidence": round(signal.confidence, 3),
                "price": round(signal.price, 2),
                "reason": signal.reason,
                "timestamp": signal.timestamp.isoformat(),
                "patternType": signal.pattern_type.value if signal.pattern_type else None,
                "targetPrice": round(signal.target_price, 2) if signal.target_price else None,
                "stopLoss": round(signal.stop_loss, 2) if signal.stop_loss else None
            })
        
        # Generate market summary
        total_symbols = len(market_data_formatted)
        positive_symbols = len([d for d in market_data_formatted if d["changePercent"] > 0])
        negative_symbols = total_symbols - positive_symbols
        
        market_sentiment = "bullish" if positive_symbols > negative_symbols else "bearish" if negative_symbols > positive_symbols else "neutral"
        
        buy_signals = len([s for s in signals_formatted if s["signalType"] == "BUY"])
        sell_signals = len([s for s in signals_formatted if s["signalType"] == "SELL"])
        
        return {
            "marketData": market_data_formatted,
            "signals": signals_formatted,
            "summary": {
                "totalSymbols": total_symbols,
                "positiveSymbols": positive_symbols,
                "negativeSymbols": negative_symbols,
                "marketSentiment": market_sentiment,
                "buySignals": buy_signals,
                "sellSignals": sell_signals,
                "lastUpdated": datetime.now().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

@router.get("/signal/{symbol}", response_model=dict)
async def get_single_signal(symbol: str):
    """
    Get detailed AI trading signal for a single symbol
    
    Provides in-depth analysis including technical indicators and pattern details
    """
    try:
        symbol = symbol.upper()
        
        signals = await ai_engine.generate_trading_signals([symbol])
        
        if not signals:
            raise HTTPException(status_code=404, detail=f"No signal available for {symbol}")
        
        signal = signals[0]
        
        # Get additional technical data
        async with market_service:
            historical_data = await market_service.get_historical_data(symbol, days=50)
        
        return {
            "symbol": signal.symbol,
            "signalType": signal.signal_type.value,
            "confidence": round(signal.confidence, 3),
            "price": round(signal.price, 2),
            "reason": signal.reason,
            "timestamp": signal.timestamp.isoformat(),
            "patternType": signal.pattern_type.value if signal.pattern_type else None,
            "targetPrice": round(signal.target_price, 2) if signal.target_price else None,
            "stopLoss": round(signal.stop_loss, 2) if signal.stop_loss else None,
            "historicalDataPoints": len(historical_data),
            "recommendation": {
                "action": signal.signal_type.value,
                "strength": "strong" if signal.confidence > 0.8 else "moderate" if signal.confidence > 0.6 else "weak",
                "riskLevel": "low" if signal.confidence > 0.8 else "medium" if signal.confidence > 0.6 else "high"
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching signal: {str(e)}")

@router.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint for AI trading service"""
    return {
        "status": "healthy",
        "service": "AI Trading Service",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Real-time market data",
            "AI pattern recognition", 
            "Technical analysis",
            "Trading signals",
            "Risk management"
        ]
    }
