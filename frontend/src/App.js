import React, { useState } from 'react';
import { Container, Box, Typography, Divider, Button, AppBar, Toolbar, IconButton } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import SearchForm from './components/SearchForm';
import ReportPreview from './components/Report/ReportPreview';
import FullReportModal from './components/Report/FullReportModal';
import { HeaderBox, ReportContainer } from './components/UI/styles';
import ReportTable from './components/UI/StyledTable';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f4f6f8',
    },
  },
  typography: {
    h6: {
      fontWeight: 'bold',
    },
    body1: {
      fontSize: '1rem',
    },
  },
});

const Navbar = () => {
  const goToAdmin = () => {
    window.open('http://localhost:8000/admin', '_blank');
  };

  return (
    <AppBar
      position="static"
      sx={{
        background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
        boxShadow: '0 3px 5px 2px rgba(25, 118, 210, .3)',
        mb: 2,
      }}
    >
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 'bold',
            letterSpacing: 1,
            transition: 'transform 0.3s ease-in-out',
            '&:hover': {
              transform: 'scale(1.05)',
            },
          }}
        >
        </Typography>
        <Button
          variant="contained"
          color="secondary"
          startIcon={<AdminPanelSettingsIcon />}
          onClick={goToAdmin}
          sx={{
            borderRadius: 20,
            textTransform: 'none',
            fontWeight: 'medium',
            px: 2.5,
            py: 0.75,
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
              backgroundColor: '#c51162',
            },
          }}
        >
          Войти как администратор
        </Button>
      </Toolbar>
    </AppBar>
  );
};

const Home = ({ text, setText, report, setReport, loading, setLoading, openPreviewModal, setOpenPreviewModal, medications, setMedications, fuzzySearch, setFuzzySearch }) => {
  const handleTextChange = (event) => {
    setText(event.target.value);
  };

  const handleOnSave = (report) => {
    setReport(report);
  };

  const handleSearch = async () => {
    setLoading(true);
    const body = { text: text };
    if (fuzzySearch) body['fuzzy'] = true;

    const response = await fetch('http://127.0.0.1:8000/api/v1/find_medications/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    const data = await response.json();

    const highlightedText = data.highlighted_text;
    const medications = data.drugs;

    setReport(highlightedText);
    setMedications(medications);
    console.log(medications);
    setLoading(false);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([report], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'report.txt';
    document.body.appendChild(element);
    element.click();
  };

  return (
    <Container maxWidth="md">
      <HeaderBox>
        <Typography variant="h4">Поиск лекарств и побочных эффектов</Typography>
        <Typography variant="body1">
          Используйте это приложение для поиска лекарств и их побочных эффектов в научных текстах.
        </Typography>
      </HeaderBox>

      <SearchForm
        text={text}
        onTextChange={handleTextChange}
        onSearch={handleSearch}
        loading={loading}
        fuzzySearch={fuzzySearch}
        setFuzzySearch={setFuzzySearch}
      />

      {report && (
        <ReportContainer>
          <Typography variant="h6" sx={{ marginBottom: 2 }}>Отчет:</Typography>
          <Box sx={{ marginBottom: 2 }}>
            <Typography variant="body1" component="span">
              В отчете выделены найденные лекарственные препараты.
            </Typography>
            <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
          </Box>
          <ReportPreview
            report={report}
            onShowFullReport={() => setOpenPreviewModal(true)}
            onDownload={handleDownload}
            onSaveReport={handleOnSave}
          />
        </ReportContainer>
      )}

      <FullReportModal
        open={openPreviewModal}
        onClose={() => setOpenPreviewModal(false)}
        report={report}
        onDownload={handleDownload}
      />

      {report && medications.length > 0 && (
        <Box
          sx={{
            width: 'calc(100vw - 100px)',
            marginLeft: 'calc(-50vw + 50% + 16px)',
            marginRight: 'calc(-50vw + 50% + 16px)',
            paddingX: 4,
            marginTop: 14,
          }}
        >
          <ReportTable medications={medications} setMedications={setMedications}/>
        </Box>
      )}
    </Container>
  );
};

const App = () => {
  const [text, setText] = useState('');
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(false);
  const [openPreviewModal, setOpenPreviewModal] = useState(false);
  const [medications, setMedications] = useState([]);
  const [fuzzySearch, setFuzzySearch] = useState(false);

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Navbar />
        <Routes>
          <Route
            path="/"
            element={
              <Home
                text={text}
                setText={setText}
                report={report}
                setReport={setReport}
                loading={loading}
                setLoading={setLoading}
                openPreviewModal={openPreviewModal}
                setOpenPreviewModal={setOpenPreviewModal}
                medications={medications}
                setMedications={setMedications}
                fuzzySearch={fuzzySearch}
                setFuzzySearch={setFuzzySearch}
              />
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
};

export default App;