/**
 * NSE Securities Test Page
 * Phase 3 Frontend Integration - Testing NSE Securities API
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
} from '@mui/material';
import {
  Refresh,
  Search,
  TrendingUp,
} from '@mui/icons-material';
import { NSESecuritiesService, NSEInstrument, MarketMoversResponse } from '../services/nseSecuritiesService';

const NSETestPage: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [instruments, setInstruments] = useState<NSEInstrument[]>([]);
  const [marketMovers, setMarketMovers] = useState<MarketMoversResponse | null>(null);
  const [searchResults, setSearchResults] = useState<NSEInstrument[]>([]);
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    const loadHealth = async () => {
      try {
        setLoadingState('health', true);
        setError('health', null);
        const healthData = await NSESecuritiesService.getHealth();
        setHealth(healthData);
      } catch (err) {
        setError('health', 'Failed to connect to backend');
        console.error('Health check error:', err);
      } finally {
        setLoadingState('health', false);
      }
    };
    
    loadHealth();
  }, []);

  const setLoadingState = (key: string, isLoading: boolean) => {
    setLoading(prev => ({ ...prev, [key]: isLoading }));
  };

  const setError = (key: string, error: string | null) => {
    setErrors(prev => ({ ...prev, [key]: error || '' }));
  };

  const loadHealthStatus = async () => {
    try {
      setLoadingState('health', true);
      setError('health', null);
      const healthData = await NSESecuritiesService.getHealth();
      setHealth(healthData);
    } catch (err) {
      setError('health', 'Failed to connect to backend');
      console.error('Health check error:', err);
    } finally {
      setLoadingState('health', false);
    }
  };

  const loadInstruments = async () => {
    try {
      setLoadingState('instruments', true);
      setError('instruments', null);
      const data = await NSESecuritiesService.getInstruments({ limit: 10 });
      setInstruments(data);
    } catch (err) {
      setError('instruments', 'Failed to load instruments');
      console.error('Instruments error:', err);
    } finally {
      setLoadingState('instruments', false);
    }
  };

  const loadMarketMovers = async () => {
    try {
      setLoadingState('movers', true);
      setError('movers', null);
      const data = await NSESecuritiesService.getMarketMovers();
      setMarketMovers(data);
    } catch (err) {
      setError('movers', 'Failed to load market movers');
      console.error('Market movers error:', err);
    } finally {
      setLoadingState('movers', false);
    }
  };

  const searchSecurities = async (query: string) => {
    try {
      setLoadingState('search', true);
      setError('search', null);
      const data = await NSESecuritiesService.searchSecurities(query, 5);
      setSearchResults(data);
    } catch (err) {
      setError('search', 'Failed to search securities');
      console.error('Search error:', err);
    } finally {
      setLoadingState('search', false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(price);
  };

  const getStatusChip = (status: string) => {
    return status === 'healthy' ? (
      <Chip label="Connected" color="success" size="small" />
    ) : (
      <Chip label="Disconnected" color="error" size="small" />
    );
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Typography variant="h4" gutterBottom>
        NSE Securities Integration Test - Phase 3
      </Typography>
      
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Testing backend API integration with NSE securities data
      </Typography>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        {/* Health Status */}
        <Box sx={{ flex: '1 1 300px', minWidth: 300 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Backend Health</Typography>
                <Button
                  startIcon={<Refresh />}
                  onClick={loadHealthStatus}
                  disabled={loading.health}
                  size="small"
                >
                  Refresh
                </Button>
              </Box>
              
              {loading.health && <CircularProgress size={24} />}
              {errors.health && <Alert severity="error">{errors.health}</Alert>}
              {health && (
                <Box>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <Typography variant="body2">Status:</Typography>
                    {getStatusChip(health.status)}
                  </Box>
                  <Typography variant="body2">
                    Database: <strong>{health.database}</strong>
                  </Typography>
                  <Typography variant="body2">
                    Total Instruments: <strong>{health.instruments}</strong>
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Sample Instruments */}
        <Box sx={{ flex: '1 1 300px', minWidth: 300 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Sample Instruments</Typography>
                <Button
                  startIcon={<TrendingUp />}
                  onClick={loadInstruments}
                  disabled={loading.instruments}
                  size="small"
                >
                  Load
                </Button>
              </Box>
              
              {loading.instruments && <CircularProgress size={24} />}
              {errors.instruments && <Alert severity="error">{errors.instruments}</Alert>}
              {instruments.length > 0 && (
                <List dense>
                  {instruments.slice(0, 5).map((instrument, index) => (
                    <ListItem key={instrument.id} divider={index < 4}>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle2" fontWeight="bold">
                              {instrument.symbol}
                            </Typography>
                            <Chip
                              label={instrument.market_segment.replace('_', ' ')}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={
                          <Typography variant="body2" color="text.secondary">
                            {instrument.name} • {instrument.sector}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mt: 3 }}>
        {/* Quick Search */}
        <Box sx={{ flex: '1 1 300px', minWidth: 300 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Search Test
              </Typography>
              
              <Box display="flex" gap={1} mb={2}>
                <Button 
                  variant="outlined" 
                  size="small"
                  startIcon={<Search />}
                  onClick={() => searchSecurities('RELIANCE')}
                  disabled={loading.search}
                >
                  Search "RELIANCE"
                </Button>
                <Button 
                  variant="outlined" 
                  size="small"
                  startIcon={<Search />}
                  onClick={() => searchSecurities('TCS')}
                  disabled={loading.search}
                >
                  Search "TCS"
                </Button>
              </Box>
              
              {loading.search && <CircularProgress size={24} />}
              {errors.search && <Alert severity="error">{errors.search}</Alert>}
              {searchResults.length > 0 && (
                <List dense>
                  {searchResults.map((result, index) => (
                    <ListItem key={result.id} divider={index < searchResults.length - 1}>
                      <ListItemText
                        primary={`${result.symbol} - ${result.name}`}
                        secondary={`${result.sector} • ${result.market_segment}`}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Market Movers */}
        <Box sx={{ flex: '1 1 300px', minWidth: 300 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Market Movers</Typography>
                <Button
                  startIcon={<TrendingUp />}
                  onClick={loadMarketMovers}
                  disabled={loading.movers}
                  size="small"
                >
                  Load
                </Button>
              </Box>
              
              {loading.movers && <CircularProgress size={24} />}
              {errors.movers && <Alert severity="error">{errors.movers}</Alert>}
              {marketMovers && (
                <Box>
                  <Typography variant="subtitle2" color="success.main" gutterBottom>
                    Top Gainers
                  </Typography>
                  <List dense>
                    {marketMovers.gainers.slice(0, 3).map((stock, index) => (
                      <ListItem key={stock.symbol} dense>
                        <ListItemText
                          primary={
                            <Box display="flex" justifyContent="space-between">
                              <Typography variant="body2">{stock.symbol}</Typography>
                              <Typography variant="body2" color="success.main">
                                +{stock.pchange.toFixed(2)}%
                              </Typography>
                            </Box>
                          }
                          secondary={formatPrice(stock.last_price)}
                        />
                      </ListItem>
                    ))}
                  </List>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Typography variant="subtitle2" color="error.main" gutterBottom>
                    Top Losers
                  </Typography>
                  <List dense>
                    {marketMovers.losers.slice(0, 3).map((stock, index) => (
                      <ListItem key={stock.symbol} dense>
                        <ListItemText
                          primary={
                            <Box display="flex" justifyContent="space-between">
                              <Typography variant="body2">{stock.symbol}</Typography>
                              <Typography variant="body2" color="error.main">
                                {stock.pchange.toFixed(2)}%
                              </Typography>
                            </Box>
                          }
                          secondary={formatPrice(stock.last_price)}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Container>
  );
};

export default NSETestPage;
