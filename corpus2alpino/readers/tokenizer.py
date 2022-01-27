#!/usr/bin/env python3
from spacy.tokens.span import Span
from spacy.lang.nl import Dutch


class Sentence:
    def __init__(self, span: Span):
        self.span = span

    def tokens(self):
        for token in self.span:
            yield token.text

    def text(self) -> str:
        return ' '.join(self.tokens())


class Tokenizer:
    def __init__(self):
        self.nlp = Dutch()
        self.nlp.add_pipe("sentencizer")

    def process(self, text: str):
        self.doc = self.nlp(text)

        return self.sentences()

    def sentences(self):
        for sentence in self.doc.sents:
            yield Sentence(sentence)
