"""
Trading strategies endpoints
Handles strategy backtesting, signals, and performance analysis
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.services.backtesting import (
    backtesting_engine, 
    BacktestParams, 
    StrategyType,
    BacktestResults as BacktestEngineResults
)

router = APIRouter()


class TradingSignal(BaseModel):
    """Trading signal model"""
    symbol: str
    strategy: str
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float
    timestamp: str
    explanation: str


class BacktestRequest(BaseModel):
    """Backtest request model"""
    symbol: str
    strategy: str
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    # Strategy parameters
    fast_period: int = 10
    slow_period: int = 20
    rsi_period: int = 14
    rsi_oversold: int = 30
    rsi_overbought: int = 70


class BacktestResult(BaseModel):
    """Backtest result model for API response"""
    strategy: str
    symbol: str
    start_date: str
    end_date: str
    
    # Performance metrics
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    
    # Trading metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    
    # Risk metrics
    var_95: float
    cvar_95: float
    beta: float
    alpha: float
    
    # Time series data (simplified for API)
    equity_curve_data: List[dict]
    monthly_returns_data: List[dict]


class StrategyInfo(BaseModel):
    """Strategy information model"""
    name: str
    display_name: str
    description: str
    type: str
    parameters: dict


@router.get("/signals/{symbol}")
async def getTradingSignals(symbol: str) -> List[TradingSignal]:
    """Get current trading signals for a symbol"""
    # TODO: Implement real-time signal generation
    return [
        TradingSignal(
            symbol=symbol,
            strategy="SMA_CROSSOVER",
            signal="BUY",
            confidence=0.75,
            timestamp=datetime.now().isoformat(),
            explanation="Fast SMA (10) crossed above Slow SMA (20) with strong volume"
        ),
        TradingSignal(
            symbol=symbol,
            strategy="RSI_STRATEGY",
            signal="HOLD",
            confidence=0.60,
            timestamp=datetime.now().isoformat(),
            explanation="RSI at 45 - neutral zone, waiting for oversold/overbought levels"
        )
    ]


@router.post("/backtest")
async def runBacktest(request: BacktestRequest) -> BacktestResult:
    """Run professional backtest for a strategy"""
    try:
        # Validate strategy
        strategy_mapping = {
            "SMA_CROSSOVER": StrategyType.SMA_CROSSOVER,
            "EMA_CROSSOVER": StrategyType.EMA_CROSSOVER,
            "RSI_STRATEGY": StrategyType.RSI_STRATEGY,
            "MACD_STRATEGY": StrategyType.MACD_STRATEGY,
            "BOLLINGER_BANDS": StrategyType.BOLLINGER_BANDS,
            "MEAN_REVERSION": StrategyType.MEAN_REVERSION,
        }
        
        if request.strategy not in strategy_mapping:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported strategy: {request.strategy}"
            )
        
        # Create backtest parameters
        params = BacktestParams(
            symbol=request.symbol,
            strategy=strategy_mapping[request.strategy],
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            fast_period=request.fast_period,
            slow_period=request.slow_period,
            rsi_period=request.rsi_period,
            rsi_oversold=request.rsi_oversold,
            rsi_overbought=request.rsi_overbought
        )
        
        # Run backtest
        results = await backtesting_engine.run_backtest(params)
        
        # Convert equity curve to API format
        equity_curve_data = [
            {
                "date": str(date),
                "value": float(value)
            }
            for date, value in results.equity_curve.items()
        ]
        
        # Convert monthly returns to API format
        monthly_returns_data = [
            {
                "month": str(date),
                "return": float(ret)
            }
            for date, ret in results.monthly_returns.items()
        ]
        
        # Create API response
        return BacktestResult(
            strategy=request.strategy,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            total_return=results.total_return,
            annualized_return=results.annualized_return,
            volatility=results.volatility,
            sharpe_ratio=results.sharpe_ratio,
            sortino_ratio=results.sortino_ratio,
            max_drawdown=results.max_drawdown,
            total_trades=results.total_trades,
            winning_trades=results.winning_trades,
            losing_trades=results.losing_trades,
            win_rate=results.win_rate,
            profit_factor=results.profit_factor,
            avg_win=results.avg_win,
            avg_loss=results.avg_loss,
            var_95=results.var_95,
            cvar_95=results.cvar_95,
            beta=results.beta,
            alpha=results.alpha,
            equity_curve_data=equity_curve_data,
            monthly_returns_data=monthly_returns_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backtest failed: {str(e)}"
        )


@router.get("/strategies")
async def getAvailableStrategies() -> List[StrategyInfo]:
    """Get list of available trading strategies with detailed information"""
    return [
        StrategyInfo(
            name="SMA_CROSSOVER",
            display_name="SMA Crossover",
            description="Simple Moving Average crossover strategy - buy when fast SMA crosses above slow SMA",
            type="trend_following",
            parameters={
                "fast_period": {"type": "int", "default": 10, "min": 5, "max": 50},
                "slow_period": {"type": "int", "default": 20, "min": 10, "max": 200}
            }
        ),
        StrategyInfo(
            name="RSI_STRATEGY",
            display_name="RSI Mean Reversion",
            description="RSI-based mean reversion strategy - buy oversold, sell overbought",
            type="mean_reversion",
            parameters={
                "rsi_period": {"type": "int", "default": 14, "min": 5, "max": 50},
                "rsi_oversold": {"type": "int", "default": 30, "min": 10, "max": 40},
                "rsi_overbought": {"type": "int", "default": 70, "min": 60, "max": 90}
            }
        ),
        StrategyInfo(
            name="MACD_STRATEGY",
            display_name="MACD Crossover",
            description="MACD signal line crossover strategy for trend identification",
            type="trend_following",
            parameters={
                "fast_ema": {"type": "int", "default": 12, "min": 5, "max": 50},
                "slow_ema": {"type": "int", "default": 26, "min": 10, "max": 100},
                "signal_period": {"type": "int", "default": 9, "min": 5, "max": 20}
            }
        ),
        StrategyInfo(
            name="BOLLINGER_BANDS",
            display_name="Bollinger Bands",
            description="Mean reversion strategy using Bollinger Bands",
            type="mean_reversion",
            parameters={
                "bb_period": {"type": "int", "default": 20, "min": 10, "max": 50},
                "bb_std": {"type": "float", "default": 2.0, "min": 1.0, "max": 3.0}
            }
        )
    ]
