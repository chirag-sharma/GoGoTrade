/**
 * Redux Store Configuration
 * Sets up the global state management for the trading application
 */

import { configureStore } from '@reduxjs/toolkit';
import marketDataReducer from './slices/marketDataSlice';
import chartDataReducer from './slices/chartDataSlice';
import tradingSignalsReducer from './slices/tradingSignalsSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    marketData: marketDataReducer,
    chartData: chartDataReducer,
    tradingSignals: tradingSignalsReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
