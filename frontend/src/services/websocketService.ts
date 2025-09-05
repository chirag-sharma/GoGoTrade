/**
 * WebSocket Service for Real-time Trading Data
 * Connects React frontend to WebSocket endpoints for live updates
 */

interface MarketDataItem {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  timestamp: string;
}

interface TradingSignal {
  symbol: string;
  signalType: 'BUY' | 'SELL' | 'HOLD' | 'WATCH';
  confidence: number;
  price: number;
  reason: string;
  timestamp: string;
  patternType?: string;
  targetPrice?: number;
  stopLoss?: number;
}

interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp: string;
  status?: string;
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectInterval: number = 5000;
  private maxReconnectAttempts: number = 10;
  private reconnectAttempts: number = 0;
  private subscriptions: Set<string> = new Set();
  
  // Event callbacks
  private onMarketDataCallback: ((data: MarketDataItem[]) => void) | null = null;
  private onTradingSignalsCallback: ((data: TradingSignal[]) => void) | null = null;
  private onConnectionCallback: ((connected: boolean) => void) | null = null;
  private onErrorCallback: ((error: string) => void) | null = null;

  constructor() {
    this.connect();
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    try {
      const wsUrl = process.env.NODE_ENV === 'production' 
        ? 'wss://your-domain.com/api/v1/websocket/ws'
        : 'ws://localhost:8000/api/v1/websocket/ws';
      
      this.socket = new WebSocket(wsUrl);
      
      this.socket.onopen = this.onOpen.bind(this);
      this.socket.onmessage = this.onMessage.bind(this);
      this.socket.onclose = this.onClose.bind(this);
      this.socket.onerror = this.onErrorHandler.bind(this);
      
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * Handle WebSocket connection open
   */
  private onOpen(): void {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
    
    if (this.onConnectionCallback) {
      this.onConnectionCallback(true);
    }
    
    // Resubscribe to symbols if any
    if (this.subscriptions.size > 0) {
      this.subscribeToSymbols(Array.from(this.subscriptions));
    }
    
    // Start ping-pong to keep connection alive
    this.startPingPong();
  }

  /**
   * Handle incoming WebSocket messages
   */
  private onMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      switch (message.type) {
        case 'market_data_stream':
        case 'market_data':
          if (this.onMarketDataCallback && message.data) {
            this.onMarketDataCallback(message.data);
          }
          break;
          
        case 'signals_stream':
        case 'trading_signals':
          if (this.onTradingSignalsCallback && message.data) {
            this.onTradingSignalsCallback(message.data);
          }
          break;
          
        case 'connection':
          console.log('WebSocket connection confirmed:', message);
          break;
          
        case 'subscription':
          console.log('Subscription confirmed:', message);
          break;
          
        case 'pong':
          // Keep-alive response
          break;
          
        case 'error':
          console.error('WebSocket error:', message);
          if (this.onErrorCallback) {
            this.onErrorCallback(message.data || 'Unknown error');
          }
          break;
          
        default:
          console.log('Unknown message type:', message);
      }
      
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  /**
   * Handle WebSocket connection close
   */
  private onClose(): void {
    console.log('WebSocket disconnected');
    
    if (this.onConnectionCallback) {
      this.onConnectionCallback(false);
    }
    
    this.scheduleReconnect();
  }

  /**
   * Handle WebSocket errors
   */
  private onErrorHandler(error: Event): void {
    console.error('WebSocket error:', error);
    
    if (this.onErrorCallback) {
      this.onErrorCallback('WebSocket connection error');
    }
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting in ${this.reconnectInterval}ms (attempt ${this.reconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
      if (this.onErrorCallback) {
        this.onErrorCallback('Connection lost - max reconnection attempts reached');
      }
    }
  }

  /**
   * Start ping-pong to keep connection alive
   */
  private startPingPong(): void {
    const pingInterval = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.sendMessage({ type: 'ping' });
      } else {
        clearInterval(pingInterval);
      }
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Send message to WebSocket server
   */
  private sendMessage(message: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  /**
   * Subscribe to market data for specific symbols
   */
  subscribeToSymbols(symbols: string[]): void {
    this.subscriptions = new Set(symbols);
    this.sendMessage({
      type: 'subscribe',
      symbols: symbols
    });
  }

  /**
   * Request market data for symbols
   */
  requestMarketData(symbols: string[]): void {
    this.sendMessage({
      type: 'get_market_data',
      symbols: symbols
    });
  }

  /**
   * Request trading signals for symbols
   */
  requestTradingSignals(symbols: string[]): void {
    this.sendMessage({
      type: 'get_signals',
      symbols: symbols
    });
  }

  /**
   * Set market data callback
   */
  onMarketData(callback: (data: MarketDataItem[]) => void): void {
    this.onMarketDataCallback = callback;
  }

  /**
   * Set trading signals callback
   */
  onTradingSignals(callback: (data: TradingSignal[]) => void): void {
    this.onTradingSignalsCallback = callback;
  }

  /**
   * Set connection status callback
   */
  onConnectionStatus(callback: (connected: boolean) => void): void {
    this.onConnectionCallback = callback;
  }

  /**
   * Set error callback
   */
  onError(callback: (error: string) => void): void {
    this.onErrorCallback = callback;
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }

  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

// Create singleton instance
export const webSocketService = new WebSocketService();
export default webSocketService;
