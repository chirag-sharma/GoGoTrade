/**
 * Advanced Trading Chart Component with AI Signal Overlays
 * Uses Lightweight Charts library for professional trading visualization
 */

import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, Time, CandlestickData, HistogramData } from 'lightweight-charts';
import {
  Box,
  Typography,
  ButtonGroup,
  Button,
  Paper,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
} from '@mui/material';
import {
  TrendingUp,
  Timeline,
  ShowChart,
} from '@mui/icons-material';

// Import AI service types
import { TradingSignal, HistoricalData, aiTradingService } from '../../services/aiTradingService';

interface TradingChartProps {
  symbol: string;
  signals?: TradingSignal[];
  onSymbolChange?: (symbol: string) => void;
}

export const TradingChart: React.FC<TradingChartProps> = ({
  symbol,
  signals = [],
  onSymbolChange
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M'>('1D');
  const [chartType, setChartType] = useState<'candlestick' | 'line'>('candlestick');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Available symbols for dropdown
  const availableSymbols = ['NIFTY', 'SENSEX', 'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS'];

  const handleSymbolChange = (event: SelectChangeEvent) => {
    const newSymbol = event.target.value;
    if (onSymbolChange) {
      onSymbolChange(newSymbol);
    }
  };

  const handleTimeframeChange = (newTimeframe: '1D' | '1W' | '1M' | '3M') => {
    setTimeframe(newTimeframe);
  };

  // Generate mock OHLC data for demonstration
  const generateMockOHLCData = (symbol: string, days: number): HistoricalData[] => {
    const data: HistoricalData[] = [];
    const basePrice = getBasePriceForSymbol(symbol);
    let currentPrice = basePrice;
    
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      const volatility = 0.02; // 2% daily volatility
      const change = (Math.random() - 0.5) * volatility;
      const open = currentPrice;
      const close = open * (1 + change);
      const high = Math.max(open, close) * (1 + Math.random() * 0.01);
      const low = Math.min(open, close) * (1 - Math.random() * 0.01);
      const volume = Math.floor(Math.random() * 5000000 + 1000000);
      
      data.push({
        symbol,
        timestamp: date.toISOString(),
        open,
        high,
        low,
        close,
        volume,
      });
      
      currentPrice = close;
    }
    
    return data;
  };

  const getBasePriceForSymbol = (symbol: string): number => {
    const prices: { [key: string]: number } = {
      'NIFTY': 19500,
      'SENSEX': 65000,
      'RELIANCE.NS': 2800,
      'TCS.NS': 3900,
      'INFY.NS': 1400,
      'HDFCBANK.NS': 1650,
      'ICICIBANK.NS': 950,
    };
    return prices[symbol] || 1000;
  };

  const getSignalColor = (signalType: string): string => {
    switch (signalType) {
      case 'BUY': return '#4bffb5';
      case 'SELL': return '#ff4976';
      case 'HOLD': return '#ffa726';
      case 'WATCH': return '#29b6f6';
      default: return '#9e9e9e';
    }
  };

  // Initialize and update chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Remove existing chart
    if (chartRef.current) {
      chartRef.current.remove();
    }

    // Create chart with professional styling
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: '#1a1a1a' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2B2B43' },
        horzLines: { color: '#2B2B43' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#485c7b',
      },
      timeScale: {
        borderColor: '#485c7b',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Load and display chart data
    const loadChartData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Calculate days based on timeframe
        const days = {
          '1D': 30,
          '1W': 90,
          '1M': 180,
          '3M': 365,
        }[timeframe];

        let historicalData: HistoricalData[];
        
        try {
          // Try to fetch from AI backend
          historicalData = await aiTradingService.getHistoricalData(symbol, days);
          if (historicalData.length === 0) {
            throw new Error('No data returned');
          }
        } catch {
          // Use mock data as fallback
          historicalData = generateMockOHLCData(symbol, days);
          setError('Using simulated data');
        }

        // Convert to chart format
        const candlestickData: CandlestickData[] = historicalData.map(item => ({
          time: Math.floor(new Date(item.timestamp).getTime() / 1000) as Time,
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        }));

        const volumeData: HistogramData[] = historicalData.map(item => ({
          time: Math.floor(new Date(item.timestamp).getTime() / 1000) as Time,
          value: item.volume,
          color: item.close >= item.open ? '#4bffb526' : '#ff497626',
        }));

        // Add candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
          upColor: '#4bffb5',
          downColor: '#ff4976',
          borderDownColor: '#ff4976',
          borderUpColor: '#4bffb5',
          wickDownColor: '#ff4976',
          wickUpColor: '#4bffb5',
        });

        candlestickSeries.setData(candlestickData);

        // Add volume series
        const volumeSeries = chart.addHistogramSeries({
          color: '#26a69a',
          priceFormat: {
            type: 'volume',
          },
          priceScaleId: 'volume',
        });

        volumeSeries.setData(volumeData);

        // Configure volume price scale
        chart.priceScale('volume').applyOptions({
          scaleMargins: {
            top: 0.8,
            bottom: 0,
          },
        });

        // Add AI signal markers if available
        if (signals.length > 0) {
          const markers = signals.map(signal => ({
            time: Math.floor(new Date(signal.timestamp).getTime() / 1000) as Time,
            position: (signal.signalType === 'BUY' ? 'belowBar' : 'aboveBar') as 'belowBar' | 'aboveBar',
            color: getSignalColor(signal.signalType),
            shape: (signal.signalType === 'BUY' ? 'arrowUp' : 'arrowDown') as 'arrowUp' | 'arrowDown',
            text: `${signal.signalType} ${(signal.confidence * 100).toFixed(0)}%`,
          }));

          candlestickSeries.setMarkers(markers);
        }

      } catch (err) {
        console.error('Failed to load chart data:', err);
        setError('Failed to load chart data');
      } finally {
        setLoading(false);
      }
    };

    loadChartData();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
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
      }
    };
  }, [symbol, timeframe, signals]);

  return (
    <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
      {/* Chart Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" color="primary">
            📈 {symbol} Chart
          </Typography>
          
          {loading && (
            <Chip label="Loading..." color="info" size="small" />
          )}
          
          {error && (
            <Chip label="Mock Data" color="warning" size="small" />
          )}
          
          {signals.length > 0 && (
            <Chip 
              label={`${signals.length} AI Signals`} 
              color="success" 
              size="small"
              icon={<TrendingUp />}
            />
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          {/* Symbol Selector */}
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Symbol</InputLabel>
            <Select value={symbol} onChange={handleSymbolChange}>
              {availableSymbols.map((sym) => (
                <MenuItem key={sym} value={sym}>
                  {sym}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Timeframe Buttons */}
          <ButtonGroup size="small">
            {(['1D', '1W', '1M', '3M'] as const).map((tf) => (
              <Button
                key={tf}
                variant={timeframe === tf ? 'contained' : 'outlined'}
                onClick={() => handleTimeframeChange(tf)}
              >
                {tf}
              </Button>
            ))}
          </ButtonGroup>

          {/* Chart Type Buttons */}
          <ButtonGroup size="small">
            <Button
              variant={chartType === 'candlestick' ? 'contained' : 'outlined'}
              onClick={() => setChartType('candlestick')}
              startIcon={<ShowChart />}
            >
              Candles
            </Button>
            <Button
              variant={chartType === 'line' ? 'contained' : 'outlined'}
              onClick={() => setChartType('line')}
              startIcon={<Timeline />}
            >
              Line
            </Button>
          </ButtonGroup>
        </Box>
      </Box>

      {/* Chart Container */}
      <Box
        ref={chartContainerRef}
        sx={{
          width: '100%',
          height: 400,
          bgcolor: '#1a1a1a',
          borderRadius: 1,
          overflow: 'hidden',
        }}
      />

      {/* Chart Info */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Typography variant="caption" color="text.secondary">
            🟢 Buy Signal • 🔴 Sell Signal • 🟡 Hold • 🔵 Watch
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Timeframe: {timeframe}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Volume shown below price
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default TradingChart;

  return (
    <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
      {/* Chart Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" color="primary">
            📈 {symbol} Chart
          </Typography>
          
          {loading && (
            <Chip label="Loading..." color="info" size="small" />
          )}
          
          {error && (
            <Chip label="Using Mock Data" color="warning" size="small" />
          )}
          
          {signals.length > 0 && (
            <Chip 
              label={`${signals.length} AI Signals`} 
              color="success" 
              size="small"
              icon={<TrendingUp />}
            />
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          {/* Symbol Selector */}
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Symbol</InputLabel>
            <Select value={symbol} onChange={handleSymbolChange}>
              {availableSymbols.map((sym) => (
                <MenuItem key={sym} value={sym}>
                  {sym}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Timeframe Buttons */}
          <ButtonGroup size="small">
            {(['1D', '1W', '1M', '3M'] as const).map((tf) => (
              <Button
                key={tf}
                variant={timeframe === tf ? 'contained' : 'outlined'}
                onClick={() => handleTimeframeChange(tf)}
              >
                {tf}
              </Button>
            ))}
          </ButtonGroup>

          {/* Chart Type Buttons */}
          <ButtonGroup size="small">
            <Button
              variant={chartType === 'candlestick' ? 'contained' : 'outlined'}
              onClick={() => setChartType('candlestick')}
              startIcon={<ShowChart />}
            >
              Candles
            </Button>
            <Button
              variant={chartType === 'line' ? 'contained' : 'outlined'}
              onClick={() => setChartType('line')}
              startIcon={<Timeline />}
            >
              Line
            </Button>
          </ButtonGroup>
        </Box>
      </Box>

      {/* Chart Container */}
      <Box
        ref={chartContainerRef}
        sx={{
          width: '100%',
          height: 400,
          bgcolor: '#1a1a1a',
          borderRadius: 1,
          overflow: 'hidden',
        }}
      />

      {/* Chart Info */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Typography variant="caption" color="text.secondary">
            🟢 Buy Signal • 🔴 Sell Signal • 🟡 Hold • 🔵 Watch
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Timeframe: {timeframe}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Volume shown below price
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default TradingChart;
