import re

import ahocorasick
from fastapi import Depends

from src.application.services.nlp import nlp, lemmatize
from src.infrastructure.repositories.drugs import DrugsRepo


class AhoCorasickService:

    def __init__(self, repo: DrugsRepo = Depends()):
        self._repo = repo

    @staticmethod
    def surround_non_alphanumeric_with_spaces(text: str) -> str:
        result = re.sub(r'(\W)', r' \1 ', text)
        result = re.sub(r'\s+', ' ', result).strip()
        return result

    async def build_aho_corasick(self) -> ahocorasick.Automaton:
        drugs_names = await self._repo.get_all_trade_names()
        automaton = ahocorasick.Automaton()
        for word in drugs_names:
            normalized = AhoCorasickService.surround_non_alphanumeric_with_spaces(word).lower()
            normalized_splited = [lemmatize(word_) for word_ in normalized.split(' ')]
            for i in range(len(normalized.split(' '))):
                sentence_word = ' '.join(normalized_splited[:i + 1])
                automaton.add_word(sentence_word.lower(), normalized)
                # normalized = surround_non_alphanumeric_with_spaces(sentence_word).lower()
                if normalized != sentence_word.lower():
                    automaton.add_word(normalized, normalized)
        automaton.make_automaton()
        return automaton
