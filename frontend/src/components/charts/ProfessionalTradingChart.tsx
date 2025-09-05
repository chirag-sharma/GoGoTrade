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
  IChartApi, 
  ISeriesApi,
  CandlestickData,
  HistogramData,
  LineData,
  ColorType,
  CrosshairMode,
  LineStyle
} from 'lightweight-charts';

// Import AI service types
import { TradingSignal, HistoricalData, aiTradingService } from '../../services/aiTradingService';

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

export const ProfessionalTradingChart: React.FC<TradingChartProps> = ({
  symbol,
  signals = [],
  onSymbolChange
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const smaSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M'>('1D');
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showVolume, setShowVolume] = useState(true);
  const [showSMA, setShowSMA] = useState(true);

  // Available symbols for quick selection
  const availableSymbols = ['RELIANCE', 'INFY', 'TCS', 'HDFCBANK', 'ITC', 'WIPRO', 'LT'];

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

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
        vertLine: {
          width: 1,
          color: '#C3BCDB44',
          style: LineStyle.Solid,
        },
        horzLine: {
          width: 1,
          color: '#C3BCDB44',
          style: LineStyle.Solid,
        },
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

    // Add candlestick series  
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });
    candlestickSeriesRef.current = candlestickSeries;

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume',
    });
    volumeSeriesRef.current = volumeSeries;

    // Add SMA series
    const smaSeries = chart.addLineSeries({
      color: '#2196F3',
      lineWidth: 2,
    });
    smaSeriesRef.current = smaSeries;

    // Set volume scale
    chart.priceScale('volume').applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

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
  }, []);

  // Load and update chart data
  useEffect(() => {
    const loadChartData = async () => {
      if (!chartRef.current || !candlestickSeriesRef.current || !volumeSeriesRef.current) return;
      
      setLoading(true);
      setError(null);

      try {
        console.log(`Loading chart data for ${symbol} (${timeframe})`);
        
        // Calculate date range based on timeframe
        const endDate = new Date();
        const startDate = new Date();
        
        switch (timeframe) {
          case '1D':
            startDate.setDate(endDate.getDate() - 1);
            break;
          case '1W':
            startDate.setDate(endDate.getDate() - 7);
            break;
          case '1M':
            startDate.setMonth(endDate.getMonth() - 1);
            break;
          case '3M':
            startDate.setMonth(endDate.getMonth() - 3);
            break;
        }

        // Fetch historical data
        const historicalData: HistoricalData[] = await aiTradingService.getHistoricalData(
          symbol,
          startDate.toISOString().split('T')[0],
          endDate.toISOString().split('T')[0]
        );

        if (!historicalData || historicalData.length === 0) {
          throw new Error(`No data available for ${symbol}`);
        }

        // Convert to chart format
        const candlestickData: CandlestickData[] = historicalData.map(item => ({
          time: new Date(item.timestamp).toISOString().split('T')[0],
          open: parseFloat(item.open.toString()),
          high: parseFloat(item.high.toString()),
          low: parseFloat(item.low.toString()),
          close: parseFloat(item.close.toString()),
        }));

        const volumeData: HistogramData[] = historicalData.map(item => ({
          time: new Date(item.timestamp).toISOString().split('T')[0],
          value: parseFloat(item.volume.toString()),
          color: parseFloat(item.close.toString()) >= parseFloat(item.open.toString()) ? '#26a69a80' : '#ef535080',
        }));

        // Calculate SMA (20-period)
        const smaData: LineData[] = [];
        const smaPeriod = 20;
        for (let i = smaPeriod - 1; i < candlestickData.length; i++) {
          const slice = candlestickData.slice(i - smaPeriod + 1, i + 1);
          const avgClose = slice.reduce((sum, candle) => sum + candle.close, 0) / smaPeriod;
          smaData.push({
            time: candlestickData[i].time,
            value: avgClose,
          });
        }

        // Update chart data
        candlestickSeriesRef.current.setData(candlestickData);
        if (showVolume) {
          volumeSeriesRef.current.setData(volumeData);
        } else {
          volumeSeriesRef.current.setData([]);
        }
        if (showSMA) {
          smaSeriesRef.current!.setData(smaData);
        } else {
          smaSeriesRef.current!.setData([]);
        }

        // Auto-scale to fit data
        chartRef.current.timeScale().fitContent();

        // Update state for other components
        const formattedData: ChartDataPoint[] = historicalData.map(item => ({
          time: item.timestamp,
          open: parseFloat(item.open.toString()),
          high: parseFloat(item.high.toString()),
          low: parseFloat(item.low.toString()),
          close: parseFloat(item.close.toString()),
          volume: parseFloat(item.volume.toString()),
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
  }, [symbol, timeframe, showVolume, showSMA]);

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
    if (chartData.length > 0) {
      setChartData([...chartData]); // Trigger re-render
    }
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

        {/* Chart Options */}
        <ButtonGroup variant="outlined" size="small">
          <Button
            variant={showVolume ? 'contained' : 'outlined'}
            onClick={() => setShowVolume(!showVolume)}
          >
            Volume
          </Button>
          <Button
            variant={showSMA ? 'contained' : 'outlined'}
            onClick={() => setShowSMA(!showSMA)}
          >
            SMA(20)
          </Button>
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

export default ProfessionalTradingChart;
