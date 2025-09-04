/**
 * TradingView Chart Component
 * Integrates TradingView Lightweight Charts with backend OHLCV data
 */

import React, { useEffect, useRef, useCallback, useMemo } from 'react';
import { createChart, IChartApi, UTCTimestamp } from 'lightweight-charts';
import { Box, Paper, CircularProgress, Typography } from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { fetchChartData } from '../../store/slices/chartDataSlice';
import { ChartComponentProps, TimeframeOption } from '../../types';

interface TradingViewChartProps extends ChartComponentProps {
  symbol: string;
  timeframe?: TimeframeOption;
  height?: number;
  showVolume?: boolean;
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({
  symbol,
  timeframe = '1d',
  height = 600,
  showVolume = true,
  className,
  onSymbolChange,
  onTimeframeChange
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<any>(null);
  const volumeSeriesRef = useRef<any>(null);

  // Redux selectors with proper type casting
  const chartData = useSelector((state: RootState) => (state.chartData as any)?.chartData?.[symbol]);
  const chartConfig = useSelector((state: RootState) => (state.chartData as any)?.chartConfig);
  const loading = useSelector((state: RootState) => (state.chartData as any)?.loading);
  const error = useSelector((state: RootState) => (state.chartData as any)?.error);

  // Chart configuration
  const chartOptions = useMemo(() => ({
    layout: {
      background: { color: '#1e1e1e' },
      textColor: '#DDD',
    },
    grid: {
      vertLines: { visible: true },
      horzLines: { visible: true },
    },
    crosshair: {
      mode: 1,
    },
    rightPriceScale: {
      borderVisible: false,
    },
    timeScale: {
      borderVisible: false,
      timeVisible: true,
      secondsVisible: false,
    },
    watermark: {
      color: 'rgba(11, 94, 29, 0.4)',
      visible: true,
      text: symbol,
      fontSize: 24,
      horzAlign: 'left' as const,
      vertAlign: 'bottom' as const,
    },
  }), [symbol]);

  // Candlestick series configuration
  const candlestickOptions = useMemo(() => ({
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderDownColor: '#ef5350',
    borderUpColor: '#26a69a',
    wickDownColor: '#ef5350',
    wickUpColor: '#26a69a',
  }), []);

  // Volume series configuration
  const volumeOptions = useMemo(() => ({
    color: '#26a69a',
    priceFormat: {
      type: 'volume' as const,
    },
    priceScaleId: '',
    scaleMargins: {
      top: 0.8,
      bottom: 0,
    },
  }), []);

  // Convert OHLCV data to chart format
  const formatChartData = useCallback((data: any[]) => {
    if (!data || !Array.isArray(data)) return { candlestickData: [], volumeData: [] };

    const candlestickData = data.map(item => ({
      time: (new Date(item.timestamp).getTime() / 1000) as UTCTimestamp,
      open: parseFloat(item.open),
      high: parseFloat(item.high),
      low: parseFloat(item.low),
      close: parseFloat(item.close),
    }));

    const volumeData = data.map(item => ({
      time: (new Date(item.timestamp).getTime() / 1000) as UTCTimestamp,
      value: parseFloat(item.volume),
      color: parseFloat(item.close) >= parseFloat(item.open) ? '#26a69a' : '#ef5350',
    }));

    return { candlestickData, volumeData };
  }, []);

  // Initialize chart
  const initChart = useCallback(() => {
    if (!chartContainerRef.current) return;

    // Clean up existing chart
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
      candlestickSeriesRef.current = null;
      volumeSeriesRef.current = null;
    }

    // Create new chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      ...chartOptions,
    });

    chartRef.current = chart;

    // Add candlestick series
    const candlestickSeries = (chart as any).addCandlestickSeries(candlestickOptions);
    candlestickSeriesRef.current = candlestickSeries;

    // Add volume series if enabled
    if (showVolume) {
      const volumeSeries = (chart as any).addHistogramSeries(volumeOptions);
      volumeSeriesRef.current = volumeSeries;
    }

    // Handle window resize
    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
        candlestickSeriesRef.current = null;
        volumeSeriesRef.current = null;
      }
    };
  }, [height, chartOptions, candlestickOptions, volumeOptions, showVolume]);

  // Update chart data
  const updateChartData = useCallback(() => {
    if (!chartData || !chartData.data || !candlestickSeriesRef.current) return;

    const { candlestickData, volumeData } = formatChartData(chartData.data);

    // Update candlestick series
    candlestickSeriesRef.current.setData(candlestickData);

    // Update volume series if exists
    if (volumeSeriesRef.current && showVolume) {
      volumeSeriesRef.current.setData(volumeData);
    }

    // Fit content
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent();
    }
  }, [chartData, formatChartData, showVolume]);

  // Fetch data when symbol or timeframe changes
  useEffect(() => {
    dispatch(fetchChartData({ symbol, timeframe, limit: 500 }));
  }, [dispatch, symbol, timeframe]);

  // Initialize chart on mount
  useEffect(() => {
    const cleanup = initChart();
    return cleanup;
  }, [initChart]);

  // Update chart when data changes
  useEffect(() => {
    updateChartData();
  }, [updateChartData]);

  // Handle loading state
  if (loading) {
    return (
      <Box
        className={className}
        display="flex"
        alignItems="center"
        justifyContent="center"
        height={height}
        component={Paper}
        elevation={2}
      >
        <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
          <CircularProgress />
          <Typography variant="body2" color="textSecondary">
            Loading chart data for {symbol}...
          </Typography>
        </Box>
      </Box>
    );
  }

  // Handle error state
  if (error) {
    return (
      <Box
        className={className}
        display="flex"
        alignItems="center"
        justifyContent="center"
        height={height}
        component={Paper}
        elevation={2}
      >
        <Typography variant="body1" color="error">
          Error loading chart: {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Paper 
      className={className} 
      elevation={2}
      sx={{ 
        p: 1,
        backgroundColor: 'background.paper',
        '& .tv-lightweight-charts': {
          borderRadius: 1,
        }
      }}
    >
      <div
        ref={chartContainerRef}
        style={{
          width: '100%',
          height: height,
          position: 'relative',
        }}
      />
    </Paper>
  );
};

export default TradingViewChart;
