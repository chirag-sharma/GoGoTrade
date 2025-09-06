import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  Box,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TradingIcon,
  Settings as SettingsIcon,
  Psychology as AIIcon,
  Chat as LLMIcon,
  WifiOff as MockDataIcon,
  Wifi as LiveDataIcon,
} from '@mui/icons-material';

interface TopNavigationProps {
  currentTab: number;
  onTabChange: (event: React.SyntheticEvent, newValue: number) => void;
  mockDataMode: boolean;
  onMockDataToggle: (enabled: boolean) => void;
}

const TopNavigation: React.FC<TopNavigationProps> = ({
  currentTab,
  onTabChange,
  mockDataMode,
  onMockDataToggle,
}) => {
  const tabs = [
    { label: 'Dashboard', icon: <DashboardIcon />, value: 0 },
    { label: 'Backtesting', icon: <AnalyticsIcon />, value: 1 },
    { label: 'Trading', icon: <TradingIcon />, value: 2 },
    { label: 'AI/ML Analysis', icon: <AIIcon />, value: 3 },
    { label: 'LLM Analysis', icon: <LLMIcon />, value: 4 },
  ];

  return (
    <AppBar position="sticky" elevation={1} sx={{ zIndex: 1100 }}>
      <Toolbar sx={{ justifyContent: 'space-between', minHeight: 64 }}>
        {/* Logo and Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography
            variant="h5"
            component="div"
            sx={{
              fontWeight: 'bold',
              background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            GoGoTrade
          </Typography>
        </Box>

        {/* Navigation Tabs */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1, justifyContent: 'center' }}>
          <Tabs
            value={currentTab}
            onChange={onTabChange}
            textColor="inherit"
            indicatorColor="secondary"
            sx={{
              '& .MuiTab-root': {
                minWidth: 120,
                color: 'rgba(255, 255, 255, 0.7)',
                '&.Mui-selected': {
                  color: 'white',
                },
              },
            }}
          >
            {tabs.map((tab) => (
              <Tab
                key={tab.value}
                icon={tab.icon}
                label={tab.label}
                iconPosition="start"
                sx={{
                  '& .MuiTab-iconWrapper': {
                    marginRight: 1,
                    marginBottom: 0,
                  },
                }}
              />
            ))}
          </Tabs>
        </Box>

        {/* Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* Mock Data Toggle */}
          <Tooltip title={mockDataMode ? 'Using Mock Data' : 'Using Live Data'}>
            <FormControlLabel
              control={
                <Switch
                  checked={mockDataMode}
                  onChange={(e) => onMockDataToggle(e.target.checked)}
                  size="small"
                  color="secondary"
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {mockDataMode ? <MockDataIcon fontSize="small" /> : <LiveDataIcon fontSize="small" />}
                  <Typography variant="caption">
                    {mockDataMode ? 'Mock' : 'Live'}
                  </Typography>
                </Box>
              }
              sx={{
                margin: 0,
                '& .MuiFormControlLabel-label': {
                  fontSize: '0.75rem',
                  color: 'rgba(255, 255, 255, 0.8)',
                },
              }}
            />
          </Tooltip>

          {/* Settings */}
          <Tooltip title="Settings">
            <IconButton
              color="inherit"
              sx={{
                color: 'rgba(255, 255, 255, 0.8)',
                '&:hover': {
                  color: 'white',
                },
              }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopNavigation;
