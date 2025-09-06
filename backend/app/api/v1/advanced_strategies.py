"""
Advanced Trading Strategies API Endpoints
Implements strategies from GitHub-referenced strategy documents

Based on strategy files:
- clStrategy.txt: AI-powered trading with candlestick patterns
- gptStrategy.txt: Comprehensive technical analysis approach  
- gptStrategy2.txt: Production-ready trading with risk management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from app.services.advanced_strategies import (
    advanced_strategy_engine,
    StrategyType,
    SignalType,
    TradingSignal,
    StrategyParameters
)

router = APIRouter(prefix="/advanced-strategies", tags=["Advanced Trading Strategies"])


# Request Models
class StrategyAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., 'RELIANCE', 'INFY')")
    strategy_type: str = Field(..., description="trend_following, breakout, mean_reversion, ensemble")
    timeframe: str = Field(default="5m", description="Analysis timeframe")
    custom_params: Optional[Dict[str, Any]] = Field(default=None, description="Custom strategy parameters")


class MultiTimeframeRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    timeframes: List[str] = Field(default=["5m", "15m", "1h"], description="Multiple timeframes")
    strategies: List[str] = Field(default=["trend_following", "breakout"], description="Strategies to analyze")


class StrategyParametersRequest(BaseModel):
    """Request to update strategy parameters"""
    fast_ema: Optional[int] = Field(default=20, description="Fast EMA period")
    slow_ema: Optional[int] = Field(default=50, description="Slow EMA period")
    rsi_period: Optional[int] = Field(default=14, description="RSI period")
    adx_threshold: Optional[int] = Field(default=20, description="ADX strength threshold")
    risk_per_trade: Optional[float] = Field(default=1.0, description="Risk percentage per trade")
    max_position_size: Optional[float] = Field(default=5.0, description="Maximum position size %")


# Response Models
class StrategyResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    timestamp: str
    execution_time_ms: Optional[float] = None


@router.post("/trend-following", response_model=StrategyResponse)
async def analyze_trend_following_strategy(request: StrategyAnalysisRequest):
    """
    🚀 **Trend Following Strategy**: EMA crossover + RSI pullback + ADX strength
    
    Based on gptStrategy2.txt recommendations:
    - 20/50 EMA crossover for trend direction
    - RSI pullback filter (avoid overbought/oversold extremes)
    - ADX > 20 for trend strength confirmation
    - ATR-based position sizing and stops
    - Session timing controls (Indian market hours)
    
    Perfect for trending markets with clear direction.
    """
    try:
        start_time = datetime.now()
        
        # Analyze trend following strategy
        signal = await advanced_strategy_engine.analyze_trend_following_strategy(
            symbol=request.symbol,
            timeframe=request.timeframe
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if signal:
            response_data = {
                "symbol": signal.symbol,
                "strategy": "Trend Following (EMA + RSI + ADX)",
                "signal": signal.signal.value,
                "confidence": round(signal.confidence * 100, 2),
                
                # Entry/Exit Levels
                "entry_price": signal.entry_price,
                "target_price": signal.target_price,
                "stop_loss": signal.stop_loss,
                "risk_reward_ratio": round(signal.risk_reward_ratio, 2),
                
                # Position Management
                "position_size_percent": round(signal.position_size_percent, 2),
                "atr_multiple": signal.atr_multiple,
                
                # Technical Analysis
                "technical_reasons": signal.technical_reasons,
                "indicators": signal.indicators,
                
                # AI Enhancement
                "ai_pattern": signal.ai_pattern,
                "ai_confidence": round(signal.ai_confidence * 100, 2) if signal.ai_confidence else None,
                
                # Execution Details
                "timeframe": signal.timeframe,
                "session_timing": signal.session_timing,
                
                # Strategy Summary
                "strategy_summary": f"Trend Following: {signal.signal.value} {signal.symbol} at ₹{signal.entry_price:.2f}, "
                                   f"Target: ₹{signal.target_price:.2f}, SL: ₹{signal.stop_loss:.2f}, "
                                   f"R:R = 1:{signal.risk_reward_ratio:.1f}, Size: {signal.position_size_percent:.1f}%"
            }
        else:
            response_data = {
                "symbol": request.symbol,
                "strategy": "Trend Following",
                "signal": "NO_SIGNAL",
                "message": "No trend following opportunity detected",
                "reasons": [
                    "Insufficient trend strength (ADX < 20)",
                    "EMAs not aligned for clear trend",
                    "RSI not in optimal pullback zone",
                    "Outside trading session hours"
                ]
            }
        
        return StrategyResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend following analysis failed: {str(e)}")


@router.post("/breakout", response_model=StrategyResponse)
async def analyze_breakout_strategy(request: StrategyAnalysisRequest):
    """
    💥 **Breakout Strategy**: Donchian channel breakouts with volume confirmation
    
    Based on gptStrategy2.txt recommendations:
    - Donchian/HH-HL breakouts for momentum trades
    - Volume confirmation (1.5x average volume minimum)
    - ATR-based stops for volatility adjustment
    - Extended targets for breakout momentum
    - Avoid late session entries
    
    Ideal for capturing momentum moves and range expansions.
    """
    try:
        start_time = datetime.now()
        
        # Analyze breakout strategy
        signal = await advanced_strategy_engine.analyze_breakout_strategy(
            symbol=request.symbol,
            timeframe=request.timeframe
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if signal:
            response_data = {
                "symbol": signal.symbol,
                "strategy": "Breakout (Donchian + Volume)",
                "signal": signal.signal.value,
                "confidence": round(signal.confidence * 100, 2),
                
                # Entry/Exit Levels
                "entry_price": signal.entry_price,
                "target_price": signal.target_price,
                "stop_loss": signal.stop_loss,
                "risk_reward_ratio": round(signal.risk_reward_ratio, 2),
                
                # Position Management
                "position_size_percent": round(signal.position_size_percent, 2),
                
                # Technical Analysis
                "technical_reasons": signal.technical_reasons,
                "indicators": signal.indicators,
                
                # Breakout Specific
                "donchian_high": round(signal.indicators.get("donchian_high", 0), 2),
                "donchian_low": round(signal.indicators.get("donchian_low", 0), 2),
                "volume_ratio": round(signal.indicators.get("volume_ratio", 0), 2),
                
                # AI Enhancement
                "ai_pattern": signal.ai_pattern,
                "ai_confidence": round(signal.ai_confidence * 100, 2) if signal.ai_confidence else None,
                
                # Strategy Summary
                "strategy_summary": f"Breakout: {signal.signal.value} {signal.symbol} at ₹{signal.entry_price:.2f}, "
                                   f"Volume: {signal.indicators.get('volume_ratio', 0):.1f}x avg, "
                                   f"Target: ₹{signal.target_price:.2f}, SL: ₹{signal.stop_loss:.2f}"
            }
        else:
            response_data = {
                "symbol": request.symbol,
                "strategy": "Breakout",
                "signal": "NO_SIGNAL",
                "message": "No breakout opportunity detected",
                "reasons": [
                    "No break above/below Donchian channels",
                    "Insufficient volume confirmation",
                    "Price consolidating within range",
                    "Late session timing (avoid new breakouts)"
                ]
            }
        
        return StrategyResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Breakout analysis failed: {str(e)}")


@router.post("/mean-reversion", response_model=StrategyResponse)
async def analyze_mean_reversion_strategy(request: StrategyAnalysisRequest):
    """
    ↩️ **Mean Reversion Strategy**: RSI bands + VWAP anchor (Intraday only)
    
    Based on gptStrategy2.txt recommendations:
    - RSI extreme levels (25/75) for reversal signals
    - VWAP as anchor point for fair value
    - Tight risk management (smaller position sizes)
    - Avoid late session (mean reversion risky near close)
    - Use cautiously due to transaction costs
    
    Best for ranging markets with clear support/resistance.
    """
    try:
        start_time = datetime.now()
        
        # Analyze mean reversion strategy
        signal = await advanced_strategy_engine.analyze_mean_reversion_strategy(
            symbol=request.symbol,
            timeframe=request.timeframe
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if signal:
            response_data = {
                "symbol": signal.symbol,
                "strategy": "Mean Reversion (RSI + VWAP)",
                "signal": signal.signal.value,
                "confidence": round(signal.confidence * 100, 2),
                
                # Entry/Exit Levels
                "entry_price": signal.entry_price,
                "target_price": signal.target_price,
                "stop_loss": signal.stop_loss,
                "risk_reward_ratio": round(signal.risk_reward_ratio, 2),
                
                # Position Management (Smaller sizes for mean reversion)
                "position_size_percent": round(signal.position_size_percent, 2),
                "risk_note": "Reduced position size for mean reversion strategy",
                
                # Technical Analysis
                "technical_reasons": signal.technical_reasons,
                "indicators": signal.indicators,
                
                # Mean Reversion Specific
                "rsi_level": round(signal.indicators.get("rsi", 0), 1),
                "vwap_level": round(signal.indicators.get("vwap", 0), 2),
                "vwap_deviation": round(signal.indicators.get("vwap_deviation", 0), 2),
                
                # AI Enhancement
                "ai_pattern": signal.ai_pattern,
                "ai_confidence": round(signal.ai_confidence * 100, 2) if signal.ai_confidence else None,
                
                # Strategy Summary
                "strategy_summary": f"Mean Reversion: {signal.signal.value} {signal.symbol} at ₹{signal.entry_price:.2f}, "
                                   f"RSI: {signal.indicators.get('rsi', 0):.1f}, "
                                   f"VWAP: ₹{signal.indicators.get('vwap', 0):.2f}, "
                                   f"Target: ₹{signal.target_price:.2f}"
            }
        else:
            response_data = {
                "symbol": request.symbol,
                "strategy": "Mean Reversion",
                "signal": "NO_SIGNAL",
                "message": "No mean reversion opportunity detected",
                "reasons": [
                    "RSI not at extreme levels (25/75)",
                    "Price too far from VWAP anchor",
                    "Late in session (avoid mean reversion)",
                    "Insufficient reversal setup"
                ]
            }
        
        return StrategyResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mean reversion analysis failed: {str(e)}")


@router.post("/ensemble", response_model=StrategyResponse)
async def analyze_ensemble_strategy(request: MultiTimeframeRequest):
    """
    🎯 **Ensemble Strategy**: Multi-strategy consensus with regime detection
    
    Based on gptStrategy2.txt recommendations:
    - Combines multiple strategy signals for consensus
    - Multi-timeframe analysis for confirmation
    - Regime-based capital allocation
    - Weighted confidence scoring
    - Agreement-based signal filtering
    
    Most reliable signals with multiple confirmations.
    """
    try:
        start_time = datetime.now()
        
        # Get ensemble signal
        signal = await advanced_strategy_engine.get_ensemble_signal(
            symbol=request.symbol,
            timeframes=request.timeframes
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if signal:
            response_data = {
                "symbol": signal.symbol,
                "strategy": "Ensemble (Multi-Strategy Consensus)",
                "signal": signal.signal.value,
                "confidence": round(signal.confidence * 100, 2),
                
                # Entry/Exit Levels
                "entry_price": signal.entry_price,
                "target_price": signal.target_price,
                "stop_loss": signal.stop_loss,
                "risk_reward_ratio": round(signal.risk_reward_ratio, 2),
                
                # Position Management
                "position_size_percent": round(signal.position_size_percent, 2),
                
                # Technical Analysis
                "technical_reasons": signal.technical_reasons,
                "indicators": signal.indicators,
                
                # Ensemble Specific
                "consensus_type": "Multiple strategy agreement",
                "timeframes_analyzed": request.timeframes,
                "strategies_analyzed": request.strategies,
                
                # AI Enhancement
                "ai_pattern": signal.ai_pattern,
                "ai_confidence": round(signal.ai_confidence * 100, 2) if signal.ai_confidence else None,
                
                # Strategy Summary
                "strategy_summary": f"Ensemble: {signal.signal.value} {signal.symbol} at ₹{signal.entry_price:.2f}, "
                                   f"Multi-strategy consensus with {signal.confidence*100:.0f}% confidence, "
                                   f"Target: ₹{signal.target_price:.2f}, SL: ₹{signal.stop_loss:.2f}"
            }
        else:
            response_data = {
                "symbol": request.symbol,
                "strategy": "Ensemble",
                "signal": "NO_CONSENSUS",
                "message": "No strategy consensus detected",
                "reasons": [
                    "Conflicting signals across strategies",
                    "Insufficient confidence levels",
                    "No clear multi-timeframe agreement",
                    "Market regime not favorable for any strategy"
                ]
            }
        
        return StrategyResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ensemble analysis failed: {str(e)}")


@router.get("/strategy-parameters", response_model=StrategyResponse)
async def get_current_strategy_parameters():
    """
    ⚙️ **Strategy Parameters**: View current strategy configuration
    
    Returns all configurable parameters for the advanced strategies:
    - EMA periods, RSI settings
    - Risk management parameters
    - Session timing controls
    - Position sizing rules
    """
    try:
        params = advanced_strategy_engine.params
        
        response_data = {
            "trend_following_params": {
                "fast_ema": params.fast_ema,
                "slow_ema": params.slow_ema,
                "rsi_period": params.rsi_period,
                "rsi_oversold": params.rsi_oversold,
                "rsi_overbought": params.rsi_overbought,
                "adx_period": params.adx_period,
                "adx_threshold": params.adx_threshold
            },
            "breakout_params": {
                "donchian_period": params.donchian_period,
                "volume_threshold": params.volume_threshold,
                "atr_period": params.atr_period,
                "atr_stop_multiplier": params.atr_stop_multiplier
            },
            "mean_reversion_params": {
                "rsi_band_lower": params.rsi_band_lower,
                "rsi_band_upper": params.rsi_band_upper,
                "vwap_deviation": params.vwap_deviation
            },
            "risk_management": {
                "max_position_size": params.max_position_size,
                "daily_loss_limit": params.daily_loss_limit,
                "risk_per_trade": params.risk_per_trade
            },
            "session_timing": {
                "session_start": params.session_start,
                "session_end": params.session_end,
                "no_trades_after": params.no_trades_after
            }
        }
        
        return StrategyResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get parameters: {str(e)}")


@router.post("/update-parameters", response_model=StrategyResponse)
async def update_strategy_parameters(request: StrategyParametersRequest):
    """
    🔧 **Update Parameters**: Modify strategy parameters in real-time
    
    Allows dynamic adjustment of strategy parameters:
    - Technical indicator periods
    - Risk management settings
    - Position sizing rules
    - Threshold values
    """
    try:
        params = advanced_strategy_engine.params
        
        # Update parameters if provided
        if request.fast_ema is not None:
            params.fast_ema = request.fast_ema
        if request.slow_ema is not None:
            params.slow_ema = request.slow_ema
        if request.rsi_period is not None:
            params.rsi_period = request.rsi_period
        if request.adx_threshold is not None:
            params.adx_threshold = request.adx_threshold
        if request.risk_per_trade is not None:
            params.risk_per_trade = request.risk_per_trade
        if request.max_position_size is not None:
            params.max_position_size = request.max_position_size
        
        response_data = {
            "message": "Strategy parameters updated successfully",
            "updated_params": {
                "fast_ema": params.fast_ema,
                "slow_ema": params.slow_ema,
                "rsi_period": params.rsi_period,
                "adx_threshold": params.adx_threshold,
                "risk_per_trade": params.risk_per_trade,
                "max_position_size": params.max_position_size
            },
            "note": "Parameters updated for current session only"
        }
        
        return StrategyResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update parameters: {str(e)}")


@router.get("/available-strategies", response_model=StrategyResponse)
async def get_available_strategies():
    """
    📋 **Available Strategies**: List all implemented strategies
    
    Returns information about all available trading strategies based on
    the GitHub-referenced strategy documents.
    """
    try:
        strategies = {
            "trend_following": {
                "name": "Trend Following",
                "description": "EMA crossover + RSI pullback + ADX strength filter",
                "timeframes": ["5m", "15m", "1h"],
                "market_type": "Trending markets",
                "risk_level": "Medium",
                "source": "gptStrategy2.txt recommendations"
            },
            "breakout": {
                "name": "Breakout Strategy", 
                "description": "Donchian channel breakouts with volume confirmation",
                "timeframes": ["15m", "1h", "4h"],
                "market_type": "Range-bound to trending transition",
                "risk_level": "Medium-High",
                "source": "gptStrategy2.txt recommendations"
            },
            "mean_reversion": {
                "name": "Mean Reversion",
                "description": "RSI bands + VWAP anchor for intraday reversals",
                "timeframes": ["1m", "5m", "15m"],
                "market_type": "Ranging/sideways markets",
                "risk_level": "High (use cautiously)",
                "source": "gptStrategy2.txt recommendations"
            },
            "ensemble": {
                "name": "Ensemble Strategy",
                "description": "Multi-strategy consensus with regime detection",
                "timeframes": ["Multiple"],
                "market_type": "All market conditions",
                "risk_level": "Low (diversified)",
                "source": "gptStrategy2.txt ensemble approach"
            }
        }
        
        return StrategyResponse(
            success=True,
            data={
                "available_strategies": strategies,
                "total_strategies": len(strategies),
                "strategy_sources": [
                    "clStrategy.txt - AI-powered trading concepts",
                    "gptStrategy.txt - Comprehensive technical analysis",
                    "gptStrategy2.txt - Production-ready implementation"
                ]
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategies: {str(e)}")


@router.get("/health")
async def advanced_strategies_health():
    """Health check for advanced strategies service"""
    return {
        "status": "healthy",
        "service": "Advanced Trading Strategies",
        "strategies": ["trend_following", "breakout", "mean_reversion", "ensemble"],
        "source": "GitHub-referenced strategy documents",
        "timestamp": datetime.now().isoformat()
    }
