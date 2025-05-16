import React from 'react';
import { Box, CircularProgress, ToggleButton, Typography } from '@mui/material';
import { Search, BlurOn, Check } from '@mui/icons-material';
import { StyledButton, StyledTextField } from './UI/styles';

const SearchForm = ({ onSearch, text, onTextChange, loading, fuzzySearch, setFuzzySearch }) => (
  <Box sx={{ marginTop: 4, padding: 3, backgroundColor: '#fff', borderRadius: 2, boxShadow: 1 }}>
    <StyledTextField
      label="Введите текст"
      multiline
      rows={14}
      variant="outlined"
      fullWidth
      value={text}
      onChange={onTextChange}
      sx={{ mb: 2 }}
    />
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
      <StyledButton
        variant="contained"
        color="primary"
        sx={{ flexGrow: 1, py: 1.2 }}
        onClick={onSearch}
        disabled={loading}
        startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Search />}
      >
        {loading ? 'Поиск...' : 'Начать поиск'}
      </StyledButton>
      <ToggleButton
        value="fuzzy"
        selected={fuzzySearch}
        onChange={() => setFuzzySearch(!fuzzySearch)}
        size="medium"
        sx={{
          py: 1,
          px: 2,
          border: '1px solid',
          borderColor: fuzzySearch ? 'success.main' : 'grey.300',
          backgroundColor: 'background.paper',
          color: 'text.primary',
          borderRadius: 1,
          textTransform: 'none',
          fontWeight: 'medium',
          '&:hover': {
            backgroundColor: 'grey.100',
          },
          transition: 'all 0.2s ease-in-out',
        }}
      >
        <BlurOn sx={{ fontSize: 20, mr: 0.5 }} />
        Нечеткий поиск
        {fuzzySearch && <Check sx={{ fontSize: 16, ml: 0.5, color: 'success.main' }} />}
      </ToggleButton>
    </Box>
    {fuzzySearch && (
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ mt: 1.5, display: 'block', textAlign: 'left', fontSize: '0.85rem', opacity: 0.7 }}
      >
        Нечеткий поиск может занять чуть больше времени
      </Typography>
    )}
  </Box>
);

export default SearchForm;