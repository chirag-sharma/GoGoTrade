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
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Psychology,
  ExpandMore,
  Article,
  Insights,
  TrendingUp,
  TrendingDown,
  Analytics,
  AutoFixHigh,
  Chat,
} from '@mui/icons-material';

interface LLMAnalysisPageProps {
  mockDataMode: boolean;
}

interface NewsArticle {
  id: string;
  title: string;
  source: string;
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  impact: number; // 0-1 scale
  timestamp: string;
  summary: string;
}

interface LLMInsight {
  category: string;
  insight: string;
  confidence: number;
  impact: 'HIGH' | 'MEDIUM' | 'LOW';
}

const LLMAnalysisPage: React.FC<LLMAnalysisPageProps> = ({ mockDataMode }) => {
  const [selectedStock, setSelectedStock] = useState('WIPRO');
  const [selectedModel, setSelectedModel] = useState('gpt4');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<LLMInsight[]>([]);
  const [newsAnalysis, setNewsAnalysis] = useState<NewsArticle[]>([]);

  const availableModels = [
    { value: 'gpt4', label: 'GPT-4 Turbo' },
    { value: 'claude', label: 'Claude 3.5 Sonnet' },
    { value: 'gemini', label: 'Gemini Pro' },
    { value: 'llama', label: 'Llama 3.1' },
  ];

  const popularStocks = ['WIPRO', 'TITAN', 'ICICIBANK', 'RELIANCE', 'TCS', 'INFY'];

  const mockNews: NewsArticle[] = [
    {
      id: '1',
      title: 'WIPRO announces major digital transformation deal worth $500M',
      source: 'Economic Times',
      sentiment: 'POSITIVE',
      impact: 0.8,
      timestamp: '2 hours ago',
      summary: 'Major enterprise client signed multi-year contract for cloud migration and AI services'
    },
    {
      id: '2', 
      title: 'IT sector faces headwinds as global spending slows',
      source: 'Business Standard',
      sentiment: 'NEGATIVE',
      impact: 0.6,
      timestamp: '4 hours ago',
      summary: 'Industry analysts warn of reduced IT spending in key markets affecting major players'
    },
    {
      id: '3',
      title: 'WIPRO leadership change signals strategic shift',
      source: 'Mint',
      sentiment: 'NEUTRAL',
      impact: 0.4,
      timestamp: '1 day ago',
      summary: 'New appointments in key positions indicate focus on emerging technologies'
    }
  ];

  const mockInsights: LLMInsight[] = [
    {
      category: 'Financial Performance',
      insight: 'Strong quarterly results with 12% YoY revenue growth indicate robust business fundamentals despite market volatility.',
      confidence: 0.85,
      impact: 'HIGH'
    },
    {
      category: 'Market Sentiment',
      insight: 'Social media sentiment analysis shows increasing positive mentions related to AI and cloud services expansion.',
      confidence: 0.78,
      impact: 'MEDIUM'
    },
    {
      category: 'Technical Analysis',
      insight: 'Chart patterns suggest potential breakout above key resistance levels with strong volume confirmation.',
      confidence: 0.72,
      impact: 'MEDIUM'
    },
    {
      category: 'Competitive Position',
      insight: 'Recent strategic partnerships strengthen position in high-growth digital transformation market segment.',
      confidence: 0.80,
      impact: 'HIGH'
    }
  ];

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    
    // Simulate LLM analysis
    setTimeout(() => {
      setAnalysisResults(mockInsights);
      setNewsAnalysis(mockNews);
      setIsAnalyzing(false);
    }, 4000);
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'POSITIVE': return 'success.main';
      case 'NEGATIVE': return 'error.main';
      default: return 'warning.main';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'POSITIVE': return <TrendingUp />;
      case 'NEGATIVE': return <TrendingDown />;
      default: return <Analytics />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'HIGH': return 'error';
      case 'MEDIUM': return 'warning';
      default: return 'info';
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          🧠 LLM Market Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Advanced language model analysis for market insights, news sentiment, and trading recommendations
        </Typography>
      </Box>

      {mockDataMode && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Demo mode: Using simulated LLM analysis. Connect to real language models for live insights.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Analysis Configuration */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AutoFixHigh sx={{ mr: 1, verticalAlign: 'bottom' }} />
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
                <InputLabel>LLM Model</InputLabel>
                <Select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  label="LLM Model"
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
                label="Analysis Depth"
                select
                defaultValue="comprehensive"
                sx={{ mb: 2 }}
              >
                <MenuItem value="quick">Quick Analysis</MenuItem>
                <MenuItem value="standard">Standard Analysis</MenuItem>
                <MenuItem value="comprehensive">Comprehensive Analysis</MenuItem>
              </TextField>

              <Button
                fullWidth
                variant="contained"
                onClick={handleRunAnalysis}
                disabled={isAnalyzing}
                startIcon={<Psychology />}
                size="large"
              >
                {isAnalyzing ? 'Analyzing...' : 'Run LLM Analysis'}
              </Button>

              {isAnalyzing && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Processing news, fundamentals, and market data...
                  </Typography>
                  <CircularProgress size={20} sx={{ ml: 1 }} />
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
                LLM Insights & Recommendations
              </Typography>

              {analysisResults.length > 0 ? (
                <Box>
                  {analysisResults.map((insight, index) => (
                    <Accordion key={index} sx={{ mb: 1 }}>
                      <AccordionSummary
                        expandIcon={<ExpandMore />}
                        aria-controls={`panel${index}-content`}
                        id={`panel${index}-header`}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                          <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                            {insight.category}
                          </Typography>
                          <Chip 
                            label={insight.impact}
                            color={getImpactColor(insight.impact) as any}
                            size="small"
                          />
                          <Typography variant="body2" color="text.secondary">
                            {(insight.confidence * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2">
                          {insight.insight}
                        </Typography>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Chat sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    Run analysis to see LLM insights
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    AI-powered analysis of market trends and news sentiment
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* News Sentiment Analysis */}
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Article sx={{ mr: 1, verticalAlign: 'bottom' }} />
                News Sentiment Analysis
              </Typography>
              
              {newsAnalysis.length > 0 ? (
                <List>
                  {newsAnalysis.map((article, index) => (
                    <React.Fragment key={article.id}>
                      <ListItem alignItems="flex-start">
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, width: '100%' }}>
                          <Box sx={{ color: getSentimentColor(article.sentiment), mt: 0.5 }}>
                            {getSentimentIcon(article.sentiment)}
                          </Box>
                          <Box sx={{ flexGrow: 1 }}>
                            <ListItemText
                              primary={article.title}
                              secondary={
                                <Box>
                                  <Typography variant="body2" color="text.secondary" gutterBottom>
                                    {article.summary}
                                  </Typography>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                                    <Typography variant="caption" color="text.secondary">
                                      {article.source} • {article.timestamp}
                                    </Typography>
                                    <Chip
                                      label={article.sentiment}
                                      size="small"
                                      sx={{ 
                                        color: 'white',
                                        bgcolor: getSentimentColor(article.sentiment)
                                      }}
                                    />
                                    <Typography variant="caption" color="text.secondary">
                                      Impact: {(article.impact * 100).toFixed(0)}%
                                    </Typography>
                                  </Box>
                                </Box>
                              }
                            />
                          </Box>
                        </Box>
                      </ListItem>
                      {index < newsAnalysis.length - 1 && <Divider variant="inset" component="li" />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Article sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    No news analysis available
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Run analysis to see news sentiment and impact assessment
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default LLMAnalysisPage;
