/**
 * Trading Dashboard Component - AI-Powered with Real-time Data
 * Main dashboard for trading interface with charts, market data, and AI signals
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Paper,
  Box,
  Typography,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Button,
  Badge,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Menu as MenuIcon,
  TrendingUp,
  Analytics,
  Notifications,
  Settings,
  Timeline,
  ShowChart,
  AccountBalance,
  Close as CloseIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

// Import Trading Data Service
import TradingDataService, {
  MarketData,
  TradingSignal,
} from '../../services/tradingDataService';

// Import Trading Chart
import SimpleProfessionalChart from '../charts/SimpleProfessionalChart';

// Utility functions for formatting
const formatPrice = (price: number): string => {
  return `₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

const formatChange = (change: number): string => {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}`;
};

const formatPercentage = (percentage: number): string => {
  const sign = percentage >= 0 ? '+' : '';
  return `${sign}${percentage.toFixed(2)}%`;
};

const getSignalColor = (signalType: string): string => {
  switch (signalType) {
    case 'BUY': return '#4caf50'; // Green
    case 'SELL': return '#f44336'; // Red
    case 'HOLD': return '#ff9800'; // Orange
    default: return '#9e9e9e'; // Gray
  }
};

const getSignalIcon = (signalType: string): string => {
  switch (signalType) {
    case 'BUY': return '🟢';
    case 'SELL': return '🔴';
    case 'HOLD': return '🟡';
    default: return '⚪';
  }
};

const DRAWER_WIDTH = 300;

const TradingDashboard: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [tradingSignals, setTradingSignals] = useState<TradingSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

    // Fetch real-time data from Trading APIs
  const fetchData = useCallback(async () => {
    const defaultSymbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK'];
    
    try {
      setLoading(true);
      setError(null);

      // Fetch market data and trading signals separately using new API structure
      const marketDataPromises = defaultSymbols.map(symbol => 
        TradingDataService.getMarketData(symbol).catch(error => {
          console.warn(`Failed to fetch market data for ${symbol}:`, error);
          return null;
        })
      );
      
      const signalsPromises = defaultSymbols.map(symbol => 
        TradingDataService.getTradingSignals(symbol).catch(error => {
          console.warn(`Failed to fetch signals for ${symbol}:`, error);
          return [];
        })
      );

      const [marketDataResults, signalResults] = await Promise.all([
        Promise.all(marketDataPromises),
        Promise.all(signalsPromises)
      ]);

      // Filter out null results and flatten arrays
      const validMarketData = marketDataResults.filter(data => data !== null) as MarketData[];
      const allSignals = signalResults.flat();

      setMarketData(validMarketData);
      setTradingSignals(allSignals);
      setLastUpdated(new Date().toLocaleTimeString());
      
    } catch (err) {
      console.error('Error fetching trading data:', err);
      setError('Failed to connect to Trading Service');
      
      // Provide basic fallback data structure
      setMarketData([]);
      setTradingSignals([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch and auto-refresh
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [fetchData]);

  const handleSymbolChange = (event: SelectChangeEvent) => {
    setSelectedSymbol(event.target.value);
  };

  const sidebarContent = (
    <Box sx={{ width: DRAWER_WIDTH, height: '100%', bgcolor: 'background.default' }}>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6" color="primary">
          Trading Tools
        </Typography>
        <IconButton onClick={() => setSidebarOpen(false)}>
          <CloseIcon />
        </IconButton>
      </Box>
      <Divider />
      
      <List>
        <ListItemButton>
          <ListItemIcon><TrendingUp color="primary" /></ListItemIcon>
          <ListItemText primary="Market Overview" />
        </ListItemButton>
        
        <ListItemButton>
          <ListItemIcon><ShowChart color="secondary" /></ListItemIcon>
          <ListItemText primary="Chart Analysis" />
        </ListItemButton>
        
        <ListItemButton>
          <ListItemIcon><Analytics color="info" /></ListItemIcon>
          <ListItemText primary="Technical Indicators" />
        </ListItemButton>
        
        <ListItemButton>
          <ListItemIcon><AccountBalance color="success" /></ListItemIcon>
          <ListItemText primary="Portfolio" />
        </ListItemButton>
        
        <Divider sx={{ my: 2 }} />
        
        <ListItemButton>
          <ListItemIcon>
            <Badge badgeContent={3} color="error">
              <Notifications />
            </Badge>
          </ListItemIcon>
          <ListItemText primary="Notifications" />
        </ListItemButton>
        
        <ListItemButton>
          <ListItemIcon><Settings /></ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItemButton>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: 'background.default' }}>
      {/* Top App Bar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            onClick={() => setSidebarOpen(true)}
            edge="start"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            🚀 GoGoTrade - AI Trading Platform
          </Typography>
          
          {loading ? (
            <CircularProgress size={24} sx={{ color: 'white', mr: 2 }} />
          ) : error ? (
            <Chip 
              label="API: Disconnected"
              color="error"
              size="small"
              sx={{ mr: 2 }}
            />
          ) : (
            <Chip 
              label={`AI Connected • ${lastUpdated}`}
              color="success"
              size="small"
              sx={{ mr: 2 }}
            />
          )}
          
          <IconButton color="inherit" onClick={fetchData} sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
          
          <FormControl size="small" sx={{ minWidth: 120, mr: 2 }}>
            <InputLabel sx={{ color: 'white' }}>Symbol</InputLabel>
            <Select
              value={selectedSymbol}
              onChange={handleSymbolChange}
              sx={{ color: 'white', '.MuiOutlinedInput-notchedOutline': { borderColor: 'white' } }}
            >
              {marketData.map((stock) => (
                <MenuItem key={stock.symbol} value={stock.symbol}>
                  {stock.symbol}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Toolbar>
      </AppBar>

      {/* Sidebar Drawer */}
      <Drawer
        anchor="left"
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        sx={{
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
          },
        }}
      >
        {sidebarContent}
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8, // Account for AppBar height
          bgcolor: 'background.default',
        }}
      >
        {error && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            {error} - Showing fallback data. Check if the AI backend is running.
          </Alert>
        )}
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Market Data Cards */}
          <Box>
            <Typography variant="h5" gutterBottom color="primary">
              Market Overview {loading && <CircularProgress size={20} />}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {marketData.map((stock) => (
              <Card 
                key={stock.symbol}
                sx={{ 
                  bgcolor: 'background.paper',
                  border: selectedSymbol === stock.symbol ? 2 : 0,
                  borderColor: 'primary.main',
                  cursor: 'pointer',
                  minWidth: 200,
                  flex: '1 1 auto',
                  '&:hover': { elevation: 8 }
                }}
                onClick={() => setSelectedSymbol(stock.symbol)}
              >
                <CardContent>
                  <Typography variant="h6" color="primary">
                    {stock.symbol}
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                    {formatPrice(stock.lastPrice)}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography 
                      variant="body2" 
                      color={stock.change >= 0 ? 'success.main' : 'error.main'}
                    >
                      {formatChange(stock.change)}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color={stock.changePercent >= 0 ? 'success.main' : 'error.main'}
                    >
                      ({formatPercentage(stock.changePercent)})
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    Vol: {stock.volume.toLocaleString('en-IN')}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Box>

          {/* Chart and Signals Section */}
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
            {/* Chart Section */}
            <Box sx={{ flex: '2 1 0', minWidth: 0 }}>
              {/* Professional Trading Chart */}
              <SimpleProfessionalChart
                symbol={selectedSymbol}
                signals={[]} // Temporarily disable signals until interface is fixed
                onSymbolChange={setSelectedSymbol}
              />
            </Box>

            {/* Trading Signals */}
            <Box sx={{ flex: '1 1 0', minWidth: 300 }}>
              <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
                <Typography variant="h6" gutterBottom color="primary">
                  🤖 AI Trading Signals
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {tradingSignals.length > 0 ? (
                    tradingSignals.map((signal, index) => (
                      <Card 
                        key={index}
                        sx={{ 
                          bgcolor: getSignalColor(signal.signalType) + '20',
                          border: 1,
                          borderColor: getSignalColor(signal.signalType)
                        }}
                      >
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Typography variant="h6">
                              {getSignalIcon(signal.signalType)}
                            </Typography>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {signal.signalType} {signal.symbol}
                            </Typography>
                            <Chip 
                              label={`${(signal.confidence * 100).toFixed(0)}%`}
                              size="small"
                              color={signal.confidence > 0.8 ? 'success' : signal.confidence > 0.6 ? 'warning' : 'default'}
                            />
                          </Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            Strategy: {signal.strategy}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 2, fontSize: '0.875rem' }}>
                            {signal.targetPrice && (
                              <Typography variant="caption" color="success.main">
                                Target: {formatPrice(signal.targetPrice)}
                              </Typography>
                            )}
                            {signal.stopLoss && (
                              <Typography variant="caption" color="error.main">
                                Stop: {formatPrice(signal.stopLoss)}
                              </Typography>
                            )}
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(signal.timestamp).toLocaleString()}
                          </Typography>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <Card sx={{ bgcolor: 'background.default' }}>
                      <CardContent>
                        <Typography variant="body2" color="text.secondary" textAlign="center">
                          {loading ? 'Loading AI signals...' : 'No trading signals available'}
                        </Typography>
                      </CardContent>
                    </Card>
                  )}
                </Box>

                {/* Trading Statistics */}
                <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    📊 Trading Statistics
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                    <Box>
                      <Typography variant="caption">Symbols Tracked</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {marketData.length}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Active Signals</Typography>
                      <Typography variant="body2" fontWeight="bold" color="primary.main">
                        {tradingSignals.length}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Buy Signals</Typography>
                      <Typography variant="body2" fontWeight="bold" color="success.main">
                        {tradingSignals.filter(s => s.signalType === 'BUY').length}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Sell Signals</Typography>
                      <Typography variant="body2" fontWeight="bold" color="error.main">
                        {tradingSignals.filter(s => s.signalType === 'SELL').length}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Paper>
            </Box>
          </Box>

          {/* Quick Actions */}
          <Box>
            <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
              <Typography variant="h6" gutterBottom color="primary">
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button variant="contained" color="success" startIcon={<TrendingUp />}>
                  Buy {selectedSymbol}
                </Button>
                <Button variant="contained" color="error" startIcon={<TrendingUp sx={{ transform: 'rotate(180deg)' }} />}>
                  Sell {selectedSymbol}
                </Button>
                <Button variant="outlined" startIcon={<Analytics />}>
                  Technical Analysis
                </Button>
                <Button variant="outlined" startIcon={<Timeline />}>
                  View History
                </Button>
              </Box>
            </Paper>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default TradingDashboard;
