import { NSEInstrument } from './nseSecuritiesService';

const WATCHLIST_STORAGE_KEY = 'gogoTrade_watchlist';

export class WatchlistService {
  /**
   * Load watchlist from localStorage
   */
  static loadWatchlist(): NSEInstrument[] {
    try {
      const saved = localStorage.getItem(WATCHLIST_STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      console.error('Failed to load watchlist from localStorage:', error);
      return [];
    }
  }

  /**
   * Save watchlist to localStorage
   */
  static saveWatchlist(watchlist: NSEInstrument[]): void {
    try {
      localStorage.setItem(WATCHLIST_STORAGE_KEY, JSON.stringify(watchlist));
    } catch (error) {
      console.error('Failed to save watchlist to localStorage:', error);
    }
  }

  /**
   * Add stock to watchlist
   */
  static addToWatchlist(stock: NSEInstrument): NSEInstrument[] {
    const currentWatchlist = this.loadWatchlist();
    const exists = currentWatchlist.find(item => item.id === stock.id);
    
    if (!exists) {
      const newWatchlist = [...currentWatchlist, stock];
      this.saveWatchlist(newWatchlist);
      return newWatchlist;
    }
    
    return currentWatchlist;
  }

  /**
   * Remove stock from watchlist
   */
  static removeFromWatchlist(stockId: number): NSEInstrument[] {
    const currentWatchlist = this.loadWatchlist();
    const filteredWatchlist = currentWatchlist.filter(item => item.id !== stockId);
    this.saveWatchlist(filteredWatchlist);
    return filteredWatchlist;
  }

  /**
   * Check if stock is in watchlist
   */
  static isInWatchlist(stockId: number): boolean {
    const watchlist = this.loadWatchlist();
    return watchlist.some(item => item.id === stockId);
  }

  /**
   * Clear entire watchlist
   */
  static clearWatchlist(): void {
    try {
      localStorage.removeItem(WATCHLIST_STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear watchlist:', error);
    }
  }

  /**
   * Get watchlist count
   */
  static getWatchlistCount(): number {
    return this.loadWatchlist().length;
  }

  /**
   * Get top stocks from watchlist (by market cap or other criteria)
   */
  static getTopWatchlistStocks(limit: number = 5): NSEInstrument[] {
    const watchlist = this.loadWatchlist();
    // Sort by market cap (Large -> Mid -> Small -> Micro)
    const segmentOrder = { 'LARGE_CAP': 0, 'MID_CAP': 1, 'SMALL_CAP': 2, 'MICRO_CAP': 3 };
    
    return watchlist
      .sort((a, b) => segmentOrder[a.market_segment] - segmentOrder[b.market_segment])
      .slice(0, limit);
  }

  /**
   * Get watchlist by market segment
   */
  static getWatchlistBySegment(segment: 'LARGE_CAP' | 'MID_CAP' | 'SMALL_CAP' | 'MICRO_CAP'): NSEInstrument[] {
    const watchlist = this.loadWatchlist();
    return watchlist.filter(stock => stock.market_segment === segment);
  }

  /**
   * Search within watchlist
   */
  static searchWatchlist(query: string): NSEInstrument[] {
    const watchlist = this.loadWatchlist();
    const searchTerm = query.toLowerCase();
    
    return watchlist.filter(stock => 
      stock.symbol.toLowerCase().includes(searchTerm) ||
      stock.name.toLowerCase().includes(searchTerm) ||
      stock.sector.toLowerCase().includes(searchTerm)
    );
  }
}

export default WatchlistService;
