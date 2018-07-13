"""
Unit test for corpus to Alpino converter.
"""

import glob
import unittest
from os import path

from corpus2alpino.paqu_writer import PaQuWriter
from corpus2alpino.converter import Converter


class TestCorpus2Alpino(unittest.TestCase):
    """
    Unit test class.
    """

    def test_get_sentences(self):
        """
        Test that sentences in a FoLiA/TEI file can be converted to Alpino-compatible input.
        """

        paqu_writer = PaQuWriter()
        converter = Converter(paqu_writer)
        test_files = self.get_files('*.xml')

        for test_file in test_files:
            print(test_file)
            expected_filename = test_file.replace('.xml', '_expected.txt')
            with open(expected_filename) as expected_file:
                self.assertListEqual(
                    list(self.get_parse_lines(converter, test_file)),
                    expected_file.readlines())

    def get_parse_lines(self, converter, test_file):
        for line in converter.get_parses([test_file]):
            for sub_line in line.split('\n'):
                yield sub_line + '\n'

    def get_files(self, pattern):
        return sorted(glob.glob(path.join(path.dirname(__file__), pattern)))
