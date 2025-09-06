import React, { useState, useEffect, useCallback } from 'react';
import {
  Autocomplete,
  TextField,
  Box,
  Typography,
  Chip,
  ListItem,
  ListItemText,
  InputAdornment,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material';
import {
  Search,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { NSESecuritiesService, NSEInstrument } from '../../services/nseSecuritiesService';

interface NSESearchProps {
  onInstrumentSelect: (instrument: NSEInstrument) => void;
  selectedInstrument?: NSEInstrument | null;
  placeholder?: string;
  autoFocus?: boolean;
  fullWidth?: boolean;
  size?: 'small' | 'medium';
  showDetails?: boolean;
}

const NSESecuritiesSearch: React.FC<NSESearchProps> = ({
  onInstrumentSelect,
  selectedInstrument,
  placeholder = "Search NSE securities...",
  autoFocus = false,
  fullWidth = true,
  size = 'medium',
  showDetails = true,
}) => {
  const [searchResults, setSearchResults] = useState<NSEInstrument[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  // Debounced search function
  const debouncedSearch = useCallback(
    (() => {
      let timeoutId: NodeJS.Timeout;
      return (query: string) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(async () => {
          if (query.length >= 2) {
            setLoading(true);
            try {
              const results = await NSESecuritiesService.searchSecurities(query, 10);
              setSearchResults(results);
            } catch (error) {
              console.error('Search failed:', error);
              setSearchResults([]);
            } finally {
              setLoading(false);
            }
          } else {
            setSearchResults([]);
          }
        }, 300);
      };
    })(),
    []
  );

  useEffect(() => {
    debouncedSearch(searchQuery);
  }, [searchQuery, debouncedSearch]);

  const handleInputChange = (event: React.SyntheticEvent, value: string) => {
    setSearchQuery(value);
  };

  const handleInstrumentChange = (event: React.SyntheticEvent, value: NSEInstrument | null) => {
    if (value) {
      onInstrumentSelect(value);
    }
  };

  const getMarketSegmentColor = (segment: string) => {
    switch (segment) {
      case 'LARGE_CAP':
        return 'primary';
      case 'MID_CAP':
        return 'secondary';
      case 'SMALL_CAP':
        return 'success';
      case 'MICRO_CAP':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatMarketSegment = (segment: string) => {
    return segment.replace('_', ' ').toUpperCase();
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Autocomplete
        open={open}
        onOpen={() => setOpen(true)}
        onClose={() => setOpen(false)}
        value={selectedInstrument}
        inputValue={searchQuery}
        onInputChange={handleInputChange}
        onChange={handleInstrumentChange}
        options={searchResults}
        getOptionLabel={(option) => option.symbol}
        filterOptions={(x) => x} // Disable built-in filtering
        isOptionEqualToValue={(option, value) => option.id === value.id}
        loading={loading}
        fullWidth={fullWidth}
        size={size}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Search NSE Securities"
            placeholder={placeholder}
            autoFocus={autoFocus}
            InputProps={{
              ...params.InputProps,
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
              endAdornment: (
                <>
                  {loading ? <CircularProgress color="inherit" size={20} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
        renderOption={(props, option) => (
          <ListItem {...props} key={option.id}>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {option.symbol}
                  </Typography>
                  <Chip
                    label={formatMarketSegment(option.market_segment)}
                    size="small"
                    color={getMarketSegmentColor(option.market_segment) as any}
                    variant="outlined"
                  />
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {option.name}
                  </Typography>
                  {showDetails && (
                    <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                      <Chip
                        label={option.sector}
                        size="small"
                        variant="outlined"
                      />
                      <Typography variant="caption" color="text.secondary">
                        ISIN: {option.isin}
                      </Typography>
                    </Box>
                  )}
                </Box>
              }
            />
          </ListItem>
        )}
        noOptionsText={
          searchQuery.length < 2
            ? "Type at least 2 characters to search"
            : loading
            ? "Searching..."
            : "No securities found"
        }
      />
      
      {selectedInstrument && showDetails && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {selectedInstrument.symbol} - {selectedInstrument.name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <Chip
                label={formatMarketSegment(selectedInstrument.market_segment)}
                color={getMarketSegmentColor(selectedInstrument.market_segment) as any}
                size="small"
              />
              <Chip
                label={selectedInstrument.sector}
                variant="outlined"
                size="small"
              />
              <Chip
                label={selectedInstrument.industry_group}
                variant="outlined"
                size="small"
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              ISIN: {selectedInstrument.isin}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Market Lot: {selectedInstrument.market_lot}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Face Value: ₹{selectedInstrument.face_value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Listed: {new Date(selectedInstrument.listing_date).toLocaleDateString()}
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default NSESecuritiesSearch;
