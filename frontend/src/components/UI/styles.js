import { styled } from '@mui/system';
import { TextField, Button, Box } from '@mui/material';

export const HeaderBox = styled(Box)(({ theme }) => ({
  background: 'linear-gradient(135deg, #3f51b5, #1976d2)',
  color: '#fff',
  padding: theme.spacing(4),
  borderRadius: '12px',
  boxShadow: theme.shadows[5],
  textAlign: 'center',
  marginBottom: theme.spacing(4),
}));

export const ReportBox = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  padding: theme.spacing(3),
  borderRadius: '12px',
  boxShadow: theme.shadows[3],
  marginBottom: theme.spacing(4),
  transition: 'transform 0.3s ease-in-out',
  '&:hover': {
    transform: 'scale(1.05)',
  },
}));

export const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: '8px',
  },
  '& .MuiInputLabel-root': {
    fontSize: '1.1rem',
  },
  marginBottom: theme.spacing(2),
}));

export const StyledButton = styled(Button)(({ theme }) => ({
  borderRadius: '8px',
  padding: theme.spacing(1.5, 4),
  fontSize: '1.1rem',
  marginTop: theme.spacing(2),
  transition: 'background-color 0.3s ease',
  '&:hover': {
    backgroundColor: theme.palette.primary.dark,
  },
}));

export const PreviewReport = styled(Box)(({ theme }) => ({
  maxHeight: '300px',
  overflowY: 'auto',
  padding: theme.spacing(2),
  backgroundColor: '#f9f9f9',
  borderRadius: '8px',
  boxShadow: theme.shadows[2],
  fontSize: '1rem',
}));

export const ReportContainer = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(4),
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.default,
  borderRadius: '12px',
  boxShadow: theme.shadows[3],
}));

export const HighlightedText = styled('span')({
  backgroundColor: 'yellow',
  fontWeight: 'bold',
});
