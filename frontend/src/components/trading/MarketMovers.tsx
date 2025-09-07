import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { NSESecuritiesService, MarketMoversResponse } from '../../services/nseSecuritiesService';

const MarketMovers: React.FC = () => {
  const [marketMovers, setMarketMovers] = useState<MarketMoversResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMarketMovers();
  }, []);

  const loadMarketMovers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await NSESecuritiesService.getMarketMovers();
      setMarketMovers(data);
    } catch (err) {
      setError('Failed to load market movers');
      console.error('Market movers error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(price);
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" onClose={() => setError(null)}>
        {error}
      </Alert>
    );
  }

  if (!marketMovers) {
    return (
      <Alert severity="info">
        No market movers data available.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Market Movers
      </Typography>
      
      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {/* Gainers */}
        <Box sx={{ flex: '1 1 300px', minWidth: 300 }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography variant="h6" color="success.main">
                  Top Gainers
                </Typography>
              </Box>
              
              <List dense>
                {marketMovers.gainers.map((stock, index) => (
                  <ListItem key={stock.symbol} divider={index < marketMovers.gainers.length - 1}>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="subtitle2" fontWeight="bold">
                            {stock.symbol}
                          </Typography>
                          <Typography variant="subtitle2" color={getChangeColor(stock.change)}>
                            {formatPrice(stock.last_price)}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2" color="text.secondary" noWrap>
                            {stock.name}
                          </Typography>
                          <Box display="flex" gap={1}>
                            <Chip
                              label={formatChange(stock.change)}
                              size="small"
                              color="success"
                              variant="outlined"
                            />
                            <Chip
                              label={formatChange(stock.pchange, true)}
                              size="small"
                              color="success"
                            />
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Box>

        {/* Losers */}
        <Box sx={{ flex: '1 1 300px', minWidth: 300 }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingDown color="error" sx={{ mr: 1 }} />
                <Typography variant="h6" color="error.main">
                  Top Losers
                </Typography>
              </Box>
              
              <List dense>
                {marketMovers.losers.map((stock, index) => (
                  <ListItem key={stock.symbol} divider={index < marketMovers.losers.length - 1}>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="subtitle2" fontWeight="bold">
                            {stock.symbol}
                          </Typography>
                          <Typography variant="subtitle2" color={getChangeColor(stock.change)}>
                            {formatPrice(stock.last_price)}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2" color="text.secondary" noWrap>
                            {stock.name}
                          </Typography>
                          <Box display="flex" gap={1}>
                            <Chip
                              label={formatChange(stock.change)}
                              size="small"
                              color="error"
                              variant="outlined"
                            />
                            <Chip
                              label={formatChange(stock.pchange, true)}
                              size="small"
                              color="error"
                            />
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default MarketMovers;
