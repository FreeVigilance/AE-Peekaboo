import React from 'react';
import { Button} from '@mui/material';
import { FileDownload } from '@mui/icons-material';

const DownloadButton = ({ report }) => {

  const handleDownload = async () => {

      const formattedReport = report.replace(/\n/g, '<br>');

      const fullHtml = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>Медицинский отчет</title>
          <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
          <style>
            body {
              font-family: 'Roboto', Arial, sans-serif;
              font-size: 12pt;
              margin: 20px;
              line-height: 1.5;
              white-space: pre-wrap;
              overflow: visible;
            }
            h1 {
              font-size: 16pt;
              margin-bottom: 20px;
            }
            p {
              margin: 0 0 15px 0;
              min-height: auto;
              overflow: visible;
            }
            span[style*="background-color: lightgreen"] {
              background-color: lightgreen;
              font-weight: bold;
              padding: 3px 6px;
              border-radius: 3px;
            }
            br {
              display: block;
              margin-bottom: 10px;
            }
          </style>
        </head>
        <body>
          <h1>Медицинский отчет</h1>
          ${formattedReport}
        </body>
        </html>
      `;

      const blob = new Blob([fullHtml], { type: 'text/html' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Отчет_по_поиску.html');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);


  };

  return (
    <>
      <Button
        variant="outlined"
        color="primary"
        sx={{
          textTransform: 'none',
          fontWeight: 'bold',
          padding: '8px 16px',
          borderRadius: '8px',
          '&:hover': {
            backgroundColor: 'rgba(25, 118, 210, 0.15)',
          },
        }}
        startIcon={<FileDownload />}
        onClick={handleDownload}
      >
        Скачать отчет
      </Button>
        </>
  );
};

export default DownloadButton;