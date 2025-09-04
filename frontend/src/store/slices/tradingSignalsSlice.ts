/**
 * Trading Signals Slice
 * Manages AI-generated trading signals and strategies
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { TradingDataService, TradingSignal } from '../../services/tradingDataService';

export interface TradingSignalsState {
  signals: Record<string, TradingSignal[]>;
  activeSignals: TradingSignal[];
  backtestResults: Record<string, any>;
  selectedStrategy: string;
  availableStrategies: string[];
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  signalFilters: {
    signalType?: 'BUY' | 'SELL' | 'HOLD';
    minConfidence?: number;
    strategy?: string;
  };
}

const initialState: TradingSignalsState = {
  signals: {},
  activeSignals: [],
  backtestResults: {},
  selectedStrategy: 'default',
  availableStrategies: ['default', 'momentum', 'mean_reversion', 'breakout'],
  loading: false,
  error: null,
  lastUpdated: null,
  signalFilters: {
    minConfidence: 0.6,
  },
};

// Async Thunks
export const fetchTradingSignals = createAsyncThunk(
  'tradingSignals/fetchTradingSignals',
  async (symbol: string) => {
    const response = await TradingDataService.getTradingSignals(symbol);
    return { symbol, signals: response };
  }
);

export const fetchMultipleTradingSignals = createAsyncThunk(
  'tradingSignals/fetchMultipleTradingSignals',
  async (symbols: string[]) => {
    const promises = symbols.map(symbol => 
      TradingDataService.getTradingSignals(symbol).then(signals => ({ symbol, signals }))
    );
    const results = await Promise.allSettled(promises);
    
    return results
      .filter((result): result is PromiseFulfilledResult<{ symbol: string; signals: TradingSignal[] }> => 
        result.status === 'fulfilled')
      .map(result => result.value);
  }
);

export const runBacktest = createAsyncThunk(
  'tradingSignals/runBacktest',
  async (strategyConfig: any) => {
    const response = await TradingDataService.runBacktest(strategyConfig);
    return { strategyId: strategyConfig.strategy, results: response };
  }
);

// Trading Signals Slice
const tradingSignalsSlice = createSlice({
  name: 'tradingSignals',
  initialState,
  reducers: {
    setSelectedStrategy: (state, action: PayloadAction<string>) => {
      state.selectedStrategy = action.payload;
    },
    updateSignalFilters: (state, action: PayloadAction<Partial<TradingSignalsState['signalFilters']>>) => {
      state.signalFilters = { ...state.signalFilters, ...action.payload };
    },
    addActiveSignal: (state, action: PayloadAction<TradingSignal>) => {
      state.activeSignals.push(action.payload);
    },
    removeActiveSignal: (state, action: PayloadAction<string>) => {
      state.activeSignals = state.activeSignals.filter(signal => signal.id !== action.payload);
    },
    clearActiveSignals: (state) => {
      state.activeSignals = [];
    },
    updateSignal: (state, action: PayloadAction<TradingSignal>) => {
      const signalIndex = state.activeSignals.findIndex(signal => signal.id === action.payload.id);
      if (signalIndex !== -1) {
        state.activeSignals[signalIndex] = action.payload;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
    resetTradingSignals: (state) => {
      state.signals = {};
      state.activeSignals = [];
      state.backtestResults = {};
      state.lastUpdated = null;
    }
  },
  extraReducers: (builder) => {
    // Fetch Trading Signals
    builder
      .addCase(fetchTradingSignals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTradingSignals.fulfilled, (state, action) => {
        state.loading = false;
        const { symbol, signals } = action.payload;
        state.signals[symbol] = signals;
        
        // Update active signals with high confidence signals
        const highConfidenceSignals = signals.filter(
          signal => signal.confidence >= (state.signalFilters.minConfidence || 0.6)
        );
        
        // Remove existing active signals for this symbol
        state.activeSignals = state.activeSignals.filter(signal => signal.symbol !== symbol);
        
        // Add new high confidence signals
        state.activeSignals.push(...highConfidenceSignals);
        
        state.lastUpdated = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchTradingSignals.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch trading signals';
      });

    // Fetch Multiple Trading Signals
    builder
      .addCase(fetchMultipleTradingSignals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMultipleTradingSignals.fulfilled, (state, action) => {
        state.loading = false;
        
        action.payload.forEach(({ symbol, signals }) => {
          state.signals[symbol] = signals;
          
          // Update active signals with high confidence signals
          const highConfidenceSignals = signals.filter(
            signal => signal.confidence >= (state.signalFilters.minConfidence || 0.6)
          );
          
          // Remove existing active signals for this symbol
          state.activeSignals = state.activeSignals.filter(signal => signal.symbol !== symbol);
          
          // Add new high confidence signals
          state.activeSignals.push(...highConfidenceSignals);
        });
        
        state.lastUpdated = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchMultipleTradingSignals.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch multiple trading signals';
      });

    // Run Backtest
    builder
      .addCase(runBacktest.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(runBacktest.fulfilled, (state, action) => {
        state.loading = false;
        const { strategyId, results } = action.payload;
        state.backtestResults[strategyId] = results;
        state.error = null;
      })
      .addCase(runBacktest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to run backtest';
      });
  },
});

export const {
  setSelectedStrategy,
  updateSignalFilters,
  addActiveSignal,
  removeActiveSignal,
  clearActiveSignals,
  updateSignal,
  clearError,
  resetTradingSignals
} = tradingSignalsSlice.actions;

export default tradingSignalsSlice.reducer;

// Selectors
export const selectTradingSignals = (state: { tradingSignals: TradingSignalsState }) => state.tradingSignals.signals;
export const selectTradingSignalsBySymbol = (symbol: string) => (state: { tradingSignals: TradingSignalsState }) => 
  state.tradingSignals.signals[symbol] || [];
export const selectActiveSignals = (state: { tradingSignals: TradingSignalsState }) => state.tradingSignals.activeSignals;
export const selectBacktestResults = (state: { tradingSignals: TradingSignalsState }) => state.tradingSignals.backtestResults;
export const selectBacktestResultsByStrategy = (strategy: string) => (state: { tradingSignals: TradingSignalsState }) => 
  state.tradingSignals.backtestResults[strategy];
export const selectSelectedStrategy = (state: { tradingSignals: TradingSignalsState }) => state.tradingSignals.selectedStrategy;
export const selectAvailableStrategies = (state: { tradingSignals: TradingSignalsState }) => state.tradingSignals.availableStrategies;
export const selectSignalFilters = (state: { tradingSignals: TradingSignalsState }) => state.tradingSignals.signalFilters;
export const selectTradingSignalsLoading = (state: { tradingSignals: TradingSignalsState }) => state.tradingSignals.loading;
export const selectTradingSignalsError = (state: { tradingSignals: TradingSignalsState }) => state.tradingSignals.error;
