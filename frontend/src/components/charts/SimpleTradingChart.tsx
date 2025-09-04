/**
 * Professional Trading Chart Component
 * Fallback to CSS/HTML-based chart visualization with AI signal overlays
 */

import React, { useEffect, useState } from 'react';
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

interface ChartDataPoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export const TradingChart: React.FC<TradingChartProps> = ({
  symbol,
  signals = [],
  onSymbolChange
}) => {
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M'>('1D');
  const [chartType, setChartType] = useState<'candlestick' | 'line'>('candlestick');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

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

  // Load chart data
  useEffect(() => {
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
        const formattedData: ChartDataPoint[] = historicalData.map(item => ({
          time: new Date(item.timestamp).toLocaleDateString(),
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
          volume: item.volume,
        }));

        setChartData(formattedData);

      } catch (err) {
        console.error('Failed to load chart data:', err);
        setError('Failed to load chart data');
      } finally {
        setLoading(false);
      }
    };

    loadChartData();
  }, [symbol, timeframe]);

  // Calculate chart dimensions and scaling
  const maxPrice = Math.max(...chartData.map(d => d.high));
  const minPrice = Math.min(...chartData.map(d => d.low));
  const priceRange = maxPrice - minPrice;

  // Render candlestick bars
  const renderCandlesticks = () => {
    return chartData.map((dataPoint, index) => {
      const isGreen = dataPoint.close >= dataPoint.open;
      const bodyHeight = Math.abs(dataPoint.close - dataPoint.open) / priceRange * 300;
      const wickTopHeight = (dataPoint.high - Math.max(dataPoint.open, dataPoint.close)) / priceRange * 300;
      const wickBottomHeight = (Math.min(dataPoint.open, dataPoint.close) - dataPoint.low) / priceRange * 300;
      const bodyTop = (maxPrice - Math.max(dataPoint.open, dataPoint.close)) / priceRange * 300;
      
      return (
        <Box
          key={index}
          sx={{
            position: 'absolute',
            left: `${(index / chartData.length) * 100}%`,
            width: `${0.8 / chartData.length * 100}%`,
            height: '300px',
          }}
        >
          {/* Wick Top */}
          {wickTopHeight > 0 && (
            <Box
              sx={{
                position: 'absolute',
                top: `${(maxPrice - dataPoint.high) / priceRange * 300}px`,
                left: '45%',
                width: '10%',
                height: `${wickTopHeight}px`,
                bgcolor: isGreen ? '#4bffb5' : '#ff4976',
              }}
            />
          )}
          
          {/* Body */}
          <Box
            sx={{
              position: 'absolute',
              top: `${bodyTop}px`,
              left: '0%',
              width: '100%',
              height: `${Math.max(bodyHeight, 1)}px`,
              bgcolor: isGreen ? '#4bffb5' : '#ff4976',
              border: `1px solid ${isGreen ? '#4bffb5' : '#ff4976'}`,
            }}
          />
          
          {/* Wick Bottom */}
          {wickBottomHeight > 0 && (
            <Box
              sx={{
                position: 'absolute',
                top: `${bodyTop + bodyHeight}px`,
                left: '45%',
                width: '10%',
                height: `${wickBottomHeight}px`,
                bgcolor: isGreen ? '#4bffb5' : '#ff4976',
              }}
            />
          )}
        </Box>
      );
    });
  };

  // Render price line chart
  const renderLineChart = () => {
    const points = chartData.map((dataPoint, index) => {
      const x = (index / (chartData.length - 1)) * 100;
      const y = ((maxPrice - dataPoint.close) / priceRange) * 100;
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg
        width="100%"
        height="300px"
        style={{ position: 'absolute', top: 0, left: 0 }}
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
      >
        <polyline
          fill="none"
          stroke="#4bffb5"
          strokeWidth="0.3"
          points={points}
        />
      </svg>
    );
  };

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
        sx={{
          width: '100%',
          height: 400,
          bgcolor: '#1a1a1a',
          borderRadius: 1,
          overflow: 'hidden',
          position: 'relative',
          border: '1px solid #2B2B43',
        }}
      >
        {/* Price Grid Lines */}
        <Box sx={{ position: 'absolute', width: '100%', height: '300px', top: '50px' }}>
          {[...Array(5)].map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                top: `${(i / 4) * 100}%`,
                width: '100%',
                height: '1px',
                bgcolor: '#2B2B43',
              }}
            />
          ))}
        </Box>

        {/* Price Labels */}
        <Box sx={{ position: 'absolute', left: 0, top: '50px', width: '60px', height: '300px' }}>
          {[...Array(5)].map((_, i) => {
            const price = maxPrice - (i / 4) * priceRange;
            return (
              <Typography
                key={i}
                variant="caption"
                sx={{
                  position: 'absolute',
                  top: `${(i / 4) * 100}%`,
                  transform: 'translateY(-50%)',
                  color: '#d1d4dc',
                  fontSize: '10px',
                }}
              >
                {price.toFixed(0)}
              </Typography>
            );
          })}
        </Box>

        {/* Chart Area */}
        <Box sx={{ position: 'absolute', left: '60px', top: '50px', right: '10px', height: '300px' }}>
          {chartType === 'candlestick' ? renderCandlesticks() : renderLineChart()}
          
          {/* AI Signal Markers */}
          {signals.map((signal, index) => (
            <Box
              key={index}
              sx={{
                position: 'absolute',
                top: signal.signalType === 'BUY' ? '280px' : '10px',
                right: '20px',
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                bgcolor: getSignalColor(signal.signalType),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                zIndex: 10,
              }}
              title={`${signal.signalType} Signal - ${(signal.confidence * 100).toFixed(0)}% confidence`}
            >
              {signal.signalType === 'BUY' ? '▲' : '▼'}
            </Box>
          ))}
        </Box>

        {/* Time Labels */}
        <Box sx={{ position: 'absolute', bottom: '10px', left: '60px', right: '10px', height: '30px' }}>
          {chartData.slice(0, 6).map((dataPoint, index) => (
            <Typography
              key={index}
              variant="caption"
              sx={{
                position: 'absolute',
                left: `${(index / 5) * 100}%`,
                transform: 'translateX(-50%)',
                color: '#d1d4dc',
                fontSize: '10px',
              }}
            >
              {dataPoint.time}
            </Typography>
          ))}
        </Box>
      </Box>

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
            Data points: {chartData.length}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default TradingChart;
