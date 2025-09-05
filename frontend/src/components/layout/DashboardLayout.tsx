import React, { useState } from 'react';
import { Box, Container, Fade } from '@mui/material';
import TopNavigation from './TopNavigation';
import TabContainer from './TabContainer';

interface DashboardLayoutProps {
  children?: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [currentTab, setCurrentTab] = useState(0);
  const [mockDataMode, setMockDataMode] = useState(true); // Start with mock data for development

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleMockDataToggle = (enabled: boolean) => {
    setMockDataMode(enabled);
    // TODO: Notify data services about mode change
    console.log(`Data mode changed to: ${enabled ? 'Mock' : 'Live'}`);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        bgcolor: 'background.default',
      }}
    >
      {/* Top Navigation */}
      <TopNavigation
        currentTab={currentTab}
        onTabChange={handleTabChange}
        mockDataMode={mockDataMode}
        onMockDataToggle={handleMockDataToggle}
      />

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        <Container
          maxWidth={false}
          disableGutters
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            p: { xs: 1, sm: 2, md: 3 },
          }}
        >
          <Fade in key={currentTab} timeout={300}>
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              <TabContainer 
                currentTab={currentTab} 
                mockDataMode={mockDataMode}
              />
            </Box>
          </Fade>
        </Container>
      </Box>
    </Box>
  );
};

export default DashboardLayout;
