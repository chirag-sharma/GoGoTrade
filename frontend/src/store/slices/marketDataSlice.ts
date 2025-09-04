/**
 * Market Data Slice
 * Manages real-time market data for various instruments
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { TradingDataService, MarketData, Instrument } from '../../services/tradingDataService';

export interface MarketDataState {
  instruments: Instrument[];
  marketData: Record<string, MarketData>;
  selectedSymbol: string;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: MarketDataState = {
  instruments: [],
  marketData: {},
  selectedSymbol: 'RELIANCE',
  loading: false,
  error: null,
  lastUpdated: null,
};

// Async Thunks
export const fetchInstruments = createAsyncThunk(
  'marketData/fetchInstruments',
  async () => {
    const response = await TradingDataService.getInstruments();
    return response;
  }
);

export const fetchMarketData = createAsyncThunk(
  'marketData/fetchMarketData',
  async (symbol: string) => {
    const response = await TradingDataService.getMarketData(symbol);
    return { symbol, data: response };
  }
);

export const fetchMultipleMarketData = createAsyncThunk(
  'marketData/fetchMultipleMarketData',
  async (symbols: string[]) => {
    const promises = symbols.map(symbol => 
      TradingDataService.getMarketData(symbol).then(data => ({ symbol, data }))
    );
    const results = await Promise.allSettled(promises);
    
    return results
      .filter((result): result is PromiseFulfilledResult<{ symbol: string; data: MarketData }> => 
        result.status === 'fulfilled')
      .map(result => result.value);
  }
);

// Market Data Slice
const marketDataSlice = createSlice({
  name: 'marketData',
  initialState,
  reducers: {
    setSelectedSymbol: (state, action: PayloadAction<string>) => {
      state.selectedSymbol = action.payload;
    },
    updateMarketData: (state, action: PayloadAction<{ symbol: string; data: MarketData }>) => {
      state.marketData[action.payload.symbol] = action.payload.data;
      state.lastUpdated = new Date().toISOString();
    },
    clearError: (state) => {
      state.error = null;
    },
    resetMarketData: (state) => {
      state.marketData = {};
      state.lastUpdated = null;
    }
  },
  extraReducers: (builder) => {
    // Fetch Instruments
    builder
      .addCase(fetchInstruments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchInstruments.fulfilled, (state, action) => {
        state.loading = false;
        state.instruments = action.payload;
        state.error = null;
      })
      .addCase(fetchInstruments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch instruments';
      });

    // Fetch Market Data
    builder
      .addCase(fetchMarketData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMarketData.fulfilled, (state, action) => {
        state.loading = false;
        state.marketData[action.payload.symbol] = action.payload.data;
        state.lastUpdated = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchMarketData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch market data';
      });

    // Fetch Multiple Market Data
    builder
      .addCase(fetchMultipleMarketData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMultipleMarketData.fulfilled, (state, action) => {
        state.loading = false;
        action.payload.forEach(({ symbol, data }) => {
          state.marketData[symbol] = data;
        });
        state.lastUpdated = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchMultipleMarketData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch multiple market data';
      });
  },
});

export const {
  setSelectedSymbol,
  updateMarketData,
  clearError,
  resetMarketData
} = marketDataSlice.actions;

export default marketDataSlice.reducer;

// Selectors
export const selectInstruments = (state: { marketData: MarketDataState }) => state.marketData.instruments;
export const selectMarketData = (state: { marketData: MarketDataState }) => state.marketData.marketData;
export const selectSelectedSymbol = (state: { marketData: MarketDataState }) => state.marketData.selectedSymbol;
export const selectMarketDataBySymbol = (symbol: string) => (state: { marketData: MarketDataState }) => 
  state.marketData.marketData[symbol];
export const selectMarketDataLoading = (state: { marketData: MarketDataState }) => state.marketData.loading;
export const selectMarketDataError = (state: { marketData: MarketDataState }) => state.marketData.error;
