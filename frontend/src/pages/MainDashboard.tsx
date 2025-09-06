/**
 * Main Trading Dashboard - NSE Securities Integration
 * Single comprehensive page with all NSE functionality
 */
import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Alert,
  Card,
  CardContent,
  Button,
  TextField,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  Tab,
  Tabs,
} from '@mui/material';
import {
  Search,
  TrendingUp,
  TrendingDown,
  Refresh,
  ShowChart,
  AccountBalance,
  RemoveRedEye,
  Star,
  StarBorder,
  Visibility,
} from '@mui/icons-material';
import { NSESecuritiesService, NSEInstrument, MarketMoversResponse, SectorPerformance } from '../services/nseSecuritiesService';

interface MainDashboardProps {
  mockDataMode: boolean;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
}

const MainDashboard: React.FC<MainDashboardProps> = ({ mockDataMode }) => {
  // State management
  const [currentTab, setCurrentTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<NSEInstrument[]>([]);
  const [selectedStock, setSelectedStock] = useState<NSEInstrument | null>(null);
  const [marketMovers, setMarketMovers] = useState<MarketMoversResponse | null>(null);
  const [sectorPerformance, setSectorPerformance] = useState<SectorPerformance[]>([]);
  const [recentInstruments, setRecentInstruments] = useState<NSEInstrument[]>([]);
  const [watchlist, setWatchlist] = useState<NSEInstrument[]>([]);
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});
  const [error, setError] = useState<string | null>(null);

  // Helper functions
  const setLoadingState = (key: string, isLoading: boolean) => {
    setLoading(prev => ({ ...prev, [key]: isLoading }));
  };

  // Watchlist functions
  const addToWatchlist = (stock: NSEInstrument) => {
    if (!watchlist.find(item => item.id === stock.id)) {
      setWatchlist(prev => [...prev, stock]);
    }
  };

  const removeFromWatchlist = (stockId: number) => {
    setWatchlist(prev => prev.filter(item => item.id !== stockId));
  };

  const isInWatchlist = (stockId: number) => {
    return watchlist.some(item => item.id === stockId);
  };

  // Load initial data
  const loadInitialData = useCallback(async () => {
    try {
      setLoadingState('initial', true);
      
      // Load recent instruments and market data in parallel
      const [instruments, movers, sectors] = await Promise.all([
        NSESecuritiesService.getInstruments({ limit: 10 }),
        NSESecuritiesService.getMarketMovers(),
        NSESecuritiesService.getSectorPerformance(),
      ]);

      setRecentInstruments(instruments);
      setMarketMovers(movers);
      setSectorPerformance(sectors);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load initial data');
    } finally {
      setLoadingState('initial', false);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
    // Load watchlist from localStorage
    const savedWatchlist = localStorage.getItem('gogoTrade_watchlist');
    if (savedWatchlist) {
      try {
        setWatchlist(JSON.parse(savedWatchlist));
      } catch (err) {
        console.error('Failed to load watchlist from localStorage:', err);
      }
    }
  }, [loadInitialData]);

  // Save watchlist to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('gogoTrade_watchlist', JSON.stringify(watchlist));
  }, [watchlist]);  // Search functionality
  const handleSearch = async () => {
    if (!searchQuery.trim() || searchQuery.length < 2) return;
    
    try {
      setLoadingState('search', true);
      const results = await NSESecuritiesService.searchSecurities(searchQuery, 8);
      setSearchResults(results);
    } catch (err) {
      console.error('Search error:', err);
      setSearchResults([]);
    } finally {
      setLoadingState('search', false);
    }
  };

  const handleStockSelect = (stock: NSEInstrument) => {
    setSelectedStock(stock);
    setCurrentTab(0); // Switch to overview tab
  };

  const formatChange = (change: number, isPercentage = false) => {
    const formatted = isPercentage 
      ? `${change > 0 ? '+' : ''}${change.toFixed(2)}%`
      : `${change > 0 ? '+' : ''}${change.toFixed(2)}`;
    return formatted;
  };

  const getChangeColor = (change: number) => {
    return change > 0 ? 'success.main' : change < 0 ? 'error.main' : 'text.secondary';
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const refreshData = () => {
    loadInitialData();
  };

  return (
    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', gap: 2, p: 2 }}>
      {/* Header */}
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              🚀 NSE Securities Trading Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time NSE stock market data with live search, market movers, and sector analysis
            </Typography>
          </Box>
          <IconButton onClick={refreshData} disabled={loading.initial}>
            <Refresh />
          </IconButton>
        </Box>
        
        {mockDataMode && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Using NSE securities database with 43 instruments. Live backend API integration active on port 8001.
          </Alert>
        )}
      </Box>

      {/* Search Bar */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              fullWidth
              placeholder="Search NSE securities (e.g., WIPRO, TITAN, ICICIBANK)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              size="medium"
            />
            <Button 
              variant="contained" 
              onClick={handleSearch}
              disabled={loading.search || searchQuery.length < 2}
              startIcon={loading.search ? <CircularProgress size={20} /> : <Search />}
            >
              Search
            </Button>
          </Box>
          
          {/* Search Results */}
          {searchResults.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Search Results ({searchResults.length})
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {searchResults.map((stock) => (
                  <Box key={stock.id} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Chip
                      label={`${stock.symbol} - ${stock.name}`}
                      clickable
                      onClick={() => handleStockSelect(stock)}
                      variant={selectedStock?.id === stock.id ? 'filled' : 'outlined'}
                      color={selectedStock?.id === stock.id ? 'primary' : 'default'}
                    />
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (isInWatchlist(stock.id)) {
                          removeFromWatchlist(stock.id);
                        } else {
                          addToWatchlist(stock);
                        }
                      }}
                      sx={{ color: isInWatchlist(stock.id) ? 'warning.main' : 'text.secondary' }}
                    >
                      {isInWatchlist(stock.id) ? <Star /> : <StarBorder />}
                    </IconButton>
                  </Box>
                ))}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Main Content Area */}
      <Box sx={{ display: 'flex', gap: 2, flexGrow: 1, overflow: 'hidden' }}>
        {/* Left Panel - Selected Stock Details */}
        <Box sx={{ flex: '1 1 60%', display: 'flex', flexDirection: 'column' }}>
          <Card sx={{ flexGrow: 1 }}>
            <CardContent>
              {selectedStock ? (
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="h5" gutterBottom>
                          {selectedStock.symbol}
                        </Typography>
                        <IconButton
                          onClick={() => {
                            if (isInWatchlist(selectedStock.id)) {
                              removeFromWatchlist(selectedStock.id);
                            } else {
                              addToWatchlist(selectedStock);
                            }
                          }}
                          sx={{ 
                            color: isInWatchlist(selectedStock.id) ? 'warning.main' : 'text.secondary',
                            '&:hover': { color: 'warning.main' }
                          }}
                        >
                          {isInWatchlist(selectedStock.id) ? <Star /> : <StarBorder />}
                        </IconButton>
                      </Box>
                      <Typography variant="body1" color="text.secondary">
                        {selectedStock.name}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip 
                        label={selectedStock.market_segment.replace('_', ' ')} 
                        color="primary" 
                        size="small" 
                      />
                      <Chip 
                        label={selectedStock.sector} 
                        variant="outlined" 
                        size="small" 
                      />
                    </Box>
                  </Box>

                  {/* Tabs for different views */}
                  <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={currentTab} onChange={handleTabChange}>
                      <Tab label="Overview" />
                      <Tab label="Chart" />
                      <Tab label="Details" />
                    </Tabs>
                  </Box>

                  <TabPanel value={currentTab} index={0}>
                    <Box>
                      <Typography variant="h6" gutterBottom>Company Overview</Typography>
                      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">ISIN</Typography>
                          <Typography variant="body1">{selectedStock.isin}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">Market Segment</Typography>
                          <Typography variant="body1">{selectedStock.market_segment.replace('_', ' ')}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">Sector</Typography>
                          <Typography variant="body1">{selectedStock.sector}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">Industry Group</Typography>
                          <Typography variant="body1">{selectedStock.industry_group}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">Face Value</Typography>
                          <Typography variant="body1">₹{selectedStock.face_value}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">Market Lot</Typography>
                          <Typography variant="body1">{selectedStock.market_lot}</Typography>
                        </Box>
                      </Box>
                    </Box>
                  </TabPanel>

                  <TabPanel value={currentTab} index={1}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 200 }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <ShowChart sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary">
                          Chart Integration Ready
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Connect with TradingView or Lightweight Charts for {selectedStock.symbol}
                        </Typography>
                      </Box>
                    </Box>
                  </TabPanel>

                  <TabPanel value={currentTab} index={2}>
                    <Box>
                      <Typography variant="h6" gutterBottom>Technical Details</Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Listed Date: {new Date(selectedStock.listing_date).toLocaleDateString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Created: {new Date(selectedStock.created_at).toLocaleDateString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Last Updated: {new Date(selectedStock.updated_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </TabPanel>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 300 }}>
                  {loading.initial ? (
                    <CircularProgress />
                  ) : (
                    <Box sx={{ textAlign: 'center' }}>
                      <Search sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                      <Typography variant="h6" color="text.secondary">
                        Search for a stock to get started
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Try searching for WIPRO, TITAN, or ICICIBANK
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Right Panel - Market Data */}
        <Box sx={{ flex: '1 1 40%', display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Recent Stocks */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Stocks ({recentInstruments.length})
              </Typography>
              <List dense>
                {recentInstruments.slice(0, 6).map((stock, index) => (
                  <ListItem 
                    key={stock.id} 
                    onClick={() => handleStockSelect(stock)}
                    divider={index < 5}
                    sx={{ cursor: 'pointer', '&:hover': { backgroundColor: 'action.hover' } }}
                  >
                    <ListItemText
                      primary={stock.symbol}
                      secondary={stock.name}
                    />
                    <Chip 
                      label={stock.market_segment.replace('_', ' ')} 
                      size="small" 
                      variant="outlined" 
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Watchlist */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Visibility sx={{ mr: 1, verticalAlign: 'bottom', color: 'primary.main' }} />
                My Watchlist ({watchlist.length})
              </Typography>
              {watchlist.length > 0 ? (
                <List dense>
                  {watchlist.slice(0, 8).map((stock, index) => (
                    <ListItem 
                      key={stock.id} 
                      divider={index < Math.min(7, watchlist.length - 1)}
                      sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                    >
                      <ListItemText
                        primary={stock.symbol}
                        secondary={stock.name}
                        onClick={() => handleStockSelect(stock)}
                        sx={{ cursor: 'pointer', flexGrow: 1, '&:hover': { color: 'primary.main' } }}
                      />
                      <Chip 
                        label={stock.market_segment.replace('_', ' ')} 
                        size="small" 
                        variant="outlined" 
                      />
                      <IconButton
                        size="small"
                        onClick={() => removeFromWatchlist(stock.id)}
                        sx={{ color: 'error.main' }}
                      >
                        <RemoveRedEye />
                      </IconButton>
                    </ListItem>
                  ))}
                  {watchlist.length > 8 && (
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', pt: 1 }}>
                      +{watchlist.length - 8} more stocks
                    </Typography>
                  )}
                </List>
              ) : (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <StarBorder sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Your watchlist is empty
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                    Search for stocks and click the ⭐ to watch them
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Try searching: WIPRO, TITAN, ICICIBANK
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Market Movers */}
          {marketMovers && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Movers
                </Typography>
                
                <Typography variant="subtitle2" color="success.main" gutterBottom>
                  <TrendingUp sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'bottom' }} />
                  Top Gainers
                </Typography>
                {marketMovers.gainers.slice(0, 3).map((stock, index) => (
                  <Box key={stock.symbol} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.5 }}>
                    <Typography variant="body2">{stock.symbol}</Typography>
                    <Typography variant="body2" color="success.main">
                      +{stock.pchange.toFixed(2)}%
                    </Typography>
                  </Box>
                ))}
                
                <Divider sx={{ my: 1 }} />
                
                <Typography variant="subtitle2" color="error.main" gutterBottom>
                  <TrendingDown sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'bottom' }} />
                  Top Losers
                </Typography>
                {marketMovers.losers.slice(0, 3).map((stock, index) => (
                  <Box key={stock.symbol} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.5 }}>
                    <Typography variant="body2">{stock.symbol}</Typography>
                    <Typography variant="body2" color="error.main">
                      {stock.pchange.toFixed(2)}%
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Sector Performance */}
          {sectorPerformance.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <AccountBalance sx={{ fontSize: 20, mr: 0.5, verticalAlign: 'bottom' }} />
                  Sector Performance
                </Typography>
                {sectorPerformance.slice(0, 5).map((sector, index) => (
                  <Box key={sector.id} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.5 }}>
                    <Typography variant="body2">{sector.sector}</Typography>
                    <Typography 
                      variant="body2" 
                      color={getChangeColor(sector.pchange)}
                    >
                      {formatChange(sector.pchange, true)}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default MainDashboard;
