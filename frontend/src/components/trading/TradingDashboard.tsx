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

// Import AI Trading Service
import {
  aiTradingService,
  MarketDataItem,
  TradingSignal,
  DashboardData,
  formatPrice,
  formatChange,
  formatPercentage,
  getSignalColor,
  getSignalIcon,
} from '../../services/aiTradingService';

// Import Trading Chart
import TradingChart from '../charts/SimpleTradingChart';

const DRAWER_WIDTH = 300;

const TradingDashboard: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE.NS');
  const [marketData, setMarketData] = useState<MarketDataItem[]>([]);
  const [tradingSignals, setTradingSignals] = useState<TradingSignal[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  // Fetch real-time data from AI Trading APIs
  const fetchData = useCallback(async () => {
    const defaultSymbols = ['NIFTY', 'SENSEX', 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'];
    
    try {
      setLoading(true);
      setError(null);

      // Fetch comprehensive dashboard data from AI backend
      const data = await aiTradingService.getDashboardData(defaultSymbols);
      
      setDashboardData(data);
      setMarketData(data.marketData);
      setTradingSignals(data.signals);
      setLastUpdated(new Date().toLocaleTimeString());
      
    } catch (err) {
      console.error('Error fetching AI data:', err);
      setError('Failed to connect to AI Trading Service');
      
      // Use safe fallback methods with mock data
      try {
        const fallbackMarketData = await aiTradingService.getMarketDataSafe(defaultSymbols);
        const fallbackSignals = await aiTradingService.getTradingSignalsSafe(defaultSymbols);
        
        setMarketData(fallbackMarketData);
        setTradingSignals(fallbackSignals);
        setLastUpdated(new Date().toLocaleTimeString() + ' (Mock Data)');
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
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
                    {formatPrice(stock.price)}
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
                  {/* Show high/low if available */}
                  {stock.high && stock.low && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        H: {formatPrice(stock.high)} | L: {formatPrice(stock.low)}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            ))}
          </Box>

          {/* Chart and Signals Section */}
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
            {/* Chart Section */}
            <Box sx={{ flex: '2 1 0', minWidth: 0 }}>
              {/* Professional Trading Chart */}
              <TradingChart
                symbol={selectedSymbol}
                signals={tradingSignals.filter(signal => signal.symbol === selectedSymbol)}
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
                            {signal.reason}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 2, fontSize: '0.875rem' }}>
                            <Typography variant="caption">
                              Price: {formatPrice(signal.price)}
                            </Typography>
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

                {/* Dashboard Summary */}
                {dashboardData?.summary && (
                  <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      📊 Market Summary
                    </Typography>
                    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                      <Box>
                        <Typography variant="caption">Symbols Tracked</Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {dashboardData.summary.totalSymbols}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption">Market Sentiment</Typography>
                        <Typography variant="body2" fontWeight="bold" color={
                          dashboardData.summary.marketSentiment === 'bullish' ? 'success.main' :
                          dashboardData.summary.marketSentiment === 'bearish' ? 'error.main' : 'warning.main'
                        }>
                          {dashboardData.summary.marketSentiment.toUpperCase()}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption">Buy Signals</Typography>
                        <Typography variant="body2" fontWeight="bold" color="success.main">
                          {dashboardData.summary.buySignals}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption">Sell Signals</Typography>
                        <Typography variant="body2" fontWeight="bold" color="error.main">
                          {dashboardData.summary.sellSignals}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                )}
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
