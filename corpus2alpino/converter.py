#!/usr/bin/env python3
from .folia_converter import FoliaConverter
from .tei_converter import TeiConverter

class Converter:
    """
    Class for converting FoLiA and TEI xml files to Alpino XML (input) files.
    """

    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.converters = [FoliaConverter(wrapper), TeiConverter(wrapper)]

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
            for converter in self.converters:
                if converter.test_file(file_name):
                    for sentence in converter.get_sentences([file_name]):
                        yield sentence
