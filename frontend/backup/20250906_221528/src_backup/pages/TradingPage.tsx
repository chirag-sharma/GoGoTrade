import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  History,
  Add,
} from '@mui/icons-material';

interface TradingPageProps {
  mockDataMode: boolean;
}

interface Position {
  id: string;
  symbol: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
}

interface Trade {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  timestamp: Date;
  status: 'FILLED' | 'PENDING' | 'CANCELLED';
}

const TradingPage: React.FC<TradingPageProps> = ({ mockDataMode }) => {
  const [positions] = useState<Position[]>([
    {
      id: '1',
      symbol: 'NIFTY',
      quantity: 50,
      avgPrice: 18400,
      currentPrice: 18750,
      pnl: 17500,
      pnlPercent: 1.9,
    },
    {
      id: '2',
      symbol: 'RELIANCE.NS',
      quantity: 25,
      avgPrice: 2500,
      currentPrice: 2480,
      pnl: -500,
      pnlPercent: -0.8,
    },
    {
      id: '3',
      symbol: 'TCS.NS',
      quantity: 10,
      avgPrice: 3800,
      currentPrice: 3850,
      pnl: 500,
      pnlPercent: 1.3,
    },
  ]);

  const [trades] = useState<Trade[]>([
    {
      id: '1',
      symbol: 'NIFTY',
      side: 'BUY',
      quantity: 50,
      price: 18400,
      timestamp: new Date(),
      status: 'FILLED',
    },
    {
      id: '2',
      symbol: 'RELIANCE.NS',
      side: 'BUY',
      quantity: 25,
      price: 2500,
      timestamp: new Date(Date.now() - 3600000),
      status: 'FILLED',
    },
    {
      id: '3',
      symbol: 'TCS.NS',
      side: 'SELL',
      quantity: 5,
      price: 3820,
      timestamp: new Date(Date.now() - 7200000),
      status: 'FILLED',
    },
  ]);

  const [orderForm, setOrderForm] = useState({
    symbol: '',
    side: 'BUY',
    quantity: '',
    price: '',
  });

  const totalPnL = positions.reduce((sum, position) => sum + position.pnl, 0);
  const portfolioValue = 500000; // Mock portfolio value

  const handlePlaceOrder = () => {
    // Mock order placement
    console.log('Placing order:', orderForm);
    // Reset form
    setOrderForm({ symbol: '', side: 'BUY', quantity: '', price: '' });
  };

  return (
    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Header */}
      <Box>
        <Typography variant="h4" component="h1" gutterBottom>
          Trading Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Monitor positions, place orders, and track trading performance
        </Typography>
        
        {mockDataMode && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Trading in simulation mode - no real orders will be placed
          </Alert>
        )}
      </Box>

      {/* Portfolio Summary */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 3 }}>
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center' }}>
              <AccountBalance sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4">
                ₹{portfolioValue.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Portfolio Value
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 3 }}>
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center' }}>
              {totalPnL >= 0 ? (
                <TrendingUp sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              ) : (
                <TrendingDown sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
              )}
              <Typography variant="h4" color={totalPnL >= 0 ? 'success.main' : 'error.main'}>
                ₹{totalPnL.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total P&L
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 3 }}>
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4">
                {positions.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Open Positions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 3 }}>
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4">
                {trades.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Trades
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ flexGrow: 1 }}>
        {/* Order Form */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Add />
                Place Order
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="Symbol"
                  value={orderForm.symbol}
                  onChange={(e) => setOrderForm(prev => ({ ...prev, symbol: e.target.value }))}
                  placeholder="e.g., NIFTY, RELIANCE.NS"
                  fullWidth
                />

                <FormControl fullWidth>
                  <InputLabel>Side</InputLabel>
                  <Select
                    value={orderForm.side}
                    label="Side"
                    onChange={(e) => setOrderForm(prev => ({ ...prev, side: e.target.value as 'BUY' | 'SELL' }))}
                  >
                    <MenuItem value="BUY">BUY</MenuItem>
                    <MenuItem value="SELL">SELL</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  label="Quantity"
                  type="number"
                  value={orderForm.quantity}
                  onChange={(e) => setOrderForm(prev => ({ ...prev, quantity: e.target.value }))}
                  fullWidth
                />

                <TextField
                  label="Price"
                  type="number"
                  value={orderForm.price}
                  onChange={(e) => setOrderForm(prev => ({ ...prev, price: e.target.value }))}
                  fullWidth
                />

                <Button
                  variant="contained"
                  size="large"
                  onClick={handlePlaceOrder}
                  disabled={!orderForm.symbol || !orderForm.quantity || !orderForm.price}
                  color={orderForm.side === 'BUY' ? 'success' : 'error'}
                  fullWidth
                >
                  Place {orderForm.side} Order
                </Button>
              </Box>

              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="caption">
                  Orders are simulated in demo mode
                </Typography>
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Positions and Trades */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
            {/* Positions */}
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Open Positions
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell align="right">Quantity</TableCell>
                        <TableCell align="right">Avg Price</TableCell>
                        <TableCell align="right">Current Price</TableCell>
                        <TableCell align="right">P&L</TableCell>
                        <TableCell align="right">P&L %</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {positions.map((position) => (
                        <TableRow key={position.id}>
                          <TableCell>{position.symbol}</TableCell>
                          <TableCell align="right">{position.quantity}</TableCell>
                          <TableCell align="right">₹{position.avgPrice}</TableCell>
                          <TableCell align="right">₹{position.currentPrice}</TableCell>
                          <TableCell align="right">
                            <Typography color={position.pnl >= 0 ? 'success.main' : 'error.main'}>
                              ₹{position.pnl.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Chip
                              label={`${position.pnlPercent > 0 ? '+' : ''}${position.pnlPercent}%`}
                              color={position.pnl >= 0 ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>

            {/* Trade History */}
            <Card elevation={2} sx={{ flexGrow: 1 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <History />
                  Trade History
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Side</TableCell>
                        <TableCell align="right">Quantity</TableCell>
                        <TableCell align="right">Price</TableCell>
                        <TableCell>Time</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {trades.map((trade) => (
                        <TableRow key={trade.id}>
                          <TableCell>{trade.symbol}</TableCell>
                          <TableCell>
                            <Chip
                              label={trade.side}
                              color={trade.side === 'BUY' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="right">{trade.quantity}</TableCell>
                          <TableCell align="right">₹{trade.price}</TableCell>
                          <TableCell>{trade.timestamp.toLocaleTimeString()}</TableCell>
                          <TableCell>
                            <Chip
                              label={trade.status}
                              color={trade.status === 'FILLED' ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TradingPage;
