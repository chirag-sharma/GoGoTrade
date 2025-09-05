import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TimelineIcon from '@mui/icons-material/Timeline';
import PsychologyIcon from '@mui/icons-material/Psychology';

// Types
interface AISignal {
  id: string;
  symbol: string;
  signal_type: string;
  strength: number;
  confidence: number;
  timestamp: string;
  price_target?: number;
  stop_loss?: number;
  model_type: string;
}

interface MarketSentiment {
  symbol: string;
  overall_score: number;
  news_sentiment: number;
  social_sentiment: number;
  institutional_sentiment?: number;
}

interface ModelPerformance {
  model_id: string;
  accuracy: number;
  precision: number;
  recall: number;
  last_updated: string;
}

const AdvancedAIComponent: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE.NS');
  const [activeTab, setActiveTab] = useState(0);
  const [aiSignals, setAiSignals] = useState<AISignal[]>([]);
  const [sentiment, setSentiment] = useState<MarketSentiment | null>(null);
  const [modelPerformance, setModelPerformance] = useState<Record<string, ModelPerformance>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Symbols for dropdown
  const symbols = [
    { value: 'RELIANCE.NS', label: 'Reliance Industries' },
    { value: 'TCS.NS', label: 'Tata Consultancy Services' },
    { value: 'HDFCBANK.NS', label: 'HDFC Bank' },
    { value: 'INFY.NS', label: 'Infosys' },
    { value: 'HINDUNILVR.NS', label: 'Hindustan Unilever' },
    { value: 'ICICIBANK.NS', label: 'ICICI Bank' },
    { value: 'SBIN.NS', label: 'State Bank of India' },
    { value: 'BHARTIARTL.NS', label: 'Bharti Airtel' },
    { value: 'ITC.NS', label: 'ITC Limited' },
    { value: 'KOTAKBANK.NS', label: 'Kotak Mahindra Bank' }
  ];

  // Mock data generation functions
  const generateMockSignals = useCallback((): AISignal[] => {
    return [
      {
        id: '1',
        symbol: selectedSymbol,
        signal_type: 'BUY',
        strength: 0.85,
        confidence: 0.92,
        timestamp: new Date().toISOString(),
        price_target: 2450,
        stop_loss: 2350,
        model_type: 'LSTM Neural Network'
      },
      {
        id: '2',
        symbol: selectedSymbol,
        signal_type: 'HOLD',
        strength: 0.65,
        confidence: 0.78,
        timestamp: new Date(Date.now() - 300000).toISOString(),
        model_type: 'CNN Pattern Recognition'
      },
      {
        id: '3',
        symbol: selectedSymbol,
        signal_type: 'SELL',
        strength: 0.72,
        confidence: 0.85,
        timestamp: new Date(Date.now() - 600000).toISOString(),
        price_target: 2380,
        stop_loss: 2420,
        model_type: 'Ensemble Model'
      },
      {
        id: '4',
        symbol: selectedSymbol,
        signal_type: 'BUY',
        strength: 0.90,
        confidence: 0.95,
        timestamp: new Date(Date.now() - 900000).toISOString(),
        price_target: 2500,
        stop_loss: 2300,
        model_type: 'Sentiment Analysis AI'
      }
    ];
  }, [selectedSymbol]);

  const generateMockSentiment = useCallback((): MarketSentiment => {
    return {
      symbol: selectedSymbol,
      overall_score: 0.72,
      news_sentiment: 0.68,
      social_sentiment: 0.75,
      institutional_sentiment: 0.73
    };
  }, [selectedSymbol]);

  const generateMockPerformance = useCallback((): Record<string, ModelPerformance> => {
    return {
      'lstm_neural_network': {
        model_id: 'lstm_neural_network',
        accuracy: 0.87,
        precision: 0.84,
        recall: 0.89,
        last_updated: new Date().toISOString()
      },
      'cnn_pattern_recognition': {
        model_id: 'cnn_pattern_recognition',
        accuracy: 0.82,
        precision: 0.80,
        recall: 0.85,
        last_updated: new Date().toISOString()
      },
      'ensemble_model': {
        model_id: 'ensemble_model',
        accuracy: 0.91,
        precision: 0.88,
        recall: 0.93,
        last_updated: new Date().toISOString()
      },
      'sentiment_analysis_ai': {
        model_id: 'sentiment_analysis_ai',
        accuracy: 0.79,
        precision: 0.76,
        recall: 0.81,
        last_updated: new Date().toISOString()
      }
    };
  }, []);

  // Data loading effect
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Simulate API calls with mock data
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        setAiSignals(generateMockSignals());
        setSentiment(generateMockSentiment());
        setModelPerformance(generateMockPerformance());
      } catch (err) {
        setError('Failed to load AI data. Using mock data for demonstration.');
        // Still show mock data on error
        setAiSignals(generateMockSignals());
        setSentiment(generateMockSentiment());
        setModelPerformance(generateMockPerformance());
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [selectedSymbol, generateMockSignals, generateMockSentiment, generateMockPerformance]);

  // Helper functions
  const getSignalColor = (signalType: string) => {
    switch (signalType.toLowerCase()) {
      case 'buy': return '#4caf50';
      case 'sell': return '#f44336';
      case 'hold': return '#ff9800';
      default: return '#757575';
    }
  };

  const getSignalIcon = (signalType: string) => {
    switch (signalType.toLowerCase()) {
      case 'buy': return <TrendingUpIcon />;
      case 'sell': return <TrendingDownIcon />;
      case 'hold': return <TimelineIcon />;
      default: return <TimelineIcon />;
    }
  };

  const getSentimentColor = (score: number) => {
    if (score >= 0.7) return '#4caf50';
    if (score >= 0.5) return '#ff9800';
    return '#f44336';
  };

  const getSentimentLabel = (score: number) => {
    if (score >= 0.7) return 'Bullish';
    if (score >= 0.5) return 'Neutral';
    return 'Bearish';
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const handleSymbolChange = (event: SelectChangeEvent<string>) => {
    setSelectedSymbol(event.target.value);
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <PsychologyIcon fontSize="large" color="primary" /> Advanced AI Analytics
      </Typography>
      
      <Typography variant="subtitle1" color="textSecondary" sx={{ mb: 3 }}>
        Real-time AI-powered trading signals, sentiment analysis, and model performance metrics
      </Typography>

      {/* Symbol Selector */}
      <Box sx={{ mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 250 }}>
          <InputLabel>Select Trading Symbol</InputLabel>
          <Select
            value={selectedSymbol}
            label="Select Trading Symbol"
            onChange={handleSymbolChange}
          >
            {symbols.map((symbol) => (
              <MenuItem key={symbol.value} value={symbol.value}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: 'primary.main'
                    }}
                  />
                  {symbol.label} ({symbol.value})
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {error && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 4 }}>
          <CircularProgress size={60} />
          <Typography variant="body2" sx={{ mt: 2 }}>
            Loading AI analytics for {selectedSymbol}...
          </Typography>
        </Box>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} variant="fullWidth">
          <Tab 
            label="AI Trading Signals" 
            icon={<TrendingUpIcon />}
            iconPosition="start"
            sx={{ textTransform: 'none' }}
          />
          <Tab 
            label="Market Sentiment" 
            icon={<PsychologyIcon />}
            iconPosition="start"
            sx={{ textTransform: 'none' }}
          />
          <Tab 
            label="Model Performance" 
            icon={<TimelineIcon />}
            iconPosition="start"
            sx={{ textTransform: 'none' }}
          />
        </Tabs>
      </Box>

      {/* AI Signals Tab */}
      {activeTab === 0 && (
        <Card elevation={3} sx={{ borderRadius: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h5" component="h2">
                AI Trading Signals - {selectedSymbol}
              </Typography>
            </Box>
            
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              Latest AI-generated trading signals with confidence scores and target prices
            </Typography>
            
            <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: 'grey.50' }}>
                    <TableCell><strong>Signal</strong></TableCell>
                    <TableCell><strong>AI Model</strong></TableCell>
                    <TableCell><strong>Strength</strong></TableCell>
                    <TableCell><strong>Confidence</strong></TableCell>
                    <TableCell><strong>Target Price</strong></TableCell>
                    <TableCell><strong>Stop Loss</strong></TableCell>
                    <TableCell><strong>Generated At</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {aiSignals.map((signal) => (
                    <TableRow key={signal.id} hover>
                      <TableCell>
                        <Chip
                          icon={getSignalIcon(signal.signal_type)}
                          label={signal.signal_type}
                          sx={{ 
                            backgroundColor: getSignalColor(signal.signal_type),
                            color: 'white',
                            fontWeight: 'bold'
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {signal.model_type}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={signal.strength * 100}
                            sx={{ width: 80, height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="body2" fontWeight="medium">
                            {(signal.strength * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={signal.confidence * 100}
                            sx={{ width: 80, height: 8, borderRadius: 4 }}
                            color="secondary"
                          />
                          <Typography variant="body2" fontWeight="medium">
                            {(signal.confidence * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium" color="primary">
                          {signal.price_target ? `₹${signal.price_target}` : '-'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium" color="error">
                          {signal.stop_loss ? `₹${signal.stop_loss}` : '-'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="textSecondary">
                          {formatTimestamp(signal.timestamp)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Market Sentiment Tab */}
      {activeTab === 1 && (
        <Card elevation={3} sx={{ borderRadius: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <PsychologyIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h5" component="h2">
                Market Sentiment Analysis - {selectedSymbol}
              </Typography>
            </Box>
            
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              AI-powered sentiment analysis from news, social media, and institutional sources
            </Typography>
            
            {sentiment && (
              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap', justifyContent: 'center' }}>
                <Card 
                  sx={{ 
                    backgroundColor: getSentimentColor(sentiment.overall_score),
                    textAlign: 'center',
                    p: 3,
                    minWidth: 180,
                    borderRadius: 2,
                    boxShadow: 3
                  }}
                >
                  <Typography variant="h3" component="div" sx={{ color: 'white', fontWeight: 'bold' }}>
                    {sentiment.overall_score.toFixed(2)}
                  </Typography>
                  <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                    Overall Sentiment
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'white', opacity: 0.9 }}>
                    {getSentimentLabel(sentiment.overall_score)}
                  </Typography>
                </Card>
                
                <Card 
                  sx={{ 
                    backgroundColor: getSentimentColor(sentiment.news_sentiment),
                    textAlign: 'center',
                    p: 3,
                    minWidth: 180,
                    borderRadius: 2,
                    boxShadow: 3
                  }}
                >
                  <Typography variant="h3" component="div" sx={{ color: 'white', fontWeight: 'bold' }}>
                    {sentiment.news_sentiment.toFixed(2)}
                  </Typography>
                  <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                    News Sentiment
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'white', opacity: 0.9 }}>
                    {getSentimentLabel(sentiment.news_sentiment)}
                  </Typography>
                </Card>
                
                <Card 
                  sx={{ 
                    backgroundColor: getSentimentColor(sentiment.social_sentiment),
                    textAlign: 'center',
                    p: 3,
                    minWidth: 180,
                    borderRadius: 2,
                    boxShadow: 3
                  }}
                >
                  <Typography variant="h3" component="div" sx={{ color: 'white', fontWeight: 'bold' }}>
                    {sentiment.social_sentiment.toFixed(2)}
                  </Typography>
                  <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                    Social Media
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'white', opacity: 0.9 }}>
                    {getSentimentLabel(sentiment.social_sentiment)}
                  </Typography>
                </Card>
                
                {sentiment.institutional_sentiment !== undefined && (
                  <Card 
                    sx={{ 
                      backgroundColor: getSentimentColor(sentiment.institutional_sentiment),
                      textAlign: 'center',
                      p: 3,
                      minWidth: 180,
                      borderRadius: 2,
                      boxShadow: 3
                    }}
                  >
                    <Typography variant="h3" component="div" sx={{ color: 'white', fontWeight: 'bold' }}>
                      {sentiment.institutional_sentiment.toFixed(2)}
                    </Typography>
                    <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                      Institutional
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', opacity: 0.9 }}>
                      {getSentimentLabel(sentiment.institutional_sentiment)}
                    </Typography>
                  </Card>
                )}
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Model Performance Tab */}
      {activeTab === 2 && (
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <TimelineIcon color="primary" sx={{ mr: 1 }} />
            <Typography variant="h5" component="h2">
              AI Model Performance Metrics
            </Typography>
          </Box>
          
          <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
            Real-time performance metrics for all active AI trading models
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            {Object.entries(modelPerformance).map(([modelId, performance]) => (
              <Card elevation={3} key={modelId} sx={{ minWidth: 320, borderRadius: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                    {performance.model_id.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Accuracy
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={performance.accuracy * 100}
                        sx={{ flexGrow: 1, height: 10, borderRadius: 5 }}
                      />
                      <Typography variant="body2" fontWeight="bold">
                        {(performance.accuracy * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Precision
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={performance.precision * 100}
                        sx={{ flexGrow: 1, height: 10, borderRadius: 5 }}
                        color="secondary"
                      />
                      <Typography variant="body2" fontWeight="bold">
                        {(performance.precision * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Recall
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={performance.recall * 100}
                        sx={{ flexGrow: 1, height: 10, borderRadius: 5 }}
                        color="success"
                      />
                      <Typography variant="body2" fontWeight="bold">
                        {(performance.recall * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                    <Typography variant="caption" color="textSecondary">
                      Last updated: {formatTimestamp(performance.last_updated)}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default AdvancedAIComponent;