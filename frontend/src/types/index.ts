/**
 * Type Definitions for Trading Application
 * Central type definitions used throughout the frontend
 */

// Redux Hook Types
export type { RootState, AppDispatch } from '../store';

// Trading Data Types
export interface Instrument {
  symbol: string;
  name: string;
  exchange: string;
  sector?: string;
  marketCap?: number;
  isActive?: boolean;
}

export interface OHLCVData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketData {
  symbol: string;
  lastPrice: number;
  change: number;
  changePercent: number;
  volume: number;
  high24h?: number;
  low24h?: number;
  timestamp: string;
}

export interface ChartData {
  symbol: string;
  timeframe: string;
  data: OHLCVData[];
}

// Trading Signal Types
export type SignalType = 'BUY' | 'SELL' | 'HOLD';

export interface TradingSignal {
  id: string;
  symbol: string;
  signalType: SignalType;
  confidence: number;
  targetPrice?: number;
  stopLoss?: number;
  timestamp: string;
  strategy: string;
  reasoning?: string;
  metadata?: Record<string, any>;
}

export interface StrategyConfig {
  id: string;
  name: string;
  description: string;
  parameters: Record<string, any>;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface BacktestResult {
  strategyId: string;
  symbol: string;
  startDate: string;
  endDate: string;
  totalReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
  profitableTrades: number;
  averageReturn: number;
  trades: TradeResult[];
  performanceMetrics: PerformanceMetrics;
}

export interface TradeResult {
  entryDate: string;
  exitDate: string;
  entryPrice: number;
  exitPrice: number;
  quantity: number;
  pnl: number;
  pnlPercent: number;
  signal: SignalType;
}

export interface PerformanceMetrics {
  totalReturn: number;
  annualizedReturn: number;
  volatility: number;
  sharpeRatio: number;
  maxDrawdown: number;
  calmarRatio: number;
  sortinoRatio: number;
  winRate: number;
  profitFactor: number;
  avgWinAmount: number;
  avgLossAmount: number;
}

// Chart Configuration Types
export interface ChartConfig {
  showVolume: boolean;
  showGrid: boolean;
  candlestickColors: CandlestickColors;
  indicators: IndicatorConfig[];
  timeframe: string;
  theme: 'light' | 'dark';
}

export interface CandlestickColors {
  upColor: string;
  downColor: string;
  borderUpColor: string;
  borderDownColor: string;
  wickUpColor: string;
  wickDownColor: string;
}

export interface IndicatorConfig {
  type: string;
  name: string;
  parameters: Record<string, any>;
  color: string;
  visible: boolean;
}

// API Response Types
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> extends APIResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// UI Types
export interface NotificationData {
  id?: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  autoHide?: boolean;
  duration?: number;
}

export interface ModalState {
  isOpen: boolean;
  data?: any;
}

export interface FilterOptions {
  symbols?: string[];
  timeframe?: string;
  signalType?: SignalType;
  minConfidence?: number;
  strategy?: string;
  dateRange?: {
    start: string;
    end: string;
  };
}

// WebSocket Types
export interface WebSocketMessage {
  type: 'market_data' | 'trading_signal' | 'system_status';
  data: any;
  timestamp: string;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval: number;
  maxReconnectAttempts: number;
}

// Utility Types
export type LoadingState = 'idle' | 'pending' | 'fulfilled' | 'rejected';

export interface AsyncState<T = any> {
  data: T | null;
  loading: LoadingState;
  error: string | null;
  lastUpdated: string | null;
}

export type TimeframeOption = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';

export interface TableColumn<T = any> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  width?: number;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T) => React.ReactNode;
}

export interface SortConfig {
  key: string;
  direction: 'asc' | 'desc';
}

// Component Props Types
export interface BaseComponentProps {
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}

export interface ChartComponentProps extends BaseComponentProps {
  symbol: string;
  timeframe?: TimeframeOption;
  height?: number;
  showVolume?: boolean;
  indicators?: IndicatorConfig[];
  onSymbolChange?: (symbol: string) => void;
  onTimeframeChange?: (timeframe: TimeframeOption) => void;
}

export interface DataTableProps<T = any> extends BaseComponentProps {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  sortable?: boolean;
  filterable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  onRowClick?: (row: T) => void;
  onSort?: (sortConfig: SortConfig) => void;
}

// Error Types
export interface APIError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export type ErrorBoundaryFallback = React.ComponentType<{
  error: Error;
  resetErrorBoundary: () => void;
}>;
