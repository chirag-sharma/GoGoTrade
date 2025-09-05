/**
 * Backtesting Component - React interface for strategy backtesting
 * Allows users to run and analyze trading strategy performance
 */

import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp,
  Analytics,
  Assessment,
  PlayArrow,
  Stop,
  Download
} from '@mui/icons-material';
import axios from 'axios';

interface BacktestRequest {
  symbol: string;
  strategy: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  strategy_params?: any;
}

interface BacktestResults {
  summary: {
    start_date: string;
    end_date: string;
    initial_capital: number;
    final_capital: number;
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    total_pnl: number;
    total_pnl_percent: number;
    sharpe_ratio: number;
    max_drawdown: number;
    avg_trade_duration_days: number;
    best_trade: number;
    worst_trade: number;
  };
  trades: Array<{
    symbol: string;
    entry_price: number;
    exit_price: number;
    quantity: number;
    entry_timestamp: string;
    exit_timestamp: string;
    pnl: number;
    pnl_percent: number;
    hold_duration_days: number;
  }>;
}

const BacktestingComponent: React.FC = () => {
  const [request, setRequest] = useState<BacktestRequest>({
    symbol: 'RELIANCE.NS',
    strategy: 'sma_crossover',
    start_date: '2024-01-01',
    end_date: '2024-12-01',
    initial_capital: 100000,
    strategy_params: {
      short_window: 20,
      long_window: 50
    }
  });

  const [results, setResults] = useState<BacktestResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const availableStrategies = [
    { id: 'sma_crossover', name: 'Simple Moving Average Crossover' },
    { id: 'rsi_strategy', name: 'RSI Mean Reversion' }
  ];

  const availableSymbols = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS', 'ICICIBANK.NS',
    'HDFCBANK.NS', 'KOTAKBANK.NS', 'LT.NS', 'ASIANPAINT.NS', 'MARUTI.NS'
  ];

  const handleRunBacktest = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post('http://localhost:8002/api/v1/backtesting/run', request);
      
      if (response.data.success) {
        setResults(response.data.results);
      } else {
        setError(response.data.error || 'Backtesting failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to connect to backtesting service');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Analytics sx={{ mr: 2, color: 'primary.main' }} />
        <Typography variant="h5" color="primary">
          Strategy Backtesting
        </Typography>
      </Box>

      {/* Configuration Panel */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Symbol</InputLabel>
            <Select
              value={request.symbol}
              label="Symbol"
              onChange={(e) => setRequest({ ...request, symbol: e.target.value })}
            >
              {availableSymbols.map((symbol) => (
                <MenuItem key={symbol} value={symbol}>
                  {symbol}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Strategy</InputLabel>
            <Select
              value={request.strategy}
              label="Strategy"
              onChange={(e) => setRequest({ ...request, strategy: e.target.value })}
            >
              {availableStrategies.map((strategy) => (
                <MenuItem key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            type="date"
            label="Start Date"
            value={request.start_date}
            onChange={(e) => setRequest({ ...request, start_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            type="date"
            label="End Date"
            value={request.end_date}
            onChange={(e) => setRequest({ ...request, end_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            type="number"
            label="Initial Capital (INR)"
            value={request.initial_capital}
            onChange={(e) => setRequest({ ...request, initial_capital: Number(e.target.value) })}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Button
            fullWidth
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
            onClick={handleRunBacktest}
            disabled={loading}
            sx={{ height: '56px' }}
          >
            {loading ? 'Running Backtest...' : 'Run Backtest'}
          </Button>
        </Grid>
      </Grid>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results Display */}
      {results && (
        <>
          {/* Summary Cards */}
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <Assessment sx={{ mr: 1 }} />
            Backtest Results
          </Typography>

          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card sx={{ bgcolor: results.summary.total_pnl >= 0 ? '#e8f5e8' : '#ffebee' }}>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total P&L
                  </Typography>
                  <Typography variant="h5" color={results.summary.total_pnl >= 0 ? 'success.main' : 'error.main'}>
                    {formatCurrency(results.summary.total_pnl)}
                  </Typography>
                  <Typography variant="body2">
                    {formatPercent(results.summary.total_pnl_percent)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Win Rate
                  </Typography>
                  <Typography variant="h5">
                    {results.summary.win_rate.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2">
                    {results.summary.winning_trades}/{results.summary.total_trades} trades
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Sharpe Ratio
                  </Typography>
                  <Typography variant="h5">
                    {results.summary.sharpe_ratio.toFixed(2)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Risk-adjusted return
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Max Drawdown
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    -{results.summary.max_drawdown.toFixed(2)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Maximum loss period
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Detailed Performance */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Initial Capital: {formatCurrency(results.summary.initial_capital)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Final Capital: {formatCurrency(results.summary.final_capital)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Best Trade: {formatCurrency(results.summary.best_trade)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Worst Trade: {formatCurrency(results.summary.worst_trade)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Avg Hold Duration: {results.summary.avg_trade_duration_days} days
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Trades: {results.summary.total_trades}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Trade History */}
          {results.trades.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Trade History (Latest 10)
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Entry Date</TableCell>
                        <TableCell>Exit Date</TableCell>
                        <TableCell>Entry Price</TableCell>
                        <TableCell>Exit Price</TableCell>
                        <TableCell>P&L</TableCell>
                        <TableCell>P&L %</TableCell>
                        <TableCell>Duration</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {results.trades.slice(-10).map((trade, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            {new Date(trade.entry_timestamp).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            {new Date(trade.exit_timestamp).toLocaleDateString()}
                          </TableCell>
                          <TableCell>₹{trade.entry_price.toFixed(2)}</TableCell>
                          <TableCell>₹{trade.exit_price.toFixed(2)}</TableCell>
                          <TableCell>
                            <Chip
                              label={formatCurrency(trade.pnl)}
                              color={trade.pnl >= 0 ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={formatPercent(trade.pnl_percent)}
                              color={trade.pnl_percent >= 0 ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{trade.hold_duration_days} days</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </Paper>
  );
};

export default BacktestingComponent;
