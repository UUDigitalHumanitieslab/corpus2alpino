"""
Unit test for FoLiA to Alpino converter.
"""

import unittest

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
        sentences = list(converter.get_sentences(["tests/example.xml"]))

        expected_file = open("tests/example_expected.txt")
        try:
            self.assertListEqual(sentences, [line.rstrip(
                '\n') for line in expected_file.readlines()])
        finally:
            expected_file.close()
