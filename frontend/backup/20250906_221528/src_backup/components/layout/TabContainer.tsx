import React, { Suspense } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

// Lazy load page components for better performance
const MainDashboard = React.lazy(() => import('../../pages/MainDashboard'));
const BacktestingPage = React.lazy(() => import('../../pages/BacktestingPage'));
const TradingPage = React.lazy(() => import('../../pages/TradingPage'));

interface TabContainerProps {
  currentTab: number;
  mockDataMode: boolean;
}

const LoadingFallback: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '400px',
      gap: 2,
    }}
  >
    <CircularProgress size={40} />
    <Typography variant="body2" color="text.secondary">
      {message}
    </Typography>
  </Box>
);

const TabContainer: React.FC<TabContainerProps> = ({ currentTab, mockDataMode }) => {
  const renderTabContent = () => {
    switch (currentTab) {
      case 0:
        return (
          <Suspense fallback={<LoadingFallback message="Loading Dashboard..." />}>
            <MainDashboard mockDataMode={mockDataMode} />
          </Suspense>
        );
      case 1:
        return (
          <Suspense fallback={<LoadingFallback message="Loading Backtesting..." />}>
            <BacktestingPage mockDataMode={mockDataMode} />
          </Suspense>
        );
      case 2:
        return (
          <Suspense fallback={<LoadingFallback message="Loading Trading..." />}>
            <TradingPage mockDataMode={mockDataMode} />
          </Suspense>
        );
      default:
        return (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '400px',
            }}
          >
            <Typography variant="h6" color="text.secondary">
              Tab not found
            </Typography>
          </Box>
        );
    }
  };

  return (
    <Box
      sx={{
        flexGrow: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {renderTabContent()}
    </Box>
  );
};

export default TabContainer;
