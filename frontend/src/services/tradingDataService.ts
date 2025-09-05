/**
 * Trading Data Service
 * Handles API calls for trading data, instruments, and market information
 */

import { apiClient } from './apiClient';

export interface Instrument {
  symbol: string;
  name: string;
  exchange: string;
}

export interface OHLCVData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketData {
  symbol: string;
  lastPrice: number;
  change: number;
  changePercent: number;
  volume: number;
  timestamp: string;
}

export interface ChartData {
  symbol: string;
  timeframe: string;
  data: OHLCVData[];
}

export interface TradingSignal {
  id: string;
  symbol: string;
  signalType: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  targetPrice?: number;
  stopLoss?: number;
  timestamp: string;
  strategy: string;
}

export class TradingDataService {
  /**
   * Get system status
   */
  static async getStatus() {
    try {
      const response = await apiClient.get('/api/v1/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching status:', error);
      throw error;
    }
  }

  /**
   * Get list of available instruments
   */
  static async getInstruments(): Promise<Instrument[]> {
    try {
      const response = await apiClient.get('/api/v1/trading-data/instruments');
      return response.data;
    } catch (error) {
      console.error('Error fetching instruments:', error);
      throw error;
    }
  }

  /**
   * Get market data for a specific symbol
   */
  static async getMarketData(symbol: string): Promise<MarketData> {
    try {
      const response = await apiClient.get(`/api/v1/trading-data/market-data/${symbol}`);
      const data = response.data;
      
      // Map API response to our interface
      return {
        symbol: data.symbol,
        lastPrice: data.price,
        change: 0, // API doesn't provide change, calculate or set default
        changePercent: data.changePercent || 0,
        volume: data.volume,
        timestamp: data.timestamp
      };
    } catch (error) {
      console.error(`Error fetching market data for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get OHLCV data for a specific symbol and timeframe
   */
  static async getOHLCVData(
    symbol: string, 
    timeframe: string = '1d',
    limit: number = 100
  ): Promise<OHLCVData[]> {
    try {
      const response = await apiClient.get(`/api/v1/trading-data/ohlcv/${symbol}`, {
        params: { timeframe, limit }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching OHLCV data for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get chart data for TradingView
   */
  static async getChartData(
    symbol: string, 
    timeframe: string = '1d',
    limit: number = 100
  ): Promise<ChartData> {
    try {
      const response = await apiClient.get(`/api/v1/charts/chart-data/${symbol}`, {
        params: { timeframe, limit }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching chart data for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get trading signals for a symbol
   */
  static async getTradingSignals(symbol: string): Promise<TradingSignal[]> {
    try {
      const response = await apiClient.get(`/api/v1/strategies/signals/${symbol}`);
      const signals = response.data;
      
      // Map API response to our interface
      return signals.map((signal: any, index: number) => ({
        id: `${symbol}-${signal.strategy}-${index}`,
        symbol: signal.symbol,
        signalType: signal.signal as 'BUY' | 'SELL' | 'HOLD',
        confidence: signal.confidence,
        targetPrice: signal.targetPrice,
        stopLoss: signal.stopLoss,
        timestamp: signal.timestamp,
        strategy: signal.strategy
      }));
    } catch (error) {
      console.error(`Error fetching trading signals for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get indicators for a symbol
   */
  static async getIndicators(
    symbol: string,
    indicators: string[] = ['sma', 'ema', 'rsi']
  ) {
    try {
      const response = await apiClient.get(`/api/v1/charts/indicators/${symbol}`, {
        params: { indicators: indicators.join(',') }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching indicators for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Run backtest for a strategy
   */
  static async runBacktest(strategyConfig: any) {
    try {
      const response = await apiClient.post('/api/v1/strategies/backtest', strategyConfig);
      return response.data;
    } catch (error) {
      console.error('Error running backtest:', error);
      throw error;
    }
  }
}

export default TradingDataService;
