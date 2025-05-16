import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Menu,
  MenuItem,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from '@mui/material';
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';
import GetAppIcon from '@mui/icons-material/GetApp';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

const ReportTable = ({ medications, setMedications }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const openMenu = Boolean(anchorEl);
  const [openDialog, setOpenDialog] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentRow, setCurrentRow] = useState(null);
  const [formData, setFormData] = useState({
    trade_name: '',
    inn: '',
    obligation: '',
    source_countries: '',
    receiver: '',
    deadline_to_submit: '',
    format: '',
    other_procedures: '',
    type_of_event: '',
  });

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const exportToCSV = () => {
    const headers = [
      'Торговое наименование',
      'Международное торговое наименование',
      'Обязательство',
      'Страны регистрации препарата',
      'Держатель регистрационного удостоверения',
      'Дедлайн подачи',
      'Формат подачи',
      'Other procedures',
      'Серьезность',
    ];

    const csvRows = [
      headers.join(';'),
      ...medications.map(row =>
        [
          row.trade_name || '',
          row.inn || '',
          row.obligation || '',
          row.source_countries || '',
          row.receiver || '',
          row.deadline_to_submit || '',
          row.format || '',
          row.other_procedures || '',
          row.type_of_event || '',
        ]
          .map(cell => `"${cell.replace(/"/g, '""')}"`)
          .join(';')
      ),
    ];

    const csvContent = csvRows.join('\n');
    const foule = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    saveAs(foule, 'medications.csv');
    handleMenuClose();
  };

  const exportToXLSX = () => {
    const worksheetData = medications.map(row => ({
      'Торговое наименование': row.trade_name || '',
      'Международное торговое наименование': row.inn || '',
      'Обязательство': row.obligation || '',
      'Страны регистрации препарата': row.source_countries || '',
      'Держатель регистрационного удостоверения': row.receiver || '',
      'Дедлайн подачи': row.deadline_to_submit || '',
      'Формат подачи': row.format || '',
      'Другие процедуты': row.other_procedures || '',
      'Серьезность': row.type_of_event || '',
    }));

    const worksheet = XLSX.utils.json_to_sheet(worksheetData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Medications');
    XLSX.writeFile(workbook, 'medications.xlsx');
    handleMenuClose();
  };

  const handleAddRow = () => {
    setIsEditing(false);
    setFormData({
      trade_name: '',
      inn: '',
      obligation: '',
      source_countries: '',
      receiver: '',
      deadline_to_submit: '',
      format: '',
      other_procedures: '',
      type_of_event: '',
    });
    setOpenDialog(true);
  };

  const handleEditRow = (row, index) => {
    setIsEditing(true);
    setCurrentRow(index);
    setFormData({ ...row });
    setOpenDialog(true);
  };

  const handleDeleteRow = (index) => {
    setMedications(medications.filter((_, i) => i !== index));
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFormSubmit = () => {

    if (isEditing) {
      const updatedMedications = [...medications];
      updatedMedications[currentRow] = formData;
      setMedications(updatedMedications);
    } else {
      setMedications([...medications, formData]);
    }
    setOpenDialog(false);
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
  };

  return (
    <Box sx={{ position: 'relative' }}>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={handleAddRow}
        aria-label="Add new row"
        sx={{
          position: 'absolute',
          top: -48,
          left: 0,
          backgroundColor: '#1976d2',
          color: 'white',
          borderRadius: 2,
          textTransform: 'none',
          fontWeight: 'medium',
          px: 2.5,
          py: 0.75,
          transition: 'all 0.3s ease',
          '&:hover': {
            backgroundColor: '#1565c0',
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
            transform: 'translateY(-2px)',
          },
        }}
      >
        Добавить строку
      </Button>

      <IconButton
        onClick={handleMenuOpen}
        sx={{
          position: 'absolute',
          top: -48,
          right: 0,
          color: '#1976d2',
          backgroundColor: 'white',
          '&:hover': {
            backgroundColor: '#f5f5f5',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          },
          transition: 'all 0.3s ease',
          zIndex: 1,
        }}
        aria-label="Export options"
      >
        <GetAppIcon />
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={openMenu}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          },
        }}
      >
        <MenuItem
          onClick={exportToCSV}
          sx={{
            fontWeight: 'medium',
            color: '#1976d2',
            '&:hover': {
              backgroundColor: '#e3f2fd',
            },
          }}
        >
          Экспорт в CSV
        </MenuItem>
        <MenuItem
          onClick={exportToXLSX}
          sx={{
            fontWeight: 'medium',
            color: '#1976d2',
            '&:hover': {
              backgroundColor: '#e3f2fd',
            },
          }}
        >
          Экспорт в XLSX
        </MenuItem>
      </Menu>

      <Dialog open={openDialog} onClose={handleDialogClose} maxWidth="md" fullWidth>
        <DialogTitle>{isEditing ? 'Редактировать строку' : 'Добавить новую строку'}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="trade_name"
            label="Торговое наименование"
            type="text"
            fullWidth
            value={formData.trade_name}
            onChange={handleFormChange}
          />
          <TextField
            margin="dense"
            name="inn"
            label="Международное торговое наименование"
            type="text"
            fullWidth
            value={formData.inn}
            onChange={handleFormChange}
          />
          <TextField
            margin="dense"
            name="obligation"
            label="Обязательство"
            type="text"
            fullWidth
            value={formData.obligation}
            onChange={handleFormChange}
          />
          <TextField
            margin="dense"
            name="source_countries"
            label="Страны регистрации препарата"
            type="text"
            fullWidth
            value={formData.source_countries}
            onChange={handleFormChange}
          />
          <TextField
            margin="dense"
            name="receiver"
            label="Держатель регистрационного удостоверения"
            type="text"
            fullWidth
            value={formData.receiver}
            onChange={handleFormChange}
          />
          <TextField
            margin="dense"
            name="deadline_to_submit"
            label="Дедлайн подачи"
            type="text"
            fullWidth
            value={formData.deadline_to_submit}
            onChange={handleFormChange}
          />
                      <TextField
            margin="dense"
            name="type_of_event"
            label="Серьезность"
            type="text"
            fullWidth
            value={formData.type_of_event}
            onChange={handleFormChange}
          />
          <TextField
            margin="dense"
            name="format"
            label="Формат подачи"
            type="text"
            fullWidth
            value={formData.format}
            onChange={handleFormChange}
          />
          <TextField
            margin="dense"
            name="other_procedures"
            label="Другие процедуры"
            type="text"
            fullWidth
            value={formData.other_procedures}
            onChange={handleFormChange}
          />

        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Отмена</Button>
          <Button onClick={handleFormSubmit} variant="contained">
            {isEditing ? 'Сохранить' : 'Добавить'}
          </Button>
        </DialogActions>
      </Dialog>

      <TableContainer
        component={Paper}
        sx={{
          marginTop: 4,
          borderRadius: 2,
          boxShadow: 3,
          maxWidth: '100%',
          maxHeight: 600,
          overflowX: 'auto',
          overflowY: 'auto',
        }}
      >
        <Table sx={{ minWidth: 1200 }} stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 150,
                  backgroundColor: '#1976d2',
                }}
              >
                Действия
              </TableCell>
              <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 200,
                  backgroundColor: '#1976d2',
                }}
              >
                Торговое наименование
              </TableCell>
              <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 200,
                  backgroundColor: '#1976d2',
                }}
              >
                Международное торговое наименование
              </TableCell>
              <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 150,
                  backgroundColor: '#1976d2',
                }}
              >
                Обязательство
              </TableCell>
              <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 200,
                  backgroundColor: '#1976d2',
                }}
              >
                Страны регистрации препарата
              </TableCell>
              <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 250,
                  backgroundColor: '#1976d2',
                }}
              >
               Держатель регистрационного удостоверения
              </TableCell>
              <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 150,
                  backgroundColor: '#1976d2',
                }}
              >
                Дедлайн подачи
              </TableCell>
                <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 120,
                  backgroundColor: '#1976d2',
                }}
              >
                Серьезность
              </TableCell>
              <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 120,
                  backgroundColor: '#1976d2',
                }}
              >
                Формат подачи
              </TableCell>
              <TableCell
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 200,
                  backgroundColor: '#1976d2',
                }}
              >
                Другие процедуры
              </TableCell>

            </TableRow>
          </TableHead>
          <TableBody>
            {medications.map((row, index) => (
              <TableRow key={index} sx={{ '&:nth-of-type(odd)': { backgroundColor: '#f5f5f5' } }}>
                <TableCell>
                  <IconButton onClick={() => handleEditRow(row, index)} aria-label="Edit row">
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDeleteRow(index)} aria-label="Delete row">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
                <TableCell>{row.trade_name}</TableCell>
                <TableCell>{row.inn || ''}</TableCell>
                <TableCell>{row.obligation || ''}</TableCell>
                <TableCell>{row.source_countries || ''}</TableCell>
                <TableCell>{row.receiver || ''}</TableCell>
                <TableCell>{row.deadline_to_submit || ''}</TableCell>
                                  <TableCell>{row.type_of_event || ''}</TableCell>

                <TableCell>{row.format || ''}</TableCell>
                <TableCell>{row.other_procedures || ''}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default ReportTable;