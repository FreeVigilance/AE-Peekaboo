from functools import lru_cache

import spacy

nlp = spacy.load('ru_core_news_sm')


@lru_cache(maxsize=1000)
def lemmatize(word):
    doc = nlp(word)
    return doc[0].lemma_