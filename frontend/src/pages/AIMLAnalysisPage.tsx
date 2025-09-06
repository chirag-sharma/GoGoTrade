import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  Paper,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Psychology,
  AutoGraph,
  Insights,
  ModelTraining,
  DataUsage,
} from '@mui/icons-material';

interface AIMLAnalysisPageProps {
  mockDataMode: boolean;
}

interface MLPrediction {
  symbol: string;
  currentPrice: number;
  predictedPrice: number;
  confidence: number;
  recommendation: 'BUY' | 'SELL' | 'HOLD';
  model: string;
}

interface TechnicalIndicator {
  name: string;
  value: number;
  signal: 'BUY' | 'SELL' | 'NEUTRAL';
  strength: number;
}

const AIMLAnalysisPage: React.FC<AIMLAnalysisPageProps> = ({ mockDataMode }) => {
  const [selectedStock, setSelectedStock] = useState('WIPRO');
  const [selectedModel, setSelectedModel] = useState('lstm');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<MLPrediction | null>(null);

  const availableModels = [
    { value: 'lstm', label: 'LSTM Neural Network' },
    { value: 'random_forest', label: 'Random Forest' },
    { value: 'xgboost', label: 'XGBoost' },
    { value: 'svm', label: 'Support Vector Machine' },
    { value: 'ensemble', label: 'Ensemble Model' },
  ];

  const popularStocks = ['WIPRO', 'TITAN', 'ICICIBANK', 'RELIANCE', 'TCS', 'INFY'];

  const technicalIndicators: TechnicalIndicator[] = [
    { name: 'RSI (14)', value: 65.4, signal: 'NEUTRAL', strength: 0.6 },
    { name: 'MACD', value: 2.3, signal: 'BUY', strength: 0.8 },
    { name: 'Bollinger Bands', value: 0.75, signal: 'SELL', strength: 0.7 },
    { name: 'Stochastic', value: 45.2, signal: 'NEUTRAL', strength: 0.5 },
    { name: 'Williams %R', value: -25.8, signal: 'BUY', strength: 0.6 },
  ];

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    
    // Simulate AI/ML analysis
    setTimeout(() => {
      const mockResult: MLPrediction = {
        symbol: selectedStock,
        currentPrice: 425.50,
        predictedPrice: 445.25,
        confidence: 0.87,
        recommendation: 'BUY',
        model: selectedModel,
      };
      setAnalysisResults(mockResult);
      setIsAnalyzing(false);
    }, 3000);
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'success.main';
      case 'SELL': return 'error.main';
      default: return 'warning.main';
    }
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'BUY': return 'success';
      case 'SELL': return 'error';
      default: return 'warning';
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          🤖 AI/ML Market Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Advanced machine learning models for stock price prediction and technical analysis
        </Typography>
      </Box>

      {mockDataMode && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Demo mode: Using simulated AI/ML predictions. Connect to real models for live analysis.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Analysis Configuration */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <ModelTraining sx={{ mr: 1, verticalAlign: 'bottom' }} />
                Analysis Configuration
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Select Stock</InputLabel>
                <Select
                  value={selectedStock}
                  onChange={(e) => setSelectedStock(e.target.value)}
                  label="Select Stock"
                >
                  {popularStocks.map((stock) => (
                    <MenuItem key={stock} value={stock}>
                      {stock}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>ML Model</InputLabel>
                <Select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  label="ML Model"
                >
                  {availableModels.map((model) => (
                    <MenuItem key={model.value} value={model.value}>
                      {model.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Prediction Horizon (Days)"
                type="number"
                defaultValue={5}
                sx={{ mb: 2 }}
              />

              <Button
                fullWidth
                variant="contained"
                onClick={handleRunAnalysis}
                disabled={isAnalyzing}
                startIcon={<Psychology />}
                size="large"
              >
                {isAnalyzing ? 'Analyzing...' : 'Run AI Analysis'}
              </Button>

              {isAnalyzing && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Processing market data...
                  </Typography>
                  <LinearProgress />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Analysis Results */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Insights sx={{ mr: 1, verticalAlign: 'bottom' }} />
                ML Prediction Results
              </Typography>

              {analysisResults ? (
                <Box>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">
                          Current Price
                        </Typography>
                        <Typography variant="h6">
                          ₹{analysisResults.currentPrice}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">
                          Predicted Price
                        </Typography>
                        <Typography variant="h6" color="success.main">
                          ₹{analysisResults.predictedPrice}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">
                          Confidence
                        </Typography>
                        <Typography variant="h6">
                          {(analysisResults.confidence * 100).toFixed(1)}%
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">
                          Recommendation
                        </Typography>
                        <Chip 
                          label={analysisResults.recommendation}
                          color={getRecommendationColor(analysisResults.recommendation) as any}
                          variant="filled"
                        />
                      </Paper>
                    </Grid>
                  </Grid>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Expected Return: {(((analysisResults.predictedPrice - analysisResults.currentPrice) / analysisResults.currentPrice) * 100).toFixed(2)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Model: {availableModels.find(m => m.value === analysisResults.model)?.label}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <AutoGraph sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    Run analysis to see ML predictions
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Select a stock and model to get started
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Technical Indicators */}
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <DataUsage sx={{ mr: 1, verticalAlign: 'bottom' }} />
                Technical Indicators Analysis
              </Typography>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Indicator</TableCell>
                      <TableCell align="right">Value</TableCell>
                      <TableCell align="center">Signal</TableCell>
                      <TableCell align="right">Strength</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {technicalIndicators.map((indicator) => (
                      <TableRow key={indicator.name}>
                        <TableCell>{indicator.name}</TableCell>
                        <TableCell align="right">{indicator.value}</TableCell>
                        <TableCell align="center">
                          <Chip
                            label={indicator.signal}
                            size="small"
                            sx={{ 
                              color: 'white',
                              bgcolor: getSignalColor(indicator.signal)
                            }}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={indicator.strength * 100}
                              sx={{ flexGrow: 1, height: 6 }}
                            />
                            <Typography variant="body2">
                              {(indicator.strength * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AIMLAnalysisPage;
