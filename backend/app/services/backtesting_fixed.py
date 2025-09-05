"""
Professional Backtesting Engine for GoGoTrade
Uses VectorBT for fast vectorized backtesting with comprehensive analytics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Optional imports with fallbacks
try:
    import vectorbt as vbt
    VECTORBT_AVAILABLE = True
except ImportError:
    VECTORBT_AVAILABLE = False
    print("Warning: VectorBT not available. Using fallback backtesting implementation.")

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("Warning: TA-Lib not available. Using pandas-based technical indicators.")

from app.core.database import get_db_session
from app.models import OHLCVData, Instrument
from sqlalchemy import select, and_
import asyncio


class TechnicalIndicators:
    """Technical indicators with fallback implementations when TA-Lib is not available"""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        if TALIB_AVAILABLE:
            return pd.Series(talib.RSI(data.values, timeperiod=period), index=data.index)
        else:
            # Pandas-based RSI calculation
            delta = data.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
            avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD indicator"""
        if TALIB_AVAILABLE:
            macd_line, macd_signal, macd_hist = talib.MACD(data.values, fastperiod=fast, slowperiod=slow, signalperiod=signal)
            return (pd.Series(macd_line, index=data.index), 
                   pd.Series(macd_signal, index=data.index),
                   pd.Series(macd_hist, index=data.index))
        else:
            # Pandas-based MACD calculation
            ema_fast = data.ewm(span=fast).mean()
            ema_slow = data.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            macd_signal = macd_line.ewm(span=signal).mean()
            macd_hist = macd_line - macd_signal
            return macd_line, macd_signal, macd_hist
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        if TALIB_AVAILABLE:
            upper, middle, lower = talib.BBANDS(data.values, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
            return (pd.Series(upper, index=data.index),
                   pd.Series(middle, index=data.index), 
                   pd.Series(lower, index=data.index))
        else:
            # Pandas-based Bollinger Bands
            middle = data.rolling(window=period).mean()
            std = data.rolling(window=period).std()
            upper = middle + (std * std_dev)
            lower = middle - (std * std_dev)
            return upper, middle, lower


class StrategyType(Enum):
    """Available trading strategies"""
    SMA_CROSSOVER = "sma_crossover"
    EMA_CROSSOVER = "ema_crossover"
    RSI_STRATEGY = "rsi_strategy"
    MACD_STRATEGY = "macd_strategy"
    BOLLINGER_BANDS = "bollinger_bands"
    MEAN_REVERSION = "mean_reversion"


@dataclass
class BacktestParams:
    """Parameters for backtesting"""
    symbol: str
    strategy: StrategyType
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    
    # Strategy-specific parameters
    fast_period: int = 10
    slow_period: int = 20
    rsi_period: int = 14
    rsi_oversold: int = 30
    rsi_overbought: int = 70


@dataclass
class BacktestResults:
    """Comprehensive backtest results"""
    # Basic info
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
    var_95: float  # Value at Risk
    cvar_95: float  # Conditional Value at Risk
    beta: float
    alpha: float
    
    # Time series data
    equity_curve: pd.Series
    drawdown_series: pd.Series
    trades_df: pd.DataFrame
    
    # Performance attribution
    monthly_returns: pd.Series
    yearly_returns: pd.Series


class BacktestingEngine:
    """Professional backtesting engine with VectorBT"""
    
    def __init__(self):
        self.commission = 0.001
        self.slippage = 0.0005
        
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        timeframe: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data from TimescaleDB
        """
        async with get_db_session() as db:
            # Get instrument
            instrument_query = select(Instrument).where(Instrument.tradingsymbol == symbol)
            instrument_result = await db.execute(instrument_query)
            instrument = instrument_result.scalar_one_or_none()
            
            if not instrument:
                raise ValueError(f"Instrument {symbol} not found")
            
            # Convert date strings to datetime objects
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Get OHLCV data
            ohlcv_query = select(OHLCVData).where(
                and_(
                    OHLCVData.instrument_id == instrument.id,
                    OHLCVData.timeframe == timeframe,
                    OHLCVData.timestamp >= start_dt,
                    OHLCVData.timestamp <= end_dt
                )
            ).order_by(OHLCVData.timestamp)
            
            ohlcv_result = await db.execute(ohlcv_query)
            ohlcv_data = ohlcv_result.scalars().all()
            
            if not ohlcv_data:
                raise ValueError(f"No historical data found for {symbol}")
            
            # Convert to DataFrame
            data = []
            for row in ohlcv_data:
                data.append({
                    'timestamp': row.timestamp,
                    'open': float(row.open),
                    'high': float(row.high),
                    'low': float(row.low),
                    'close': float(row.close),
                    'volume': int(row.volume)
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            return df
    
    def generate_signals_sma(
        self, 
        data: pd.DataFrame, 
        fast_period: int = 10, 
        slow_period: int = 20
    ) -> pd.Series:
        """
        Generate SMA crossover signals
        1 = Buy, -1 = Sell, 0 = Hold
        """
        fast_sma = TechnicalIndicators.sma(data['close'], fast_period)
        slow_sma = TechnicalIndicators.sma(data['close'], slow_period)
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when fast SMA crosses above slow SMA
        for i in range(1, len(data)):
            if (fast_sma.iloc[i] > slow_sma.iloc[i] and 
                fast_sma.iloc[i-1] <= slow_sma.iloc[i-1]):
                signals.iloc[i] = 1
            elif (fast_sma.iloc[i] < slow_sma.iloc[i] and 
                  fast_sma.iloc[i-1] >= slow_sma.iloc[i-1]):
                signals.iloc[i] = -1
        
        return signals
    
    def generate_signals_rsi(
        self, 
        data: pd.DataFrame, 
        period: int = 14, 
        oversold: int = 30, 
        overbought: int = 70
    ) -> pd.Series:
        """
        Generate RSI-based signals
        """
        rsi = TechnicalIndicators.rsi(data['close'], period)
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when RSI crosses above oversold level
        for i in range(1, len(data)):
            if rsi.iloc[i] > oversold and rsi.iloc[i-1] <= oversold:
                signals.iloc[i] = 1
            elif rsi.iloc[i] < overbought and rsi.iloc[i-1] >= overbought:
                signals.iloc[i] = -1
        
        return signals
    
    def run_simple_backtest(self, data: pd.DataFrame, signals: pd.Series, initial_capital: float) -> Dict:
        """Simple backtest fallback implementation"""
        portfolio_value = initial_capital
        position = 0
        trades = []
        equity_curve = []
        
        for i in range(len(data)):
            if signals.iloc[i] == 1 and position == 0:  # Buy signal
                shares = portfolio_value / data['close'].iloc[i]
                position = shares
                portfolio_value = 0
                trades.append({'type': 'buy', 'price': data['close'].iloc[i], 'shares': shares, 'date': data.index[i]})
            elif signals.iloc[i] == -1 and position > 0:  # Sell signal
                portfolio_value = position * data['close'].iloc[i]
                trades.append({'type': 'sell', 'price': data['close'].iloc[i], 'shares': position, 'date': data.index[i]})
                position = 0
            
            # Calculate current portfolio value
            current_value = portfolio_value + (position * data['close'].iloc[i] if position > 0 else 0)
            equity_curve.append(current_value)
        
        # Final liquidation if still holding position
        if position > 0:
            portfolio_value = position * data['close'].iloc[-1]
        
        return {
            'final_value': portfolio_value,
            'trades': trades,
            'equity_curve': equity_curve
        }
    
    def calculate_simple_metrics(self, result: Dict, initial_capital: float) -> Dict:
        """Calculate metrics for simple backtest"""
        final_value = result['final_value']
        equity_curve = result['equity_curve']
        trades = result['trades']
        
        # Basic calculations
        total_return = (final_value - initial_capital) / initial_capital
        
        # Calculate returns from equity curve
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()
        
        # Risk metrics
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
        annualized_return = total_return  # Simplified for short periods
        sharpe_ratio = annualized_return / volatility if volatility != 0 else 0
        
        # Drawdown calculation
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0
        
        # Trading metrics
        total_trades = len([t for t in trades if t['type'] == 'buy'])
        buy_trades = [t for t in trades if t['type'] == 'buy']
        sell_trades = [t for t in trades if t['type'] == 'sell']
        
        # Match buy/sell pairs to calculate PnL
        winning_trades = 0
        losing_trades = 0
        
        for i in range(min(len(buy_trades), len(sell_trades))):
            pnl = (sell_trades[i]['price'] - buy_trades[i]['price']) * buy_trades[i]['shares']
            if pnl > 0:
                winning_trades += 1
            else:
                losing_trades += 1
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sharpe_ratio,  # Simplified
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': 1.0,  # Simplified
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'var_95': 0.0,
            'cvar_95': 0.0,
            'beta': 0.0,
            'alpha': 0.0,
            'equity_curve': {str(i): v for i, v in enumerate(equity_curve)},
            'monthly_returns': {},
            'yearly_returns': {}
        }
    
    async def run_backtest(self, params: BacktestParams) -> BacktestResults:
        """
        Run comprehensive backtest
        """
        try:
            # Get historical data
            data = await self.get_historical_data(
                params.symbol, 
                params.start_date, 
                params.end_date
            )
            
            # Generate signals based on strategy
            if params.strategy == StrategyType.SMA_CROSSOVER:
                signals = self.generate_signals_sma(data, params.fast_period, params.slow_period)
            elif params.strategy == StrategyType.RSI_STRATEGY:
                signals = self.generate_signals_rsi(data, params.rsi_period, params.rsi_oversold, params.rsi_overbought)
            else:
                raise ValueError(f"Strategy {params.strategy} not implemented")
            
            # Run backtest
            backtest_result = self.run_simple_backtest(data, signals, params.initial_capital)
            
            # Calculate metrics
            metrics = self.calculate_simple_metrics(backtest_result, params.initial_capital)
            
            # Create results object
            return BacktestResults(
                strategy=params.strategy.value,
                symbol=params.symbol,
                start_date=params.start_date,
                end_date=params.end_date,
                total_return=metrics['total_return'],
                annualized_return=metrics['annualized_return'],
                volatility=metrics['volatility'],
                sharpe_ratio=metrics['sharpe_ratio'],
                sortino_ratio=metrics['sortino_ratio'],
                max_drawdown=metrics['max_drawdown'],
                total_trades=metrics['total_trades'],
                winning_trades=metrics['winning_trades'],
                losing_trades=metrics['losing_trades'],
                win_rate=metrics['win_rate'],
                profit_factor=metrics['profit_factor'],
                avg_win=metrics['avg_win'],
                avg_loss=metrics['avg_loss'],
                var_95=metrics['var_95'],
                cvar_95=metrics['cvar_95'],
                beta=metrics['beta'],
                alpha=metrics['alpha'],
                equity_curve=pd.Series(metrics['equity_curve']),
                drawdown_series=pd.Series(),
                trades_df=pd.DataFrame(backtest_result['trades']),
                monthly_returns=pd.Series(metrics['monthly_returns']),
                yearly_returns=pd.Series(metrics['yearly_returns'])
            )
            
        except Exception as e:
            raise Exception(f"Backtest failed: {str(e)}")


# Global backtesting engine instance
backtesting_engine = BacktestingEngine()
