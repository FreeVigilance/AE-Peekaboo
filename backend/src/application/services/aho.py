import re

import ahocorasick
from fastapi import Depends

from src.application.services.nlp import lemmatize
from src.infrastructure.models import Drug
from src.infrastructure.repositories.drugs import DrugsRepo


class AhoCorasickService:

    def __init__(self, repo: DrugsRepo = Depends()):
        self._repo = repo

    @staticmethod
    def surround_non_alphanumeric_with_spaces(text: str) -> str:
        """
        Окружает все непробельные символы, не являющиеся буквами или цифрами, пробелами,
        избегая лишних пробелов.

        Args:
            text: Входной текст.

        Returns:
            Текст с пробелами вокруг непробельных символов (кроме букв и цифр).
        """

        result = re.sub(r"(\W)", r" \1 ", text)
        result = re.sub(r"\s+", " ", result).strip()
        return result

    async def build_aho_corasick(self) -> ahocorasick.Automaton:
        drugs = await self._repo.get_all_drugs()
        automaton = ahocorasick.Automaton()
        for drug in drugs:
            await self.add_drug_to_automation(automaton, drug)
        automaton.make_automaton()
        return automaton

    @staticmethod
    async def add_drug_to_automation(
        automation: ahocorasick.Automaton, drug: Drug
    ):
        for word in (drug.trade_name, drug.inn):
            if not word:
                continue
            normalized = (
                AhoCorasickService.surround_non_alphanumeric_with_spaces(
                    word
                ).lower()
            )
            normalized_splited = [
                lemmatize(word_) for word_ in normalized.split(" ")
            ]
            for i in range(len(normalized.split(" "))):
                sentence_word = " ".join(normalized_splited[: i + 1])
                automation.add_word(
                    sentence_word.lower(), (normalized, drug.id, word)
                )

                if normalized != sentence_word.lower():
                    automation.add_word(normalized, (normalized, drug.id, word))
        return automation
