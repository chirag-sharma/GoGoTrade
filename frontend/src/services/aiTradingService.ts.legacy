/**
 * AI Trading Service - Frontend API Client
 * Connects React frontend to AI trading backend APIs
 */

import axios, { AxiosResponse } from 'axios';

// API Base URL
const API_BASE_URL = '/api/v1/ai-trading';

// TypeScript interfaces for API responses
export interface MarketDataItem {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  timestamp: string;
}

export interface TradingSignal {
  symbol: string;
  signalType: 'BUY' | 'SELL' | 'HOLD' | 'WATCH';
  confidence: number;
  price: number;
  reason: string;
  timestamp: string;
  patternType?: string;
  targetPrice?: number;
  stopLoss?: number;
}

export interface HistoricalData {
  symbol: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface DashboardData {
  marketData: MarketDataItem[];
  signals: TradingSignal[];
  summary: {
    totalSymbols: number;
    positiveSymbols: number;
    negativeSymbols: number;
    marketSentiment: 'bullish' | 'bearish' | 'neutral';
    buySignals: number;
    sellSignals: number;
    lastUpdated: string;
  };
}

export interface DetailedSignal extends TradingSignal {
  historicalDataPoints: number;
  recommendation: {
    action: string;
    strength: 'strong' | 'moderate' | 'weak';
    riskLevel: 'low' | 'medium' | 'high';
  };
}

/**
 * AI Trading API Service Class
 */
export class AITradingService {
  private static instance: AITradingService;
  
  private constructor() {}
  
  public static getInstance(): AITradingService {
    if (!AITradingService.instance) {
      AITradingService.instance = new AITradingService();
    }
    return AITradingService.instance;
  }

  /**
   * Get real-time market data for specified symbols
   */
  async getMarketData(symbols: string[]): Promise<MarketDataItem[]> {
    try {
      const symbolsParam = symbols.join(',');
      const response: AxiosResponse<MarketDataItem[]> = await axios.get(
        `${API_BASE_URL}/market-data?symbols=${symbolsParam}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching market data:', error);
      throw new Error('Failed to fetch market data');
    }
  }

  /**
   * Get AI trading signals for specified symbols
   */
  async getTradingSignals(symbols: string[]): Promise<TradingSignal[]> {
    try {
      const symbolsParam = symbols.join(',');
      const response: AxiosResponse<TradingSignal[]> = await axios.get(
        `${API_BASE_URL}/trading-signals?symbols=${symbolsParam}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching trading signals:', error);
      throw new Error('Failed to fetch trading signals');
    }
  }

  /**
   * Get historical OHLC data for a symbol
   */
  async getHistoricalData(symbol: string, days: number = 30): Promise<HistoricalData[]> {
    try {
      const response: AxiosResponse<HistoricalData[]> = await axios.get(
        `${API_BASE_URL}/historical-data/${symbol}?days=${days}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching historical data:', error);
      throw new Error('Failed to fetch historical data');
    }
  }

  /**
   * Get comprehensive dashboard data (market data + signals + summary)
   */
  async getDashboardData(symbols?: string[]): Promise<DashboardData> {
    try {
      const defaultSymbols = 'NIFTY,SENSEX,RELIANCE.NS,TCS.NS,INFY.NS';
      const symbolsParam = symbols ? symbols.join(',') : defaultSymbols;
      
      const response: AxiosResponse<DashboardData> = await axios.get(
        `${API_BASE_URL}/dashboard-data?symbols=${symbolsParam}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw new Error('Failed to fetch dashboard data');
    }
  }

  /**
   * Get detailed AI signal analysis for a single symbol
   */
  async getDetailedSignal(symbol: string): Promise<DetailedSignal> {
    try {
      const response: AxiosResponse<DetailedSignal> = await axios.get(
        `${API_BASE_URL}/signal/${symbol}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching detailed signal:', error);
      throw new Error('Failed to fetch detailed signal');
    }
  }

  /**
   * Check AI trading service health
   */
  async getHealthStatus(): Promise<{ status: string; service: string; features: string[] }> {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      return response.data;
    } catch (error) {
      console.error('Error checking AI service health:', error);
      throw new Error('Failed to check AI service health');
    }
  }

  /**
   * Get market data with error handling and fallback
   */
  async getMarketDataSafe(symbols: string[]): Promise<MarketDataItem[]> {
    try {
      return await this.getMarketData(symbols);
    } catch (error) {
      console.warn('Using fallback market data due to API error:', error);
      // Return mock data as fallback
      return this.getMockMarketData(symbols);
    }
  }

  /**
   * Get trading signals with error handling and fallback
   */
  async getTradingSignalsSafe(symbols: string[]): Promise<TradingSignal[]> {
    try {
      return await this.getTradingSignals(symbols);
    } catch (error) {
      console.warn('Using fallback signals due to API error:', error);
      // Return mock signals as fallback
      return this.getMockTradingSignals(symbols);
    }
  }

  /**
   * Mock data for fallback scenarios
   */
  private getMockMarketData(symbols: string[]): MarketDataItem[] {
    const mockPrices: { [key: string]: number } = {
      'NIFTY': 19500,
      'SENSEX': 65000,
      'RELIANCE.NS': 2500,
      'TCS.NS': 3600,
      'INFY.NS': 1400,
    };

    return symbols.map(symbol => ({
      symbol,
      price: mockPrices[symbol] || 1000,
      change: Math.random() * 100 - 50,
      changePercent: Math.random() * 4 - 2,
      volume: Math.floor(Math.random() * 10000000),
      high: (mockPrices[symbol] || 1000) * 1.02,
      low: (mockPrices[symbol] || 1000) * 0.98,
      open: mockPrices[symbol] || 1000,
      timestamp: new Date().toISOString(),
    }));
  }

  private getMockTradingSignals(symbols: string[]): TradingSignal[] {
    const signalTypes: ('BUY' | 'SELL' | 'HOLD' | 'WATCH')[] = ['BUY', 'SELL', 'HOLD', 'WATCH'];
    
    return symbols.slice(0, 2).map((symbol, index) => ({
      symbol,
      signalType: signalTypes[index % signalTypes.length],
      confidence: 0.7 + Math.random() * 0.3,
      price: 2500 + Math.random() * 100,
      reason: `AI pattern analysis detected ${signalTypes[index % signalTypes.length].toLowerCase()} opportunity`,
      timestamp: new Date().toISOString(),
      targetPrice: 2600 + Math.random() * 100,
      stopLoss: 2400 + Math.random() * 50,
    }));
  }
}

// Export singleton instance
export const aiTradingService = AITradingService.getInstance();

// Utility functions for data formatting
export const formatPrice = (price: number): string => {
  return `₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export const formatChange = (change: number): string => {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}`;
};

export const formatPercentage = (percentage: number): string => {
  const sign = percentage >= 0 ? '+' : '';
  return `${sign}${percentage.toFixed(2)}%`;
};

export const getSignalColor = (signalType: string): string => {
  switch (signalType) {
    case 'BUY': return '#4caf50'; // Green
    case 'SELL': return '#f44336'; // Red
    case 'HOLD': return '#ff9800'; // Orange
    case 'WATCH': return '#2196f3'; // Blue
    default: return '#9e9e9e'; // Gray
  }
};

export const getSignalIcon = (signalType: string): string => {
  switch (signalType) {
    case 'BUY': return '🟢';
    case 'SELL': return '🔴';
    case 'HOLD': return '🟡';
    case 'WATCH': return '🔵';
    default: return '⚪';
  }
};
