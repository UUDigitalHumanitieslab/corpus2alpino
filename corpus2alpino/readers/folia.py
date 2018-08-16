#!/usr/bin/env python3
"""
Module for converting FoLiA xml files to parsable utterances.
"""

from typing import Iterable

from pynlpl.formats import folia

from .alpino_brackets import escape_id, escape_word, format_add_lex, format_folia
from corpus2alpino.abstracts import Reader
from corpus2alpino.models import CollectedFile, Document, MetadataValue, Utterance


class FoliaReader(Reader):
    """
    Class for converting FoLiA xml files to documents.
    """

    def read(self, collected_file: CollectedFile) -> Iterable[Document]:
        try:
            doc = folia.Document(string=collected_file.content,
                                 autodeclare=True,
                                 loadsetdefinitions=False)

            doc_metadata = self.get_metadata_dict(doc.metadata.items())

            yield Document(collected_file,
                           list(self.get_utterances(doc, doc_metadata)),
                           doc_metadata)
        except Exception as e:
            raise Exception(collected_file.relpath + "/" +
                            collected_file.filename) from e

    def get_utterances(self, doc, doc_metadata):
        """
        Read FoLiA file and return Alpino parsable sentences.
        """

        paragraph = None
        sentence = None
        words = []

        for word in doc.words():
            for ancestor in word.ancestors():
                if type(ancestor) is folia.Sentence:
                    if sentence != ancestor and words:
                        yield self.get_sentence(sentence, words, doc_metadata)
                        words = []

                    sentence = ancestor
                elif type(ancestor) is folia.Paragraph:
                    if paragraph != ancestor and words:
                        yield self.get_sentence(sentence, words, doc_metadata)
                        words = []

                    paragraph = ancestor
            words.append(word)

        if words:
            yield self.get_sentence(sentence, words, doc_metadata)

    def get_sentence(self, sentence, words, doc_metadata):
        """
        Convert a FoLiA sentence object to an Alpino compatible string to parse.
        """

        words = sentence.words()
        word_strings = map(lambda word: self.get_word_string(word), words)
        line = " ".join(filter(lambda word: word != '', word_strings))
        sentence_id = escape_id(sentence.id)
        sentence_metadata = self.get_metadata_dict(
            sentence.getmetadata().items(),
            doc_metadata)

        return Utterance(line, sentence_id, sentence_metadata, line)

    def get_word_string(self, word):
        """
        Get a string representing this word and any additional known properties to add to the parse.
        """

        try:
            text = word.text()
        except folia.NoSuchText:
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
