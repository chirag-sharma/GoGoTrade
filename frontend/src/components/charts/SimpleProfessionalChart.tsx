import React, { useEffect, useRef, useState } from 'react';
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
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  Timeline,
  Refresh,
} from '@mui/icons-material';
import { 
  createChart, 
  ColorType,
  CrosshairMode
} from 'lightweight-charts';

// Import service types
import { TradingSignal } from '../../services/tradingDataService';

interface TradingChartProps {
  symbol: string;
  signals?: TradingSignal[];
  onSymbolChange?: (symbol: string) => void;
}

interface ChartDataPoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export const SimpleProfessionalChart: React.FC<TradingChartProps> = ({
  symbol,
  signals = [],
  onSymbolChange
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candlestickSeriesRef = useRef<any>(null);
  
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M'>('1M');
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Available symbols for quick selection
  const availableSymbols = ['RELIANCE', 'INFY', 'TCS', 'HDFCBANK', 'ITC', 'WIPRO', 'LT'];

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    try {
      // Create the chart
      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: 500,
        layout: {
          background: { type: ColorType.Solid, color: '#1a1a1a' },
          textColor: '#d1d4dc',
        },
        grid: {
          vertLines: { color: '#2a2a2a' },
          horzLines: { color: '#2a2a2a' },
        },
        crosshair: {
          mode: CrosshairMode.Normal,
        },
        rightPriceScale: {
          borderColor: '#485158',
        },
        timeScale: {
          borderColor: '#485158',
          timeVisible: true,
          secondsVisible: false,
        },
      });

      chartRef.current = chart;

      // Add candlestick series using type assertion for compatibility
      const candlestickSeries = (chart as any).addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      });
      candlestickSeriesRef.current = candlestickSeries;

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
    } catch (err) {
      console.error('Chart initialization failed:', err);
      setError('Failed to initialize chart');
    }
  }, []);

  // Load and update chart data
  useEffect(() => {
    const loadChartData = async () => {
      if (!chartRef.current || !candlestickSeriesRef.current) return;
      
      setLoading(true);
      setError(null);

      try {
        console.log(`Loading chart data for ${symbol} (${timeframe})`);
        
        // Fetch chart data from new API
        const response = await fetch(`http://localhost:8000/api/v1/charts/chart-data/${symbol}?timeframe=${timeframe.toLowerCase()}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch data: ${response.status}`);
        }
        
        const chartApiResponse = await response.json();
        console.log('Chart API response:', chartApiResponse);
        
        if (!chartApiResponse.candlesticks || chartApiResponse.candlesticks.length === 0) {
          throw new Error(`No data available for ${symbol}`);
        }

        // Convert API response to chart format
        const candlestickData = chartApiResponse.candlesticks.map((candle: any) => ({
          time: candle.time,
          open: parseFloat(candle.open.toString()),
          high: parseFloat(candle.high.toString()),
          low: parseFloat(candle.low.toString()),
          close: parseFloat(candle.close.toString()),
        }));

        // Update chart data
        candlestickSeriesRef.current.setData(candlestickData);

        // Auto-scale to fit data
        chartRef.current.timeScale().fitContent();

        // Update state for other components
        const formattedData: ChartDataPoint[] = candlestickData.map((candle: any) => ({
          time: candle.time,
          open: candle.open,
          high: candle.high,
          low: candle.low,
          close: candle.close,
          volume: Math.floor(Math.random() * 1000000) + 500000, // Mock volume
        }));

        setChartData(formattedData);

      } catch (err: any) {
        console.error('Failed to load chart data:', err);
        setError(`Failed to load chart data: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    loadChartData();
  }, [symbol, timeframe]);

  // Handle timeframe change
  const handleTimeframeChange = (newTimeframe: '1D' | '1W' | '1M' | '3M') => {
    setTimeframe(newTimeframe);
  };

  // Handle symbol change
  const handleSymbolChange = (event: SelectChangeEvent) => {
    const newSymbol = event.target.value;
    if (onSymbolChange) {
      onSymbolChange(newSymbol);
    }
  };

  // Refresh data
  const handleRefresh = () => {
    setChartData([...chartData]); // Trigger re-render
  };

  // Get latest price and change
  const latestPrice = chartData.length > 0 ? chartData[chartData.length - 1].close : 0;
  const previousPrice = chartData.length > 1 ? chartData[chartData.length - 2].close : latestPrice;
  const priceChange = latestPrice - previousPrice;
  const priceChangePercent = previousPrice > 0 ? (priceChange / previousPrice) * 100 : 0;
  const isPositive = priceChange >= 0;

  // Signal indicators
  const latestSignal = signals.length > 0 ? signals[signals.length - 1] : null;
  const signalColor = latestSignal?.signalType === 'BUY' ? 'success' : latestSignal?.signalType === 'SELL' ? 'error' : 'info';

  return (
    <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Timeline color="primary" />
          <Typography variant="h5" fontWeight="bold">
            Professional Trading Chart
          </Typography>
          <Chip
            label={symbol}
            color="primary"
            variant="outlined"
            icon={<TrendingUp />}
          />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* Symbol Selector */}
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Symbol</InputLabel>
            <Select
              value={symbol}
              label="Symbol"
              onChange={handleSymbolChange}
            >
              {availableSymbols.map((sym) => (
                <MenuItem key={sym} value={sym}>{sym}</MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Refresh Button */}
          <Button
            variant="outlined"
            size="small"
            onClick={handleRefresh}
            disabled={loading}
            startIcon={<Refresh />}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Price Info */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 2 }}>
        <Typography variant="h4" fontWeight="bold">
          ₹{latestPrice.toFixed(2)}
        </Typography>
        <Typography
          variant="h6"
          color={isPositive ? 'success.main' : 'error.main'}
          sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
        >
          {isPositive ? '+' : ''}{priceChange.toFixed(2)} ({isPositive ? '+' : ''}{priceChangePercent.toFixed(2)}%)
        </Typography>
        {latestSignal && (
          <Chip
            label={`${latestSignal.signalType} Signal`}
            color={signalColor}
            size="small"
            variant="filled"
          />
        )}
      </Box>

      {/* Controls */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        {/* Timeframe Selector */}
        <ButtonGroup variant="outlined" size="small">
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
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Loading Indicator */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 500 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Chart Container */}
      <Box
        ref={chartContainerRef}
        sx={{
          width: '100%',
          height: 500,
          borderRadius: 1,
          border: 1,
          borderColor: 'divider',
          display: loading ? 'none' : 'block',
        }}
      />

      {/* Chart Info */}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Data points: {chartData.length} | Timeframe: {timeframe} | Symbol: {symbol}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Professional TradingView Charts • Real-time Updates
        </Typography>
      </Box>
    </Paper>
  );
};

export default SimpleProfessionalChart;
