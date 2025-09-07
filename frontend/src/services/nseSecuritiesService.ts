/**
 * NSE Securities Service
 * Handles all NSE (National Stock Exchange) related API calls
 */

import { apiClient } from './apiClient';

// Types for NSE Securities
export interface NSEInstrument {
  id: number;
  symbol: string;
  name: string;
  isin: string;
  listing_date: string;
  market_segment: 'LARGE_CAP' | 'MID_CAP' | 'SMALL_CAP' | 'MICRO_CAP';
  sector: string;
  industry_group: string;
  face_value: number;
  market_lot: number;
  created_at: string;
  updated_at: string;
}

export interface NSEInstrumentExtended {
  id: number;
  instrument_id: number;
  tradingsymbol: string;
  last_price: number;
  change: number;
  pchange: number;
  volume: number;
  average_price: number;
  oi: number;
  net_change: number;
  lower_circuit_limit: number;
  upper_circuit_limit: number;
  last_trade_time: string;
  oi_day_high: number;
  oi_day_low: number;
  depth_buy_quantity: number;
  depth_sell_quantity: number;
  created_at: string;
  updated_at: string;
}

export interface MarketStats {
  id: number;
  date: string;
  nifty_50: number;
  nifty_change: number;
  nifty_pchange: number;
  sensex: number;
  sensex_change: number;
  sensex_pchange: number;
  market_cap: number;
  total_turnover: number;
  advances: number;
  declines: number;
  unchanged: number;
  created_at: string;
}

export interface SectorPerformance {
  id: number;
  date: string;
  sector: string;
  rank: number;
  change: number;
  pchange: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
  pb_ratio: number;
  dividend_yield: number;
  created_at: string;
}

export interface SearchParams {
  q?: string;
  market_segment?: string;
  sector?: string;
  limit?: number;
  offset?: number;
}

export interface HealthResponse {
  status: string;
  database: string;
  instruments: number;
}

export interface MarketMoversResponse {
  gainers: Array<{
    symbol: string;
    name: string;
    last_price: number;
    change: number;
    pchange: number;
    volume: number;
  }>;
  losers: Array<{
    symbol: string;
    name: string;
    last_price: number;
    change: number;
    pchange: number;
    volume: number;
  }>;
}

/**
 * NSE Securities API Service
 */
export class NSESecuritiesService {
  
  /**
   * Get health status of the backend
   */
  static async getHealth(): Promise<HealthResponse> {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * Search for securities by symbol or name
   */
  static async searchSecurities(query: string, limit: number = 10): Promise<NSEInstrument[]> {
    try {
      const response = await apiClient.get('/api/v1/instruments/search', {
        params: { query, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Search securities failed:', error);
      throw error;
    }
  }

  /**
   * Get instruments with filtering options
   */
  static async getInstruments(params: SearchParams = {}): Promise<NSEInstrument[]> {
    try {
      const response = await apiClient.get('/api/v1/instruments', { params });
      return response.data;
    } catch (error) {
      console.error('Get instruments failed:', error);
      throw error;
    }
  }

  /**
   * Get market movers (gainers and losers)
   */
  static async getMarketMovers(): Promise<MarketMoversResponse> {
    try {
      const response = await apiClient.get('/api/v1/market-movers');
      return response.data;
    } catch (error) {
      console.error('Get market movers failed:', error);
      throw error;
    }
  }

  /**
   * Get sector performance data
   */
  static async getSectorPerformance(): Promise<SectorPerformance[]> {
    try {
      const response = await apiClient.get('/api/v1/sectors');
      return response.data;
    } catch (error) {
      console.error('Get sector performance failed:', error);
      throw error;
    }
  }

  /**
   * Get market segments
   */
  static async getMarketSegments(): Promise<string[]> {
    return ['LARGE_CAP', 'MID_CAP', 'SMALL_CAP', 'MICRO_CAP'];
  }

  /**
   * Get available sectors
   */
  static async getSectors(): Promise<string[]> {
    try {
      const instruments = await this.getInstruments({ limit: 1000 });
      const sectorSet = new Set(instruments.map(inst => inst.sector));
      const sectors = Array.from(sectorSet);
      return sectors.filter(sector => sector && sector.trim() !== '');
    } catch (error) {
      console.error('Get sectors failed:', error);
      throw error;
    }
  }

  /**
   * Get detailed information for a specific instrument
   */
  static async getInstrumentDetails(instrumentId: number): Promise<{
    instrument: NSEInstrument;
    extended?: NSEInstrumentExtended;
  }> {
    try {
      // Note: This would require additional endpoint implementation
      const instruments = await this.getInstruments();
      const instrument = instruments.find(inst => inst.id === instrumentId);
      
      if (!instrument) {
        throw new Error(`Instrument with ID ${instrumentId} not found`);
      }

      return { instrument };
    } catch (error) {
      console.error('Get instrument details failed:', error);
      throw error;
    }
  }

  /**
   * Get market statistics
   */
  static async getMarketStats(): Promise<MarketStats[]> {
    try {
      // This would require additional endpoint implementation
      // For now, return mock data or implement when backend endpoint is ready
      const response = await apiClient.get('/api/v1/market-stats');
      return response.data;
    } catch (error) {
      console.error('Get market stats failed:', error);
      // Return empty array if endpoint not implemented
      return [];
    }
  }
}

export default NSESecuritiesService;
