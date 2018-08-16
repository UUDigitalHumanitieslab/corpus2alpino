#!/usr/bin/env python3
"""
Module for converting FoLiA xml files to parsable utterances.
"""

from typing import Iterable

import ucto
from pynlpl.formats import folia

from .alpino_brackets import escape_id, escape_word, format_add_lex, format_folia
from corpus2alpino.abstracts import Reader
from corpus2alpino.models import CollectedFile, Document, MetadataValue, Utterance


class FoliaReader(Reader):
    """
    Class for converting FoLiA xml files to documents.
    """

    def __init__(self, tokenizer=None) -> None:
        self.tokenizer = tokenizer if tokenizer else ucto.Tokenizer(
            "tokconfig-nld")

    def read(self, collected_file: CollectedFile) -> Iterable[Document]:
        try:
            doc = folia.Document(string=collected_file.content,
                                 autodeclare=True,
                                 loadsetdefinitions=False)
            self.tokenize(doc)
            doc_metadata = self.get_metadata_dict(doc.metadata.items())

            yield Document(collected_file,
                           list(self.get_utterances(doc, doc_metadata)),
                           doc_metadata)
        except Exception as e:
            raise Exception(collected_file.relpath + "/" +
                            collected_file.filename) from e

    def tokenize(self, element):
        """
        Tokenizes all the text which isn't tokenized yet.
        """

        for item in element:
            if isinstance(item, folia.AbstractElement):
                if isinstance(item, folia.Paragraph):
                    for sentence in item.sentences():
                        break
                    else:
                        self.tokenize_paragraph(item)
                else:
                    self.tokenize(item)

    def tokenize_paragraph(self, paragraph):
        text = ''
        for textContent in paragraph.select(folia.TextContent):
            text += textContent.text()
        self.tokenizer.process(text)
        for line in self.tokenizer.sentences():
            sentence = paragraph.add(folia.Sentence)
            for word in line.split(' '):
                if word:
                    sentence.add(folia.Word, word)

    def get_utterances(self, doc, doc_metadata):
        """
        Read FoLiA file and return Alpino parsable sentences.
        """

        paragraph = None
        sentence = None
        words = []

        for word in doc.words():
            # new utterance: different sentence/paragraph
            try:
                word_sentence = word.sentence()
            except folia.NoSuchAnnotation:
                word_sentence = None
            try:
                word_paragraph = word.paragraph()
            except folia.NoSuchAnnotation:
                word_paragraph = None

            if word_sentence != sentence or word_paragraph != paragraph:
                if words:
                    if sentence or paragraph:
                        yield self.create_utterance(paragraph, sentence, words, doc_metadata)
                    words = []
                sentence = word_sentence
                paragraph = word_paragraph

            words.append(word)

        if words and (sentence or paragraph):
            yield self.create_utterance(paragraph, sentence, words, doc_metadata)

    def create_utterance(self, paragraph, sentence, words, doc_metadata):
        """
        Convert a FoLiA object to an Alpino compatible string to parse.
        """

        word_strings = map(lambda word: self.get_word_string(word), words)
        line = " ".join(filter(lambda word: word != '', word_strings))

        if sentence:
            container = sentence
        else:
            container = paragraph

        sentence_id = escape_id(container.id)
        sentence_metadata = self.get_metadata_dict(
            container.getmetadata().items(),
            doc_metadata)

        return Utterance(line, sentence_id, sentence_metadata, line)

    def get_word_string(self, word):
        """
        Get a string representing this word and any additional known properties to add to the parse.
        """

        try:
            text = word.toktext()
        except folia.NoSuchText:
            text = None

        if text == None:
            data = word.data
            for item in data:
                if type(item) == folia.TextContent:
                    text = item.text()
                    break
            else:
                return ''

        try:
            correction = word.getcorrection()

            if correction.hastext() and correction.text() != text:
                return format_add_lex(correction.text(), text)
        except folia.NoSuchAnnotation:
            pass

        try:
            lemma = word.lemma()
            pos = word.pos()

            if lemma and pos:
                return format_folia(lemma, pos, text)
        except folia.NoSuchAnnotation:
            pass

        return escape_word(text)

    def get_metadata_dict(self, native_metadata, filter_by=None):
        metadata = {}
        for key, value in native_metadata:
            if filter_by == None or not key in filter_by \
                    or filter_by[key].value != value:
                metadata[key] = MetadataValue(value)
        return metadata

    def test_file(self, file: CollectedFile):
        """
        Determine whether this is a FoLiA XML file
        """

        return '<FoLiA' in file.content[0:400]
