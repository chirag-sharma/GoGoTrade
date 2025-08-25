# GoGoTrade - AI-Powered Indian Stock Trading Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.5+-blue.svg)](https://www.typescriptlang.org/)

An AI-powered trading platform designed specifically for Indian stock markets (NSE/BSE) with advanced pattern recognition, risk management, and regulatory compliance.

## 🎯 Project Overview

GoGoTrade leverages artificial intelligence to:
- **Read candlestick charts** and detect trading patterns
- **Analyze trade patterns** using technical indicators
- **Implement various trading strategies** with backtesting
- **Execute trades** with comprehensive risk management
- **Ensure SEBI compliance** for algorithmic trading

## 🏗️ Architecture

- **Backend**: Python/FastAPI with TimescaleDB and Redis
- **Frontend**: React/TypeScript with TradingView Lightweight Charts
- **Data**: Zerodha Kite Connect WebSocket streaming
- **AI/ML**: TA-Lib, VectorBT, Backtrader for strategy development
- **Compliance**: SEBI algo trading requirements with audit trails

## 📋 Implementation Timeline

**Current Status**: Project Initialization (Week 1)  
**Target MVP**: 8 weeks (October 20, 2025)  
**Advanced Features**: 6 months (February 2026)

See [Implementation Roadmap](docs/TODO.md) for detailed timeline.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- Zerodha Kite Connect API account

### Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd GoGoTrade

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
npm start

# Start services
docker-compose up -d
```

## 📁 Project Structure

```
GoGoTrade/
├── README.md                 # This file
├── docs/                     # All documentation
│   ├── TODO.md              # Implementation roadmap
│   ├── IMPLEMENTATION_CONTEXT.md  # Development history
│   └── Strategies/          # Original strategy analysis
├── tests/                   # All test files
├── backend/                 # Python FastAPI application
├── frontend/                # React TypeScript application
├── docker-compose.yml       # Service orchestration
└── requirements.txt         # Python dependencies
```

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **TimescaleDB**: Time-series database for OHLCV data
- **Redis**: Caching and real-time data
- **TA-Lib**: Technical analysis indicators
- **VectorBT**: Vectorized backtesting
- **Backtrader**: Event-driven backtesting

### Frontend
- **React**: Modern UI framework
- **TypeScript**: Type-safe JavaScript
- **TradingView Lightweight Charts**: Professional trading charts
- **Redux Toolkit**: State management
- **Material-UI**: UI components

## 📈 Key Features

### Current Phase (Week 1-2)
- [x] Real-time NSE/BSE data streaming
- [x] Interactive candlestick charts
- [x] Basic pattern recognition
- [x] SEBI compliance framework

### Upcoming Phases
- [ ] Advanced technical indicators
- [ ] AI-powered pattern recognition
- [ ] Strategy backtesting engine
- [ ] Paper trading system
- [ ] Live trading with risk management

## 🛡️ Risk Management & Compliance

- **SEBI Compliance**: All orders tagged for algorithmic trading
- **Risk Controls**: Position sizing, daily loss limits, circuit breakers
- **Audit Trail**: Comprehensive logging for regulatory requirements
- **Kill Switch**: Emergency stop mechanisms for all trading activities

## 📊 Strategy Framework

The platform implements multiple trading strategies:
1. **Trend Following**: EMA crossovers with RSI filters
2. **Breakout**: Donchian channel breakouts with ATR stops
3. **Mean Reversion**: RSI-based reversals with VWAP anchors

## 🤝 Contributing

1. All tests must be in `tests/` directory
2. All documentation in `docs/` directory
3. Follow the implementation roadmap in `docs/TODO.md`
4. Ensure SEBI compliance in all trading features

## 📄 License

This project is for educational and research purposes. Please ensure compliance with local financial regulations before live trading.

---

**⚠️ Disclaimer**: This software is for educational purposes only. Always consult with financial advisors and ensure compliance with local regulations before engaging in algorithmic trading.
