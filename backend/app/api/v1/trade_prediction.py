"""
API endpoints for Advanced Trade Prediction Service
Provides precise trade direction, entry/exit points, and pattern analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from app.services.ai_trade_prediction import (
    ai_trade_prediction_service,
    TradeDirection, 
    CandlestickPattern,
    TradeSignal
)

router = APIRouter(prefix="/trade-prediction", tags=["Trade Prediction"])


# Request Models
class TradePredictionRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., 'RELIANCE', 'INFY')")
    timeframe: str = Field(default="1D", description="Analysis timeframe")
    custom_inputs: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Custom analysis inputs (risk tolerance, market view, etc.)"
    )


class CandlestickAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    timeframe: str = Field(default="1D", description="Candlestick timeframe")
    lookback_days: int = Field(default=5, description="Number of days to analyze")


class ShortSellAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol for short selling")
    resistance_level: Optional[float] = Field(None, description="Key resistance level")
    risk_tolerance: str = Field(default="medium", description="Risk tolerance (low/medium/high)")


class RiskRewardOptimizationRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    trade_direction: str = Field(..., description="BUY/SELL/SHORT_SELL")
    entry_price: float = Field(..., description="Planned entry price")
    capital: float = Field(..., description="Available capital")
    risk_tolerance: str = Field(default="medium", description="Risk tolerance level")


# Response Models
class TradePredictionResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    timestamp: str
    execution_time_ms: Optional[float] = None


@router.post("/predict-trade", response_model=TradePredictionResponse)
async def predict_trade_direction(request: TradePredictionRequest):
    """
    🎯 **CORE FEATURE**: Predict optimal trade direction with precise entry/exit points
    
    This is the main endpoint for your trading AI. It provides:
    - Trade direction (BUY/SELL/SHORT_SELL/HOLD) 
    - Exact entry price with reasoning
    - Target price levels
    - Stop-loss levels
    - Position sizing recommendations
    - Risk-reward analysis
    - Candlestick pattern analysis
    - Custom input integration
    """
    try:
        start_time = datetime.now()
        
        # Get comprehensive trade prediction
        trade_signal = await ai_trade_prediction_service.predict_trade_direction(
            symbol=request.symbol,
            timeframe=request.timeframe,
            custom_inputs=request.custom_inputs
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Format response with all critical trading information
        response_data = {
            "symbol": trade_signal.symbol,
            "analysis_type": "trade_prediction",
            "timestamp": trade_signal.timestamp.isoformat(),
            
            # Core Prediction
            "trade_direction": trade_signal.direction.value,
            "confidence_percent": round(trade_signal.confidence * 100, 2),
            
            # Price Levels
            "entry_price": trade_signal.entry_price,
            "target_price": trade_signal.target_price,
            "stop_loss": trade_signal.stop_loss,
            
            # Risk Management
            "risk_reward_ratio": trade_signal.risk_reward_ratio,
            "position_size_percent": trade_signal.position_size_percent,
            
            # Pattern Analysis
            "candlestick_pattern": trade_signal.primary_pattern.value if trade_signal.primary_pattern else None,
            "pattern_strength": trade_signal.pattern_strength,
            
            # Supporting Analysis
            "technical_reasons": trade_signal.technical_reasons,
            "risk_factors": trade_signal.risk_factors,
            "timeframe": trade_signal.timeframe,
            
            # Execution Details
            "order_type": trade_signal.order_type,
            "validity": trade_signal.validity,
            
            # Trade Summary
            "trade_summary": f"{trade_signal.direction.value} {trade_signal.symbol} at ₹{trade_signal.entry_price:.2f}, "
                           f"Target: ₹{trade_signal.target_price:.2f}, SL: ₹{trade_signal.stop_loss:.2f}, "
                           f"R:R = 1:{trade_signal.risk_reward_ratio:.1f}"
        }
        
        return TradePredictionResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trade prediction failed: {str(e)}")


@router.post("/candlestick-analysis", response_model=TradePredictionResponse) 
async def analyze_candlestick_patterns(request: CandlestickAnalysisRequest):
    """
    📊 **Candlestick Pattern Recognition**: Advanced pattern analysis with AI
    
    Identifies and analyzes candlestick patterns including:
    - Bullish patterns (Hammer, Engulfing, Morning Star, etc.)
    - Bearish patterns (Shooting Star, Dark Cloud, Evening Star, etc.)
    - Neutral patterns (Doji, Spinning Top, etc.)
    - Pattern strength and reliability
    - Volume confirmation
    - Price targets based on patterns
    """
    try:
        start_time = datetime.now()
        
        # Perform candlestick pattern analysis
        pattern_analysis = await ai_trade_prediction_service.analyze_candlestick_patterns(
            symbol=request.symbol,
            timeframe=request.timeframe,
            lookback_days=request.lookback_days
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if pattern_analysis:
            response_data = {
                "symbol": request.symbol,
                "analysis_type": "candlestick_patterns",
                "timeframe": request.timeframe,
                "lookback_days": request.lookback_days,
                
                # Pattern Details
                "primary_pattern": pattern_analysis.pattern.value,
                "pattern_name": pattern_analysis.pattern_name,
                "signal_type": pattern_analysis.signal_type,
                "strength": pattern_analysis.strength,
                "reliability": pattern_analysis.reliability,
                "confirmation_required": pattern_analysis.confirmation_required,
                "description": pattern_analysis.description,
                
                # Trading Implications
                "trading_action": "BUY" if pattern_analysis.signal_type == "BULLISH" else "SELL" if pattern_analysis.signal_type == "BEARISH" else "HOLD",
                "pattern_validity": f"Pattern strength: {pattern_analysis.strength}/10, Reliability: {pattern_analysis.reliability}%",
                
                # Analysis Summary
                "analysis_summary": f"Detected {pattern_analysis.pattern_name} pattern with {pattern_analysis.signal_type.lower()} bias. "
                                   f"Strength: {pattern_analysis.strength}/10, Historical success rate: {pattern_analysis.reliability}%"
            }
        else:
            response_data = {
                "symbol": request.symbol,
                "analysis_type": "candlestick_patterns",
                "message": "No significant candlestick patterns detected",
                "recommendation": "Monitor for pattern formation or use other technical indicators"
            }
        
        return TradePredictionResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Candlestick analysis failed: {str(e)}")


@router.post("/short-sell-analysis", response_model=TradePredictionResponse)
async def analyze_short_sell_opportunity(request: ShortSellAnalysisRequest):
    """
    📉 **Short Selling Analysis**: Specialized analysis for short selling opportunities
    
    Provides comprehensive short selling analysis including:
    - Short viability assessment
    - Optimal short entry points
    - Cover target levels
    - Risk management for shorts
    - Margin requirements consideration
    - Squeeze risk assessment
    """
    try:
        start_time = datetime.now()
        
        # Perform short selling analysis using trade prediction
        trade_signal = await ai_trade_prediction_service.predict_trade_direction(
            symbol=request.symbol,
            custom_inputs={
                "analysis_focus": "short_selling",
                "resistance_level": request.resistance_level,
                "risk_tolerance": request.risk_tolerance,
                "short_specific_analysis": True
            }
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Check if AI recommends short selling
        short_viable = trade_signal.direction == TradeDirection.SHORT_SELL
        
        response_data = {
            "symbol": request.symbol,
            "analysis_type": "short_sell_analysis",
            
            # Short Selling Assessment
            "short_recommendation": "YES" if short_viable else "NO",
            "confidence": round(trade_signal.confidence * 100, 2),
            "short_reasoning": trade_signal.technical_reasons[0] if trade_signal.technical_reasons else "Pattern analysis",
            
            # Entry/Exit Levels
            "short_entry_price": trade_signal.entry_price if short_viable else None,
            "cover_target": trade_signal.target_price if short_viable else None,
            "stop_loss": trade_signal.stop_loss if short_viable else None,
            
            # Risk Management
            "position_size_percent": trade_signal.position_size_percent if short_viable else 0,
            "risk_reward_ratio": trade_signal.risk_reward_ratio if short_viable else 0,
            
            # Short-Specific Risks
            "short_risks": [
                "Short squeeze risk",
                "Margin call risk", 
                "Borrowing cost",
                "Dividend risk"
            ] + (trade_signal.risk_factors if short_viable else []),
            
            # Market Context
            "market_conditions": "Favorable for shorting" if short_viable else "Not ideal for shorting",
            "alternative_strategy": "Consider put options or wait for better setup" if not short_viable else None
        }
        
        return TradePredictionResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Short sell analysis failed: {str(e)}")


@router.post("/optimize-risk-reward", response_model=TradePredictionResponse)
async def optimize_risk_reward_parameters(request: RiskRewardOptimizationRequest):
    """
    ⚖️ **Risk-Reward Optimization**: Optimize position sizing, stop-loss, and targets
    
    Provides optimal risk-reward parameters including:
    - Position sizing based on volatility
    - Multiple stop-loss levels (conservative/aggressive)
    - Primary and secondary targets
    - Risk-reward ratio optimization
    - Scaling and profit-taking strategies
    """
    try:
        start_time = datetime.now()
        
        # Get optimization recommendations
        optimization = await ai_trade_prediction_service.optimize_entry_exit_points(
            symbol=request.symbol,
            trade_direction=TradeDirection(request.trade_direction),
            custom_analysis={
                "entry_price": request.entry_price,
                "capital": request.capital,
                "risk_tolerance": request.risk_tolerance
            }
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response_data = {
            "symbol": request.symbol,
            "analysis_type": "risk_reward_optimization",
            "trade_direction": request.trade_direction,
            "entry_price": request.entry_price,
            
            # Optimized Parameters
            "optimal_position_size": optimization.get("optimal_position_size", 0),
            "position_reasoning": optimization.get("position_reasoning", ""),
            
            # Stop Loss Levels
            "stop_loss_levels": optimization.get("stop_loss_levels", {}),
            
            # Target Levels  
            "target_levels": optimization.get("target_levels", {}),
            
            # Risk Metrics
            "risk_reward_ratios": optimization.get("risk_reward_ratios", []),
            
            # Strategy Details
            "scaling_strategy": optimization.get("scaling_strategy", ""),
            "trailing_stop": optimization.get("trailing_stop", ""),
            "adjustment_triggers": optimization.get("adjustment_triggers", []),
            
            # Execution Guidance
            "execution_strategy": optimization.get("execution_strategy", ""),
            "session_timing": optimization.get("session_timing", ""),
            "risk_management": optimization.get("risk_management", [])
        }
        
        return TradePredictionResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk-reward optimization failed: {str(e)}")


@router.get("/supported-patterns", response_model=TradePredictionResponse)
async def get_supported_candlestick_patterns():
    """
    📋 **Supported Patterns**: List all candlestick patterns recognized by the AI
    """
    try:
        patterns = {
            "bullish_patterns": {
                "hammer": "Bullish reversal at bottom",
                "bullish_engulfing": "Strong bullish reversal",
                "morning_star": "Three-candle bullish reversal",
                "piercing_line": "Bullish reversal pattern",
                "bullish_harami": "Potential bullish reversal",
                "dragonfly_doji": "Bullish reversal doji"
            },
            "bearish_patterns": {
                "shooting_star": "Bearish reversal at top",
                "bearish_engulfing": "Strong bearish reversal", 
                "evening_star": "Three-candle bearish reversal",
                "dark_cloud_cover": "Bearish reversal pattern",
                "bearish_harami": "Potential bearish reversal",
                "gravestone_doji": "Bearish reversal doji"
            },
            "neutral_patterns": {
                "doji": "Indecision candle",
                "spinning_top": "Small body with wicks",
                "hanging_man": "Potential bearish at top"
            }
        }
        
        return TradePredictionResponse(
            success=True,
            data={
                "supported_patterns": patterns,
                "total_patterns": sum(len(v) for v in patterns.values()),
                "pattern_categories": list(patterns.keys())
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patterns: {str(e)}")


@router.get("/health")
async def trade_prediction_health():
    """Health check for trade prediction service"""
    return {
        "status": "healthy",
        "service": "AI Trade Prediction",
        "features": [
            "trade_direction_prediction",
            "candlestick_pattern_analysis", 
            "short_sell_analysis",
            "risk_reward_optimization"
        ],
        "timestamp": datetime.now().isoformat()
    }
