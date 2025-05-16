import React from 'react';
import { Modal, Box, Typography, IconButton } from '@mui/material';
import { Close } from '@mui/icons-material';

const FullReportModal = ({ open, onClose, report }) => {
  return (
    <Modal open={open} onClose={onClose}>
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '80%',
          maxHeight: '90vh',
          backgroundColor: 'white',
          padding: 4,
          borderRadius: 2,
          boxShadow: 3,
          overflow: 'hidden',
        }}
      >
        <IconButton
          onClick={onClose}
          sx={{
            position: 'absolute',
            top: '8px',
            right: '8px',
            zIndex: 10,
            color: '#1976d2',
            '&:hover': {
              backgroundColor: 'rgba(25, 118, 210, 0.1)',
              transform: 'scale(1.1)',
            },
            transition: 'transform 0.2s ease, background-color 0.2s ease',
          }}
        >
          <Close sx={{ fontSize: '1.5rem' }} />
        </IconButton>

        <Box
          sx={{
            maxHeight: '75vh',
            overflowY: 'auto',
            marginTop: 4,
          }}
        >
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
        </Box>
      </Box>
    </Modal>
  );
};

export default FullReportModal;
