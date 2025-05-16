import React, { useState, useEffect, useRef } from 'react';
import { Modal, Box, Button, IconButton, Typography, CircularProgress } from '@mui/material';
import { Close } from '@mui/icons-material';

const EditReportModal = ({ open, onClose, report, onSave }) => {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editingText, setEditingText] = useState('');
  const inputRef = useRef(null);

  const clickTimer = useRef(null);
  const lastClick = useRef({ time: 0, index: null });
  const DOUBLE_CLICK_DELAY = 200; // порог в миллисекундах

  useEffect(() => {
    if (open) {
      setLoading(true);
      setEditingIndex(null);
      setTimeout(() => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(report, 'text/html');
        const nodes = Array.from(doc.body.childNodes);
        const parsedWords = [];

        const processText = (text, isHighlighted = false) => {
          for (let i = 0; i < text.length; i++) {
            const char = text[i];
            if (/\s/.test(char)) {
              parsedWords.push({ text: char, highlighted: false, isWord: false });
            } else {
              let word = char;
              while (i + 1 < text.length && !/\s/.test(text[i + 1])) {
                word += text[++i];
              }
              parsedWords.push({ text: word, highlighted: isHighlighted, isWord: true });
            }
          }
        };

        nodes.forEach(node => {
          if (node.nodeType === Node.TEXT_NODE) {
            processText(node.textContent, false);
          } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'SPAN') {
            const style = node.getAttribute('style') || '';
            const isHighlighted = style.includes('background-color: yellow');
            processText(node.textContent, isHighlighted);
          }
        });

        setWords(parsedWords);
        setLoading(false);
      }, 250);
    }
  }, [open, report]);

  const handleWordClick = index => {
    if (editingIndex === index) return;
    setWords(prev =>
      prev.map((w, i) => (i === index ? { ...w, highlighted: !w.highlighted } : w))
    );
  };

  const handleDouble = index => {
    if (!words[index].isWord) return;
    setEditingIndex(index);
    setEditingText(words[index].text);
  };

  const handleCustomClick = index => {
    const now = Date.now();
    if (lastClick.current.index === index && now - lastClick.current.time < DOUBLE_CLICK_DELAY) {
      clearTimeout(clickTimer.current);
      lastClick.current = { time: 0, index: null };
      handleDouble(index);
    } else {
      lastClick.current = { time: now, index };
      clickTimer.current = setTimeout(() => {
        handleWordClick(index);
        lastClick.current = { time: 0, index: null };
      }, DOUBLE_CLICK_DELAY);
    }
  };

  const handleEditChange = e => setEditingText(e.target.value);

  const commitEdit = () => {
    setWords(prev =>
      prev.map((w, i) => (i === editingIndex ? { ...w, text: editingText } : w))
    );
    setEditingIndex(null);
    setEditingText('');
  };

  const handleKeyDown = e => {
    if (e.key === 'Enter') {
      e.preventDefault();
      inputRef.current.blur();
    } else if (e.key === 'Escape') {
      setEditingIndex(null);
      setEditingText('');
    }
  };

  const renderHighlightedText = () =>
    words.map((word, i) => {
      if (!word.isWord) return <span key={i}>{word.text}</span>;
      if (i === editingIndex) {
        return (
          <input
            key={i}
            ref={inputRef}
            value={editingText}
            onChange={handleEditChange}
            onBlur={commitEdit}
            onKeyDown={handleKeyDown}
            style={{
              fontSize: '1rem',
              lineHeight: 1.6,
              border: '1px dashed #999',
              padding: '2px',
              marginRight: '2px',
            }}
            autoFocus
          />
        );
      }
      return (
        <span
          key={i}
          onClick={() => handleCustomClick(i)}
          style={{
            cursor: 'pointer',
            backgroundColor: word.highlighted ? 'yellow' : 'transparent',
            marginRight: '2px',
            wordWrap: 'break-word',
          }}
        >
          {word.text}
        </span>
      );
    });

  const handleSave = () => {
    const updated = words
      .map(w => {
        if (!w.isWord) return w.text;
        return w.highlighted
          ? `<span style="background-color: yellow;">${w.text}</span>`
          : w.text;
      })
      .join('');
    onSave(updated);
    onClose();
  };

  const handleCancel = () => {
    setWords([]);
    onClose();
  };

  return (
    <Modal open={open} onClose={handleCancel} closeAfterTransition>
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          bgcolor: 'white',
          borderRadius: 2,
          boxShadow: 24,
          width: '80%',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          outline: 'none',
        }}
      >
        <IconButton
          onClick={handleCancel}
          sx={{ position: 'absolute', top: 8, right: 8 }}
          aria-label="Закрыть"
          size="small"
        >
          <Close fontSize="small" />
        </IconButton>

        <Typography variant="h6" sx={{ p: 2, borderBottom: '1px solid #ddd' }}>
          Редактирование отчета
        </Typography>

        <Typography
          variant="body1"
          sx={{
            px: 2,
            pb: 1,
            fontSize: '1rem',
            color: 'text.secondary',
            borderBottom: '1px solid #ddd',
          }}
        >
          Нажмите на слово, чтобы выделить / снять выделение цветом.<br />
          Дважды нажмите, чтобы исправить опечатку в слове.
        </Typography>

        {loading ? (
          <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <CircularProgress size={40} />
          </Box>
        ) : (
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              p: 2,
              fontSize: '1rem',
              backgroundColor: '#fafafa',
              lineHeight: 1.6,
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word',
            }}
          >
            {renderHighlightedText()}
          </Box>
        )}

        <Box
          sx={{
            borderTop: '1px solid #ddd',
            p: 2,
            display: 'flex',
            justifyContent: 'flex-end',
            position: 'sticky',
            bottom: 0,
            bgcolor: 'white',
          }}
        >
          <Button onClick={handleCancel} sx={{ mr: 1 }}>
            Отменить изменения
          </Button>
          <Button variant="contained" onClick={handleSave}>
            Сохранить изменения
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default EditReportModal;
