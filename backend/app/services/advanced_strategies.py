"""
Advanced Trading Strategies Implementation
Based on strategy documents: clStrategy.txt, gptStrategy.txt, gptStrategy2.txt

Implements:
1. Trend-following strategies (EMA crossover + RSI filter)
2. Breakout strategies (Donchian/HH-HL break)
3. Mean-reversion strategies (RSI bands + VWAP)
4. AI-assisted pattern recognition
5. Risk management with ATR-based position sizing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio

from app.services.market_data import MarketDataService
from app.services.ai_trade_prediction import ai_trade_prediction_service
from app.ai_prompts.prompt_manager import AIPromptManager

# Import TA-Lib for technical indicators (as recommended in strategies)
try:
    import talib as ta
except ImportError:
    print("TA-Lib not available, using pandas-ta fallback")
    import pandas_ta as ta


class StrategyType(Enum):
    """Strategy types based on strategy documents"""
    TREND_FOLLOWING = "trend_following"
    BREAKOUT = "breakout" 
    MEAN_REVERSION = "mean_reversion"
    AI_PATTERN_RECOGNITION = "ai_pattern"
    ENSEMBLE = "ensemble"


class SignalType(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    EXIT = "EXIT"


@dataclass
class TradingSignal:
    """Enhanced trading signal with all strategy components"""
    symbol: str
    strategy: StrategyType
    signal: SignalType
    confidence: float  # 0.0 to 1.0
    
    # Price levels
    entry_price: float
    target_price: float
    stop_loss: float
    
    # Risk management
    position_size_percent: float
    risk_reward_ratio: float
    atr_multiple: float
    
    # Technical analysis
    technical_reasons: List[str]
    indicators: Dict[str, float]
    
    # AI analysis
    ai_pattern: Optional[str]
    ai_confidence: Optional[float]
    
    # Execution details
    timeframe: str
    session_timing: str
    
    timestamp: datetime


@dataclass 
class StrategyParameters:
    """Strategy parameters from strategy documents"""
    # Trend Following Parameters
    fast_ema: int = 20
    slow_ema: int = 50
    rsi_period: int = 14
    rsi_oversold: int = 30
    rsi_overbought: int = 70
    adx_period: int = 14
    adx_threshold: int = 20
    
    # Breakout Parameters
    donchian_period: int = 20
    volume_threshold: float = 1.5  # 1.5x average volume
    atr_period: int = 14
    atr_stop_multiplier: float = 2.0
    
    # Mean Reversion Parameters
    rsi_band_lower: int = 25
    rsi_band_upper: int = 75
    vwap_deviation: float = 0.5  # 0.5% from VWAP
    
    # Risk Management
    max_position_size: float = 5.0  # Max 5% per position
    daily_loss_limit: float = 2.0   # Max 2% daily loss
    risk_per_trade: float = 1.0     # 1% risk per trade
    
    # Session Timing (Indian Market)
    session_start: str = "09:15"
    session_end: str = "15:30"
    no_trades_after: str = "15:00"  # No new trades in last 30 mins


class AdvancedTradingStrategies:
    """
    Advanced trading strategies implementation based on strategy documents
    Combines traditional technical analysis with AI-powered insights
    """
    
    def __init__(self):
        self.market_data_service = MarketDataService()
        self.ai_service = ai_trade_prediction_service
        self.prompt_manager = AIPromptManager()
        self.params = StrategyParameters()
        
        # Strategy state management
        self.active_positions = {}
        self.daily_pnl = 0.0
        self.trade_count = 0
        
    async def analyze_trend_following_strategy(
        self, 
        symbol: str, 
        timeframe: str = "5m"
    ) -> Optional[TradingSignal]:
        """
        Trend-following strategy: 20/50 EMA cross + RSI pullback filter + ADX strength gate
        As recommended in gptStrategy2.txt
        """
        try:
            # Get market data
            data = await self.market_data_service.get_historical_data(symbol, timeframe, days=50)
            if data.empty:
                return None
            
            # Calculate indicators
            close_prices = data['close'].values
            
            # EMA crossover
            ema_20 = self._calculate_ema(close_prices, self.params.fast_ema)
            ema_50 = self._calculate_ema(close_prices, self.params.slow_ema)
            
            # RSI for pullback confirmation
            rsi = self._calculate_rsi(close_prices, self.params.rsi_period)
            
            # ADX for trend strength
            adx = self._calculate_adx(data)
            
            current_price = close_prices[-1]
            current_ema_20 = ema_20[-1]
            current_ema_50 = ema_50[-1]
            current_rsi = rsi[-1]
            current_adx = adx[-1]
            
            # Check session timing
            if not self._is_trading_session():
                return None
            
            # Signal logic
            signal = SignalType.HOLD
            confidence = 0.0
            technical_reasons = []
            
            # Bullish signal: EMA 20 > EMA 50, RSI pullback, strong ADX
            if (current_ema_20 > current_ema_50 and 
                current_rsi > self.params.rsi_oversold and 
                current_rsi < 60 and  # Not overbought
                current_adx > self.params.adx_threshold):
                
                signal = SignalType.BUY
                confidence = 0.7 + (current_adx - self.params.adx_threshold) / 100
                technical_reasons = [
                    f"Bullish EMA crossover (20: {current_ema_20:.2f}, 50: {current_ema_50:.2f})",
                    f"RSI pullback level at {current_rsi:.1f}",
                    f"Strong trend strength ADX: {current_adx:.1f}"
                ]
            
            # Bearish signal: EMA 20 < EMA 50, RSI oversold relief, strong ADX
            elif (current_ema_20 < current_ema_50 and 
                  current_rsi < self.params.rsi_overbought and 
                  current_rsi > 40 and  # Not oversold
                  current_adx > self.params.adx_threshold):
                
                signal = SignalType.SELL
                confidence = 0.7 + (current_adx - self.params.adx_threshold) / 100
                technical_reasons = [
                    f"Bearish EMA crossover (20: {current_ema_20:.2f}, 50: {current_ema_50:.2f})",
                    f"RSI resistance level at {current_rsi:.1f}",
                    f"Strong trend strength ADX: {current_adx:.1f}"
                ]
            
            if signal == SignalType.HOLD:
                return None
            
            # Calculate position sizing and risk levels
            atr = self._calculate_atr(data)
            entry_price = current_price
            
            if signal == SignalType.BUY:
                stop_loss = entry_price - (atr * self.params.atr_stop_multiplier)
                target_price = entry_price + (atr * 3.0)  # 3:1 R:R
            else:  # SELL
                stop_loss = entry_price + (atr * self.params.atr_stop_multiplier)
                target_price = entry_price - (atr * 3.0)
            
            # Position sizing based on ATR
            risk_amount = abs(entry_price - stop_loss)
            position_size = min(
                self.params.risk_per_trade / (risk_amount / entry_price) * 100,
                self.params.max_position_size
            )
            
            # Get AI confirmation
            ai_analysis = await self._get_ai_confirmation(symbol, signal, current_price)
            
            return TradingSignal(
                symbol=symbol,
                strategy=StrategyType.TREND_FOLLOWING,
                signal=signal,
                confidence=min(confidence * ai_analysis.get("confidence", 1.0), 1.0),
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                position_size_percent=position_size,
                risk_reward_ratio=abs(target_price - entry_price) / abs(entry_price - stop_loss),
                atr_multiple=self.params.atr_stop_multiplier,
                technical_reasons=technical_reasons,
                indicators={
                    "ema_20": current_ema_20,
                    "ema_50": current_ema_50,
                    "rsi": current_rsi,
                    "adx": current_adx,
                    "atr": atr
                },
                ai_pattern=ai_analysis.get("pattern"),
                ai_confidence=ai_analysis.get("ai_confidence"),
                timeframe=timeframe,
                session_timing="First 5 hours of session",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Trend following analysis failed: {e}")
            return None
    
    async def analyze_breakout_strategy(
        self, 
        symbol: str, 
        timeframe: str = "15m"
    ) -> Optional[TradingSignal]:
        """
        Breakout strategy: Donchian/HH-HL break with ATR-based stops + volume confirmation
        As recommended in gptStrategy2.txt
        """
        try:
            # Get market data
            data = await self.market_data_service.get_historical_data(symbol, timeframe, days=30)
            if data.empty:
                return None
            
            # Calculate Donchian channels
            high_prices = data['high'].values
            low_prices = data['low'].values
            close_prices = data['close'].values
            volume = data['volume'].values
            
            donchian_high = pd.Series(high_prices).rolling(self.params.donchian_period).max().values
            donchian_low = pd.Series(low_prices).rolling(self.params.donchian_period).min().values
            
            current_price = close_prices[-1]
            current_high = high_prices[-1]
            current_low = low_prices[-1]
            current_volume = volume[-1]
            avg_volume = np.mean(volume[-20:])  # 20-period average
            
            # Volume confirmation
            volume_confirmed = current_volume > (avg_volume * self.params.volume_threshold)
            
            if not volume_confirmed:
                return None
            
            signal = SignalType.HOLD
            confidence = 0.0
            technical_reasons = []
            
            # Bullish breakout: price breaks above Donchian high
            if current_high > donchian_high[-2]:  # Previous period high
                signal = SignalType.BUY
                confidence = 0.75
                technical_reasons = [
                    f"Breakout above {self.params.donchian_period}-period high",
                    f"Volume confirmation: {current_volume/avg_volume:.1f}x average",
                    "Fresh momentum detected"
                ]
            
            # Bearish breakdown: price breaks below Donchian low
            elif current_low < donchian_low[-2]:  # Previous period low
                signal = SignalType.SELL
                confidence = 0.75
                technical_reasons = [
                    f"Breakdown below {self.params.donchian_period}-period low",
                    f"Volume confirmation: {current_volume/avg_volume:.1f}x average",
                    "Weakness momentum detected"
                ]
            
            if signal == SignalType.HOLD:
                return None
            
            # Calculate risk levels
            atr = self._calculate_atr(data)
            entry_price = current_price
            
            if signal == SignalType.BUY:
                stop_loss = donchian_low[-1]  # Use Donchian low as stop
                target_price = entry_price + (atr * 4.0)  # Extended target for breakouts
            else:  # SELL
                stop_loss = donchian_high[-1]  # Use Donchian high as stop
                target_price = entry_price - (atr * 4.0)
            
            # Position sizing
            risk_amount = abs(entry_price - stop_loss)
            position_size = min(
                self.params.risk_per_trade / (risk_amount / entry_price) * 100,
                self.params.max_position_size
            )
            
            # Get AI confirmation
            ai_analysis = await self._get_ai_confirmation(symbol, signal, current_price)
            
            return TradingSignal(
                symbol=symbol,
                strategy=StrategyType.BREAKOUT,
                signal=signal,
                confidence=min(confidence * ai_analysis.get("confidence", 1.0), 1.0),
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                position_size_percent=position_size,
                risk_reward_ratio=abs(target_price - entry_price) / abs(entry_price - stop_loss),
                atr_multiple=atr,
                technical_reasons=technical_reasons,
                indicators={
                    "donchian_high": donchian_high[-1],
                    "donchian_low": donchian_low[-1],
                    "volume_ratio": current_volume / avg_volume,
                    "atr": atr
                },
                ai_pattern=ai_analysis.get("pattern"),
                ai_confidence=ai_analysis.get("ai_confidence"),
                timeframe=timeframe,
                session_timing="Avoid last 30 minutes",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Breakout analysis failed: {e}")
            return None
    
    async def analyze_mean_reversion_strategy(
        self, 
        symbol: str, 
        timeframe: str = "5m"
    ) -> Optional[TradingSignal]:
        """
        Mean-reversion intraday: RSI bands + VWAP anchor
        As recommended in gptStrategy2.txt - use cautiously due to costs
        """
        try:
            # Get intraday data
            data = await self.market_data_service.get_historical_data(symbol, timeframe, days=2)
            if data.empty:
                return None
            
            close_prices = data['close'].values
            volume = data['volume'].values
            
            # Calculate indicators
            rsi = self._calculate_rsi(close_prices, self.params.rsi_period)
            vwap = self._calculate_vwap(data)
            
            current_price = close_prices[-1]
            current_rsi = rsi[-1]
            current_vwap = vwap[-1]
            
            # Check if it's late in session (avoid mean reversion near close)
            current_time = datetime.now().time()
            no_trades_time = datetime.strptime(self.params.no_trades_after, "%H:%M").time()
            
            if current_time > no_trades_time:
                return None
            
            signal = SignalType.HOLD
            confidence = 0.0
            technical_reasons = []
            
            # Bullish mean reversion: RSI oversold + near VWAP
            vwap_deviation = abs(current_price - current_vwap) / current_vwap * 100
            
            if (current_rsi < self.params.rsi_band_lower and 
                vwap_deviation < self.params.vwap_deviation):
                
                signal = SignalType.BUY
                confidence = 0.6  # Lower confidence for mean reversion
                technical_reasons = [
                    f"RSI oversold at {current_rsi:.1f}",
                    f"Price near VWAP (deviation: {vwap_deviation:.2f}%)",
                    "Mean reversion opportunity"
                ]
            
            # Bearish mean reversion: RSI overbought + near VWAP
            elif (current_rsi > self.params.rsi_band_upper and 
                  vwap_deviation < self.params.vwap_deviation):
                
                signal = SignalType.SELL
                confidence = 0.6
                technical_reasons = [
                    f"RSI overbought at {current_rsi:.1f}",
                    f"Price near VWAP (deviation: {vwap_deviation:.2f}%)",
                    "Mean reversion opportunity"
                ]
            
            if signal == SignalType.HOLD:
                return None
            
            # Tight risk management for mean reversion
            atr = self._calculate_atr(data)
            entry_price = current_price
            
            if signal == SignalType.BUY:
                stop_loss = entry_price - (atr * 1.0)  # Tight stop
                target_price = current_vwap  # Target back to VWAP
            else:  # SELL
                stop_loss = entry_price + (atr * 1.0)
                target_price = current_vwap
            
            # Smaller position size for mean reversion
            risk_amount = abs(entry_price - stop_loss)
            position_size = min(
                (self.params.risk_per_trade * 0.5) / (risk_amount / entry_price) * 100,  # Half normal risk
                self.params.max_position_size * 0.6  # Smaller max size
            )
            
            # Get AI confirmation
            ai_analysis = await self._get_ai_confirmation(symbol, signal, current_price)
            
            return TradingSignal(
                symbol=symbol,
                strategy=StrategyType.MEAN_REVERSION,
                signal=signal,
                confidence=min(confidence * ai_analysis.get("confidence", 1.0), 1.0),
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                position_size_percent=position_size,
                risk_reward_ratio=abs(target_price - entry_price) / abs(entry_price - stop_loss),
                atr_multiple=1.0,
                technical_reasons=technical_reasons,
                indicators={
                    "rsi": current_rsi,
                    "vwap": current_vwap,
                    "vwap_deviation": vwap_deviation,
                    "atr": atr
                },
                ai_pattern=ai_analysis.get("pattern"),
                ai_confidence=ai_analysis.get("ai_confidence"),
                timeframe=timeframe,
                session_timing="Avoid last 30 minutes",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Mean reversion analysis failed: {e}")
            return None
    
    async def get_ensemble_signal(
        self, 
        symbol: str, 
        timeframes: List[str] = ["5m", "15m", "1h"]
    ) -> Optional[TradingSignal]:
        """
        Ensemble strategy: Combine multiple strategy signals
        As recommended in gptStrategy2.txt - route capital by regime
        """
        try:
            signals = []
            
            # Get signals from all strategies
            trend_signal = await self.analyze_trend_following_strategy(symbol, timeframes[0])
            breakout_signal = await self.analyze_breakout_strategy(symbol, timeframes[1])
            mean_rev_signal = await self.analyze_mean_reversion_strategy(symbol, timeframes[0])
            
            # Filter valid signals
            if trend_signal:
                signals.append(trend_signal)
            if breakout_signal:
                signals.append(breakout_signal)
            if mean_rev_signal:
                signals.append(mean_rev_signal)
            
            if not signals:
                return None
            
            # Ensemble logic: Agreement and confidence weighting
            buy_signals = [s for s in signals if s.signal == SignalType.BUY]
            sell_signals = [s for s in signals if s.signal == SignalType.SELL]
            
            if len(buy_signals) > len(sell_signals) and buy_signals:
                # Take the highest confidence buy signal
                best_signal = max(buy_signals, key=lambda x: x.confidence)
                best_signal.strategy = StrategyType.ENSEMBLE
                best_signal.technical_reasons.append("Ensemble agreement: Multiple bullish signals")
                return best_signal
            
            elif len(sell_signals) > len(buy_signals) and sell_signals:
                # Take the highest confidence sell signal
                best_signal = max(sell_signals, key=lambda x: x.confidence)
                best_signal.strategy = StrategyType.ENSEMBLE
                best_signal.technical_reasons.append("Ensemble agreement: Multiple bearish signals")
                return best_signal
            
            return None
            
        except Exception as e:
            print(f"Ensemble analysis failed: {e}")
            return None
    
    # Technical Indicator Helper Methods
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        try:
            # Try TA-Lib first
            return ta.EMA(prices, timeperiod=period)
        except:
            # Fallback to pandas calculation
            return pd.Series(prices).ewm(span=period).mean().values
    
    def _calculate_rsi(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Relative Strength Index"""
        try:
            return ta.RSI(prices, timeperiod=period)
        except:
            # Fallback calculation
            delta = np.diff(prices)
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)
            
            avg_gain = pd.Series(gain).rolling(period).mean()
            avg_loss = pd.Series(loss).rolling(period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return np.concatenate([[np.nan], rsi.values])
    
    def _calculate_adx(self, data: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Calculate Average Directional Index"""
        try:
            return ta.ADX(data['high'].values, data['low'].values, data['close'].values, timeperiod=period)
        except:
            # Simplified ADX calculation
            return np.full(len(data), 25.0)  # Default moderate strength
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            atr_values = ta.ATR(data['high'].values, data['low'].values, data['close'].values, timeperiod=period)
            return atr_values[-1] if not np.isnan(atr_values[-1]) else 0.0
        except:
            # Fallback: simple range calculation
            high_low = data['high'] - data['low']
            return high_low.tail(period).mean()
    
    def _calculate_vwap(self, data: pd.DataFrame) -> np.ndarray:
        """Calculate Volume Weighted Average Price"""
        try:
            typical_price = (data['high'] + data['low'] + data['close']) / 3
            cumulative_volume = data['volume'].cumsum()
            cumulative_typical_price_volume = (typical_price * data['volume']).cumsum()
            return (cumulative_typical_price_volume / cumulative_volume).values
        except:
            return data['close'].values
    
    def _is_trading_session(self) -> bool:
        """Check if current time is within trading session"""
        current_time = datetime.now().time()
        session_start = datetime.strptime(self.params.session_start, "%H:%M").time()
        session_end = datetime.strptime(self.params.session_end, "%H:%M").time()
        
        return session_start <= current_time <= session_end
    
    async def _get_ai_confirmation(self, symbol: str, signal: SignalType, price: float) -> Dict:
        """Get AI confirmation for the trading signal"""
        try:
            # Use the AI trade prediction service for confirmation
            ai_signal = await self.ai_service.predict_trade_direction(
                symbol=symbol,
                custom_inputs={
                    "confirmation_mode": True,
                    "expected_signal": signal.value,
                    "current_price": price
                }
            )
            
            return {
                "confidence": ai_signal.confidence if ai_signal else 0.5,
                "pattern": ai_signal.primary_pattern.value if ai_signal and ai_signal.primary_pattern else None,
                "ai_confidence": ai_signal.confidence if ai_signal else 0.0
            }
        except:
            return {"confidence": 0.7, "pattern": None, "ai_confidence": 0.0}


# Global strategy engine instance
advanced_strategy_engine = AdvancedTradingStrategies()
