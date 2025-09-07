import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  Paper,
  Divider,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Assessment,
  Code,
  TrendingUp,
} from '@mui/icons-material';

interface BacktestingPageProps {
  mockDataMode: boolean;
}

const BacktestingPage: React.FC<BacktestingPageProps> = ({ mockDataMode }) => {
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const predefinedStrategies = [
    { value: 'sma_crossover', label: 'SMA Crossover' },
    { value: 'rsi_strategy', label: 'RSI Strategy' },
    { value: 'bollinger_bands', label: 'Bollinger Bands' },
    { value: 'macd_strategy', label: 'MACD Strategy' },
  ];

  const handleRunBacktest = async () => {
    setIsRunning(true);
    
    // Simulate backtesting process
    setTimeout(() => {
      setResults({
        totalReturn: 15.67,
        sharpeRatio: 1.34,
        maxDrawdown: -8.45,
        winRate: 68.5,
        totalTrades: 127,
        avgReturn: 0.85,
      });
      setIsRunning(false);
    }, 3000);
  };

  return (
    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Header */}
      <Box>
        <Typography variant="h4" component="h1" gutterBottom>
          Strategy Backtesting
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Test trading strategies against historical data and analyze performance
        </Typography>
        
        {mockDataMode && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Using mock historical data for backtesting
          </Alert>
        )}
      </Box>

      <Grid container spacing={3} sx={{ flexGrow: 1 }}>
        {/* Strategy Configuration */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card elevation={2} sx={{ height: 'fit-content' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Strategy Configuration
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Select Strategy</InputLabel>
                  <Select
                    value={selectedStrategy}
                    label="Select Strategy"
                    onChange={(e) => setSelectedStrategy(e.target.value)}
                  >
                    {predefinedStrategies.map((strategy) => (
                      <MenuItem key={strategy.value} value={strategy.value}>
                        {strategy.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <TextField
                  label="Symbol"
                  defaultValue="NIFTY"
                  fullWidth
                />

                <TextField
                  label="Start Date"
                  type="date"
                  defaultValue="2023-01-01"
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                />

                <TextField
                  label="End Date"
                  type="date"
                  defaultValue="2024-01-01"
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                />

                <TextField
                  label="Initial Capital"
                  type="number"
                  defaultValue="100000"
                  fullWidth
                />

                <Button
                  variant="contained"
                  size="large"
                  startIcon={isRunning ? <Stop /> : <PlayArrow />}
                  onClick={handleRunBacktest}
                  disabled={!selectedStrategy || isRunning}
                  fullWidth
                >
                  {isRunning ? 'Running...' : 'Run Backtest'}
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Custom Strategy Builder - Priority Feature */}
          <Card elevation={2} sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Code />
                Custom Strategy Builder
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Create and test your own trading strategies
              </Typography>
              
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Code />}
                sx={{ mt: 2 }}
              >
                Build Custom Strategy
              </Button>
              
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="caption">
                  <strong>Coming Soon:</strong> Visual strategy builder with drag-drop indicators and code editor
                </Typography>
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Panel */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Assessment />
                Backtest Results
              </Typography>
              
              {!results && !isRunning && (
                <Box
                  sx={{
                    flexGrow: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexDirection: 'column',
                    gap: 2,
                  }}
                >
                  <TrendingUp sx={{ fontSize: 64, color: 'text.secondary' }} />
                  <Typography variant="h6" color="text.secondary">
                    Select a strategy and run backtest to see results
                  </Typography>
                </Box>
              )}

              {isRunning && (
                <Box
                  sx={{
                    flexGrow: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexDirection: 'column',
                    gap: 2,
                  }}
                >
                  <Typography variant="h6">Running Backtest...</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Analyzing historical data and executing strategy
                  </Typography>
                </Box>
              )}

              {results && (
                <Box sx={{ flexGrow: 1 }}>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid size={{ xs: 6, md: 3 }}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="success.main">
                          {results.totalReturn}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Total Return
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid size={{ xs: 6, md: 3 }}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="primary.main">
                          {results.sharpeRatio}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Sharpe Ratio
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid size={{ xs: 6, md: 3 }}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="error.main">
                          {results.maxDrawdown}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Max Drawdown
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid size={{ xs: 6, md: 3 }}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="warning.main">
                          {results.winRate}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Win Rate
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>

                  <Divider sx={{ my: 2 }} />

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body1">
                      <strong>Total Trades:</strong> {results.totalTrades}
                    </Typography>
                    <Typography variant="body1">
                      <strong>Avg Return per Trade:</strong> {results.avgReturn}%
                    </Typography>
                  </Box>

                  <Alert severity="success">
                    Strategy shows profitable performance with acceptable risk metrics
                  </Alert>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BacktestingPage;
