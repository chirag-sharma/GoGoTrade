import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import { Box, Paper, Typography } from '@mui/material';

interface CandlestickData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TradingSignal {
  timestamp: string;
  signalType: 'BUY' | 'SELL' | 'HOLD' | 'WATCH';
  price: number;
  confidence: number;
  symbol: string;
  reason: string;
}

interface PlotlyTradingChartProps {
  data: CandlestickData[];
  signals?: TradingSignal[];
  title?: string;
  height?: number;
}

const PlotlyTradingChart: React.FC<PlotlyTradingChartProps> = ({
  data,
  signals = [],
  title = "Trading Chart",
  height = 600
}) => {
  const chartData = useMemo(() => {
    const traces: any[] = [];
    
    // Candlestick trace
    if (data.length > 0) {
      traces.push({
        type: 'candlestick',
        x: data.map(d => d.timestamp),
        open: data.map(d => d.open),
        high: data.map(d => d.high),
        low: data.map(d => d.low),
        close: data.map(d => d.close),
        name: 'Price',
        increasing: { line: { color: '#26C281' } },
        decreasing: { line: { color: '#FF4747' } },
        showlegend: false
      });
    }

    // Volume trace
    if (data.length > 0) {
      traces.push({
        type: 'bar',
        x: data.map(d => d.timestamp),
        y: data.map(d => d.volume),
        name: 'Volume',
        yaxis: 'y2',
        marker: {
          color: data.map(d => d.close > d.open ? '#26C281' : '#FF4747'),
          opacity: 0.6
        },
        showlegend: false
      });
    }

    // Buy signals
    const buySignals = signals.filter(s => s.signalType === 'BUY');
    if (buySignals.length > 0) {
      traces.push({
        type: 'scatter',
        mode: 'markers',
        x: buySignals.map(s => s.timestamp),
        y: buySignals.map(s => s.price),
        name: 'Buy Signal',
        marker: {
          symbol: 'triangle-up',
          size: 12,
          color: '#26C281',
          line: { width: 2, color: 'white' }
        }
      });
    }

    // Sell signals
    const sellSignals = signals.filter(s => s.signalType === 'SELL');
    if (sellSignals.length > 0) {
      traces.push({
        type: 'scatter',
        mode: 'markers',
        x: sellSignals.map(s => s.timestamp),
        y: sellSignals.map(s => s.price),
        name: 'Sell Signal',
        marker: {
          symbol: 'triangle-down',
          size: 12,
          color: '#FF4747',
          line: { width: 2, color: 'white' }
        }
      });
    }

    return traces;
  }, [data, signals]);

  const layout = useMemo(() => ({
    title: {
      text: title,
      font: { size: 16, color: '#333' }
    },
    xaxis: {
      type: 'date',
      rangeslider: { visible: false },
      showgrid: true,
      gridcolor: '#f0f0f0'
    },
    yaxis: {
      title: 'Price ($)',
      side: 'left',
      showgrid: true,
      gridcolor: '#f0f0f0'
    },
    yaxis2: {
      title: 'Volume',
      overlaying: 'y',
      side: 'right',
      showgrid: false,
      range: [0, Math.max(...data.map(d => d.volume)) * 4]
    },
    plot_bgcolor: 'white',
    paper_bgcolor: 'white',
    height: height,
    margin: { l: 60, r: 60, t: 40, b: 40 },
    hovermode: 'x unified',
    legend: {
      x: 0,
      y: 1,
      bgcolor: 'rgba(255, 255, 255, 0.8)'
    }
  }), [title, height, data]);

  const config = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
    responsive: true
  };

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box>
        <Plot
          data={chartData}
          layout={layout}
          config={config}
          style={{ width: '100%' }}
        />
      </Box>
    </Paper>
  );
};

export default PlotlyTradingChart;
