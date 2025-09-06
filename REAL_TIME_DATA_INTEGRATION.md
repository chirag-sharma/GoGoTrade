# Real-Time Data Integration Documentation

## Overview

The GoGoTrade platform now includes a comprehensive real-time data integration system that provides:

- **Live Market Data Feeds**: Real-time price updates from multiple sources
- **WebSocket Streaming**: Real-time price and signal streaming to clients
- **Automated Signal Generation**: AI-powered trading signals based on live data
- **Technical Analysis**: Real-time calculation of technical indicators
- **Database Integration**: Efficient storage using TimescaleDB hypertables

## Architecture

### Components

1. **RealTimeDataIntegration** (`real_time_data.py`)
   - Core service managing data feeds and subscriptions
   - Handles multiple data sources (Zerodha, Alpha Vantage, etc.)
   - Manages WebSocket connections and price updates

2. **MarketDataProcessor** (`market_data_processor.py`)
   - Processes live market data and calculates technical indicators
   - Generates trading signals based on real-time analysis
   - Stores signals in TimescaleDB for historical tracking

3. **Real-Time API** (`real_time_data.py` API)
   - REST endpoints for subscription management
   - WebSocket endpoint for live streaming
   - Signal and price retrieval endpoints

### Data Flow

```
Market Data Sources → RealTimeDataIntegration → MarketDataProcessor → Database
                                    ↓
                              WebSocket Clients ← API Endpoints
```

## API Endpoints

### REST Endpoints

#### Subscription Management
- `POST /api/v1/real-time/subscribe` - Subscribe to live data for symbols
- `POST /api/v1/real-time/unsubscribe` - Unsubscribe from symbols

#### Live Data Retrieval
- `GET /api/v1/real-time/price/{symbol}` - Get current price for symbol
- `GET /api/v1/real-time/prices` - Get all live prices
- `GET /api/v1/real-time/signals` - Get active trading signals
- `GET /api/v1/real-time/signals/{symbol}` - Get signals for specific symbol
- `GET /api/v1/real-time/status` - Get system status

#### Testing
- `POST /api/v1/real-time/test/generate-sample-data` - Generate test data

### WebSocket Endpoint

- `WS /api/v1/real-time/ws` - Real-time data streaming

#### WebSocket Commands

```json
// Subscribe to a symbol
{
  "action": "subscribe",
  "symbol": "AAPL"
}

// Unsubscribe from a symbol
{
  "action": "unsubscribe", 
  "symbol": "AAPL"
}

// Get current price
{
  "action": "get_price",
  "symbol": "AAPL"
}

// Ping for connection health
{
  "action": "ping"
}
```

#### WebSocket Responses

```json
// Price update
{
  "type": "price_update",
  "symbol": "AAPL",
  "data": {
    "ltp": 150.25,
    "change": 2.15,
    "change_percent": 1.45,
    "volume": 1234567,
    "timestamp": "2025-09-06T10:30:00Z",
    "source": "zerodha_mock"
  }
}

// Trading signal
{
  "type": "trading_signal", 
  "data": {
    "symbol": "AAPL",
    "signal_type": "BUY",
    "confidence": 0.85,
    "target_price": 155.00,
    "stop_loss": 145.00,
    "reasoning": "RSI oversold; MACD bullish crossover",
    "generated_at": "2025-09-06T10:30:00Z"
  }
}

// Subscription confirmation
{
  "type": "subscription_confirmed",
  "symbol": "AAPL",
  "status": "subscribed"
}
```

## Database Schema

### Live Price Storage (Redis)

```
Key: live_prices
Hash Fields:
  - AAPL: {"ltp": 150.25, "change": 2.15, ...}
  - GOOGL: {"ltp": 2750.50, "change": -5.25, ...}
```

### OHLCV Data (TimescaleDB)

Table: `ohlcv_data` (Hypertable)
- Real-time 1-minute candles
- Automatic compression after 30 days
- Continuous aggregates for 5m, 15m, 1h timeframes

### Trading Signals (TimescaleDB)

Table: `trading_signals` (Hypertable)
- AI-generated signals with confidence scores
- Automatic expiry and archival
- Links to instruments and strategies

## Technical Indicators

The system calculates the following indicators in real-time:

### Trend Indicators
- **Simple Moving Averages**: SMA 10, 20, 50
- **Exponential Moving Averages**: EMA 12, 26
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Upper, Middle, Lower bands

### Momentum Indicators
- **RSI**: Relative Strength Index (14-period)
- **MACD Histogram**: MACD signal line divergence

### Volume Indicators
- **Volume SMA**: 10-period volume average
- **Volume Comparison**: Current vs average volume

### Volatility Indicators
- **ATR**: Average True Range (14-period)
- **Bollinger Band Width**: Band expansion/contraction

### Support/Resistance
- **Dynamic Levels**: 20-period high/low levels
- **Price Action**: Current price relative to key levels

## Signal Generation Logic

### Signal Strength Calculation

```python
signal_strength = 0

# RSI Analysis
if rsi < 30: signal_strength += 2  # Oversold
if rsi > 70: signal_strength -= 2  # Overbought

# Moving Average Analysis  
if price > sma_10 > sma_20: signal_strength += 1  # Uptrend
if price < sma_10 < sma_20: signal_strength -= 1  # Downtrend

# MACD Analysis
if macd > macd_signal: signal_strength += 1  # Bullish
else: signal_strength -= 1  # Bearish

# Volume Confirmation
if volume > avg_volume * 1.5:
    signal_strength += 1 if signal_strength > 0 else -1
```

### Signal Types

- **BUY**: `signal_strength >= 3`, confidence 0.9
- **SELL**: `signal_strength <= -3`, confidence 0.9
- **HOLD**: `abs(signal_strength) < 2`, no signal generated

### Target and Stop Loss Calculation

```python
if signal_type == "BUY":
    target_price = current_price + (atr * 2.0)
    stop_loss = current_price - (atr * 1.5)
    
elif signal_type == "SELL":
    target_price = current_price - (atr * 2.0) 
    stop_loss = current_price + (atr * 1.5)
```

## Data Sources

### Primary Source: Yahoo Finance (yfinance)

1. **Live Price Data**
   - Real-time stock prices for US and Indian markets
   - 30-second update frequency (respecting rate limits)
   - Batch processing for multiple symbols
   - Automatic retry on failures

2. **Historical OHLCV Data**
   - Intraday data with multiple timeframes (1m, 5m, 15m, 1h, 1d)
   - Historical periods up to 2 years
   - Automatic data validation and cleaning

3. **Market Information**
   - Market status and trading hours
   - Volume and market cap data
   - Currency and exchange information

### Supported Symbols

**US Stocks:**
- AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA, NFLX, AMD, INTC

**Indian Stocks (NSE):**
- RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS
- HINDUNILVR.NS, ITC.NS, SBIN.NS, BHARTIARTL.NS, KOTAKBANK.NS

### Rate Limiting and Optimization

- **Batch Requests**: Up to 10 symbols per request
- **Update Frequency**: 30 seconds for live prices, 5 minutes for historical data
- **Connection Pooling**: Thread executor for async operations
- **Caching**: Symbol mapping and ticker object caching
- **Error Handling**: Automatic retry with exponential backoff

## Performance Considerations

### Optimization Features

1. **Connection Pooling**
   - PostgreSQL: 5-connection pool with overflow
   - Redis: 20-connection pool
   - WebSocket: Efficient connection management

2. **Data Buffering**
   - Price updates batched for database writes
   - Real-time updates prioritized for WebSocket clients
   - Background workers for heavy processing

3. **TimescaleDB Optimizations**
   - 7-day chunk intervals for OHLCV data
   - Automatic compression after 30 days
   - Continuous aggregates for common queries

4. **Caching Strategy**
   - Live prices: 1-second TTL in Redis
   - Trading signals: 5-minute TTL
   - Market status: Session-based caching

### Scalability

- **Horizontal Scaling**: Multiple worker processes
- **Load Balancing**: WebSocket connection distribution
- **Data Partitioning**: Time-based data sharding
- **Async Processing**: Non-blocking I/O throughout

## Testing

### Test Script

Run the comprehensive test script:

```bash
cd backend
python test_real_time_integration.py
```

### Test Coverage

1. **API Status**: Endpoint health checks
2. **Subscription Management**: Subscribe/unsubscribe functionality
3. **Live Prices**: Price retrieval and updates
4. **Trading Signals**: Signal generation and retrieval
5. **WebSocket Streaming**: Real-time data flow
6. **Sample Data**: Test data generation

### Test Results Example

```
🚀 Starting comprehensive real-time data integration test...

🔍 Test 1: API Status
✅ API Status: {'is_market_open': True, 'market_session': 'Regular', ...}

🔍 Test 2: Sample Data Generation  
✅ Sample data generation: Sample data generation started

🔍 Test 3: Data Subscription
✅ Subscription successful: {'status': 'success', 'symbols': ['AAPL', 'GOOGL', 'MSFT', 'TSLA']}

🔍 Test 4: Live Prices
✅ Live price for AAPL: $1,023.45 (+1.25%)
✅ Live price for GOOGL: $2,756.78 (-0.85%)

🔍 Test 5: Trading Signals
✅ Active signals: 3
   📈 AAPL: BUY (confidence: 85.0%)
   📈 MSFT: SELL (confidence: 72.0%)

🔍 Test 6: WebSocket Real-Time Updates
🔌 Connecting to WebSocket: ws://localhost:8000/api/v1/real-time/ws
✅ WebSocket connected
📡 Subscribed to AAPL
📊 AAPL: $1,025.67 (+1.47%)
📊 AAPL: $1,024.89 (+1.39%)
🚨 Signal: AAPL BUY (85.0%)

🎉 Comprehensive test completed successfully!
```

## Monitoring and Alerts

### Health Checks

- **Database Connectivity**: PostgreSQL and Redis health
- **Data Feed Status**: Source connection monitoring  
- **WebSocket Connections**: Active client tracking
- **Signal Generation**: Processing performance metrics

### Alert Conditions

- **Data Lag**: Updates delayed > 10 seconds
- **Connection Loss**: Data source disconnection
- **High Error Rate**: > 5% failed operations
- **Memory Usage**: > 80% system memory

## Security Considerations

### Data Protection

- **API Rate Limiting**: Prevent abuse of endpoints
- **WebSocket Authentication**: Secure connection establishment
- **Data Encryption**: TLS for all data transmission
- **Access Control**: Role-based API access

### Compliance

- **Audit Logging**: All trading signal generation logged
- **Data Retention**: Regulatory compliance for trade data
- **Algorithm Tracking**: SEBI compliance for algo trading
- **Risk Controls**: Position limits and circuit breakers

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Replace rule-based signals with ML models
   - Real-time feature engineering
   - Model training on live data

2. **Advanced Analytics**
   - Market microstructure analysis
   - Order book dynamics
   - Cross-asset correlations

3. **Enhanced Data Sources**
   - News sentiment integration
   - Social media sentiment analysis
   - Economic calendar integration

4. **Performance Optimization**
   - GPU acceleration for calculations
   - Stream processing with Apache Kafka
   - Edge computing for latency reduction

### Roadmap

- **Q1 2025**: ML model integration
- **Q2 2025**: Advanced order types
- **Q3 2025**: Multi-exchange support
- **Q4 2025**: Institutional features

---

## Getting Started

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Test Yahoo Finance Service**:
   ```bash
   python test_yahoo_finance.py
   ```

3. **Start the Backend**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Subscribe to Live Data**:
   ```bash
   # US Stocks
   curl -X POST http://localhost:8000/api/v1/real-time/subscribe \
        -H "Content-Type: application/json" \
        -d '{"symbols": ["AAPL", "GOOGL", "MSFT"]}'
   
   # Indian Stocks
   curl -X POST http://localhost:8000/api/v1/real-time/subscribe \
        -H "Content-Type: application/json" \
        -d '{"symbols": ["RELIANCE", "TCS", "INFY"]}'
   ```

5. **Get Live Prices**:
   ```bash
   # After waiting 60 seconds for data to be fetched
   curl http://localhost:8000/api/v1/real-time/price/AAPL
   curl http://localhost:8000/api/v1/real-time/price/RELIANCE
   ```

6. **Run Comprehensive Test**:
   ```bash
   python test_real_time_integration.py
   ```

7. **Connect WebSocket Client**:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/api/v1/real-time/ws');
   
   // Subscribe to Apple stock
   ws.send(JSON.stringify({"action": "subscribe", "symbol": "AAPL"}));
   
   // Subscribe to Reliance (Indian stock)
   ws.send(JSON.stringify({"action": "subscribe", "symbol": "RELIANCE"}));
   ```

## Yahoo Finance Features

### Real Market Data
- ✅ Live prices from Yahoo Finance for 20+ symbols
- ✅ Real market movements and volatility
- ✅ Actual trading volumes and market cap
- ✅ Multi-currency support (USD for US stocks, INR for Indian stocks)

### Data Quality
- ✅ Professional-grade market data
- ✅ Real-time price updates (30-second frequency)
- ✅ Historical data for backtesting
- ✅ Market status and trading hours

### Geographic Coverage
- ✅ US Markets: NASDAQ, NYSE
- ✅ Indian Markets: NSE (National Stock Exchange)
- ✅ Automatic symbol mapping (.NS suffix for Indian stocks)
- ✅ Multi-timezone support

The real-time data integration system now provides actual market data from Yahoo Finance, supporting both US and Indian stock markets with professional-grade data quality! 📊📈
