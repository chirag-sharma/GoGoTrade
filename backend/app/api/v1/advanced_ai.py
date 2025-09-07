"""
Advanced AI Trading API Endpoints
Provides access to neural network-based trading signals and market analysis
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..services.advanced_ai import advanced_ai_engine, AISignal, MarketSentiment, AIModelType

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/ai-signals/{symbol}")
async def get_ai_signals(
    symbol: str,
    timeframe: str = Query("1D", description="Timeframe for analysis"),
    models: Optional[str] = Query(None, description="Comma-separated list of model types to use")
) -> Dict[str, Any]:
    """
    Get comprehensive AI trading signals for a symbol
    """
    try:
        # Generate AI signals
        signals = await advanced_ai_engine.generate_ai_signals(symbol, timeframe)
        
        # Filter by requested models if specified
        if models:
            requested_models = [model.strip().upper() for model in models.split(",")]
            signals = [
                signal for signal in signals 
                if signal.model_type.value.upper() in requested_models
            ]
        
        # Convert signals to response format
        signal_data = []
        for signal in signals:
            signal_data.append({
                "symbol": signal.symbol,
                "signal_strength": signal.signal_strength,
                "confidence": signal.confidence,
                "model_type": signal.model_type.value,
                "reason": signal.reason,
                "timestamp": signal.timestamp.isoformat(),
                "features_used": signal.features_used,
                "predicted_price": signal.predicted_price,
                "price_direction": signal.price_direction,
                "time_horizon": signal.time_horizon
            })
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "signals": signal_data,
            "signal_count": len(signal_data),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting AI signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating AI signals: {str(e)}")

@router.get("/ai-signals/{symbol}/ensemble")
async def get_ensemble_signal(
    symbol: str,
    timeframe: str = Query("1D", description="Timeframe for analysis")
) -> Dict[str, Any]:
    """
    Get ensemble AI signal that combines all models
    """
    try:
        signals = await advanced_ai_engine.generate_ai_signals(symbol, timeframe)
        
        # Find ensemble signal
        ensemble_signal = None
        for signal in signals:
            if signal.model_type == AIModelType.ENSEMBLE_SIGNAL:
                ensemble_signal = signal
                break
        
        if not ensemble_signal:
            raise HTTPException(status_code=404, detail="No ensemble signal generated")
        
        return {
            "symbol": symbol,
            "signal_strength": ensemble_signal.signal_strength,
            "confidence": ensemble_signal.confidence,
            "reason": ensemble_signal.reason,
            "timestamp": ensemble_signal.timestamp.isoformat(),
            "features_used": ensemble_signal.features_used,
            "time_horizon": ensemble_signal.time_horizon,
            "recommendation": _get_trading_recommendation(ensemble_signal)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ensemble signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating ensemble signal: {str(e)}")

@router.get("/market-sentiment/{symbol}")
async def get_market_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Get comprehensive market sentiment analysis
    """
    try:
        # This would integrate with the advanced AI engine's sentiment analysis
        # For now, return simulated sentiment data
        sentiment_data = {
            "symbol": symbol,
            "overall_sentiment": 0.15,
            "sentiment_score": "Slightly Bullish",
            "news_sentiment": 0.2,
            "social_sentiment": 0.1,
            "institutional_sentiment": 0.3,
            "sentiment_sources": ["news_api", "twitter_api", "institutional_flow"],
            "sentiment_factors": [
                {"factor": "Recent earnings beat", "impact": 0.3, "confidence": 0.8},
                {"factor": "Positive analyst upgrades", "impact": 0.2, "confidence": 0.7},
                {"factor": "Market sector strength", "impact": 0.1, "confidence": 0.6}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return sentiment_data
        
    except Exception as e:
        logger.error(f"Error getting market sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

@router.get("/ai-models/performance")
async def get_model_performance() -> Dict[str, Any]:
    """
    Get performance metrics for all AI models
    """
    try:
        model_performances = {}
        
        for model_id in advanced_ai_engine.models.keys():
            performance = await advanced_ai_engine.get_model_performance(model_id)
            model_performances[model_id] = performance
        
        return {
            "models": model_performances,
            "total_models": len(model_performances),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving model performance: {str(e)}")

@router.post("/ai-models/{model_id}/update-performance")
async def update_model_performance(
    model_id: str,
    accuracy: float = Query(..., ge=0.0, le=1.0, description="New accuracy score")
) -> Dict[str, Any]:
    """
    Update model performance based on backtesting results
    """
    try:
        await advanced_ai_engine.update_model_performance(model_id, accuracy)
        
        return {
            "model_id": model_id,
            "new_accuracy": accuracy,
            "updated_at": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error updating model performance: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating performance: {str(e)}")

@router.get("/market-regime/{symbol}")
async def get_market_regime(symbol: str) -> Dict[str, Any]:
    """
    Detect current market regime for better signal interpretation
    """
    try:
        # This would use the market regime detection from advanced AI
        # For now, return simulated regime data
        regime_data = {
            "symbol": symbol,
            "current_regime": "trending_bull",
            "regime_strength": 0.7,
            "regime_duration": "12 days",
            "regime_factors": {
                "trend_strength": 0.8,
                "volatility_level": 0.3,
                "volume_pattern": "increasing",
                "support_resistance": "strong_support"
            },
            "regime_recommendations": {
                "strategy_focus": "momentum_following",
                "risk_adjustment": "moderate_increase",
                "signal_confidence": "high"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return regime_data
        
    except Exception as e:
        logger.error(f"Error detecting market regime for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error detecting regime: {str(e)}")

@router.get("/ai-predictions/{symbol}")
async def get_price_predictions(
    symbol: str,
    horizon: str = Query("1d", description="Prediction horizon (1d, 1w, 1m)"),
    confidence_threshold: float = Query(0.6, description="Minimum confidence threshold")
) -> Dict[str, Any]:
    """
    Get AI-based price predictions with confidence intervals
    """
    try:
        signals = await advanced_ai_engine.generate_ai_signals(symbol, "1D")
        
        # Filter for prediction signals with sufficient confidence
        prediction_signals = [
            signal for signal in signals 
            if signal.predicted_price and signal.confidence >= confidence_threshold
        ]
        
        if not prediction_signals:
            return {
                "symbol": symbol,
                "horizon": horizon,
                "predictions": [],
                "message": "No predictions meet the confidence threshold"
            }
        
        predictions = []
        for signal in prediction_signals:
            predictions.append({
                "model_type": signal.model_type.value,
                "predicted_price": signal.predicted_price,
                "confidence": signal.confidence,
                "direction": signal.price_direction,
                "reasoning": signal.reason,
                "features": signal.features_used
            })
        
        # Calculate consensus prediction
        if predictions:
            weighted_price = sum(p["predicted_price"] * p["confidence"] for p in predictions) / sum(p["confidence"] for p in predictions)
            avg_confidence = sum(p["confidence"] for p in predictions) / len(predictions)
            
            consensus = {
                "consensus_price": round(weighted_price, 2),
                "consensus_confidence": round(avg_confidence, 3),
                "prediction_range": {
                    "min": round(min(p["predicted_price"] for p in predictions), 2),
                    "max": round(max(p["predicted_price"] for p in predictions), 2)
                }
            }
        else:
            consensus = None
        
        return {
            "symbol": symbol,
            "horizon": horizon,
            "predictions": predictions,
            "consensus": consensus,
            "prediction_count": len(predictions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting price predictions for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")

def _get_trading_recommendation(signal: AISignal) -> Dict[str, str]:
    """Convert AI signal to trading recommendation"""
    strength = signal.signal_strength
    confidence = signal.confidence
    
    if strength > 0.5 and confidence > 0.7:
        action = "Strong Buy"
        rationale = "High confidence bullish signal"
    elif strength > 0.2 and confidence > 0.6:
        action = "Buy"
        rationale = "Moderate bullish signal"
    elif strength < -0.5 and confidence > 0.7:
        action = "Strong Sell"
        rationale = "High confidence bearish signal"
    elif strength < -0.2 and confidence > 0.6:
        action = "Sell"
        rationale = "Moderate bearish signal"
    elif confidence < 0.5:
        action = "Hold"
        rationale = "Low confidence signal"
    else:
        action = "Watch"
        rationale = "Neutral signal, monitor for changes"
    
    return {
        "action": action,
        "rationale": rationale,
        "risk_level": "High" if confidence < 0.6 else "Medium" if confidence < 0.8 else "Low"
    }
