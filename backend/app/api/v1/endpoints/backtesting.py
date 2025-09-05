"""
Backtesting API endpoints
Provides backtesting functionality for AI trading strategies
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import pandas as pd
from ....services.backtesting import BacktestingEngine, simple_moving_average_strategy
from ....services.market_data import MarketDataService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for API requests/responses
class BacktestRequest(BaseModel):
    symbol: str
    strategy: str
    start_date: str  # ISO format
    end_date: str    # ISO format
    initial_capital: float = 100000.0
    strategy_params: Optional[Dict[str, Any]] = None

class BacktestResponse(BaseModel):
    success: bool
    message: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class StrategyListResponse(BaseModel):
    strategies: List[Dict[str, Any]]

# Available strategies
AVAILABLE_STRATEGIES = {
    "sma_crossover": {
        "name": "Simple Moving Average Crossover",
        "description": "Buy when short MA crosses above long MA, sell when it crosses below",
        "parameters": {
            "short_window": {"type": "int", "default": 20, "min": 5, "max": 100},
            "long_window": {"type": "int", "default": 50, "min": 20, "max": 200}
        }
    },
    "rsi_strategy": {
        "name": "RSI Mean Reversion",
        "description": "Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)",
        "parameters": {
            "rsi_window": {"type": "int", "default": 14, "min": 5, "max": 30},
            "oversold_threshold": {"type": "float", "default": 30, "min": 10, "max": 40},
            "overbought_threshold": {"type": "float", "default": 70, "min": 60, "max": 90}
        }
    }
}

@router.get("/strategies", response_model=StrategyListResponse)
async def get_available_strategies():
    """Get list of available backtesting strategies"""
    try:
        strategies = []
        for key, strategy in AVAILABLE_STRATEGIES.items():
            strategies.append({
                "id": key,
                "name": strategy["name"],
                "description": strategy["description"],
                "parameters": strategy["parameters"]
            })
        
        return StrategyListResponse(strategies=strategies)
        
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """Run a backtest for specified strategy and parameters"""
    try:
        # Validate strategy
        if request.strategy not in AVAILABLE_STRATEGIES:
            return BacktestResponse(
                success=False,
                message="Invalid strategy",
                error=f"Strategy '{request.strategy}' not found"
            )
        
        # Parse dates
        try:
            start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
        except ValueError as e:
            return BacktestResponse(
                success=False,
                message="Invalid date format",
                error=str(e)
            )
        
        # Validate date range
        if start_date >= end_date:
            return BacktestResponse(
                success=False,
                message="Invalid date range",
                error="Start date must be before end date"
            )
        
        if (end_date - start_date).days < 30:
            return BacktestResponse(
                success=False,
                message="Invalid date range",
                error="Date range must be at least 30 days"
            )
        
        # Get historical data
        market_service = MarketDataService()
        historical_data = market_service.get_historical_data_range(
            request.symbol, 
            start_date, 
            end_date
        )
        
        if not historical_data:
            return BacktestResponse(
                success=False,
                message="No historical data available",
                error=f"No data found for {request.symbol} in specified date range"
            )
        
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create backtesting engine
        engine = BacktestingEngine(initial_capital=request.initial_capital)
        engine.add_historical_data(request.symbol, df)
        
        # Get strategy function
        strategy_func = get_strategy_function(request.strategy, request.strategy_params)
        
        # Run backtest
        results = engine.run_backtest(request.symbol, strategy_func, start_date, end_date)
        
        # Format results
        formatted_results = {
            "summary": {
                "start_date": results.start_date.isoformat(),
                "end_date": results.end_date.isoformat(),
                "initial_capital": request.initial_capital,
                "final_capital": request.initial_capital + results.total_pnl,
                "total_trades": results.total_trades,
                "winning_trades": results.winning_trades,
                "losing_trades": results.losing_trades,
                "win_rate": round(results.win_rate, 2),
                "total_pnl": round(results.total_pnl, 2),
                "total_pnl_percent": round(results.total_pnl_percent, 2),
                "sharpe_ratio": round(results.sharpe_ratio, 2),
                "max_drawdown": round(results.max_drawdown, 2),
                "avg_trade_duration_days": results.avg_trade_duration.days,
                "best_trade": round(results.best_trade, 2),
                "worst_trade": round(results.worst_trade, 2)
            },
            "trades": [
                {
                    "symbol": trade.symbol,
                    "entry_price": round(trade.entry_price, 2),
                    "exit_price": round(trade.exit_price, 2),
                    "quantity": trade.quantity,
                    "entry_timestamp": trade.entry_timestamp.isoformat(),
                    "exit_timestamp": trade.exit_timestamp.isoformat(),
                    "pnl": round(trade.pnl, 2),
                    "pnl_percent": round(trade.pnl_percent, 2),
                    "hold_duration_days": trade.hold_duration.days
                }
                for trade in results.trades
            ],
            "equity_curve": [
                {
                    "timestamp": point["timestamp"].isoformat(),
                    "total_value": round(point["total_value"], 2),
                    "return_percent": round(point["return_percent"], 2)
                }
                for point in results.equity_curve
            ]
        }
        
        return BacktestResponse(
            success=True,
            message=f"Backtest completed successfully. {results.total_trades} trades executed.",
            results=formatted_results
        )
        
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        return BacktestResponse(
            success=False,
            message="Backtest failed",
            error=str(e)
        )

@router.get("/sample-data/{symbol}")
async def get_sample_data(symbol: str, days: int = 365):
    """Get sample historical data for backtesting"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        market_service = MarketDataService()
        historical_data = market_service.get_historical_data_range(symbol, start_date, end_date)
        
        if not historical_data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        return {
            "symbol": symbol,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data_points": len(historical_data),
            "sample_data": historical_data[:10]  # First 10 records
        }
        
    except Exception as e:
        logger.error(f"Error getting sample data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_strategy_function(strategy_name: str, params: Optional[Dict[str, Any]] = None):
    """Get strategy function with parameters"""
    if strategy_name == "sma_crossover":
        def strategy_func(data):
            short_window = params.get("short_window", 20) if params else 20
            long_window = params.get("long_window", 50) if params else 50
            return simple_moving_average_strategy(data, short_window, long_window)
        return strategy_func
    
    elif strategy_name == "rsi_strategy":
        def rsi_strategy_func(data):
            # RSI strategy implementation
            rsi_window = params.get("rsi_window", 14) if params else 14
            oversold = params.get("oversold_threshold", 30) if params else 30
            overbought = params.get("overbought_threshold", 70) if params else 70
            return rsi_strategy(data, rsi_window, oversold, overbought)
        return rsi_strategy_func
    
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

def rsi_strategy(data: pd.DataFrame, window: int = 14, oversold: float = 30, overbought: float = 70):
    """RSI-based trading strategy"""
    # Calculate RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    signals = []
    position = False
    
    for i in range(window, len(data)):
        current_rsi = data['RSI'].iloc[i]
        
        # Buy signal: RSI < oversold and not in position
        if current_rsi < oversold and not position:
            signals.append({
                'timestamp': data['timestamp'].iloc[i],
                'action': 'BUY',
                'price': data['close'].iloc[i],
                'reason': f'RSI oversold: {current_rsi:.2f}'
            })
            position = True
        
        # Sell signal: RSI > overbought and in position
        elif current_rsi > overbought and position:
            signals.append({
                'timestamp': data['timestamp'].iloc[i],
                'action': 'SELL',
                'price': data['close'].iloc[i],
                'reason': f'RSI overbought: {current_rsi:.2f}'
            })
            position = False
    
    return signals
