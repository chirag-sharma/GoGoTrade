/**
 * UI Slice
 * Manages application UI state, themes, and user interface preferences
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface UIState {
  theme: 'light' | 'dark';
  sidebar: {
    isOpen: boolean;
    selectedTab: string;
  };
  modals: {
    settingsOpen: boolean;
    aboutOpen: boolean;
    strategyConfigOpen: boolean;
    backtestResultsOpen: boolean;
  };
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: string;
    autoHide?: boolean;
  }>;
  loading: {
    global: boolean;
    components: Record<string, boolean>;
  };
  layout: {
    chartHeight: number;
    sidebarWidth: number;
    showToolbar: boolean;
    showStatusBar: boolean;
  };
  preferences: {
    autoRefreshInterval: number; // in seconds
    defaultTimeframe: string;
    maxActiveSignals: number;
    showNotifications: boolean;
    soundEnabled: boolean;
  };
}

const initialState: UIState = {
  theme: 'dark',
  sidebar: {
    isOpen: true,
    selectedTab: 'instruments',
  },
  modals: {
    settingsOpen: false,
    aboutOpen: false,
    strategyConfigOpen: false,
    backtestResultsOpen: false,
  },
  notifications: [],
  loading: {
    global: false,
    components: {},
  },
  layout: {
    chartHeight: 600,
    sidebarWidth: 300,
    showToolbar: true,
    showStatusBar: true,
  },
  preferences: {
    autoRefreshInterval: 30,
    defaultTimeframe: '1d',
    maxActiveSignals: 10,
    showNotifications: true,
    soundEnabled: false,
  },
};

// UI Slice
const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Theme Actions
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },

    // Sidebar Actions
    toggleSidebar: (state) => {
      state.sidebar.isOpen = !state.sidebar.isOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebar.isOpen = action.payload;
    },
    setSidebarTab: (state, action: PayloadAction<string>) => {
      state.sidebar.selectedTab = action.payload;
    },

    // Modal Actions
    openModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      state.modals[action.payload] = true;
    },
    closeModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      state.modals[action.payload] = false;
    },
    closeAllModals: (state) => {
      Object.keys(state.modals).forEach(key => {
        state.modals[key as keyof UIState['modals']] = false;
      });
    },

    // Notification Actions
    addNotification: (state, action: PayloadAction<Omit<UIState['notifications'][0], 'id' | 'timestamp'>>) => {
      const notification = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      };
      state.notifications.unshift(notification);
      
      // Keep only the latest 50 notifications
      if (state.notifications.length > 50) {
        state.notifications = state.notifications.slice(0, 50);
      }
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        notification => notification.id !== action.payload
      );
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },

    // Loading Actions
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.global = action.payload;
    },
    setComponentLoading: (state, action: PayloadAction<{ component: string; loading: boolean }>) => {
      state.loading.components[action.payload.component] = action.payload.loading;
    },
    clearComponentLoading: (state, action: PayloadAction<string>) => {
      delete state.loading.components[action.payload];
    },

    // Layout Actions
    updateLayout: (state, action: PayloadAction<Partial<UIState['layout']>>) => {
      state.layout = { ...state.layout, ...action.payload };
    },
    setChartHeight: (state, action: PayloadAction<number>) => {
      state.layout.chartHeight = action.payload;
    },
    setSidebarWidth: (state, action: PayloadAction<number>) => {
      state.layout.sidebarWidth = action.payload;
    },
    toggleToolbar: (state) => {
      state.layout.showToolbar = !state.layout.showToolbar;
    },
    toggleStatusBar: (state) => {
      state.layout.showStatusBar = !state.layout.showStatusBar;
    },

    // Preference Actions
    updatePreferences: (state, action: PayloadAction<Partial<UIState['preferences']>>) => {
      state.preferences = { ...state.preferences, ...action.payload };
    },
    setAutoRefreshInterval: (state, action: PayloadAction<number>) => {
      state.preferences.autoRefreshInterval = action.payload;
    },
    setDefaultTimeframe: (state, action: PayloadAction<string>) => {
      state.preferences.defaultTimeframe = action.payload;
    },
    toggleNotifications: (state) => {
      state.preferences.showNotifications = !state.preferences.showNotifications;
    },
    toggleSound: (state) => {
      state.preferences.soundEnabled = !state.preferences.soundEnabled;
    },

    // Reset Actions
    resetUI: (state) => {
      return { ...initialState, theme: state.theme }; // Preserve theme
    },
  },
});

export const {
  setTheme,
  toggleTheme,
  toggleSidebar,
  setSidebarOpen,
  setSidebarTab,
  openModal,
  closeModal,
  closeAllModals,
  addNotification,
  removeNotification,
  clearNotifications,
  setGlobalLoading,
  setComponentLoading,
  clearComponentLoading,
  updateLayout,
  setChartHeight,
  setSidebarWidth,
  toggleToolbar,
  toggleStatusBar,
  updatePreferences,
  setAutoRefreshInterval,
  setDefaultTimeframe,
  toggleNotifications,
  toggleSound,
  resetUI
} = uiSlice.actions;

export default uiSlice.reducer;

// Selectors
export const selectTheme = (state: { ui: UIState }) => state.ui.theme;
export const selectSidebar = (state: { ui: UIState }) => state.ui.sidebar;
export const selectModals = (state: { ui: UIState }) => state.ui.modals;
export const selectNotifications = (state: { ui: UIState }) => state.ui.notifications;
export const selectLoading = (state: { ui: UIState }) => state.ui.loading;
export const selectLayout = (state: { ui: UIState }) => state.ui.layout;
export const selectPreferences = (state: { ui: UIState }) => state.ui.preferences;
export const selectComponentLoading = (component: string) => (state: { ui: UIState }) => 
  state.ui.loading.components[component] || false;
