import React, { useState } from 'react';
import { Box, Typography, IconButton } from '@mui/material';
import { Visibility, Edit } from '@mui/icons-material';
import DownloadButton from '../DownloadButton';
import { ReportBox, PreviewReport } from '../UI/styles';
import EditReportModal from './EditReportModal';

const ReportPreview = ({ report, onShowFullReport, onDownload, onSaveReport }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleEditClick = () => setIsModalOpen(true);

  const handleCloseModal = () => setIsModalOpen(false);

  return (
    <ReportBox
      sx={{
        position: 'relative',
        borderRadius: 2,
        boxShadow: 3,
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          zIndex: 10,
          backgroundColor: 'white',
          borderRadius: '50%',
          boxShadow: 1,
        }}
      >
        <IconButton
          onClick={handleEditClick}
          aria-label="Редактировать отчет"
          sx={{
            color: '#1976d2',
            '&:hover': {
              backgroundColor: 'rgba(25, 118, 210, 0.1)',
              transform: 'scale(1.1)',
            },
            transition: 'transform 0.2s ease, background-color 0.2s ease',
          }}
        >
          <Edit sx={{ fontSize: '1.2rem' }} />
        </IconButton>
      </Box>

      <PreviewReport sx={{ padding: '16px', backgroundColor: '#fafafa' }}>
        <Typography
          variant="body1"
          component="div"
        sx={{
          lineHeight: 1.6,
          color: '#333',
          fontSize: '1rem',
          whiteSpace: 'pre-wrap',
        }}
        dangerouslySetInnerHTML={{ __html: report }}
        />
       </PreviewReport>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', padding: '8px 16px', backgroundColor: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton
            onClick={onShowFullReport}
            aria-label="Просмотреть полный отчет"
            sx={{
              color: '#1976d2',
              '&:hover': {
                backgroundColor: 'rgba(25, 118, 210, 0.1)',
                transform: 'scale(1.1)',
              },
              transition: 'transform 0.2s ease, background-color 0.2s ease',
            }}
          >
            <Visibility sx={{ fontSize: '1.5rem' }} />
          </IconButton>
          <Typography variant="body1" sx={{ marginLeft: 1, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>
            Просмотреть полный отчет
          </Typography>
        </Box>
        <DownloadButton report={report} onDownload={onDownload} />
      </Box>

      <EditReportModal
        open={isModalOpen}
        onClose={handleCloseModal}
        report={report}
        onSave={onSaveReport}
      />
    </ReportBox>
  );
};

export default ReportPreview;
