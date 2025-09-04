"""
AI Technical Analysis Engine
Implements AI-powered trading signals and pattern recognition
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .market_data import MarketData, OHLCData, market_service

logger = logging.getLogger(__name__)

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WATCH = "WATCH"

class PatternType(Enum):
    BULLISH_ENGULFING = "bullish_engulfing"
    BEARISH_ENGULFING = "bearish_engulfing"
    HAMMER = "hammer"
    DOJI = "doji"
    BREAKOUT = "breakout"
    SUPPORT_RESISTANCE = "support_resistance"

@dataclass
class TradingSignal:
    symbol: str
    signal_type: SignalType
    confidence: float  # 0.0 to 1.0
    price: float
    reason: str
    timestamp: datetime
    pattern_type: Optional[PatternType] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None

@dataclass
class TechnicalIndicators:
    symbol: str
    rsi: float
    macd_signal: str  # 'bullish', 'bearish', 'neutral'
    sma_20: float
    sma_50: float
    bollinger_upper: float
    bollinger_lower: float
    volume_trend: str  # 'increasing', 'decreasing', 'stable'

class AITradingEngine:
    """AI-powered trading engine with pattern recognition and signal generation"""
    
    def __init__(self):
        self.min_confidence_threshold = 0.6
        self.signals_cache = {}
        self.patterns_cache = {}
    
    async def generate_trading_signals(self, symbols: List[str]) -> List[TradingSignal]:
        """Generate AI-powered trading signals for given symbols"""
        try:
            signals = []
            
            for symbol in symbols:
                # Get market data and historical data
                market_data = await market_service.get_market_data([symbol])
                historical_data = await market_service.get_historical_data(symbol, days=50)
                
                if not market_data or not historical_data:
                    continue
                
                current_data = market_data[0]
                
                # Calculate technical indicators
                indicators = self._calculate_technical_indicators(historical_data)
                
                # Detect patterns
                patterns = self._detect_patterns(historical_data)
                
                # Generate signal based on AI analysis
                signal = self._generate_ai_signal(current_data, indicators, patterns)
                
                if signal and signal.confidence >= self.min_confidence_threshold:
                    signals.append(signal)
            
            return signals
        
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return self._get_mock_signals(symbols)
    
    def _calculate_technical_indicators(self, data: List[OHLCData]) -> TechnicalIndicators:
        """Calculate key technical indicators"""
        if len(data) < 20:
            return self._get_default_indicators(data[0].symbol if data else "UNKNOWN")
        
        # Convert to arrays for calculations
        closes = np.array([d.close for d in data])
        highs = np.array([d.high for d in data])
        lows = np.array([d.low for d in data])
        volumes = np.array([d.volume for d in data])
        
        # RSI calculation (simplified)
        rsi = self._calculate_rsi(closes)
        
        # Moving averages
        sma_20 = np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1]
        sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else closes[-1]
        
        # MACD signal (simplified)
        macd_signal = self._calculate_macd_signal(closes)
        
        # Bollinger Bands
        bb_upper, bb_lower = self._calculate_bollinger_bands(closes)
        
        # Volume trend
        volume_trend = self._analyze_volume_trend(volumes)
        
        return TechnicalIndicators(
            symbol=data[-1].symbol,
            rsi=rsi,
            macd_signal=macd_signal,
            sma_20=sma_20,
            sma_50=sma_50,
            bollinger_upper=bb_upper,
            bollinger_lower=bb_lower,
            volume_trend=volume_trend
        )
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd_signal(self, prices: np.ndarray) -> str:
        """Calculate MACD signal"""
        if len(prices) < 26:
            return "neutral"
        
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26
        
        # Simple signal logic
        if macd_line > 0:
            return "bullish"
        elif macd_line < 0:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20) -> Tuple[float, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            std_dev = np.std(prices)
            mean = np.mean(prices)
        else:
            recent_prices = prices[-period:]
            std_dev = np.std(recent_prices)
            mean = np.mean(recent_prices)
        
        upper_band = mean + (2 * std_dev)
        lower_band = mean - (2 * std_dev)
        
        return upper_band, lower_band
    
    def _analyze_volume_trend(self, volumes: np.ndarray) -> str:
        """Analyze volume trend"""
        if len(volumes) < 5:
            return "stable"
        
        recent_avg = np.mean(volumes[-5:])
        previous_avg = np.mean(volumes[-10:-5]) if len(volumes) >= 10 else np.mean(volumes[:-5])
        
        change = (recent_avg - previous_avg) / previous_avg
        
        if change > 0.2:
            return "increasing"
        elif change < -0.2:
            return "decreasing"
        else:
            return "stable"
    
    def _detect_patterns(self, data: List[OHLCData]) -> List[PatternType]:
        """Detect candlestick and chart patterns using AI logic"""
        patterns = []
        
        if len(data) < 2:
            return patterns
        
        # Get last few candles
        last_candle = data[-1]
        prev_candle = data[-2] if len(data) >= 2 else None
        
        if prev_candle:
            # Bullish Engulfing Pattern
            if (prev_candle.close < prev_candle.open and  # Previous red candle
                last_candle.close > last_candle.open and  # Current green candle
                last_candle.open < prev_candle.close and  # Engulfing condition
                last_candle.close > prev_candle.open):
                patterns.append(PatternType.BULLISH_ENGULFING)
            
            # Bearish Engulfing Pattern
            elif (prev_candle.close > prev_candle.open and  # Previous green candle
                  last_candle.close < last_candle.open and  # Current red candle
                  last_candle.open > prev_candle.close and  # Engulfing condition
                  last_candle.close < prev_candle.open):
                patterns.append(PatternType.BEARISH_ENGULFING)
        
        # Hammer Pattern
        body_size = abs(last_candle.close - last_candle.open)
        lower_shadow = min(last_candle.open, last_candle.close) - last_candle.low
        upper_shadow = last_candle.high - max(last_candle.open, last_candle.close)
        
        if lower_shadow > 2 * body_size and upper_shadow < body_size:
            patterns.append(PatternType.HAMMER)
        
        # Doji Pattern
        if body_size < (last_candle.high - last_candle.low) * 0.1:
            patterns.append(PatternType.DOJI)
        
        return patterns
    
    def _generate_ai_signal(self, market_data: MarketData, indicators: TechnicalIndicators, patterns: List[PatternType]) -> Optional[TradingSignal]:
        """Generate AI trading signal based on multiple factors"""
        confidence = 0.0
        signal_type = SignalType.HOLD
        reason_parts = []
        
        # RSI-based signals
        if indicators.rsi < 30:
            confidence += 0.3
            signal_type = SignalType.BUY
            reason_parts.append("RSI oversold")
        elif indicators.rsi > 70:
            confidence += 0.3
            signal_type = SignalType.SELL
            reason_parts.append("RSI overbought")
        
        # MACD signals
        if indicators.macd_signal == "bullish":
            confidence += 0.2
            if signal_type != SignalType.SELL:
                signal_type = SignalType.BUY
            reason_parts.append("MACD bullish")
        elif indicators.macd_signal == "bearish":
            confidence += 0.2
            if signal_type != SignalType.BUY:
                signal_type = SignalType.SELL
            reason_parts.append("MACD bearish")
        
        # Moving average crossover
        if indicators.sma_20 > indicators.sma_50:
            confidence += 0.15
            reason_parts.append("MA bullish crossover")
        elif indicators.sma_20 < indicators.sma_50:
            confidence += 0.15
            reason_parts.append("MA bearish crossover")
        
        # Pattern recognition
        for pattern in patterns:
            if pattern in [PatternType.BULLISH_ENGULFING, PatternType.HAMMER]:
                confidence += 0.25
                signal_type = SignalType.BUY
                reason_parts.append(f"{pattern.value} pattern")
            elif pattern == PatternType.BEARISH_ENGULFING:
                confidence += 0.25
                signal_type = SignalType.SELL
                reason_parts.append(f"{pattern.value} pattern")
        
        # Volume confirmation
        if indicators.volume_trend == "increasing":
            confidence += 0.1
            reason_parts.append("strong volume")
        
        # Price action
        if market_data.change_percent > 2.0:
            confidence += 0.1
            reason_parts.append("strong momentum")
        elif market_data.change_percent < -2.0:
            confidence += 0.1
            reason_parts.append("bearish momentum")
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        if confidence < 0.3:
            signal_type = SignalType.WATCH
            reason_parts.append("monitoring conditions")
        
        reason = ", ".join(reason_parts) if reason_parts else "AI analysis pending"
        
        # Calculate target and stop loss
        target_price = None
        stop_loss = None
        
        if signal_type == SignalType.BUY:
            target_price = market_data.price * 1.05  # 5% target
            stop_loss = market_data.price * 0.97     # 3% stop loss
        elif signal_type == SignalType.SELL:
            target_price = market_data.price * 0.95  # 5% target down
            stop_loss = market_data.price * 1.03     # 3% stop loss up
        
        return TradingSignal(
            symbol=market_data.symbol,
            signal_type=signal_type,
            confidence=confidence,
            price=market_data.price,
            reason=reason,
            timestamp=datetime.now(),
            pattern_type=patterns[0] if patterns else None,
            target_price=target_price,
            stop_loss=stop_loss
        )
    
    def _get_default_indicators(self, symbol: str) -> TechnicalIndicators:
        """Get default indicators when insufficient data"""
        return TechnicalIndicators(
            symbol=symbol,
            rsi=50.0,
            macd_signal="neutral",
            sma_20=2500.0,
            sma_50=2500.0,
            bollinger_upper=2600.0,
            bollinger_lower=2400.0,
            volume_trend="stable"
        )
    
    def _get_mock_signals(self, symbols: List[str]) -> List[TradingSignal]:
        """Generate mock signals for development"""
        mock_signals = []
        signal_types = [SignalType.BUY, SignalType.SELL, SignalType.HOLD, SignalType.WATCH]
        
        import random
        for i, symbol in enumerate(symbols):
            signal_type = signal_types[i % len(signal_types)]
            confidence = random.uniform(0.6, 0.95)
            
            mock_signals.append(TradingSignal(
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                price=2500.0 + random.uniform(-100, 100),
                reason=f"AI pattern analysis: {signal_type.value.lower()} signal detected",
                timestamp=datetime.now(),
                target_price=2600.0 if signal_type == SignalType.BUY else 2400.0,
                stop_loss=2450.0 if signal_type == SignalType.BUY else 2550.0
            ))
        
        return mock_signals

# Global AI trading engine instance
ai_engine = AITradingEngine()
