#!/usr/bin/env python3
"""
Module for converting FoLiA xml files to Alpino XML (input) files.
"""

from pynlpl.formats import folia

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
            doc = folia.Document(file=file_name)
            # doc.sentences() will skip quotes
            for paragraph in doc.paragraphs():
                for sentence in paragraph.sentences():
                    yield self.get_sentence(sentence)

    def get_sentence(self, sentence):
        """
        Convert a FoLiA sentence object to an Alpino compatible string to parse.
        """

        words = sentence.words()
        line = " ".join(self.get_word_string(word) for word in words)
        sentence_id = self.escape_id(sentence.id)
        metadata = {}

        return (line, sentence_id, metadata)

    def get_word_string(self, word):
        """
        Get a string representing this word and any additional known properties to add to the parse.
        """

        try:
            correction = word.getcorrection()
            text = word.text()
            return f"[ @add_lex {self.escape_word(correction.text())} {self.escape_word(text)} ]" \
                if correction.hastext() and correction.text() != text \
                else self.escape_word(text)
        except folia.NoSuchAnnotation:
            return self.escape_word(word.text())

    def escape_id(self, sentence_id):
        """
        Escape an id to be Alpino compatible.
        """

        return self.escape_word(sentence_id.replace("|", "_"))

    def escape_word(self, text):
        """
        Escape a word to be Alpino compatible.
        """

        return text.replace("[", "\\[").replace("]", "\\]")

    def test_file(self, file_name):
        """
        Determine whether this is a FoLiA XML file
        """

        with open(file_name) as file:
            for _ in range(0, 5):
                line = file.readline()
                if not line:
                    return False
                if '<FoLiA' in line:
                    return True
        
        return False
