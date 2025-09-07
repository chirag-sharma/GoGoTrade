# How to Check if GoGoTrade System is Working

This guide explains how to verify that your GoGoTrade system with Yahoo Finance integration is working properly.

## 🚀 Quick Start Commands

### 1. Start the System
```bash
cd backend
./startup.sh
# or manually:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Quick Status Check
```bash
# Lightweight status check
python quick_check.py

# Comprehensive health check
python system_health_check.py
```

### 3. Test Yahoo Finance Integration
```bash
# Test Yahoo Finance service directly
python test_yahoo_finance.py

# Test full real-time integration
python test_real_time_integration.py
```

## 📋 Manual Verification Steps

### Step 1: Check Backend Server
✅ **Expected**: Server running on http://localhost:8000

```bash
curl http://localhost:8000/api/v1/status
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0",
  "api_endpoints": [...]
}
```

### Step 2: Check API Documentation
✅ **Expected**: Interactive API docs accessible

Visit: http://localhost:8000/docs

You should see the FastAPI interactive documentation with all endpoints.

### Step 3: Test Yahoo Finance Integration

#### 3a. Subscribe to Live Data
```bash
curl -X POST http://localhost:8000/api/v1/real-time/subscribe \
     -H "Content-Type: application/json" \
     -d '{"symbols": ["AAPL", "GOOGL", "RELIANCE"]}'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Subscribed to 3 symbols",
  "symbols": ["AAPL", "GOOGL", "RELIANCE"],
  "active_subscriptions": 3
}
```

#### 3b. Wait and Check Live Prices
```bash
# Wait 60 seconds for Yahoo Finance data to be fetched
sleep 60

# Check individual price
curl http://localhost:8000/api/v1/real-time/price/AAPL

# Check all prices
curl http://localhost:8000/api/v1/real-time/prices
```

**Expected Response for AAPL:**
```json
{
  "symbol": "AAPL",
  "ltp": 174.25,
  "change": 2.15,
  "change_percent": 1.25,
  "volume": 45678901,
  "previous_close": 172.10,
  "currency": "USD",
  "exchange": "NMS",
  "source": "yahoo_finance",
  "timestamp": "2025-09-06T10:30:00Z"
}
```

### Step 4: Check Trading Signals
```bash
curl http://localhost:8000/api/v1/real-time/signals
```

**Expected**: List of trading signals (may be empty initially)

### Step 5: Test WebSocket Connection

#### Using Python:
```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/real-time/ws"
    
    async with websockets.connect(uri) as websocket:
        # Subscribe to AAPL
        await websocket.send(json.dumps({"action": "subscribe", "symbol": "AAPL"}))
        
        # Listen for updates
        for _ in range(5):
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.run(test_websocket())
```

#### Using Browser Console:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/real-time/ws');
ws.onopen = () => {
    console.log('Connected');
    ws.send(JSON.stringify({"action": "subscribe", "symbol": "AAPL"}));
};
ws.onmessage = (event) => {
    console.log('Received:', JSON.parse(event.data));
};
```

### Step 6: Test AI Services

#### Technical Analysis:
```bash
curl -X POST http://localhost:8000/api/v1/ai-enhanced/technical-analysis \
     -H "Content-Type: application/json" \
     -d '{
       "symbol": "AAPL",
       "timeframe": "1d",
       "indicators": ["RSI", "MACD", "SMA"]
     }'
```

#### Trade Prediction:
```bash
curl -X POST http://localhost:8000/api/v1/trade-prediction/predict \
     -H "Content-Type: application/json" \
     -d '{
       "symbol": "AAPL",
       "timeframe": "1h",
       "analysis_depth": "standard"
     }'
```

## 🔍 Automated Health Checks

### Complete System Health Check
```bash
python system_health_check.py
```

This script will:
- ✅ Check all dependencies
- ✅ Verify backend server
- ✅ Test API endpoints
- ✅ Validate database connection
- ✅ Test Yahoo Finance integration
- ✅ Check trading signals
- ✅ Test AI services
- ✅ Verify WebSocket connectivity

### Expected Output:
```
🚀 GoGoTrade System Health Check
⏰ Started at: 2025-09-06 10:30:00

============================================================
🔍 Python Dependencies
============================================================
✅ PASS Package - fastapi
✅ PASS Package - yfinance
✅ PASS Package - pandas
...

============================================================
🔍 Backend Server Status
============================================================
✅ PASS Backend Server
    Running on http://localhost:8000

============================================================
🔍 Yahoo Finance Integration
============================================================
    ⏳ Waiting 45 seconds for Yahoo Finance data...
✅ PASS Live Price - AAPL
    $174.25 (+1.25%) from yahoo_finance
✅ PASS Live Price - RELIANCE
    ₹2456.75 (+0.85%) from yahoo_finance
✅ PASS Yahoo Finance Overall
    2/2 symbols working

============================================================
🔍 Test Summary
============================================================
📊 Total Tests: 15
✅ Passed: 14
❌ Failed: 1
📈 Success Rate: 93.3%

🎉 System Status: HEALTHY
The GoGoTrade system is working properly!
```

## 🐛 Troubleshooting Common Issues

### Issue 1: Backend Not Starting
**Symptoms:** Connection refused errors
**Solutions:**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Install dependencies
pip install -r requirements.txt

# Start manually with debug
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

### Issue 2: No Live Price Data
**Symptoms:** 404 errors for price endpoints
**Solutions:**
```bash
# 1. Subscribe to symbols first
curl -X POST http://localhost:8000/api/v1/real-time/subscribe \
     -H "Content-Type: application/json" \
     -d '{"symbols": ["AAPL"]}'

# 2. Wait 60 seconds for data
sleep 60

# 3. Check status
curl http://localhost:8000/api/v1/real-time/status
```

### Issue 3: Yahoo Finance Rate Limiting
**Symptoms:** Empty responses or HTTP 429 errors
**Solutions:**
- Wait longer between requests (Yahoo Finance has rate limits)
- Use fewer symbols in batch requests
- Check Yahoo Finance service status

### Issue 4: Database Connection Issues
**Symptoms:** 500 errors, database errors in logs
**Solutions:**
```bash
# Initialize database
python scripts/init_db.py

# Check database file
ls -la gogotrade.db

# Reset database if corrupted
rm gogotrade.db && python scripts/init_db.py
```

## 📊 Monitoring Dashboard URLs

When system is working, these URLs should be accessible:

- **API Documentation**: http://localhost:8000/docs
- **API Status**: http://localhost:8000/api/v1/status
- **Real-time Status**: http://localhost:8000/api/v1/real-time/status
- **Live Prices**: http://localhost:8000/api/v1/real-time/prices
- **Trading Signals**: http://localhost:8000/api/v1/real-time/signals

## 🎯 Success Indicators

Your system is working properly when:

1. ✅ Backend server responds to health checks
2. ✅ Yahoo Finance integration returns real price data
3. ✅ WebSocket connections work
4. ✅ Trading signals are generated (may take time)
5. ✅ AI services respond to requests
6. ✅ Database operations succeed

## 📈 Performance Expectations

- **Price Updates**: Every 30 seconds (Yahoo Finance rate limit)
- **Signal Generation**: Every 5 minutes
- **WebSocket Latency**: < 100ms
- **API Response Time**: < 2 seconds
- **Yahoo Finance Data**: Real market prices with ~15-minute delay

Run the health check scripts regularly to ensure everything is working correctly!
