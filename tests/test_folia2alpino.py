"""
Unit test for FoLiA to Alpino converter.
"""

import glob
import unittest
from os import path

from folia2alpino.alpino_wrappers import AlpinoPassthroughWrapper
from folia2alpino.converter import Converter


class TestFolia2Alpino(unittest.TestCase):
    """
    Unit test class.
    """

    def test_get_sentences(self):
        """
        Test that sentences in a FoLiA file can be converted to Alpino-compatible input.
        """

        alpino = AlpinoPassthroughWrapper()
        converter = Converter(alpino)
        sentences = list(self.get_lines(converter))

        self.assertGreaterEqual(
            len(sentences), 1, "Should have at least one test file")

        expected_lines = []
        for expected_filename in self.get_files("*_expected.txt"):
            with open(expected_filename) as expected_file:
                expected_lines.extend([
                    line.rstrip('\n') for line in expected_file.readlines()
                ])

        self.assertListEqual(sentences, expected_lines)

    def get_lines(self, converter):
        for (line, sentence_id, metadata) in converter.get_sentences(self.get_files('*.xml')):
            for key in metadata:
                value = metadata[key].replace(
                    '\n', '\\n').replace('\r', '').strip()
                yield f'@{key}={value}'
            yield f'{sentence_id}|{line.strip()}'

    def get_files(self, pattern):
        return sorted(glob.glob(path.join(path.dirname(__file__), pattern)))
