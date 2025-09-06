import { useState, useEffect, useCallback } from 'react';
import { NSEInstrument } from '../services/nseSecuritiesService';
import WatchlistService from '../services/watchlistService';

export interface UseWatchlistReturn {
  watchlist: NSEInstrument[];
  addToWatchlist: (stock: NSEInstrument) => void;
  removeFromWatchlist: (stockId: number) => void;
  isInWatchlist: (stockId: number) => boolean;
  clearWatchlist: () => void;
  watchlistCount: number;
  searchWatchlist: (query: string) => NSEInstrument[];
  getWatchlistBySegment: (segment: 'LARGE_CAP' | 'MID_CAP' | 'SMALL_CAP' | 'MICRO_CAP') => NSEInstrument[];
  getTopWatchlistStocks: (limit?: number) => NSEInstrument[];
}

/**
 * Custom hook for managing watchlist state across the application
 */
export const useWatchlist = (): UseWatchlistReturn => {
  const [watchlist, setWatchlist] = useState<NSEInstrument[]>([]);

  // Load initial watchlist on mount
  useEffect(() => {
    const initialWatchlist = WatchlistService.loadWatchlist();
    setWatchlist(initialWatchlist);
  }, []);

  // Add stock to watchlist
  const addToWatchlist = useCallback((stock: NSEInstrument) => {
    const updatedWatchlist = WatchlistService.addToWatchlist(stock);
    setWatchlist(updatedWatchlist);
  }, []);

  // Remove stock from watchlist
  const removeFromWatchlist = useCallback((stockId: number) => {
    const updatedWatchlist = WatchlistService.removeFromWatchlist(stockId);
    setWatchlist(updatedWatchlist);
  }, []);

  // Check if stock is in watchlist
  const isInWatchlist = useCallback((stockId: number) => {
    return watchlist.some(item => item.id === stockId);
  }, [watchlist]);

  // Clear entire watchlist
  const clearWatchlist = useCallback(() => {
    WatchlistService.clearWatchlist();
    setWatchlist([]);
  }, []);

  // Search within watchlist
  const searchWatchlist = useCallback((query: string) => {
    return WatchlistService.searchWatchlist(query);
  }, []);

  // Get watchlist by market segment
  const getWatchlistBySegment = useCallback((segment: 'LARGE_CAP' | 'MID_CAP' | 'SMALL_CAP' | 'MICRO_CAP') => {
    return WatchlistService.getWatchlistBySegment(segment);
  }, []);

  // Get top watchlist stocks
  const getTopWatchlistStocks = useCallback((limit: number = 5) => {
    return WatchlistService.getTopWatchlistStocks(limit);
  }, []);

  return {
    watchlist,
    addToWatchlist,
    removeFromWatchlist,
    isInWatchlist,
    clearWatchlist,
    watchlistCount: watchlist.length,
    searchWatchlist,
    getWatchlistBySegment,
    getTopWatchlistStocks,
  };
};

export default useWatchlist;
