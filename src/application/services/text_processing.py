"""Содержит сервис для управления событиями."""

import ahocorasick
import textdistance
from fastapi import Depends
from src.application.services.nlp import lemmatize, nlp
from src.infrastructure.repositories.drugs import DrugsRepo


class TextProcessingService:
    """Сервис обработки текста."""
    def __init__(self, repo: DrugsRepo = Depends()):
        self._repo = repo

    async def highlight_medications_in_text(self, automaton: ahocorasick.Automaton, text: str) -> str:
        matches = []

        doc = nlp(text)
        for start_idx in range(len(doc)):
            is_phrase_start_found = False
            if not doc[start_idx].text.isalpha(): continue
            for end_idx in range(start_idx + 1, min(start_idx + 8, len(doc)) + 1):
                original_phrase = ' '.join([token.text for token in doc[start_idx:end_idx]])
                lower_original_phrase = original_phrase.lower()
                lemmatized_phrase = ' '.join([lemmatize(word) for word in lower_original_phrase.split(' ')])
                striped_phrase = lemmatized_phrase.strip()
                for _, value in automaton.iter(striped_phrase):
                    if striped_phrase.startswith('кет'):
                        print(striped_phrase, value)
                    damerau_levenshtein_distance = textdistance.damerau_levenshtein.normalized_similarity(value, striped_phrase)
                    if not damerau_levenshtein_distance >= 0.85:
                        continue

                    start = doc[start_idx].idx
                    end = doc[end_idx - 1].idx + len(doc[end_idx - 1].text)
                    phrase_to_highlight = str(doc[start_idx:end_idx])
                    matches.append((start, end, phrase_to_highlight))
                    continue
        return await self._highlight_matches(text, matches)

    @staticmethod
    async def _highlight_matches(highlighted_text, matches):
        sorted_matches = sorted(matches, key=lambda x: (x[0], -(x[1] - x[0])))
        filtered_matches = []
        last_end = -1
        for start, end, word in sorted_matches:
            if start >= last_end:
                filtered_matches.append((start, end, word))
                last_end = end

        offset = 0
        for start, end, word in filtered_matches:
            if word and word[-1] in '.,':
                highlighted_word = word[:-1]
                replacement = f'<span style="background-color: yellow; font-weight: bold;">{highlighted_word}</span>{word[-1]}'
            else:
                replacement = f'<span style="background-color: yellow; font-weight: bold;">{word}</span>'
            # replacement = f'<span style="background-color: yellow; font-weight: bold;">{word}</span>'
            highlighted_text = (
                    highlighted_text[:start + offset] + replacement + highlighted_text[end + offset:]
            )
            offset += len(replacement) - (end - start)

        return highlighted_text
