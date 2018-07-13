#!/usr/bin/env python3
"""
Module for converting FoLiA xml files to Alpino XML (input) files.
"""

from pynlpl.formats import folia

from .alpino_brackets import escape_id, escape_word, format_add_lex, format_folia


class FoliaConverter:
    """
    Class for converting FoLiA xml files to Alpino XML (input) files.

    Arguments:
        wrapper --- Wrapper for communicating with the Alpino parser.
    """

    def __init__(self, wrapper):
        self.wrapper = wrapper

    def get_parses(self, file_names):
        """
        Get the parses and a wrapping treebank xml structure.
        """

        sentences = self.get_sentences(file_names)
        return self.wrapper.parse_lines(sentences)

    def get_sentences(self, file_names):
        """
        Read FoLiA files and return Alpino parsable sentences.
        """

        for file_name in file_names:
            doc = folia.Document(file=file_name, loadsetdefinitions=True)
            doc_metadata = self.get_metadata_dict(doc.metadata.items())

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
        line = " ".join(self.get_word_string(word) for word in words)
        sentence_id = escape_id(sentence.id)
        sentence_metadata = self.get_metadata_dict(
            sentence.getmetadata().items(),
            doc_metadata)

        return (line, sentence_id, doc_metadata, sentence_metadata)

    def get_word_string(self, word):
        """
        Get a string representing this word and any additional known properties to add to the parse.
        """

        text = word.text()

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
                    or filter_by[key] != value:
                metadata[key] = value
        return metadata

    def test_file(self, file_name):
        """
        Determine whether this is a FoLiA XML file
        """

        with open(file_name, encoding='utf-8') as file:
            for _ in range(0, 5):
                line = file.readline()
                if not line:
                    return False
                if '<FoLiA' in line:
                    return True

        return False
