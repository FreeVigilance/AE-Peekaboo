import React, { useState, useEffect, useRef } from 'react';
import { Modal, Box, IconButton, Typography, CircularProgress, Button } from '@mui/material';
import { Check, Close } from '@mui/icons-material';

const EditReportModal = ({ open, onClose, report, onSave }) => {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editingText, setEditingText] = useState('');
  const inputRef = useRef(null);

  const clickTimer = useRef(null);
  const lastClick = useRef({ time: 0, index: null });
  const DOUBLE_CLICK_DELAY = 200;

  useEffect(() => {
    if (open) {
      setLoading(true);
      setEditingIndex(null);
      setTimeout(() => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(report, 'text/html');
        const nodes = Array.from(doc.body.childNodes);
        const parsedWords = [];

        const processText = (text, highlightColor = null) => {
          for (let i = 0; i < text.length; i++) {
            const char = text[i];
            if (/\s/.test(char)) {
              parsedWords.push({ text: char, highlightColor: null, isWord: false });
            } else {
              let word = char;
              while (i + 1 < text.length && !/\s/.test(text[i + 1])) {
                word += text[++i];
              }
              parsedWords.push({ text: word, highlightColor, isWord: true });
            }
          }
        };

        nodes.forEach((node) => {
          if (node.nodeType === Node.TEXT_NODE) {
            processText(node.textContent, null);
          } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'SPAN') {
            const style = node.getAttribute('style') || '';
            const isYellow = style.includes('background-color: yellow');
            const isLightGreen = style.includes('background-color: lightgreen');
            const highlightColor = isYellow ? 'yellow' : isLightGreen ? 'lightgreen' : null;
            processText(node.textContent, highlightColor);
          }
        });

        setWords(parsedWords);
        setLoading(false);
      }, 250);
    }
  }, [open, report]);

  const handleWordClick = (index) => {
    if (editingIndex === index) return;
    setWords((prevWords) =>
      prevWords.map((word, i) =>
        i === index
          ? {
              ...word,
              highlightColor:
                word.highlightColor === 'lightgreen'
                  ? null
                  : word.highlightColor === 'yellow'
                  ? null
                  : 'lightgreen',
            }
          : word
      )
    );
  };

  const handleDouble = (index) => {
    if (!words[index].isWord) return;
    setEditingIndex(index);
    setEditingText(words[index].text);
  };

  const handleCustomClick = (index) => {
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

  const handleEditChange = (e) => setEditingText(e.target.value);

  const commitEdit = () => {
    setWords((prev) =>
      prev.map((w, i) => (i === editingIndex ? { ...w, text: editingText } : w))
    );
    setEditingIndex(null);
    setEditingText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      inputRef.current.blur();
    } else if (e.key === 'Escape') {
      setEditingIndex(null);
      setEditingText('');
    }
  };

  const renderHighlightedText = () =>
    words.map((word, index) => {
      if (!word.isWord) return <span key={index}>{word.text}</span>;
      if (index === editingIndex) {
        return (
          <input
            key={index}
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
          key={index}
          onClick={() => handleCustomClick(index)}
          style={{
            cursor: 'pointer',
            backgroundColor: word.highlightColor || 'transparent',
            marginRight: '2px',
            wordWrap: 'break-word',
          }}
        >
          {word.text}
        </span>
      );
    });

  const handleSave = () => {
    const updatedReport = words
      .map((word) =>
        word.isWord && word.highlightColor
          ? `<span style="background-color: ${word.highlightColor}; font-weight: bold;">${word.text}</span>`
          : word.text
      )
      .join('');
    onSave(updatedReport);
    onClose();
  };

  const handleCancel = () => {
    setWords([]);
    setEditingIndex(null);
    setEditingText('');
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
          <Box
            sx={{
 створення: 'center',
              alignItems: 'center',
            }}
          >
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
            backgroundColor: 'white',
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