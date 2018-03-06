"""
Unit test for corpus to Alpino converter.
"""

import glob
import unittest
from os import path

from corpus2alpino.alpino_wrappers import AlpinoPassthroughWrapper
from corpus2alpino.converter import Converter


class TestCorpus2Alpino(unittest.TestCase):
    """
    Unit test class.
    """

    def test_get_sentences(self):
        """
        Test that sentences in a FoLiA/TEI file can be converted to Alpino-compatible input.
        """

        alpino = AlpinoPassthroughWrapper()
        converter = Converter(alpino)
        test_files = self.get_files('*.xml')

        sentences = list(self.get_lines(converter, test_files))

        self.assertGreaterEqual(
            len(sentences), 1, "Should have at least one test file")

        expected_lines = []
        for expected_filename in [f.replace('.xml', '_expected.txt') for f in test_files]:
            with open(expected_filename) as expected_file:
                expected_lines.extend([
                    line.rstrip('\n') for line in expected_file.readlines()
                ])

        self.assertListEqual(sentences, expected_lines)

    def get_lines(self, converter, files):
        for (line, sentence_id, metadata) in converter.get_sentences(files):
            for key in metadata:
                value = metadata[key].replace(
                    '\n', '\\n').replace('\r', '').strip()
                yield f'@{key}={value}'
            yield f'{sentence_id}|{line.strip()}'

    def get_files(self, pattern):
        return sorted(glob.glob(path.join(path.dirname(__file__), pattern)))
