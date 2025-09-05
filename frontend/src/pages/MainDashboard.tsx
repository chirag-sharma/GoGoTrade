import React from 'react';
import { Box, Grid, Paper, Typography, Alert } from '@mui/material';
import TradingChart from '../components/charts/TradingChart';
import AIInsights from '../components/ai/AIInsights';

interface MainDashboardProps {
  mockDataMode: boolean;
}

const MainDashboard: React.FC<MainDashboardProps> = ({ mockDataMode }) => {
  return (
    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* Header */}
      <Box sx={{ mb: 1 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Trading Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Real-time market analysis with AI-powered insights
        </Typography>
        
        {mockDataMode && (
          <Alert severity="info" sx={{ mt: 1 }}>
            Currently using mock data for development. Toggle to "Live" for real market data.
          </Alert>
        )}
      </Box>

      {/* Main Content Grid */}
      <Grid container spacing={3} sx={{ flexGrow: 1, overflow: 'hidden' }}>
        {/* Trading Chart - Left Panel (70%) */}
        <Grid size={{ xs: 12, lg: 8 }} sx={{ display: 'flex', flexDirection: 'column' }}>
          <Paper
            elevation={2}
            sx={{
              flexGrow: 1,
              display: 'flex',
              flexDirection: 'column',
              p: 2,
              minHeight: 0, // Important for proper flex behavior
            }}
          >
            <Box sx={{ mb: 2 }}>
              <Typography variant="h6" component="h2">
                Price Chart
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Interactive trading chart with technical indicators
              </Typography>
            </Box>
            
            <Box sx={{ flexGrow: 1, minHeight: 0 }}>
              <TradingChart mockDataMode={mockDataMode} />
            </Box>
          </Paper>
        </Grid>

        {/* AI Insights - Right Panel (30%) */}
        <Grid size={{ xs: 12, lg: 4 }} sx={{ display: 'flex', flexDirection: 'column' }}>
          <Paper
            elevation={2}
            sx={{
              flexGrow: 1,
              display: 'flex',
              flexDirection: 'column',
              p: 2,
              minHeight: 0, // Important for proper flex behavior
            }}
          >
            <Box sx={{ mb: 2 }}>
              <Typography variant="h6" component="h2">
                AI Insights
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI-powered trading signals and market analysis
              </Typography>
            </Box>
            
            <Box sx={{ flexGrow: 1, minHeight: 0, overflow: 'auto' }}>
              <AIInsights mockDataMode={mockDataMode} />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MainDashboard;
