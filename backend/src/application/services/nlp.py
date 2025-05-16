from functools import lru_cache

import spacy

nlp = spacy.load("ru_core_news_sm")


@lru_cache(maxsize=10000)
def lemmatize(word):
    try:
        doc = nlp(word)
        return doc[0].lemma_
    except Exception:
        return word
