# GoGoTrade Database Architecture Documentation

## Overview
GoGoTrade uses a sophisticated database architecture built on **TimescaleDB** (PostgreSQL extension for time-series data) with **Redis** for caching and real-time data. The system is designed for high-frequency trading data with compliance tracking.

## Database Technology Stack

### Primary Database: TimescaleDB
- **Engine**: PostgreSQL 13+ with TimescaleDB extension
- **Purpose**: Time-series data storage with automatic partitioning
- **Features**: Hypertables, continuous aggregates, compression policies
- **Connection**: Async SQLAlchemy with psycopg (asyncpg driver)

### Cache Layer: Redis
- **Purpose**: Real-time data caching, session management, pub/sub
- **Features**: Connection pooling, async operations
- **Use Cases**: Live market data, signal caching, user sessions

## Database Schema

### 1. `instruments` - Master Instrument Registry
**Purpose**: Static reference data for all tradable instruments

| Column | Type | Description | Index |
|--------|------|-------------|-------|
| `id` | UUID | Primary key, unique instrument ID | PK |
| `instrument_token` | BigInteger | Broker's unique token | Unique |
| `exchange_token` | BigInteger | Exchange identifier | |
| `tradingsymbol` | String(50) | Trading symbol (e.g., "RELIANCE") | Index |
| `name` | String(200) | Full instrument name | |
| `last_price` | Numeric(10,2) | Last traded price | |
| `expiry` | DateTime | Expiry date (for F&O) | |
| `strike` | Numeric(10,2) | Strike price (for options) | |
| `tick_size` | Numeric(10,4) | Minimum price movement | |
| `lot_size` | Integer | Minimum trading quantity | |
| `instrument_type` | Enum | EQUITY/FUTURES/OPTIONS/CURRENCY/COMMODITY | |
| `segment` | String(10) | Market segment (NSE/BSE/NFO) | |
| `exchange` | String(10) | Exchange name | |
| `created_at` | DateTime | Record creation timestamp | |
| `updated_at` | DateTime | Last update timestamp | |

**Relationships**: 
- One-to-many with `ohlcv_data`, `trades`, `trading_signals`

---

### 2. `ohlcv_data` - Time Series Price Data (TimescaleDB Hypertable)
**Purpose**: Historical and real-time OHLCV candlestick data

| Column | Type | Description | Index |
|--------|------|-------------|-------|
| `instrument_id` | UUID | Foreign key to instruments | PK |
| `timestamp` | DateTime(TZ) | Candle timestamp | PK |
| `timeframe` | String(10) | Candle period (1m/5m/15m/1h/1d) | PK |
| `open` | Numeric(12,4) | Opening price | |
| `high` | Numeric(12,4) | Highest price | |
| `low` | Numeric(12,4) | Lowest price | |
| `close` | Numeric(12,4) | Closing price | |
| `volume` | BigInteger | Trading volume | |
| `open_interest` | BigInteger | Open interest (F&O only) | |
| `trades_count` | Integer | Number of trades | |
| `created_at` | DateTime | Record insertion time | |

**TimescaleDB Features**:
- **Hypertable**: Partitioned by `timestamp` with 7-day chunks
- **Compression**: Enabled after 30 days with segment-by: `instrument_id, timeframe`
- **Continuous Aggregates**: Real-time 5m candles from 1m data
- **Indexes**: 
  - `idx_ohlcv_timestamp` on `timestamp`
  - `idx_ohlcv_instrument_time` on `(instrument_id, timestamp)`

**Data Retention**: 
- Raw 1m data: 2 years
- Compressed historical data: 10+ years
- Real-time aggregations for multiple timeframes

---

### 3. `trades` - Individual Trade Records (TimescaleDB Hypertable)
**Purpose**: Audit trail for all trades, compliance tracking

| Column | Type | Description | Index |
|--------|------|-------------|-------|
| `order_id` | String(100) | Unique order identifier | PK |
| `order_timestamp` | DateTime(TZ) | Order placement time | PK |
| `instrument_id` | UUID | Foreign key to instruments | Index |
| `exchange_order_id` | String(100) | Exchange order ID | |
| `transaction_type` | Enum | BUY/SELL | |
| `quantity` | Integer | Order quantity | |
| `price` | Numeric(12,4) | Order price | |
| `order_type` | Enum | MARKET/LIMIT/STOP_LOSS/STOP_LOSS_MARKET | |
| `order_status` | Enum | PENDING/OPEN/COMPLETE/CANCELLED/REJECTED | |
| `executed_quantity` | Integer | Filled quantity | |
| `pending_quantity` | Integer | Remaining quantity | |
| `cancelled_quantity` | Integer | Cancelled quantity | |
| `average_price` | Numeric(12,4) | Average execution price | |
| `algo_id` | String(50) | Algorithm identifier (SEBI compliance) | Index |
| `strategy_id` | String(50) | Strategy identifier | Index |
| `user_id` | String(50) | User/client identifier | Index |
| `exchange_timestamp` | DateTime | Exchange timestamp | |
| `created_at` | DateTime | Record creation | |
| `updated_at` | DateTime | Last update | |

**TimescaleDB Features**:
- **Hypertable**: Partitioned by `order_timestamp` with 1-day chunks
- **Indexes**:
  - `idx_trades_timestamp` on `order_timestamp`
  - `idx_trades_instrument_time` on `(instrument_id, order_timestamp)`
  - `idx_trades_user_time` on `(user_id, order_timestamp)`
  - `idx_trades_algo_strategy` on `(algo_id, strategy_id)`

**Compliance**: SEBI algo trading requirements met with algo_id and strategy_id tracking

---

### 4. `trading_signals` - AI Generated Signals (TimescaleDB Hypertable)
**Purpose**: Store AI/ML generated trading recommendations

| Column | Type | Description | Index |
|--------|------|-------------|-------|
| `instrument_id` | UUID | Foreign key to instruments | PK |
| `generated_at` | DateTime(TZ) | Signal generation time | PK |
| `strategy_name` | String(100) | Strategy that generated signal | PK |
| `signal_type` | Enum | BUY/SELL/HOLD/STRONG_BUY/STRONG_SELL | |
| `confidence_score` | Numeric(5,4) | Confidence level (0.0-1.0) | |
| `target_price` | Numeric(12,4) | Target price for signal | |
| `stop_loss` | Numeric(12,4) | Stop loss level | |
| `timeframe` | String(10) | Signal timeframe | Index |
| `indicators_used` | Text | JSON of indicators (RSI, MACD, etc.) | |
| `market_condition` | String(50) | Bull/Bear/Sideways | |
| `expires_at` | DateTime | Signal expiry time | |
| `is_active` | Boolean | Signal active status | Index |
| `created_at` | DateTime | Record creation | |
| `updated_at` | DateTime | Last update | |

**TimescaleDB Features**:
- **Hypertable**: Partitioned by `generated_at` with 7-day chunks
- **Indexes**:
  - `idx_signals_timestamp` on `generated_at`
  - `idx_signals_active_time` on `(is_active, generated_at)`
  - `idx_signals_timeframe` on `(timeframe, generated_at)`

---

### 5. `market_sessions` - Market Timing Reference
**Purpose**: Track market hours and holidays for different exchanges

| Column | Type | Description | Index |
|--------|------|-------------|-------|
| `id` | UUID | Primary key | PK |
| `exchange` | String(10) | Exchange name | Index |
| `segment` | String(10) | Market segment | |
| `session_date` | DateTime | Trading date | Index |
| `pre_market_start` | DateTime | Pre-market start time | |
| `market_open` | DateTime | Market open time | |
| `market_close` | DateTime | Market close time | |
| `post_market_end` | DateTime | Post-market end time | |
| `is_trading_day` | Boolean | Trading day flag | |
| `is_holiday` | Boolean | Holiday flag | |
| `holiday_reason` | String(200) | Holiday description | |
| `created_at` | DateTime | Record creation | |

**Constraints**:
- Unique: `(exchange, segment, session_date)`

---

## Data Storage Patterns

### Time-Series Data Storage
```sql
-- OHLCV data partitioned by time
SELECT * FROM ohlcv_data 
WHERE timestamp >= '2024-01-01' 
  AND timestamp < '2024-01-02'
  AND instrument_id = 'uuid-here'
  AND timeframe = '1m';
```

### Real-Time Data Pipeline
1. **Live Data Ingestion**: WebSocket → Redis → PostgreSQL
2. **Batch Processing**: Hourly aggregation jobs
3. **Continuous Aggregates**: Real-time 5m/15m/1h candles from 1m data

### Materialized Views
```sql
-- Daily OHLCV summary
CREATE MATERIALIZED VIEW daily_ohlcv AS
SELECT 
    instrument_id,
    DATE(timestamp) as date,
    first(open, timestamp) as open,
    max(high) as high,
    min(low) as low,
    last(close, timestamp) as close,
    sum(volume) as volume
FROM ohlcv_data 
WHERE timeframe = '1d'
GROUP BY instrument_id, DATE(timestamp);

-- Real-time 5-minute candles
CREATE MATERIALIZED VIEW ohlcv_5m
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('5 minutes', timestamp) AS bucket,
    instrument_id,
    first(open, timestamp) as open,
    max(high) as high,
    min(low) as low,
    last(close, timestamp) as close,
    sum(volume) as volume
FROM ohlcv_data 
WHERE timeframe = '1m'
GROUP BY bucket, instrument_id;
```

## Performance Optimizations

### TimescaleDB Optimizations
- **Chunk Intervals**: 7 days for OHLCV, 1 day for trades
- **Compression**: Automatic after 30 days
- **Indexes**: Compound indexes on frequently queried columns
- **Parallel Queries**: Enabled for large time range queries

### Connection Pooling
```python
# Async connection pool settings
DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600
```

### Redis Caching Strategy
- **Live Prices**: 1-second TTL
- **Signals**: 5-minute TTL
- **Market Data**: Session-based TTL

## Data Relationships

```
instruments (1) ──→ (∞) ohlcv_data
           (1) ──→ (∞) trades  
           (1) ──→ (∞) trading_signals

market_sessions ──→ Trading hours reference
```

## Compliance & Audit

### SEBI Requirements
- **Algo Trading ID**: Required in `trades.algo_id`
- **Strategy Tracking**: `trades.strategy_id`
- **Timestamp Precision**: Microsecond precision
- **Audit Trail**: Complete trade lifecycle tracking

### Data Retention
- **OHLCV**: 10+ years (compressed)
- **Trades**: 7 years (regulatory requirement)
- **Signals**: 2 years
- **Market Sessions**: Permanent reference

## Real-Time Data Integration Plan

Now I'll implement the real-time data integration system based on this database structure.
