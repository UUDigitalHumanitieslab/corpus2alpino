#!/usr/bin/env python3
from spacy.tokenizer import Tokenizer
from spacy.lang.nl import Dutch
nlp = Dutch()
nlp.add_pipe("sentencizer")


class Sentence:
    def __init__(self, text: str):
        self.text = text

    def tokens(self):
        for token in nlp.tokenizer():
            yield token.text


def tokenizer(text: str):
    doc = nlp(text)
    for sentence in doc.sents:
        yield Sentence(sentence.text)
