import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Divider,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Psychology,
  Analytics,
  Info,
} from '@mui/icons-material';

interface AIInsightsProps {
  mockDataMode: boolean;
}

interface TradingSignal {
  id: string;
  type: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  symbol: string;
  reason: string;
  timestamp: Date;
  price: number;
}

interface MarketSentiment {
  overall: 'bullish' | 'bearish' | 'neutral';
  score: number;
  factors: string[];
}

const AIInsights: React.FC<AIInsightsProps> = ({ mockDataMode }) => {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [sentiment, setSentiment] = useState<MarketSentiment | null>(null);
  const [loading, setLoading] = useState(true);

  // Mock data for development
  const generateMockSignals = (): TradingSignal[] => [
    {
      id: '1',
      type: 'BUY',
      confidence: 85,
      symbol: 'NIFTY',
      reason: 'Strong technical breakout above resistance',
      timestamp: new Date(),
      price: 18750,
    },
    {
      id: '2',
      type: 'SELL',
      confidence: 72,
      symbol: 'RELIANCE.NS',
      reason: 'Bearish divergence in RSI',
      timestamp: new Date(Date.now() - 300000),
      price: 2480,
    },
    {
      id: '3',
      type: 'HOLD',
      confidence: 60,
      symbol: 'TCS.NS',
      reason: 'Sideways consolidation pattern',
      timestamp: new Date(Date.now() - 600000),
      price: 3850,
    },
  ];

  const generateMockSentiment = (): MarketSentiment => ({
    overall: 'bullish',
    score: 75,
    factors: [
      'Strong institutional buying',
      'Positive earnings outlook',
      'Favorable technical indicators',
      'Reduced volatility',
    ],
  });

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      
      if (mockDataMode) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        setSignals(generateMockSignals());
        setSentiment(generateMockSentiment());
      } else {
        // TODO: Fetch real data from API
        try {
          // const response = await fetch('/api/v1/ai-trading/signals');
          // const data = await response.json();
          // setSignals(data.signals);
          // setSentiment(data.sentiment);
        } catch (error) {
          console.error('Error fetching AI insights:', error);
        }
      }
      
      setLoading(false);
    };

    loadData();
  }, [mockDataMode]);

  const getSignalIcon = (type: TradingSignal['type']) => {
    switch (type) {
      case 'BUY':
        return <TrendingUp color="success" />;
      case 'SELL':
        return <TrendingDown color="error" />;
      case 'HOLD':
        return <TrendingFlat color="warning" />;
      default:
        return <Info />;
    }
  };

  const getSignalColor = (type: TradingSignal['type']) => {
    switch (type) {
      case 'BUY':
        return 'success';
      case 'SELL':
        return 'error';
      case 'HOLD':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getSentimentIcon = (sentiment: MarketSentiment['overall']) => {
    switch (sentiment) {
      case 'bullish':
        return <TrendingUp color="success" />;
      case 'bearish':
        return <TrendingDown color="error" />;
      case 'neutral':
        return <TrendingFlat color="warning" />;
      default:
        return <Info />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Loading AI insights...
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
      {/* Market Sentiment */}
      {sentiment && (
        <Card elevation={1}>
          <CardContent sx={{ pb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Psychology sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6" component="h3">
                Market Sentiment
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              {getSentimentIcon(sentiment.overall)}
              <Typography variant="subtitle1" textTransform="capitalize">
                {sentiment.overall}
              </Typography>
              <Chip
                label={`${sentiment.score}%`}
                size="small"
                color={sentiment.overall === 'bullish' ? 'success' : sentiment.overall === 'bearish' ? 'error' : 'warning'}
              />
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Confidence Score
              </Typography>
              <LinearProgress
                variant="determinate"
                value={sentiment.score}
                color={sentiment.overall === 'bullish' ? 'success' : sentiment.overall === 'bearish' ? 'error' : 'warning'}
                sx={{ height: 8, borderRadius: 1 }}
              />
            </Box>
            
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Key Factors
              </Typography>
              {sentiment.factors.map((factor, index) => (
                <Chip
                  key={index}
                  label={factor}
                  size="small"
                  variant="outlined"
                  sx={{ mr: 0.5, mb: 0.5 }}
                />
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Trading Signals */}
      <Card elevation={1} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ pb: 1, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Analytics sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h3">
              Trading Signals
            </Typography>
          </Box>
          
          {signals.length === 0 ? (
            <Alert severity="info" sx={{ mt: 1 }}>
              No trading signals available at the moment.
            </Alert>
          ) : (
            <List sx={{ flexGrow: 1, overflow: 'auto', p: 0 }}>
              {signals.map((signal, index) => (
                <React.Fragment key={signal.id}>
                  <ListItem sx={{ px: 0, alignItems: 'flex-start' }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Avatar
                        sx={{
                          width: 32,
                          height: 32,
                          bgcolor: `${getSignalColor(signal.type)}.light`,
                        }}
                      >
                        {getSignalIcon(signal.type)}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Chip
                            label={signal.type}
                            size="small"
                            color={getSignalColor(signal.type) as any}
                          />
                          <Typography variant="subtitle2">
                            {signal.symbol}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {signal.confidence}%
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" sx={{ mb: 0.5 }}>
                            {signal.reason}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ₹{signal.price.toLocaleString()} • {signal.timestamp.toLocaleTimeString()}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < signals.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {mockDataMode && (
        <Alert severity="info" sx={{ mt: 1 }}>
          <Typography variant="caption">
            Displaying mock AI insights for development
          </Typography>
        </Alert>
      )}
    </Box>
  );
};

export default AIInsights;
