/**
 * Chart Data Slice
 * Manages OHLCV data and chart configurations for TradingView integration
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { TradingDataService, ChartData } from '../../services/tradingDataService';

export interface ChartDataState {
  chartData: Record<string, ChartData>;
  indicators: Record<string, any>;
  selectedTimeframe: string;
  availableTimeframes: string[];
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  chartConfig: {
    showVolume: boolean;
    showGrid: boolean;
    candlestickColors: {
      upColor: string;
      downColor: string;
      borderUpColor: string;
      borderDownColor: string;
      wickUpColor: string;
      wickDownColor: string;
    };
  };
}

const initialState: ChartDataState = {
  chartData: {},
  indicators: {},
  selectedTimeframe: '1d',
  availableTimeframes: ['1m', '5m', '15m', '1h', '4h', '1d', '1w'],
  loading: false,
  error: null,
  lastUpdated: null,
  chartConfig: {
    showVolume: true,
    showGrid: true,
    candlestickColors: {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderUpColor: '#26a69a',
      borderDownColor: '#ef5350',
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    },
  },
};

// Async Thunks
export const fetchChartData = createAsyncThunk(
  'chartData/fetchChartData',
  async ({ symbol, timeframe, limit }: { symbol: string; timeframe?: string; limit?: number }) => {
    const response = await TradingDataService.getChartData(
      symbol, 
      timeframe || '1d', 
      limit || 100
    );
    return response;
  }
);

export const fetchOHLCVData = createAsyncThunk(
  'chartData/fetchOHLCVData',
  async ({ symbol, timeframe, limit }: { symbol: string; timeframe?: string; limit?: number }) => {
    const response = await TradingDataService.getOHLCVData(
      symbol, 
      timeframe || '1d', 
      limit || 100
    );
    return { symbol, timeframe: timeframe || '1d', data: response };
  }
);

export const fetchIndicators = createAsyncThunk(
  'chartData/fetchIndicators',
  async ({ symbol, indicators }: { symbol: string; indicators: string[] }) => {
    const response = await TradingDataService.getIndicators(symbol, indicators);
    return { symbol, indicators: response };
  }
);

// Chart Data Slice
const chartDataSlice = createSlice({
  name: 'chartData',
  initialState,
  reducers: {
    setSelectedTimeframe: (state, action: PayloadAction<string>) => {
      state.selectedTimeframe = action.payload;
    },
    updateChartConfig: (state, action: PayloadAction<Partial<ChartDataState['chartConfig']>>) => {
      state.chartConfig = { ...state.chartConfig, ...action.payload };
    },
    toggleVolume: (state) => {
      state.chartConfig.showVolume = !state.chartConfig.showVolume;
    },
    toggleGrid: (state) => {
      state.chartConfig.showGrid = !state.chartConfig.showGrid;
    },
    setCandlestickColors: (state, action: PayloadAction<Partial<ChartDataState['chartConfig']['candlestickColors']>>) => {
      state.chartConfig.candlestickColors = { 
        ...state.chartConfig.candlestickColors, 
        ...action.payload 
      };
    },
    clearChartData: (state, action: PayloadAction<string>) => {
      delete state.chartData[action.payload];
      delete state.indicators[action.payload];
    },
    clearError: (state) => {
      state.error = null;
    },
    resetChartData: (state) => {
      state.chartData = {};
      state.indicators = {};
      state.lastUpdated = null;
    }
  },
  extraReducers: (builder) => {
    // Fetch Chart Data
    builder
      .addCase(fetchChartData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchChartData.fulfilled, (state, action) => {
        state.loading = false;
        state.chartData[action.payload.symbol] = action.payload;
        state.lastUpdated = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchChartData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch chart data';
      });

    // Fetch OHLCV Data
    builder
      .addCase(fetchOHLCVData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOHLCVData.fulfilled, (state, action) => {
        state.loading = false;
        const { symbol, timeframe, data } = action.payload;
        if (!state.chartData[symbol]) {
          state.chartData[symbol] = {
            symbol,
            timeframe,
            data: []
          };
        }
        state.chartData[symbol].data = data;
        state.chartData[symbol].timeframe = timeframe;
        state.lastUpdated = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchOHLCVData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch OHLCV data';
      });

    // Fetch Indicators
    builder
      .addCase(fetchIndicators.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchIndicators.fulfilled, (state, action) => {
        state.loading = false;
        const { symbol, indicators } = action.payload;
        state.indicators[symbol] = indicators;
        state.error = null;
      })
      .addCase(fetchIndicators.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch indicators';
      });
  },
});

export const {
  setSelectedTimeframe,
  updateChartConfig,
  toggleVolume,
  toggleGrid,
  setCandlestickColors,
  clearChartData,
  clearError,
  resetChartData
} = chartDataSlice.actions;

export default chartDataSlice.reducer;

// Selectors
export const selectChartData = (state: { chartData: ChartDataState }) => state.chartData.chartData;
export const selectChartDataBySymbol = (symbol: string) => (state: { chartData: ChartDataState }) => 
  state.chartData.chartData[symbol];
export const selectIndicators = (state: { chartData: ChartDataState }) => state.chartData.indicators;
export const selectIndicatorsBySymbol = (symbol: string) => (state: { chartData: ChartDataState }) => 
  state.chartData.indicators[symbol];
export const selectSelectedTimeframe = (state: { chartData: ChartDataState }) => state.chartData.selectedTimeframe;
export const selectAvailableTimeframes = (state: { chartData: ChartDataState }) => state.chartData.availableTimeframes;
export const selectChartConfig = (state: { chartData: ChartDataState }) => state.chartData.chartConfig;
export const selectChartDataLoading = (state: { chartData: ChartDataState }) => state.chartData.loading;
export const selectChartDataError = (state: { chartData: ChartDataState }) => state.chartData.error;
