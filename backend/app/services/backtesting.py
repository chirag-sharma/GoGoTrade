"""
Professional Backtesting Engine for GoGoTrade
Requires VectorBT and pandas-ta for professional backtesting and technical analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Required imports - raise proper errors if not available
try:
    import vectorbt as vbt
except ImportError as e:
    raise ImportError(
        "VectorBT is required for professional backtesting. "
        "Please install it with: pip install vectorbt"
    ) from e

# Technical analysis with modern libraries (No C dependencies!)
try:
    import pandas_ta as ta
except ImportError as e:
    raise ImportError(
        "pandas-ta is required for technical indicators. "
        "Please install it with: pip install pandas-ta"
    ) from e

from app.core.database import get_db_session
from app.models import OHLCVData, Instrument
from sqlalchemy import select, and_
import asyncio


class TechnicalIndicators:
    """Professional technical indicators using pandas-ta (no C dependencies!)"""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average using pandas-ta"""
        return ta.sma(data, length=period)
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average using pandas-ta"""
        return ta.ema(data, length=period)
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index using pandas-ta"""
        try:
            return ta.rsi(data, length=period)
        except Exception as e:
            raise RuntimeError(f"Failed to calculate RSI: {str(e)}") from e
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD indicator using pandas-ta"""
        try:
            macd_df = ta.macd(data, fast=fast, slow=slow, signal=signal)
            macd_line = macd_df[f'MACD_{fast}_{slow}_{signal}']
            macd_signal = macd_df[f'MACDs_{fast}_{slow}_{signal}']
            macd_hist = macd_df[f'MACDh_{fast}_{slow}_{signal}']
            return macd_line, macd_signal, macd_hist
        except Exception as e:
            raise RuntimeError(f"Failed to calculate MACD: {str(e)}") from e
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands using pandas-ta"""
        try:
            bbands_df = ta.bbands(data, length=period, std=std_dev)
            upper = bbands_df[f'BBU_{period}_{std_dev}']
            middle = bbands_df[f'BBM_{period}_{std_dev}']
            lower = bbands_df[f'BBL_{period}_{std_dev}']
            return upper, middle, lower
        except Exception as e:
            raise RuntimeError(f"Failed to calculate Bollinger Bands: {str(e)}") from e


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
    
    def run_vectorbt_backtest(self, data: pd.DataFrame, signals: pd.Series, initial_capital: float) -> Dict:
        """Professional backtest using VectorBT"""
        try:
            # Convert signals to VectorBT format
            entries = signals == 1
            exits = signals == -1
            
            # Create portfolio using VectorBT
            portfolio = vbt.Portfolio.from_signals(
                data['close'],
                entries=entries,
                exits=exits,
                init_cash=initial_capital,
                freq='1D'
            )
            
            # Extract comprehensive statistics
            stats = portfolio.stats()
            
            return {
                'portfolio': portfolio,
                'stats': stats,
                'final_value': portfolio.value().iloc[-1],
                'trades': portfolio.trades.records_arr,
                'equity_curve': portfolio.value().values
            }
            
        except Exception as e:
            raise RuntimeError(f"VectorBT backtest failed: {str(e)}") from e
    
    def calculate_vectorbt_metrics(self, result: Dict, initial_capital: float) -> Dict:
        """Calculate comprehensive metrics using VectorBT results"""
        try:
            portfolio = result['portfolio']
            stats = result['stats']
            
            # Get portfolio statistics
            total_return = stats['Total Return [%]'] / 100 if 'Total Return [%]' in stats else 0
            sharpe_ratio = stats['Sharpe Ratio'] if 'Sharpe Ratio' in stats else 0
            max_drawdown = stats['Max Drawdown [%]'] / 100 if 'Max Drawdown [%]' in stats else 0
            
            # Trading statistics
            trades_stats = portfolio.trades.stats()
            total_trades = trades_stats['Total Trades'] if 'Total Trades' in trades_stats else 0
            win_rate = trades_stats['Win Rate [%]'] / 100 if 'Win Rate [%]' in trades_stats else 0
            
            # Returns and volatility
            returns = portfolio.returns()
            volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
            annualized_return = (1 + total_return) ** (252 / len(portfolio.value())) - 1 if len(portfolio.value()) > 0 else 0
            
            # Calculate additional metrics
            winning_trades = int(total_trades * win_rate) if total_trades > 0 else 0
            losing_trades = total_trades - winning_trades
            
            # Value at Risk (95%)
            var_95 = returns.quantile(0.05) if len(returns) > 0 else 0
            cvar_95 = returns[returns <= var_95].mean() if len(returns) > 0 and var_95 < 0 else 0
            
            return {
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': stats.get('Sortino Ratio', sharpe_ratio),
                'max_drawdown': max_drawdown,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'profit_factor': trades_stats.get('Profit Factor', 1.0),
                'avg_win': trades_stats.get('Avg Win [%]', 0) / 100,
                'avg_loss': trades_stats.get('Avg Loss [%]', 0) / 100,
                'var_95': var_95,
                'cvar_95': cvar_95,
                'beta': 0.0,  # Would need benchmark for calculation
                'alpha': 0.0,  # Would need benchmark for calculation
                'equity_curve': {str(i): v for i, v in enumerate(result['equity_curve'])},
                'monthly_returns': {},  # Simplified for now
                'yearly_returns': {}    # Simplified for now
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to calculate VectorBT metrics: {str(e)}") from e
    
    async def run_backtest(self, params: BacktestParams) -> BacktestResults:
        """
        Run comprehensive backtest using VectorBT
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
            
            # Run VectorBT backtest
            backtest_result = self.run_vectorbt_backtest(data, signals, params.initial_capital)
            
            # Calculate comprehensive metrics
            metrics = self.calculate_vectorbt_metrics(backtest_result, params.initial_capital)
            
            # Extract portfolio for additional data
            portfolio = backtest_result['portfolio']
            
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
                equity_curve=portfolio.value(),
                drawdown_series=portfolio.drawdown(),
                trades_df=portfolio.trades.records_readable,
                monthly_returns=pd.Series(metrics['monthly_returns']),
                yearly_returns=pd.Series(metrics['yearly_returns'])
            )
            
        except ImportError as e:
            raise RuntimeError(
                "Required libraries (VectorBT, pandas-ta) are not installed. "
                "Please install them with: pip install vectorbt pandas-ta"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Backtest failed: {str(e)}") from e


# Global backtesting engine instance
backtesting_engine = BacktestingEngine()
