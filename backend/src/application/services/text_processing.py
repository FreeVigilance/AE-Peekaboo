import asyncio
import math
import os
import time

import ahocorasick
from fastapi import Depends
from rapidfuzz.distance import DamerauLevenshtein

from src.application.services.nlp import lemmatize, nlp
from src.infrastructure.repositories.drugs import DrugsRepo
from src.infrastructure.schemas.text_processing import DrugTable


class BKTree:

    class Node:
        def __init__(self, word: str, drug_id: int):
            self.word = word
            self.drug_id = drug_id
            self.children = {}

    def __init__(self, distance_func):
        self.root = None
        self.distance_func = distance_func

    def add(self, word: str, drug_id: int):
        """Add a word with its drug ID to the BK-tree."""
        if not word:
            return
        if not self.root:
            self.root = self.Node(word, drug_id)
            return
        current = self.root
        while True:
            dist = self.distance_func(word, current.word)
            if dist in current.children:
                current = current.children[dist]
            else:
                current.children[dist] = self.Node(word, drug_id)
                break

    def search(self, word: str, max_dist: int) -> list[tuple[str, int, int]]:
        """Search for words within max_dist of the query word, returning (word, drug_id, distance)."""
        if not self.root:
            return []
        results = []
        self._search_recursive(self.root, word, max_dist, results)
        return results

    def _search_recursive(
        self, node: Node, word: str, max_dist: int, results: list
    ):
        if not node:
            return
        dist = self.distance_func(word, node.word)
        if dist <= max_dist:
            results.append((node.word, node.drug_id, dist))
        min_dist = max(0, dist - max_dist)
        max_dist_bound = dist + max_dist
        for child_dist in range(int(min_dist), int(max_dist_bound) + 1):
            if child_dist in node.children:
                self._search_recursive(
                    node.children[child_dist], word, max_dist, results
                )


class TextProcessingService:
    """Сервис обработки текста."""

    _prepositions_to_exclude = {
        "в",
        "на",
        "с",
        "по",
        "для",
        "из",
        "к",
        "у",
        "о",
        "об",
        "от",
        "при",
        "про",
        "над",
        "под",
        "а",
        "но",
    }

    def __init__(self, repo: DrugsRepo = Depends()):
        self._repo = repo
        self._bk_tree = None

    async def _initialize_bk_tree(self, drugs):
        if self._bk_tree is None:
            self._bk_tree = BKTree(
                lambda s1, s2: int(
                    DamerauLevenshtein.distance(s1.lower(), s2.lower())
                )
            )
            for drug in drugs:
                if drug.trade_name and len(drug.trade_name) > 3:
                    self._bk_tree.add(drug.trade_name.lower(), drug.id)
                if drug.inn and len(drug.inn) > 3:
                    self._bk_tree.add(drug.inn.lower(), drug.id)

    async def find_medications(
        self, automaton: ahocorasick.Automaton, text: str, fuzzy: bool
    ):
        text, ids, matches = await self.highlight_medications_in_text(
            automaton, text, fuzzy=fuzzy
        )
        founded_words = [match[-1] for match in matches]
        print(founded_words)
        drugs_data = await self._repo.get_drug_info(ids, founded_words)
        drugs_data = [DrugTable.model_validate(drug) for drug in drugs_data]
        return {"highlighted_text": text, "drugs": drugs_data}

    @staticmethod
    async def _process_token_chunk(
        token_data: list[tuple[str, int, int]],
        bk_tree_data: tuple,
        existing_matches: list[tuple[int, int, str, int, str]],
    ) -> tuple[list[tuple[int, int, str, int, str]], set[int]]:
        """Синхронная обработка подмножества токенов для нечеткого поиска с BK-деревом."""
        bk_tree = BKTree(
            lambda s1, s2: int(
                DamerauLevenshtein.distance(s1.lower(), s2.lower())
            )
        )
        for word, drug_id in bk_tree_data:
            bk_tree.add(word, drug_id)

        matches = []
        founded_drugs_ids = set()

        for text, idx, length in token_data:
            if not text.isalpha() or len(text) < 3:
                continue
            lemmatized_word = lemmatize(text.lower()).strip()
            if not lemmatized_word:
                continue

            start = idx
            end = idx + length
            is_already_matched = any(
                m[0] <= start < m[1] or m[0] < end <= m[1]
                for m in existing_matches
            )
            if is_already_matched:
                continue

            max_dist = 1
            candidates = bk_tree.search(lemmatized_word, max_dist)

            best_candidate = None
            min_dist = float("inf")
            query_first_char = lemmatized_word[0] if lemmatized_word else ""
            for word, drug_id, dist in candidates:
                if word and word[0].lower() == query_first_char.lower():
                    if dist < min_dist:
                        min_dist = dist
                        best_candidate = (drug_id, dist)

            if best_candidate and best_candidate[0] not in founded_drugs_ids:
                drug_id, _ = best_candidate
                matches.append((start, end, text, drug_id, "yellow"))
                founded_drugs_ids.add(drug_id)

        return matches, founded_drugs_ids

    async def highlight_medications_in_text(
        self, automaton: ahocorasick.Automaton, text: str, fuzzy=False
    ) -> tuple:
        all_drugs = await self._repo.get_all_drugs()
        matches = []
        founded_drugs_ids = set()

        doc = nlp(text)

        potential_matches = []

        for start_idx in range(len(doc)):
            if not doc[start_idx].text.isalpha():
                continue
            for end_idx in range(
                start_idx + 1, min(start_idx + 8, len(doc)) + 1
            ):
                original_phrase = " ".join(
                    [token.text for token in doc[start_idx:end_idx]]
                )
                lower_original_phrase = original_phrase.lower()
                lemmatized_phrase = " ".join(
                    [
                        lemmatize(word)
                        for word in lower_original_phrase.split(" ")
                    ]
                )
                striped_phrase = lemmatized_phrase.strip()
                for _, (value, id, word) in automaton.iter(striped_phrase):
                    damerau_levenshtein_distance = (
                        DamerauLevenshtein.normalized_similarity(
                            value, striped_phrase
                        )
                    )
                    if not damerau_levenshtein_distance >= 0.8:
                        continue
                    start = doc[start_idx].idx
                    end = doc[end_idx - 1].idx + len(doc[end_idx - 1].text)
                    phrase_to_highlight = str(doc[start_idx:end_idx])
                    potential_matches.append(
                        {
                            "start": start,
                            "end": end,
                            "phrase": phrase_to_highlight,
                            "id": id,
                            "color": "lightgreen",
                            "word_count": len(phrase_to_highlight.split()),
                            "word": word,
                        }
                    )

        matches = []
        processed_ranges = set()
        for match in sorted(
            potential_matches, key=lambda x: (-x["word_count"], x["start"])
        ):
            start, end = match["start"], match["end"]
            is_overlapping = False
            for processed_start, processed_end in processed_ranges:
                if not (end <= processed_start or start >= processed_end):
                    is_overlapping = True
                    break
            if not is_overlapping:
                matches.append(
                    (start, end, match["phrase"], match["id"], match["color"], match['word'])
                )
                processed_ranges.add((start, end))
                founded_drugs_ids.add(match["id"])

        if not fuzzy:
            return (
                await self._highlight_matches(text, matches),
                founded_drugs_ids,
                matches
            )

        await self._initialize_bk_tree(all_drugs)

        bk_tree_data = []
        for drug in all_drugs:
            if drug.trade_name and len(drug.trade_name) > 3:
                bk_tree_data.append((drug.trade_name.lower(), drug.id))
            if drug.inn and len(drug.inn) > 3:
                bk_tree_data.append((drug.inn.lower(), drug.id))

        token_data = [
            (token.text, token.idx, len(token.text)) for token in doc
        ]
        chunk_matches, chunk_ids = await self._process_token_chunk(token_data, bk_tree_data, matches)

        matches.extend(chunk_matches)
        founded_drugs_ids.update(chunk_ids)
        return await self._highlight_matches(text, matches), founded_drugs_ids, matches

    @staticmethod
    async def _highlight_matches(highlighted_text, matches):
        sorted_matches = sorted(matches, key=lambda x: (x[0], -(x[1] - x[0])))
        filtered_matches = []
        last_end = -1
        for start, end, word, drug_id, color, _ in sorted_matches:
            if start >= last_end:
                filtered_matches.append((start, end, word, drug_id, color))
                last_end = end

        offset = 0
        for start, end, word, drug_id, color in filtered_matches:
            words = word.split()
            preposition = ""
            highlighted_word = word
            if (
                words
                and words[0].lower()
                in TextProcessingService._prepositions_to_exclude
            ):
                preposition = words[0] + " "
                highlighted_word = " ".join(words[1:])
            if highlighted_word and highlighted_word[-1] in ".,-":
                highlighted_part = highlighted_word[:-1]
                replacement = f'{preposition}<span style="background-color: {color}; font-weight: bold;">{highlighted_part}</span>{highlighted_word[-1]}'
            else:
                replacement = f'{preposition}<span style="background-color: {color}; font-weight: bold;">{highlighted_word}</span>'
            highlighted_text = (
                highlighted_text[: start + offset]
                + replacement
                + highlighted_text[end + offset :]
            )
            offset += len(replacement) - (end - start)
        return highlighted_text
