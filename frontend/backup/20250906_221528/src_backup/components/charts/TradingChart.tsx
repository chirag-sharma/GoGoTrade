import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, CandlestickData, Time } from 'lightweight-charts';
import { Box, Typography, CircularProgress, Alert, Toolbar, Button, ButtonGroup } from '@mui/material';
import { TrendingUp, ShowChart, BarChart } from '@mui/icons-material';

interface TradingChartProps {
  mockDataMode: boolean;
}

interface ChartSettings {
  symbol: string;
  timeframe: string;
  chartType: 'candlestick' | 'line' | 'area';
}

const TradingChart: React.FC<TradingChartProps> = ({ mockDataMode }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<any | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<ChartSettings>({
    symbol: 'NIFTY',
    timeframe: '1h',
    chartType: 'candlestick'
  });

  // Generate mock data for development
  const generateMockData = (): CandlestickData[] => {
    const data: CandlestickData[] = [];
    const baseDate = new Date('2024-01-01');
    let currentPrice = 18500; // Starting price for NIFTY
    
    for (let i = 0; i < 100; i++) {
      const time = new Date(baseDate.getTime() + i * 60 * 60 * 1000); // 1 hour intervals
      
      // Generate realistic price movement
      const change = (Math.random() - 0.5) * 100; // Random change
      const volatility = Math.random() * 50;
      
      const open = currentPrice;
      const close = open + change;
      const high = Math.max(open, close) + Math.random() * volatility;
      const low = Math.min(open, close) - Math.random() * volatility;
      
      data.push({
        time: (time.getTime() / 1000) as Time,
        open,
        high,
        low,
        close
      });
      
      currentPrice = close;
    }
    
    return data;
  };

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    try {
      // Create chart instance
      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: 400,
        layout: {
          textColor: '#333',
        },
        grid: {
          vertLines: { color: '#f0f0f0' },
          horzLines: { color: '#f0f0f0' },
        },
        rightPriceScale: {
          borderColor: '#cccccc',
        },
        timeScale: {
          borderColor: '#cccccc',
          timeVisible: true,
          secondsVisible: false,
        },
      });

      // Create candlestick series using a simple approach for v5
      const series = (chart as any).addCandlestickSeries({
        upColor: '#4caf50',
        downColor: '#f44336',
        borderDownColor: '#f44336',
        borderUpColor: '#4caf50',
        wickDownColor: '#f44336',
        wickUpColor: '#4caf50',
      });

      // Load data
      const data = mockDataMode ? generateMockData() : [];
      series.setData(data);
      
      // Fit content
      chart.timeScale().fitContent();

      // Store refs
      chartRef.current = chart;
      seriesRef.current = series;
      
      setLoading(false);
      setError(null);

      // Handle resize
      const handleResize = () => {
        if (chart && chartContainerRef.current) {
          chart.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        }
      };

      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        if (chart) {
          chart.remove();
        }
      };
    } catch (err) {
      console.error('Chart initialization error:', err);
      setError('Failed to initialize chart');
      setLoading(false);
    }
  }, [mockDataMode, settings.symbol, settings.timeframe]);

  // Handle chart type change
  const handleChartTypeChange = (newType: ChartSettings['chartType']) => {
    setSettings(prev => ({ ...prev, chartType: newType }));
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          minHeight: 400,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ margin: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Chart Controls */}
      <Toolbar variant="dense" sx={{ minHeight: 48, px: 0 }}>
        <Typography variant="subtitle2" sx={{ mr: 2 }}>
          {settings.symbol} - {settings.timeframe}
        </Typography>
        
        <Box sx={{ flexGrow: 1 }} />
        
        <ButtonGroup size="small" variant="outlined">
          <Button
            startIcon={<BarChart />}
            variant={settings.chartType === 'candlestick' ? 'contained' : 'outlined'}
            onClick={() => handleChartTypeChange('candlestick')}
          >
            Candles
          </Button>
          <Button
            startIcon={<ShowChart />}
            variant={settings.chartType === 'line' ? 'contained' : 'outlined'}
            onClick={() => handleChartTypeChange('line')}
          >
            Line
          </Button>
          <Button
            startIcon={<TrendingUp />}
            variant={settings.chartType === 'area' ? 'contained' : 'outlined'}
            onClick={() => handleChartTypeChange('area')}
          >
            Area
          </Button>
        </ButtonGroup>
      </Toolbar>

      {/* Chart Container */}
      <Box
        ref={chartContainerRef}
        sx={{
          flexGrow: 1,
          minHeight: 0,
          '& > div': {
            borderRadius: 1,
          },
        }}
      />
      
      {mockDataMode && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
          Displaying mock data for development
        </Typography>
      )}
    </Box>
  );
};

export default TradingChart;
